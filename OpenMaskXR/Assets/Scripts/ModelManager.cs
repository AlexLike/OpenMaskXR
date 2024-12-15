using Leguar.TotalJSON;
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.XR.Interaction.Toolkit.Interactables;
using UnityEngine.XR.Interaction.Toolkit.Transformers;

public class ModelManager : MonoBehaviour
{
    public static int instanceCount = -1;
    public Transform qrCodeTransform;

    [SerializeField] private GameObject dioramaTable;
    [SerializeField] private UIController uiController;
    [SerializeField] private SliderHistogram sliderHistogram;

    [Header("Animation Settings")]
    [SerializeField] private float spawnDurationHeight = 1.5f;
    [SerializeField] private float spawnDurationRotation = 2.5f;
    [SerializeField] private float scalingDuration = 2.5f;

    private GameObject currentModel;
    private Coroutine currentAnimationCoroutine;
    private Coroutine currentScalingCoroutine;

    private int histogramBins;
    private Dictionary<int, double[]> featureVectors;
    private Dictionary<int, double> dotProducts;
    private float queryThreshold = 0.7f; // set by slider
    private Vector3 initialPosition;
    private Vector3 targetPosition;
    private Quaternion initialRotation = Quaternion.identity;
    private Quaternion targetRotation = Quaternion.Euler(0, 90f, 0f); // Rotate 90 degrees around the Y-axis
    private string lastQuery = "";
    private double[] queryVector;
    private Transform instances;

    private Vector3 lastDioramaPos;
    private float lastDioramaScale;
    private bool isModelLifesize = false;

    private bool passthroughActive = false;

    private void Start()
    {
        histogramBins = sliderHistogram.GetNumBins();

        // Initialize JSON feature vectors by loading them from streaming assets and saving them at persistentDataPath
        // in case not already found there
        SetupJSONFiles();
    }

    private void SetupJSONFiles()
    {
        BetterStreamingAssets.Initialize();

        // Get all files in the StreamingAssets directory
        string[] files = BetterStreamingAssets.GetFiles("\\", "*.json", SearchOption.AllDirectories);

        // Iterate over each file
        foreach (string relativePath in files)
        {
            // Compute the corresponding path in persistentDataPath
            string persistentFilePath = Path.Combine(Application.persistentDataPath, relativePath);
            //Debug.Log("Persistent file path: " + persistentFilePath);

            // Check if the file exists in persistentDataPath
            if (File.Exists(persistentFilePath))
            {
                //Debug.Log("File already exists in persistentDataPath: " + persistentFilePath);
                continue; // File already exists, skip to the next file
            }

            // Copy the file from streamingAssets to persistentDataPath
            string json = BetterStreamingAssets.ReadAllText(relativePath);
            File.WriteAllText(persistentFilePath, json);
        }
    }

    public void SpawnModel(GameObject model)
    {
        // Set initial position to be below the ground and in front of the XR camera
        Vector3 forwardDir = Camera.main.transform.forward;
        forwardDir.y = 0f; // ignore camera's vertical tilt
        forwardDir.Normalize();
        initialPosition = Camera.main.transform.position + forwardDir;
        initialPosition.y = -0.42f;

        // Set target position to be in front of the XR camera but above ground
        targetPosition = initialPosition;
        targetPosition.y = 1.2f;

        if (model != null)
        {
            currentModel = Instantiate(dioramaTable, initialPosition, Quaternion.identity);

            // Spawn model as a child of the diorama table
            Instantiate(model, initialPosition, initialRotation, currentModel.transform);

            // Set JSON feature vectors
            ParseJson(model.name);

            // Search grandchild called Instances
            foreach (Transform child in currentModel.transform)
            {
                Transform tmp = child.Find("Instances");
                if (tmp != null)
                {
                    instances = tmp;
                    break;
                }
            }

            foreach (Transform instance in instances)
            {
                // TODO: probably better to not do this at runtime and only use a fixed set of e.g. 10 materials
                Color randomColor = UnityEngine.Random.ColorHSV(0, 1, 0.75f, 0.75f, 0.6f, 0.6f, 0.42f, 0.42f);
                instance.GetComponent<Renderer>().material.SetColor("_BaseColor", randomColor);
                //instance.GetComponent<Renderer>().material.SetColor("_HighlightColor", randomColor);
            }

            if (currentAnimationCoroutine != null)
            {
                StopCoroutine(currentAnimationCoroutine);
            }
            currentAnimationCoroutine = StartCoroutine(AnimateModel(true));
        }
    }

    public void DespawnCurrentModel()
    {
        if (currentModel != null)
        {
            if (currentAnimationCoroutine != null)
            {
                StopCoroutine(currentAnimationCoroutine);
            }

            if (currentScalingCoroutine != null)
            {
                StopCoroutine(currentScalingCoroutine);
            }

            if (isModelLifesize)
            {
                // Just remove the model without any fancy animation
                Destroy(currentModel);
            }
            else
            {
                currentAnimationCoroutine = StartCoroutine(AnimateModel(false));
            }
        }
    }

    private IEnumerator AnimateModel(bool spawn)
    {
        float elapsedTime = 0f;

        Vector3 startPos = currentModel.transform.position;
        Vector3 endPos = spawn ? targetPosition : initialPosition;

        Quaternion startRot = spawn ? currentModel.transform.rotation : targetRotation;
        Quaternion endRot = spawn ? targetRotation : currentModel.transform.rotation;

        while (elapsedTime < spawnDurationHeight || elapsedTime < spawnDurationRotation)
        {
            elapsedTime += Time.deltaTime;

            if (elapsedTime < spawnDurationHeight)
            {
                // Easen only the Y position between the start and end points
                float newY = EasingFunction.EaseInOutCubic(startPos.y, endPos.y, elapsedTime / spawnDurationHeight);
                currentModel.transform.position = new Vector3(currentModel.transform.position.x, newY, currentModel.transform.position.z);
            }

            if (elapsedTime < spawnDurationRotation)
            {
                // Lerp rotation from start to end
                currentModel.transform.rotation = Quaternion.Slerp(startRot, endRot, EasingFunction.EaseInOutSine(0f, 1f, elapsedTime / spawnDurationRotation));
            }

            yield return null;
        }

        // Ensure final position and rotation are set correctly
        currentModel.transform.SetPositionAndRotation(new Vector3(currentModel.transform.position.x, endPos.y, currentModel.transform.position.z), endRot);

        // By default we first animate to diorama mode. If the user previously set lifesize mode, animate to lifesize mode
        if (isModelLifesize)
        {
            SetModelSize(true);
        }

        if (!spawn)
        {
            Destroy(currentModel);
        }
    }

    public void SetModelSize(bool lifesize)
    {
        isModelLifesize = lifesize;

        // Don't show the model itself when in passthrough && lifesize mode
        GameObject modelMesh = UnityUtils.FindChild(currentModel.transform, "default");
        if (modelMesh != null && modelMesh.GetComponent<MeshRenderer>() != null)
        {
            modelMesh.GetComponent<MeshRenderer>().enabled = !lifesize || !passthroughActive;
        }

        // We disable at the start when scaling up, and at the end when scaling down
        if (lifesize)
        {
            currentModel.GetComponent<CapsuleCollider>().enabled = false;
            currentModel.GetComponent<XRGrabInteractable>().enabled = false;
            currentModel.GetComponent<XRGeneralGrabTransformer>().enabled = false;
        }

        // In case we are already scaling, stop the current coroutine
        if (currentScalingCoroutine != null)
        {
            StopCoroutine(currentScalingCoroutine);
        }

        // Animate scaling of model to/from lifesize
        if (lifesize)
        {
            currentScalingCoroutine = StartCoroutine(AnimateModelToLifesize());
        }
        else
        {
            currentScalingCoroutine = StartCoroutine(AnimateModelToDioramaSize());
        }
    }

    private IEnumerator AnimateModelToLifesize()
    {
        lastDioramaPos = currentModel.transform.position;
        lastDioramaScale = currentModel.transform.localScale.x;

        float elapsedTime = 0f;
        float startScale = currentModel.transform.localScale.x; // scale is uniform in all axis
        float endScale = 10f;

        // If set and in MR mode use QR code transform, otherwise just descend to ground
        Vector3 startPos = currentModel.transform.position;
        Vector3 endPos;
        Quaternion startRot = currentModel.transform.rotation;
        Quaternion endRot;
        // A bit hacky, but we only want to use the QR code transform if we display the custom scan
        if (qrCodeTransform != null && uiController.queryMenuTitle.text == "Custom Scan")
        {
            endPos = qrCodeTransform.position;

            // Subtract local offset of instances to parent for endPos
            GameObject instances = UnityUtils.FindChild(currentModel.transform, "Instances");
            endPos -= instances.transform.localPosition * endScale;
            endRot = qrCodeTransform.rotation;
        }
        else
        {
            endPos = currentModel.transform.position;
            endPos.y = 0f;
            endRot = currentModel.transform.rotation;
        }

        // Model descends to ground in first phase and potentially rotates
        while (elapsedTime < scalingDuration / 2)
        {
            elapsedTime += Time.deltaTime;
            currentModel.transform.position = EasingFunction.Ease(startPos, endPos, 2 * elapsedTime / scalingDuration, EaseType.EaseInOutSine);

            if (qrCodeTransform != null)
            {
                currentModel.transform.rotation = Quaternion.Slerp(startRot, endRot, EasingFunction.EaseInOutSine(0f, 1f, 2 * elapsedTime / scalingDuration));
            }
            yield return null;
        }

        // Disable diorama table
        currentModel.transform.Find("Model").GetComponent<MeshRenderer>().enabled = false;

        // Model scales up in second phase
        while (elapsedTime < scalingDuration)
        {
            elapsedTime += Time.deltaTime;
            float newScale = EasingFunction.EaseInOutSine(startScale, endScale, (2 * elapsedTime - scalingDuration) / scalingDuration);
            currentModel.transform.localScale = new Vector3(newScale, newScale, newScale);
            yield return null;
        }

        // Ensure final scale is set correctly
        currentModel.transform.localScale = new Vector3(endScale, endScale, endScale);

        // In case of custom scan, additionally fix the translation to Marker
        if (uiController.queryMenuTitle.text == "Custom Scan")
        {
            GameObject marker = UnityUtils.FindChild(currentModel.transform, "Marker");
            Vector3 markerOffset = qrCodeTransform.position - marker.transform.position;
            Vector3 start = currentModel.transform.position;
            Vector3 end = currentModel.transform.position + markerOffset;

            while (elapsedTime < scalingDuration + 1)
            {
                elapsedTime += Time.deltaTime;
                currentModel.transform.position = EasingFunction.Ease(start, end, elapsedTime - scalingDuration, EaseType.EaseInOutSine);
                yield return null;
            }

            currentModel.transform.position = end;
        }
    }

    private IEnumerator AnimateModelToDioramaSize()
    {

        float elapsedTime = 0f;
        float startScale = currentModel.transform.localScale.x; // scale is uniform in all axis
        float endScale = lastDioramaScale;

        Vector3 startPos = currentModel.transform.position;
        Vector3 endPos = startPos;
        endPos.y = lastDioramaPos.y;

        // Model scales down in first phase
        while (elapsedTime < scalingDuration / 2)
        {
            elapsedTime += Time.deltaTime;
            float newScale = EasingFunction.EaseInOutSine(startScale, endScale, 2 * elapsedTime / scalingDuration);
            currentModel.transform.localScale = new Vector3(newScale, newScale, newScale);
            yield return null;
        }

        // Ensure scale is set correctly
        currentModel.transform.localScale = new Vector3(endScale, endScale, endScale);

        // Enable diorama table
        currentModel.transform.Find("Model").GetComponent<MeshRenderer>().enabled = true;

        // Model ascends in second phase
        while (elapsedTime < scalingDuration)
        {
            elapsedTime += Time.deltaTime;
            currentModel.transform.position = EasingFunction.Ease(startPos, endPos, (2 * elapsedTime - scalingDuration) / scalingDuration, EaseType.EaseInOutSine);
            yield return null;
        }

        // Re-enable XR manipulations
        currentModel.GetComponent<CapsuleCollider>().enabled = true;
        currentModel.GetComponent<XRGrabInteractable>().enabled = true;
        currentModel.GetComponent<XRGeneralGrabTransformer>().enabled = true;
    }

    public void SetQueryThreshold(float newThreshold)
    {
        queryThreshold = newThreshold / histogramBins; // normalize threshold to [0, 1]
        QueryModel(lastQuery);
    }

    public void QueryModel(string query)
    {
        if (query == lastQuery)
        {
            if (queryVector == null)
            {
                Debug.LogWarning("Still waiting for server response...");
                return;
            }
            // Don't have to do server access for getting embedding
            List<int> matchingKeys = GetKeysByDotProductThreshold(queryThreshold);

            //Debug.Log("Adjusting threshold to " + queryThreshold);
            //Debug.Log($"Matching keys: {string.Join(", ", matchingKeys)}");

            uiController.UpdateQueryMenuInfo(queryThreshold, matchingKeys.Count);

            // Highlight the matching instances
            foreach (Transform instance in instances)
            {
                int instanceId = int.Parse(instance.name);
                instance.GetComponent<Renderer>().enabled = matchingKeys.Contains(instanceId);
            }
        }
        else
        {
            queryVector = null;
            lastQuery = query;

            Debug.Log("Requesting feature vector for query: '" + query + "' from server");
            // API call to get feature vector from query and highlight matching instances when done
            StartCoroutine(TextQuery("https://rhino-good-jennet.ngrok-free.app/text-to-CLIP", $"{{\"text\":\"{query}\"}}"));


            // For testing purposes, use the feature vector of the first instance
            /*******************************************************************/
            //Debug.LogWarning("PURPOSEFULLY NOT QUERYING SERVER!");
            //queryVector = featureVectors[0];
            //Normalize(queryVector);
            //ComputeDotProducts(queryVector);
            //List<int> matchingKeys = GetKeysByDotProductThreshold(queryThreshold);
            ////Debug.Log($"Matching keys: {string.Join(", ", matchingKeys)}");

            //// Highlight the matching instances
            //foreach (Transform instance in instances)
            //{
            //    int instanceId = int.Parse(instance.name);
            //    instance.GetComponent<Renderer>().enabled = matchingKeys.Contains(instanceId);
            //}

            //StartCoroutine(uiController.DemonstrateSlider());
            /*******************************************************************/
        }
    }

    private IEnumerator TextQuery(string url, string text)
    {
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(text);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.timeout = 10;
            request.SetRequestHeader("Content-Type", "application/json");

            // Send the request and wait for a response
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Response: " + request.downloadHandler.text);

                // Parse response JSON to get the feature vector
                JSON responseJson = JSON.ParseString(request.downloadHandler.text);
                queryVector = responseJson.GetJArray("CLIP_embedding").AsDoubleArray();
                Normalize(queryVector);

                Debug.Log("Received feature vector: " + string.Join(", ", queryVector));

                // Compare the query vector to all feature vectors in the JSON file
                // Precompute dot products
                ComputeDotProducts(queryVector);

                //List<int> matchingKeys = GetKeysByFraction(queryVector, queryThreshold);
                List<int> matchingKeys = GetKeysByDotProductThreshold(queryThreshold);
                //Debug.Log($"Matching keys: {string.Join(", ", matchingKeys)}");

                // Highlight the matching instances
                foreach (Transform instance in instances)
                {
                    int instanceId = int.Parse(instance.name);
                    instance.GetComponent<Renderer>().enabled = matchingKeys.Contains(instanceId);
                }

                StartCoroutine(uiController.DemonstrateSlider());
            }
            else
            {
                Debug.LogError("Error: " + request.error);
            }

            request.Dispose();
        }
    }

    private void ParseJson(string scanName)
    {
        featureVectors = new Dictionary<int, double[]>();
        string path = Path.Combine(Application.persistentDataPath, $"{scanName}.json");
        if (File.Exists(path))
        {
            ProcessJson(File.ReadAllText(path));
        }
        else
        {
            Debug.LogWarning("No JSON file found for scan: " + scanName);
        }
    }

    private void Normalize(double[] vec)
    {
        double normSquared = ComputeDotProduct(vec, vec);

        // If instance is zero vector, do nothing
        if (normSquared == 0)
        {
            return;
        }

        double norm = Math.Sqrt(normSquared);
        for (int i = 0; i < vec.Length; i++)
        {
            vec[i] /= norm;
        }
    }

    private void ProcessJson(string json)
    {
        var jsonObject = JSON.ParseString(json);
        instanceCount = jsonObject.Keys.Length;

        foreach (string key in jsonObject.Keys)
        {
            double[] vec = jsonObject.GetJArray(key).AsDoubleArray();
            Normalize(vec);
            featureVectors.Add(int.Parse(key), vec);
        }
    }

    public List<int> GetKeysByFraction(float threshold)
    {
        // Sort the dictionary by dot product result in descending order
        var sortedResults = dotProducts
            .OrderByDescending(pair => pair.Value)
            .ToList();

        // Calculate the number of entries to return based on the threshold fraction
        int countToReturn = (int)(sortedResults.Count * (1 - threshold));

        // Extract the top fraction of keys and return them
        List<int> topKeys = sortedResults
            .Take(countToReturn)
            .Select(pair => pair.Key)
            .ToList();

        return topKeys;
    }

    // Should be only called once per query
    void ComputeDotProducts(double[] inputVector)
    {
        dotProducts = new Dictionary<int, double>();

        foreach (var entry in featureVectors)
        {
            int key = entry.Key;
            double[] vector = entry.Value;

            if (vector.Length == inputVector.Length) // Ensure vectors are of the same dimension
            {
                double dotProduct = ComputeDotProduct(inputVector, vector);
                dotProducts[key] = dotProduct;
            }
            else
            {
                Debug.LogWarning($"Vector size mismatch for key {key}");
            }
        }

        int binCount;
        float[] binValues = new float[histogramBins];
        // Could also make this run in O(n) but since n is small, this is fine
        // Note that we only look at the treshold range [0,1] and not [-1, 1]
        for (int i = 0; i < histogramBins; i++)
        {
            binCount = 0;
            float lowerThreshold = i / (float)histogramBins;
            float upperThreshold = (i + 1) / (float)histogramBins;

            foreach (var entry in dotProducts)
            {
                if (entry.Value >= lowerThreshold && entry.Value < upperThreshold)
                {
                    binCount++;
                }
            }

            binValues[i] = binCount;
        }

        //Debug.Log($"Histogram values: {string.Join(", ", binValues)}");

        float maxCount = binValues.Max();
        for (int i = 0; i < histogramBins; i++)
        {
            binValues[i] /= maxCount;
        }
        sliderHistogram.UpdateBinValues(binValues);
    }

    public List<int> GetKeysByDotProductThreshold(float threshold)
    {
        List<int> resultKeys = new List<int>();

        foreach (var entry in dotProducts)
        {
            if (entry.Value >= threshold)
            {
                resultKeys.Add(entry.Key);
            }
        }

        return resultKeys;
    }

    public void SetPassthroughActive(bool active)
    {
        passthroughActive = active;
    }

    private double ComputeDotProduct(double[] vector1, double[] vector2)
    {
        double dotProduct = 0.0f;
        for (int i = 0; i < vector1.Length; i++)
        {
            dotProduct += vector1[i] * vector2[i];
        }
        return dotProduct;
    }
}
