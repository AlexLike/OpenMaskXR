using UnityEngine;

public class ObjectHighlighter : MonoBehaviour
{
    public Material glowMaterial;          // Assign a glow material in the Inspector
    public float maxIntensity = 5f;        // Maximum glow intensity
    public float minIntensity = 1f;        // Minimum glow intensity
    public float frequency = 1f;           // Frequency for sinusoidal glow
    private GameObject highlightedObject;  // The object currently being highlighted
    private Material originalMaterial;     // To store the original material of the object

    void Update()
    {
        // If there’s a highlighted object, apply a sinusoidal glow effect
        if (highlightedObject != null)
        {
            float emissionIntensity = minIntensity + (Mathf.Sin(Time.time * frequency) + 1) / 2 * (maxIntensity - minIntensity);
            glowMaterial.SetFloat("_EmissionIntensity", emissionIntensity);
        }
    }

    // Method to set the object to highlight
    public void SetHighlightedObject(GameObject targetObject)
    {
        // Reset previous object, if any
        if (highlightedObject != null)
        {
            RemoveHighlight();
        }

        // Store the new object
        highlightedObject = targetObject;
        Renderer renderer = highlightedObject.GetComponent<Renderer>();

        if (renderer != null)
        {
            // Store the original material to restore later
            originalMaterial = renderer.material;

            // Apply the glow material
            renderer.material = glowMaterial;
        }
    }

    // Method to remove the highlight from the current object
    public void RemoveHighlight()
    {
        if (highlightedObject != null && originalMaterial != null)
        {
            // Restore the original material
            Renderer renderer = highlightedObject.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material = originalMaterial;
            }

            // Clear the highlighted object
            highlightedObject = null;
        }
    }
}
