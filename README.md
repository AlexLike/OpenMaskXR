<p align="center">

  <h1 align="center">OpenMaskXR:<br>Open-Vocabulary Scene Understanding in Extended Reality</h1>
  <p align="center">
    <strong>Alexander Zank, 
    Michael Siebenmann
    Hanqiu Li Cai, 
    Omar Majzoub</strong> 
  </p>
</p>

<p align="center">
  <a href="">
    <img src="img/cvg-siplab-eth-logos-white.png" alt="SIPLAB and AIT at ETH Zürich." width="50%">
  </a>
</p>

<p align="center">
  <a href="">
    <img src="img/teaser.png" alt="Teaser Figure" width="100%">
  </a>
</p>


**OpenMaskXR** is our semester project for ETH's Mixed Reality course. We bring [OpenMask3D](https://openmask3d.github.io) to Extended Reality.
With OpenMaskXR, we demonstrate an end-to-end workflow for advanced scene understanding in XR. We implement various
software components whose tasks range from scanning the environment using commodity hardware to processing and displaying it for
open-vocabulary object querying.

## 🛠 Setup
If you want to run OpenMaskXR yourself, you need to run both the XR client and the server at the same time.

### ✨ XR Client
<p align="center">
  <a href="">
    <img src="img/home_menu.png" alt="Home Menu UI" width="42%">
  </a>
</p>

We include a Meta Quest 3 build under the [Releases](https://github.com/AlexLike/OpenMaskXR/releases/latest) of this repository.
Note that our application requires internet access.
As OpenMaskXR uses OpenXR as an XR plug-in manager, you may also create a build for other MR headsets, such as the Magic Leap 2, HTC Vive Focus 3 or Pico 4.
To do so, follow these steps:
1. Install Unity 6000.0.23f1 (higher versions of Unity 6 are untested, but likely to work as well)
2. Clone this repository and open the folder `OpenMaskXR/OpenMaskXR` with Unity
3. Follow the (Unity) guide for setting up your VR headset in an OpenXR project
4. Adapt line 403 in `ModelManager.cs` to use your static ngrok domain (see next section for more ngrok details) with route `/text-to-CLIP`:
   ```csharp
   StartCoroutine(TextQuery("<your-static-url>/text-to-CLIP", $"{{\"text\":\"{query}\"}}"));
   ```
6. Create and run a build through `File > Build And Run` or use `Ctrl + B`

### 🖥️ Server
While you can explore our pre-processed ScanNet200 scenes in XR without having to run the server, it is required for querying.
The server exposes an API that can be used to embed text into CLIP vectors, as CLIP unfortunately cannot run on the headset.
Note that the following steps only set up a server for this sole purpose of embedding text into CLIP.
If you wish to use our pre- and post-processing scripts working with point cloud and RGB-D data, you need to install further packages.
To run the server, follow these steps:
1. Install [ngrok](https://ngrok.com/docs/getting-started/) and Python 3.11
2. Create an ngrok account and connect the agent to your account (see their Quickstart linked in step 1)
3. Create a static domain in your ngrok dashboard
4. Clone this repository and checkout the `laptop-workaround` branch
5. Navigate to `Server/main`
6. Create a virtual environment with `python -m venv .venv` and **activate** it
7. Install necessary packages through `pip install -r requirements.txt`
8. Run the API script: `python api.py`
9. In a parallel terminal, run the following: `ngrok http 1234 --url=<your-static-url>`
