using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(RectTransform))]
public class SliderHistogram : MonoBehaviour
{

    [SerializeField]
    private Slider slider;

    [SerializeField]
    private Color binColorHighlighted = Color.blue;

    [SerializeField]
    private Color binColor = Color.gray;

    private RectTransform rectTransform;
    private int numBins;
    private float[] binValues;
    private GameObject[] binObjects;

    void Start()
    {
        Initialize();
    }

    public int GetNumBins()
    {
        return (int)slider.maxValue;
    }

    public void UpdateBinValues(float[] values)
    {
        binValues = values;
        DrawHistogram();
    }

    void Initialize()
    {
        if (rectTransform != null)
            return; // Already initialized

        rectTransform = GetComponent<RectTransform>();
        numBins = GetNumBins();

        binObjects = new GameObject[numBins];
        for (int i = 0; i < numBins; i++)
        {
            GameObject bin = new GameObject($"Bin_{i}", typeof(Image));
            bin.transform.SetParent(rectTransform, false);
            bin.GetComponent<Image>().color = binColor;
            bin.GetComponent<Image>().raycastTarget = false;
            binObjects[i] = bin;
        }

        HideBins();
    }

    public void HideBins()
    {
        if (binObjects == null)
            return;

        foreach (GameObject bin in binObjects)
            bin.SetActive(false);
    }

    public void ShowBins()
    {
        if (binObjects == null)
            return;

        foreach (GameObject bin in binObjects)
            bin.SetActive(true);
    }

    /* For testing purposes */
    void GenerateRandomHistogram()
    {
        binValues = new float[numBins];
        for (int i = 0; i < numBins; i++)
        {
            binValues[i] = Random.Range(0f, 1f);
        }
    }

    void DrawHistogram()
    {
        if (binObjects == null)
            Initialize();

        float binWidth = rectTransform.rect.width / numBins;  // Calculate bin width based on container

        for (int i = 0; i < numBins; i++)
        {
            RectTransform binRect = binObjects[i].GetComponent<RectTransform>();
            binRect.anchorMin = new Vector2(i * binWidth / rectTransform.rect.width, 0);
            binRect.anchorMax = new Vector2((i + 1) * binWidth / rectTransform.rect.width, 0);
            binRect.sizeDelta = new Vector2(1, binValues[i] * rectTransform.rect.height / 2); // only fill half of slider
            binRect.pivot = new Vector2(0.5f, 0);  // Align to bottom
        }

        ShowBins();

        UpdateHistogramColor();
    }

    void UpdateHistogramColor()
    {
        for (int i = 0; i < numBins; i++)
        {
            if (i < (int)slider.value)
                binObjects[i].gameObject.GetComponent<Image>().color = binColor;
            else
                binObjects[i].gameObject.GetComponent<Image>().color = binColorHighlighted;
        }
    }

    public void OnSliderValueChanged()
    {
        UpdateHistogramColor();
    }
}
