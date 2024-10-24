#     ____                   __  ___           __  _  __ ____
#    / __ \____  ___  ____  /  |/  /___ ______/ /_| |/ // __ \
#   / / / / __ \/ _ \/ __ \/ /|_/ / __ `/ ___/ //_/   // /_/ /
#  / /_/ / /_/ /  __/ / / / /  / / /_/ (__  ) ,< /   |/ _, _/
#  \____/ .___/\___/_/ /_/_/  /_/\__,_/____/_/|_/_/|_/_/ |_|
#      /_/
#
#  Created by Hanqiu Li Cai, Michael Siebenmann, Omar Majzoub, and Alexander Zank
#  and available under the MIT License. (See <ProjectRoot>/LICENSE.)

import torch
import clip

MODEL = "ViT-L/14@336px"  # used by OpenMask3D
assert MODEL in clip.available_models()

device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps" if torch.mps.is_available() else "cpu"
)
model, _ = clip.load(MODEL, device=device)


def encode(text: str) -> torch.Tensor:
    """Computes the CLIP representation (768) of the provided string."""
    text = clip.tokenize(text).to(device)
    with torch.no_grad():
        batched_output = model.encode_text(text)
    return batched_output.squeeze().cpu()
