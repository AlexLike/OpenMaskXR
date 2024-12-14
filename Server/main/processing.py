#     ____                   __  ___           __  _  __ ____
#    / __ \____  ___  ____  /  |/  /___ ______/ /_| |/ // __ \
#   / / / / __ \/ _ \/ __ \/ /|_/ / __ `/ ___/ //_/   // /_/ /
#  / /_/ / /_/ /  __/ / / / /  / / /_/ (__  ) ,< /   |/ _, _/
#  \____/ .___/\___/_/ /_/_/  /_/\__,_/____/_/|_/_/|_/_/ |_|
#      /_/
#
#  Created by Hanqiu Li Cai, Michael Siebenmann, Omar Majzoub, and Alexander Zank
#  and available under the MIT License. (See <ProjectRoot>/LICENSE.)

from processing_helpers import (
    render_depth_image,
    color_pcd_from_frame,
    sample_pcd,
    fill_outlier_colors,
    get_triangle_ids,
)

import torch
import text2clip
import os
import numpy as np
import open3d as o3d
import cv2
import shutil
import PIL
import base64
import io
import json


def preprocess(scan_path: str, output_path: str):
    """
    Preprocesses a scanned scene by rendering depth images and generating a colored point cloud
    from posed RGB frames and the reconstruction mesh.

    Args:
        scan_path (str): Path to the directory containing the input files.
        output_path (str): Path to the output directory for the processed scene.
    """
    # Input Paths
    scan_path = os.path.abspath(scan_path)
    mesh_path = os.path.join(scan_path, "mesh.obj")
    rgb_frames_path = os.path.join(scan_path, "images")
    camera_extrinsics_path = os.path.join(scan_path, "poses")
    intrinsics_path = os.path.join(scan_path, "intrinsics.txt")
    marker_transform_path = os.path.join(scan_path, "markerTransform.txt")

    # Output Paths
    output_path = os.path.abspath(output_path)
    if os.path.exists(output_path):
        raise FileExistsError(
            f"Output at {output_path} already exists. Please remove it first if you wish to override"
        )
    pcd_output_path = os.path.join(output_path, "scene.ply")
    depth_output_path = os.path.join(output_path, "depth")
    os.makedirs(depth_output_path)
    color_output_path = os.path.join(output_path, "color")
    os.makedirs(color_output_path)
    pose_output_path = os.path.join(output_path, "pose")
    os.makedirs(pose_output_path)
    intrinsics_output_path = os.path.join(output_path, "intrinsic")
    os.makedirs(intrinsics_output_path)
    intrinsics_output_path = os.path.join(intrinsics_output_path, "intrinsic_color.txt")
    marker_transform_output_path = os.path.join(output_path, "markerTransform.txt")
    mesh_output_path = os.path.join(output_path, "mesh.obj")

    # Load mesh
    mesh = o3d.io.read_triangle_mesh(mesh_path)
    # Convert mesh to uncolored point cloud
    pcd = sample_pcd(mesh)
    # Load camera intrinsics
    camera_intrinsics = np.loadtxt(intrinsics_path)

    # Process each frame
    frame_count = len(os.listdir(rgb_frames_path))
    for frame_nr in range(frame_count):
        # Read camera pose
        camera_pose_path = os.path.join(camera_extrinsics_path, f"{frame_nr}.txt")
        camera_pose = np.loadtxt(camera_pose_path)
        # Load RGB frame
        rgb_frame_path = os.path.join(rgb_frames_path, f"{frame_nr}.jpeg")
        rgb_frame = cv2.imread(rgb_frame_path)
        rgb_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2RGB)
        # Render depth image
        depth_image = render_depth_image(
            mesh, rgb_frame.shape[1], rgb_frame.shape[0], camera_intrinsics, camera_pose
        )
        # Save depth image
        cv2.imwrite(os.path.join(depth_output_path, f"{frame_nr}.png"), depth_image)

        # Color the point cloud
        pcd = color_pcd_from_frame(
            pcd, rgb_frame, depth_image, camera_pose, camera_intrinsics
        )
    # Fill outliers in the point cloud
    pcd_filled = fill_outlier_colors(pcd, k=100, outlier_threshold=0.3)

    # Save the processed point cloud
    o3d.io.write_point_cloud(pcd_output_path, pcd_filled)

    # Copying files from the scan directory to the output directory
    for file_name in os.listdir(rgb_frames_path):
        source_path = os.path.join(rgb_frames_path, file_name)
        dest_path = os.path.join(color_output_path, file_name)
        shutil.copy(source_path, dest_path)

    for file_name in os.listdir(camera_extrinsics_path):
        source_path = os.path.join(camera_extrinsics_path, file_name)
        dest_path = os.path.join(pose_output_path, file_name)
        shutil.copy(source_path, dest_path)

    shutil.copy(intrinsics_path, intrinsics_output_path)
    shutil.copy(marker_transform_path, marker_transform_output_path)
    shutil.copy(mesh_path, mesh_output_path)

    print(f"Preprocessed scan '{scan_path}' for OpenMask3D at '{output_path}'.")


def postprocess(scene_path: str) -> None:
    """
    Post-processes the output of the OpenMask3D model for a given scene,
    generating segmented point clouds, meshes, and CLIP results in a reusable structure.
    Args:
        scene_name (str): Name of the scene folder containing the input files.
    """
    # Input Paths
    scene_path = os.path.abspath(scene_path)
    point_cloud_path = os.path.join(scene_path, "scene.ply")
    masks_path = os.path.join(scene_path, "output", "scene_masks.pt")
    clip_results_path = os.path.join(
        scene_path, "output", "scene_openmask3d_features.npy"
    )
    reconstructed_mesh_path = os.path.join(scene_path, "reconstruction.obj")
    topk_index_path = os.path.join(scene_path, "output", "topk_indicesy")

    # Define output paths
    output_folder = os.path.join(scene_path, "postprocess_output")
    output_pcd_folder = os.path.join(output_folder, "point_clouds")
    output_clip_path = os.path.join(output_folder, "clip.json")
    output_topk_base64_path = os.path.join(output_folder, "topk_base64.json")

    # Ensure output directories exist
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_pcd_folder, exist_ok=True)

    # Load the files
    print("Loading files...")
    pcd = o3d.io.read_point_cloud(point_cloud_path)
    mesh = o3d.io.read_triangle_mesh(reconstructed_mesh_path)
    masks = torch.load(masks_path)
    clip_results = np.load(clip_results_path, allow_pickle=True)
    topk_images_per_instance = np.load(topk_index_path, allow_pickle=True)

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
        # Get the topk images for the current instance
        topk_images = topk_images_per_instance[i]
        # Convert the topk images to base64
        topk_base64 = []
        for topk_image in topk_images:
            # Image is the index, we access the image from the folder of the scene
            # Try jpg or jpeg (only two formats supported)
            try:
                image_path = os.path.join(scene_path, "images", f"{topk_image}.jpeg")
                image = PIL.Image.open(image_path)
                # Convert to base64
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                topk_base64.append(img_str)
            except FileNotFoundError:
                image_path = os.path.join(scene_path, "images", f"{topk_image}.jpg")
                image = PIL.Image.open(image_path)
                # Convert to base64
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                topk_base64.append(img_str)
        # Store the topk images as base64 in the dictionary
        topk_base64_dict = {str(i): topk_base64}

    # Export the clip results JSON
    with open(output_clip_path, "w") as f:
        json.dump(clip_dict, f)
    print(f"Clip results exported to {output_clip_path}")
    # Export the triangle indices JSON
    with open(os.path.join(output_folder, "triangle_ids.json"), "w") as f:
        json.dump(triangle_ids_dict, f)
    print(f"Triangle indices exported to {output_folder}/triangle_ids.json")
    # Export the topk images as base64 JSON
    with open(output_topk_base64_path, "w") as f:
        json.dump(topk_base64_dict, f)
    print(f"Topk images exported to {output_topk_base64_path}")


def encode_query(text: str) -> torch.Tensor:
    """Generates the CLIP representation of a user's raw query in natural language."""
    # TODO: Ask LLM to extract subject from human query, e.g.,
    # "Show me something green I can sit on." -> "something to sit on",
    # "I want to sit on the chair!" -> "a chair",
    # "Where are the green cubes?" -> "a green cube"
    subject = text
    openmask3d_prompt = f"{subject} in a scene"
    return text2clip.encode(openmask3d_prompt)
