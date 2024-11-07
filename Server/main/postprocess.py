#     ____                   __  ___           __  _  __ ____
#    / __ \____  ___  ____  /  |/  /___ ______/ /_| |/ // __ \
#   / / / / __ \/ _ \/ __ \/ /|_/ / __ `/ ___/ //_/   // /_/ /
#  / /_/ / /_/ /  __/ / / / /  / / /_/ (__  ) ,< /   |/ _, _/
#  \____/ .___/\___/_/ /_/_/  /_/\__,_/____/_/|_/_/|_/_/ |_|
#      /_/
#
#  Created by Hanqiu Li Cai, Michael Siebenmann, Omar Majzoub, and Alexander Zank
#  and available under the MIT License. (See <ProjectRoot>/LICENSE.)

import numpy as np
import open3d as o3d
import torch
import json
import os
from postprocess_helpers import get_triangle_ids

def post_process(scene_name: str) -> None:
    """
    Post-processes the output of the OpenMask3D model for a given scene,
    generating segmented point clouds, meshes, and CLIP results in a reusable structure.

    Args:
        scene_name (str): Name of the scene folder containing the input files.
    """

    # Define scene path
    scene_path = os.path.join("scenes", scene_name)

    # Define input paths based on the provided structure
    point_cloud_path = os.path.join(scene_path, "scene.ply")
    masks_path = os.path.join(scene_path, "output", "scene_masks.pt")
    clip_results_path = os.path.join(scene_path, "output", "scene_openmask3d_features.npy")
    reconstructed_mesh_path = os.path.join(scene_path, "reconstruction.obj")
    
    # Define output paths
    output_folder = os.path.join(scene_path, "postprocess_output")
    output_pcd_folder = os.path.join(output_folder, "point_clouds")
    output_clip_path = os.path.join(output_folder, "clip.json")

    # Ensure output directories exist
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_pcd_folder, exist_ok=True)

    # Load the files
    print("Loading files...")
    pcd = o3d.io.read_point_cloud(point_cloud_path)
    mesh = o3d.io.read_triangle_mesh(reconstructed_mesh_path)
    masks = torch.load(masks_path)
    clip_results = np.load(clip_results_path, allow_pickle=True)

    # Initialize dictionaries to store clip and mesh data
    clip_dict = {}
    triangle_ids_dict = {}

    # Read the number of instances
    num_instances = masks.shape[1]
    # Set to track triangles already assigned to an instance
    assigned_triangles = set()

    print("Processing instances...")
    # Process each instance
    for i in range(num_instances):
        # Get the triangle indices for the current instance
        triangle_ids = get_triangle_ids(mesh, pcd, masks, i, assigned_triangles)
        assigned_triangles.update(triangle_ids)
        triangle_ids_dict[str(i)] = triangle_ids
        # Store the clip results as a list in the dictionary
        clip_dict[str(i)] = clip_results[i].tolist()

    # Export the clip results JSON
    with open(output_clip_path, "w") as f:
        json.dump(clip_dict, f)
    print(f"Clip results exported to {output_clip_path}")
    # Export the triangle indices JSON
    with open(os.path.join(output_folder, "triangle_ids.json"), "w") as f:
        json.dump(triangle_ids_dict, f)

# Example usage
if __name__ == "__main__":
    scene_name = "0024_00-living-room"
    post_process(scene_name)