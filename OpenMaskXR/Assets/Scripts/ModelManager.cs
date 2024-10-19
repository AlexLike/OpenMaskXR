using System.Collections;
using UnityEngine;

public class ModelManager : MonoBehaviour
{
    [SerializeField] private GameObject dioramaTable;

    [Header("Spawn Settings")]
    [SerializeField] private float spawnDurationHeight = 1.5f;
    [SerializeField] private float spawnDurationRotation = 2.5f;

    private GameObject currentModel;
    private Coroutine currentAnimationCoroutine;

    private Vector3 initialPosition;
    private Vector3 targetPosition;
    private Quaternion initialRotation = Quaternion.identity;
    private Quaternion targetRotation = Quaternion.Euler(0, 90f, 0f); // Rotate 90 degrees around the Y-axis

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
            currentModel = Instantiate(model, initialPosition, initialRotation);

            // Spawn diorama table directly below model as child object
            float yMin = currentModel.GetComponentInChildren<Renderer>().bounds.min.y; // Note that this assumes the model has a single mesh renderer
            Vector3 tablePosition = new Vector3(currentModel.transform.position.x, yMin - 0.042f, currentModel.transform.position.z);
            Instantiate(dioramaTable, tablePosition, Quaternion.identity, currentModel.transform);

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
}
