using System.Collections;
using UnityEditor.Search;
using UnityEngine;
using UnityEngine.Networking;

public class ConnectivityManager : MonoBehaviour
{
    [SerializeField]
    private UIController uiController;

    [SerializeField]
    private float checkInterval = 10f; // in seconds
    private string serverUrl = "https://rhino-good-jennet.ngrok-free.app/text-to-CLIP";

    private bool isInternetConnected = true;
    private bool isServerReachable = true;

    void Start()
    {
        StartCoroutine(CheckConnectivityLoop());
    }

    IEnumerator CheckConnectivityLoop()
    {
        while (true)
        {
            yield return StartCoroutine(CheckInternetAccess());
            if (isInternetConnected)
            {
                yield return StartCoroutine(CheckServerReachability());
            }

            yield return new WaitForSeconds(checkInterval);
        }
    }

    IEnumerator CheckInternetAccess()
    {
        if (Application.internetReachability == NetworkReachability.NotReachable)
        {
            if (isInternetConnected)
            {
                uiController.ShowWarning("No internet connection.");
                isInternetConnected = false;
            }
        }
        else
        {
            if (!isInternetConnected)
            {
                uiController.HideWarning();
                isInternetConnected = true;
            }
        }
        yield return null;
    }

    IEnumerator CheckServerReachability()
    {
        using (UnityWebRequest request = new UnityWebRequest(serverUrl, "POST"))
        {
            string testQuery = $"{{\"text\":\"chair\"}}";
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(testQuery);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.timeout = 5;
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
            {
                if (isServerReachable)
                {
                    uiController.ShowWarning("Remote server is unreachable");
                    isServerReachable = false;
                }
            }
            else
            {
                if (!isServerReachable)
                {
                    uiController.HideWarning();
                    isServerReachable = true;
                }
            }
        }
    }
}
