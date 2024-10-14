using System.Collections;
using UnityEngine;

public class ModelManager : MonoBehaviour
{
    [SerializeField] private GameObject model;
    [SerializeField] private float spawnDurationHeight = 1.5f;
    [SerializeField] private float spawnDurationRotation = 2.5f;

    private Vector3 initialPosition;
    private Vector3 targetPosition;
    private Quaternion initialRotation;
    private Quaternion targetRotation;

    private void Start()
    {
        if (model != null)
        {
            initialPosition = model.transform.position;
            initialPosition.y = -0.42f;

            targetPosition = model.transform.position;
            targetPosition.y = 1.2f;

            initialRotation = model.transform.rotation;
            targetRotation = initialRotation * Quaternion.Euler(0, 90f, 0f); // Rotate 90 degrees around the Y-axis
        }
    }

    public void Animate(bool spawn)
    {
        model.SetActive(true);

        if (model != null)
        {
            StartCoroutine(AnimateModel(spawn));
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
                model.transform.position = new Vector3(model.transform.position.x, newY, model.transform.position.z);
            }

            if (elapsedTime < spawnDurationRotation)
            {
                // Lerp rotation from start to end
                model.transform.rotation = Quaternion.Slerp(startRot, endRot, EasingFunction.EaseInOutSine(0f, 1f, elapsedTime / spawnDurationRotation));
            }

            yield return null;
        }

        // Ensure final position and rotation are set correctly
        model.transform.position = new Vector3(model.transform.position.x, endPos.y, model.transform.position.z);
        model.transform.rotation = endRot;

        if (!spawn)
        {
            model.SetActive(false);
        }
    }
}
