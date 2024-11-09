using Leguar.TotalJSON;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class ModelManager : MonoBehaviour
{

    [SerializeField] private GameObject dioramaTable;

    [Header("Spawn Settings")]
    [SerializeField] private float spawnDurationHeight = 1.5f;
    [SerializeField] private float spawnDurationRotation = 2.5f;

    private GameObject currentModel;
    private Coroutine currentAnimationCoroutine;

    private Dictionary<int, float[]> featureVectors;

    private float queryThreshold = 0.7f; // set by slider
    private Vector3 initialPosition;
    private Vector3 targetPosition;
    private Quaternion initialRotation = Quaternion.identity;
    private Quaternion targetRotation = Quaternion.Euler(0, 90f, 0f); // Rotate 90 degrees around the Y-axis
    private string lastQuery = "";

    private void Start()
    {
        ParseJson();
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
            float yMaxParent = currentModel.GetComponentInChildren<Renderer>().bounds.max.y;
            float yMinChild = model.GetComponentInChildren<Renderer>().bounds.min.y;
            Vector3 modelPosition = new Vector3(initialPosition.x, yMaxParent - yMinChild, initialPosition.z);

            // Spawn model as a child of the diorama table
            Instantiate(model, modelPosition, initialRotation, currentModel.transform);


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
            currentAnimationCoroutine = StartCoroutine(AnimateModel(false));
        }
    }

    private IEnumerator AnimateModel(bool spawn)
    {
        float elapsedTime = 0f;

        Vector3 startPos = spawn ? initialPosition : targetPosition;
        Vector3 endPos = spawn ? targetPosition : initialPosition;

        Quaternion startRot = spawn ? initialRotation : targetRotation;
        Quaternion endRot = spawn ? targetRotation : initialRotation;

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

        if (!spawn)
        {
            Destroy(currentModel);
        }
    }

    public void SetQueryThreshold(float newThreshold)
    {
        queryThreshold = newThreshold;
        QueryModel(lastQuery);
    }

    public void QueryModel(string query)
    {
        lastQuery = query;

        // Convert query to a feature vector
        // For now, we'll just use the first vector in the dummy JSON file
        float[] queryVector = featureVectors[0];

        // Compare the query vector to all feature vectors in the JSON file
        List<int> matchingKeys = GetKeysByDotProductThreshold(queryVector, queryThreshold);

        // Print the matching keys
        Debug.Log($"Matching keys: {string.Join(", ", matchingKeys)}");
    }

    private void ParseJson()
    {
        // Load a dummy file for now
        featureVectors = new Dictionary<int, float[]>();
        string path = Path.Combine(Application.streamingAssetsPath, "clip_example.json");
        if (File.Exists(path))
        {
            string json = File.ReadAllText(path);
            JSON jsonObject = JSON.ParseString(json);
            foreach (string key in jsonObject.Keys)
            {
                float[] vec = jsonObject.GetJArray(key).AsFloatArray();
                featureVectors.Add(int.Parse(key), vec);
            }
        }
        else
        {
            Debug.LogError("Cannot find JSON file at path: " + path);
        }
    }

    public List<int> GetKeysByDotProductThreshold(float[] inputVector, float threshold)
    {
        List<int> resultKeys = new List<int>();

        foreach (var entry in featureVectors)
        {
            int key = entry.Key;
            float[] vector = entry.Value;

            if (vector.Length == inputVector.Length) // Ensure vectors are of the same dimension
            {
                float dotProduct = ComputeDotProduct(inputVector, vector);
                if (dotProduct > threshold)
                {
                    resultKeys.Add(key);
                }
            }
            else
            {
                Debug.LogWarning($"Vector size mismatch for key {key}");
            }
        }

        return resultKeys;
    }

    private float ComputeDotProduct(float[] vector1, float[] vector2)
    {
        float dotProduct = 0.0f;
        for (int i = 0; i < vector1.Length; i++)
        {
            dotProduct += vector1[i] * vector2[i];
        }
        return dotProduct;
    }
}
