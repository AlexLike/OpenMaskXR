using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class UIController : MonoBehaviour
{
    [SerializeField] private ModelManager modelManager;

    [Header("Home Menu")]
    [SerializeField] private GameObject homeMenuParent;

    [Header("Query Menu")]
    public TextMeshProUGUI queryMenuTitle;
    [SerializeField] private GameObject queryMenuParent;
    [SerializeField] private GameObject queryMenuSliderScreen;
    [SerializeField] private GameObject queryMenuPromptScreen;
    [SerializeField] private TextMeshProUGUI queryMenuPlaceholderText;
    [SerializeField] private Button queryMenuVoiceInputButton;
    [SerializeField] private Slider queryMenuSlider;
    [SerializeField] private TextMeshProUGUI nrOfMatchingInstances;
    [SerializeField] private TextMeshProUGUI currentTreshold;
    [SerializeField] private SliderHistogram sliderHistogram;

    [Header("Warnings Panel")]
    [SerializeField] private GameObject warningsPanelParent;
    [SerializeField] private TextMeshProUGUI warningsPanelText;

    [Header("Debug Log Panel")]
    [SerializeField] private GameObject debugLogPanelParent;

    [Header("Animation Settings")]
    [SerializeField] private float fadeDuration = 0.5f;
    [SerializeField] private float sliderDemonstrationDuration = 2f;

    public void ToggleQueryMenuVisibility(bool isVisible)
    {
        CanvasGroup[] canvasGroups = queryMenuParent.GetComponentsInChildren<CanvasGroup>();
        StartCoroutine(FadeMenu(queryMenuParent, canvasGroups, isVisible));
    }

    public void InitQueryMenu(string modelName)
    {
        ToggleQueryMenuVisibility(true);
        queryMenuTitle.text = modelName;
        QueryMenuToggleSliderScreen(false);
    }

    public void QueryMenuToggleSliderScreen(bool isSliderScreen)
    {
        queryMenuSliderScreen.SetActive(isSliderScreen);
        queryMenuPromptScreen.SetActive(!isSliderScreen);

        if (!isSliderScreen)
        {
            if (ModelManager.instanceCount > 0)
                queryMenuPlaceholderText.text = $"Query {ModelManager.instanceCount} objects...";
            else
                queryMenuPlaceholderText.text = "Enter a query here...";

            sliderHistogram.HideBins();
        }
    }

    public void ToggleDebugLogVisibility(bool isVisible)
    {
        debugLogPanelParent.SetActive(isVisible);
    }

    public void SetVoiceButtonColor(bool isRed)
    {
        var colors = queryMenuVoiceInputButton.colors;
        colors.normalColor = isRed ? Color.red : new Color(48 / 255f, 48 / 255f, 48 / 255f);
        queryMenuVoiceInputButton.colors = colors;
    }

    public void UpdateQueryMenuInfo(float threshold, int instanceCount)
    {
        currentTreshold.text = $"{threshold:F3}"; // Show only three decimal places
        nrOfMatchingInstances.text = instanceCount.ToString();
    }

    public void ToggleHomeMenuVisibility(bool isVisible)
    {
        CanvasGroup[] canvasGroups = homeMenuParent.GetComponentsInChildren<CanvasGroup>();
        StartCoroutine(FadeMenu(homeMenuParent, canvasGroups, isVisible));
    }

    public void ShowWarning(string warning)
    {
        warningsPanelText.text = warning;

        CanvasGroup[] canvasGroups = warningsPanelParent.GetComponentsInChildren<CanvasGroup>();
        StartCoroutine(FadeMenu(warningsPanelParent, canvasGroups, true));
    }

    public void HideWarning()
    {
        CanvasGroup[] canvasGroups = warningsPanelParent.GetComponentsInChildren<CanvasGroup>();
        StartCoroutine(FadeMenu(warningsPanelParent, canvasGroups, false));
    }

    public IEnumerator DemonstrateSlider()
    {
        float elapsedTime = 0f;
        float min = queryMenuSlider.minValue;
        float max = queryMenuSlider.maxValue;
        float lower = min + 0.25f * (max - min);
        float upper = min + 0.75f * (max - min);
        float middle = (max + min) / 2f;

        // Start threshold at 0.5f, then move to 0f, 1f and back to 0.5f
        while (elapsedTime < sliderDemonstrationDuration)
        {
            elapsedTime += Time.deltaTime;

            if (elapsedTime < sliderDemonstrationDuration / 3f)
            {
                queryMenuSlider.value = EasingFunction.EaseInOutCubic(middle, lower, 3f * elapsedTime / sliderDemonstrationDuration);
            }
            else if (elapsedTime < 2f * sliderDemonstrationDuration / 3f)
            {
                queryMenuSlider.value = EasingFunction.EaseInOutCubic(lower, upper, (elapsedTime - sliderDemonstrationDuration / 3) / (sliderDemonstrationDuration / 3));
            }
            else
            {
                queryMenuSlider.value = EasingFunction.EaseInOutCubic(upper, middle, (elapsedTime - 2 * sliderDemonstrationDuration / 3) / (sliderDemonstrationDuration / 3));
            }

            yield return null;
        }
    }

    private IEnumerator FadeMenu(GameObject parent, CanvasGroup[] canvasGroups, bool isVisible)
    {
        // Delay the fade-in animation by 1 second to allow the spawning/despawning of the model to play first
        if (isVisible)
            yield return new WaitForSeconds(1f);

        if (isVisible)
            parent.SetActive(true);

        float startAlpha = isVisible ? 0f : 1f;
        float endAlpha = isVisible ? 1f : 0f;
        float elapsedTime = 0f;

        // Gradually fade alpha over time
        while (elapsedTime < fadeDuration)
        {
            elapsedTime += Time.deltaTime;
            float currentAlpha = Mathf.Lerp(startAlpha, endAlpha, elapsedTime / fadeDuration);

            foreach (CanvasGroup cg in canvasGroups)
            {
                cg.alpha = currentAlpha;
            }

            yield return null;
        }

        // Ensure the final alpha is set properly
        foreach (CanvasGroup cg in canvasGroups)
        {
            cg.alpha = endAlpha;
            cg.interactable = isVisible;
            cg.blocksRaycasts = isVisible;
        }

        // Deactivate the menu if it is no longer visible
        if (!isVisible)
            parent.SetActive(false);
    }
}
