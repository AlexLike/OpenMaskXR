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
import os
import numpy as np
import open3d as o3d
import opencv as cv2
import shutil
from Server.main.processing_helpers import render_depth_image, color_pcd_from_frame, sample_pcd, fill_outlier_colors

def process_scene(scene_name):
    """
    Processes a scene by rendering depth images and coloring a point cloud from RGB frames and poses.

    Parameters:
    - scene_name (str): The name of the scene to process (e.g., "Sergi").
    - mesh_dir (str): Directory where the mesh, images, poses, and intrinsics are stored.
    - output_dir (str): Directory where the output depth images and point cloud will be saved.
    
    Returns:
    - None
    """
    # Set paths
    scene_path = os.path.join("Resources", "Examples", "Ours", scene_name)
    mesh_path = os.path.join(scene_path, "mesh.obj")
    rgb_frames_path = os.path.join(scene_path, "images")  # RGB frames directory
    camera_extrinsics_path = os.path.join(scene_path, "poses")  # Camera poses directory
    intrinsics_path = os.path.join(scene_path, "intrinsics.txt")  # Camera intrinsics file
    marker_transform_path = os.path.join(scene_path, "markerTransform.txt")  # Marker transforms file

    # Create scene directory in Server/main/scenes/ "scene_name"
    output_dir = os.path.join("Server", "main", "scenes", scene_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    depth_output_dir = os.path.join(output_dir, "depth")
    if not os.path.exists(depth_output_dir):
        os.makedirs(depth_output_dir)

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
        depth_image_path = os.path.join(depth_output_dir, f"{frame_nr}.png")
        cv2.imwrite(depth_image_path, depth_image)

        # Color the point cloud
        pcd = color_pcd_from_frame(pcd, rgb_frame, depth_image, camera_pose, camera_intrinsics)
    # Fill outliers in the point cloud
    pcd_filled = fill_outlier_colors(pcd, k=100, outlier_threshold=0.3)

    # Save the processed point cloud
    pcd_output_path = os.path.join(output_dir, "scene.ply")
    o3d.io.write_point_cloud(pcd_output_path, pcd_filled)
    print(f"Processed scene '{scene_name}' and saved colored point cloud to {pcd_output_path}")

    # Copying files from the scene directory to the output directory
        # Files from images are copied into output directory/color/
    color_output_dir = os.path.join(output_dir, "color")
    if not os.path.exists(color_output_dir):
        os.makedirs(color_output_dir)
    for file_name in os.listdir(rgb_frames_path):
        source_path = os.path.join(rgb_frames_path, file_name)
        dest_path = os.path.join(color_output_dir, file_name)
        shutil.copy(source_path, dest_path)

    # Files from poses are copied into output directory/pose/
    pose_output_dir = os.path.join(output_dir, "pose")
    if not os.path.exists(pose_output_dir):
        os.makedirs(pose_output_dir)
    for file_name in os.listdir(camera_extrinsics_path):
        source_path = os.path.join(camera_extrinsics_path, file_name)
        dest_path = os.path.join(pose_output_dir, file_name)
        shutil.copy(source_path, dest_path)

    # intrinsics.txt is copied into output directory/intrinsic/
    intrinsic_output_dir = os.path.join(output_dir, "intrinsic")
    if not os.path.exists(intrinsic_output_dir):
        os.makedirs(intrinsic_output_dir)
    shutil.copy(intrinsics_path, os.path.join(intrinsic_output_dir, "intrinsics.txt"))

    # markerTransform.txt is copied over directly
    marker_transform_dest_path = os.path.join(output_dir, "markerTransform.txt")
    shutil.copy(marker_transform_path, marker_transform_dest_path)

    # mesh.obj is copied into output directory directly
    mesh_dest_path = os.path.join(output_dir, "mesh.obj")
    shutil.copy(mesh_path, mesh_dest_path)

    print(f"Copied all files to main/scenes directory: {output_dir}")


def encode_query(text: str) -> torch.Tensor:
    """Generates the CLIP representation of a user's raw query in natural language."""
    # TODO: Ask LLM to extract subject from human query, e.g.,
    # "Show me something green I can sit on." -> "something to sit on",
    # "I want to sit on the chair!" -> "a chair",
    # "Where are the green cubes?" -> "a green cube"
    subject = text
    openmask3d_prompt = f"{subject} in a scene"
    return text2clip.encode(openmask3d_prompt)
