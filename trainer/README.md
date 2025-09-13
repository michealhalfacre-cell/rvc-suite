\# RVC Trainer (RunPod Template)



This pod template gives you everything you need to \*\*train an RVC (Retrieval-based Voice Conversion) model\*\* on RunPod.



\## Features

\- JupyterLab interface (runs on port 8888).

\- Pre-installed RVC WebUI code + dependencies.

\- Tools for dataset cleaning, trimming, and normalization (ffmpeg, sox).

\- GPU-accelerated training with PyTorch.



\## How to Use

1\. Launch this template on a GPU pod (L40S or RTX 4090 recommended).

2\. Open JupyterLab in your browser:

&nbsp;  - Go to your pod in the RunPod dashboard.

&nbsp;  - Click \*\*Connect → HTTP Services\*\*.

&nbsp;  - You’ll see a link for \*\*JupyterLab\*\* (on port 8888). Click it.

3\. Inside JupyterLab:

&nbsp;  - Upload your dataset into `/workspace/data/`.

&nbsp;  - Place raw audio inside `/workspace/data/datasets/<voice\_name>/`.

4\. Use the RVC scripts inside the `rvc/` folder to:

&nbsp;  - Preprocess and normalize your dataset.

&nbsp;  - Train your RVC model.

5\. Trained models will be saved to:/workspace/data/models/<voice_name>/ ## Next Step: Inference After training: - Copy/export the model folder into the /models directory used by the **RVC Inference Serverless template**. - Deploy the inference worker to convert any input audio into your cloned voice. --- ### GPU Notes - **RTX 4090 or L40S**: best speed/price. - Training costs: usually **$4–$9 AUD/hr** depending on GPU type. - Spot instances are cheaper if you don’t mind interruptions. where does that go?



