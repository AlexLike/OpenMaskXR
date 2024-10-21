using System.Collections;
using TMPro;
using UnityEngine;

public class UIController : MonoBehaviour
{
    [Header("Home Menu")]
    [SerializeField] private GameObject homeMenuParent;

    [Header("Query Menu")]
    [SerializeField] private GameObject queryMenuParent;
    [SerializeField] private TextMeshProUGUI queryMenuTitle;
    [SerializeField] private TextMeshProUGUI queryMenuPreviewText;
    [SerializeField] private GameObject queryMenuSliderScreen;
    [SerializeField] private GameObject queryMenuPromptScreen;

    [Header("Animation Settings")]
    [SerializeField] private float fadeDuration = 0.5f;

    public void ToggleQueryMenuVisibility(bool isVisible)
    {
        CanvasGroup[] canvasGroups = queryMenuParent.GetComponentsInChildren<CanvasGroup>();
        StartCoroutine(FadeMenu(queryMenuParent, canvasGroups, isVisible));
    }

    public void InitQueryMenu(string modelName)
    {
        ToggleQueryMenuVisibility(true);
        queryMenuTitle.text = modelName;
        queryMenuPreviewText.text = "Query 16 objects...";
        QueryMenuToggleSliderScreen(false);
    }

    public void QueryMenuToggleSliderScreen(bool isSliderScreen)
    {
        queryMenuSliderScreen.SetActive(isSliderScreen);
        queryMenuPromptScreen.SetActive(!isSliderScreen);

        if (!isSliderScreen)
            queryMenuPreviewText.text = "Query 16 objects...";
    }

    public void ToggleHomeMenuVisibility(bool isVisible)
    {
        CanvasGroup[] canvasGroups = homeMenuParent.GetComponentsInChildren<CanvasGroup>();
        StartCoroutine(FadeMenu(homeMenuParent, canvasGroups, isVisible));
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
