using UnityEngine;

public class SinusoidalGlow : MonoBehaviour
{
    public Material glowMaterial;           // Assign the material with the glowing shader in the Inspector
    public float maxIntensity = 5f;         // Maximum intensity of the glow
    public float minIntensity = 1f;         // Minimum intensity of the glow
    public float frequency = 1f;            // Frequency of the sine wave (how fast it oscillates)

    void Update()
    {
        // Calculate the sinusoidal emission intensity
        float emissionIntensity = minIntensity + (Mathf.Sin(Time.time * frequency) + 1) / 2 * (maxIntensity - minIntensity);

        // Set the emission intensity on the material
        glowMaterial.SetFloat("_EmissionIntensity", emissionIntensity);
    }
}
