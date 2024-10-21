using TMPro;
using UnityEngine;
using UnityEngine.UI;
using Whisper.Utils;

namespace Whisper.Samples
{
    /// <summary>
    /// Stream transcription from microphone input.
    /// </summary>
    public class StreamingMic : MonoBehaviour
    {
        public WhisperManager whisper;
        public MicrophoneRecord microphoneRecord;
        public UIController uiController;

        [Header("UI")]
        [SerializeField]
        private Button button;
        [SerializeField]
        private TextMeshProUGUI previewText;
        [SerializeField]
        private TextMeshProUGUI sliderText;
        private WhisperStream _stream;

        [SerializeField]
        private Color standardButtonColor = Color.black;

        [SerializeField]
        private Color recordingButtonColor = Color.red;

        private async void Start()
        {
            _stream = await whisper.CreateStream(microphoneRecord);
            _stream.OnResultUpdated += OnResult;
            _stream.OnSegmentUpdated += OnSegmentUpdated;
            _stream.OnSegmentFinished += OnSegmentFinished;
            _stream.OnStreamFinished += OnFinished;

            microphoneRecord.OnRecordStop += OnRecordStop;
            button.onClick.AddListener(OnButtonPressed);
        }

        private void OnButtonPressed()
        {
            if (!microphoneRecord.IsRecording)
            {
                _stream.StartStream(); // TODO: check if this needs to be stopped somewhere as well
                microphoneRecord.StartRecord();
            }
            else
                microphoneRecord.StopRecord();

            var colors = button.colors;
            colors.normalColor = microphoneRecord.IsRecording ? recordingButtonColor : standardButtonColor;
            button.colors = colors;
        }

        private void OnRecordStop(AudioChunk recordedAudio)
        {
            var colors = button.colors;
            colors.normalColor = standardButtonColor;
            button.colors = colors;
        }

        private void OnResult(string result)
        {
            string transcription = result.Replace("[BLANK_AUDIO]", "");
            previewText.text = transcription;
        }

        private void OnSegmentUpdated(WhisperResult segment)
        {
            print($"Segment updated: {segment.Result}");
        }

        private void OnSegmentFinished(WhisperResult segment)
        {
            print($"Segment finished: {segment.Result}");
        }

        private void OnFinished(string finalResult)
        {
            string transcription = finalResult.Replace("[BLANK_AUDIO]", "").Trim();

            if (transcription.LastIndexOf('.') == transcription.Length - 1)
                transcription = transcription.Substring(0, transcription.Length - 1);

            // We want to stay on the query screen if result is empty
            if (transcription == "")
                return;

            sliderText.text = transcription;
            uiController.QueryMenuToggleSliderScreen(true);
        }
    }
}
