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
import text2clip


def fake_depth():
    return


def sample_mesh_and_color():
    return


def data_to_open_mask_3d():
    return


def encode_query(text: str) -> torch.Tensor:
    """Generates the CLIP representation of a user's raw query in natural language."""
    # TODO: Ask LLM to extract subject from human query, e.g.,
    # "Show me something green I can sit on." -> "something to sit on",
    # "I want to sit on the chair!" -> "a chair",
    # "Where are the green cubes?" -> "a green cube"
    subject = text

    openmask3d_prompt = f"{subject} in a scene"
    return text2clip.encode(openmask3d_prompt)
