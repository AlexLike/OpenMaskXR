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
from postprocess_helpers import mask_point_cloud, mesh_to_dict

def post_process(scene_name: str):
    """
    Post-processes the output of the OpenMask3D model for a given scene,
    generating segmented point clouds, meshes, and CLIP results in a reusable structure.

    Args:
        scene_name (str): Name of the scene folder containing the input files.
    """

    # Define scene path
    scene_path = os.path.join("scenes", scene_name)

    # Define input paths based on the provided structure
    point_cloud_path = os.path.join(scene_path, "scene_data", f"{scene_name}.ply")
    masks_path = os.path.join(scene_path, "o3d_outputs", f"{scene_name}_masks.pt")
    clip_results_path = os.path.join(scene_path, "o3d_outputs", f"{scene_name}_openmask3d_features.npy")
    
    # Define output paths
    output_folder = os.path.join(scene_path, "postprocess_output")
    output_pcd_folder = os.path.join(output_folder, "point_clouds")
    output_clip_path = os.path.join(output_folder, "clip.json")
    output_mesh_path = os.path.join(output_folder, "mesh.json")

    # Ensure output directories exist
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_pcd_folder, exist_ok=True)

    # Load the files
    pcd = o3d.io.read_point_cloud(point_cloud_path)
    masks = torch.load(masks_path)
    clip_results = np.load(clip_results_path, allow_pickle=True)

    # Initialize dictionaries to store clip and mesh data
    clip_dict = {}

    # Read the number of instances
    num_instances = masks.shape[1]

    # Process each instance
    for i in range(num_instances):
        # Create and save the point cloud for the current instance
        queried_pcd = mask_point_cloud(pcd, masks, i)
        queried_pcd_path = os.path.join(output_pcd_folder, f"scene_example_instance_{i}.ply")
        o3d.io.write_point_cloud(queried_pcd_path, queried_pcd)

        # TODO: Don't need to export the point clouds, we will instead just return a list of triangles
        # That belong to each instance, and then we can use that to generate the mesh on the client side
        
        del queried_pcd

        # Store the clip results as a list in the dictionary
        clip_dict[str(i)] = clip_results[i].tolist()

    # Export the clip results JSON
    with open(output_clip_path, "w") as f:
        json.dump(clip_dict, f)

    print(f"Clip results exported to {output_clip_path}")

# Example usage
if __name__ == "__main__":
    scene_name = "scene_example"
    post_process(scene_name)