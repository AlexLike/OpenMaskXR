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
import open3d.core as o3c
import cv2
import os
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors

def sample_pcd(mesh: o3d.geometry.TriangleMesh, number_of_points: int = 200000, downsampling_ratio: float = 0.75) -> o3d.geometry.PointCloud:
    """
    Converts a triangle mesh to an uncolored point cloud by sampling points from the surface of the mesh.

    Parameters:
    mesh (o3d.geometry.TriangleMesh): Open3D triangle mesh.
    number_of_points (int): Number of points to sample uniformly.
    downsampling_ratio (float): Downsampling ratio for Poisson disk sampling.

    Returns:
    o3d.geometry.PointCloud: Open3D point cloud.
    """

    # Sample points from the surface of the mesh
    pcd = mesh.sample_points_uniformly(number_of_points=number_of_points)
    pcd = mesh.sample_points_poisson_disk(number_of_points=int(number_of_points * downsampling_ratio), pcl=pcd)

    # Strip the colors from the point cloud (Painted white)
    pcd.colors = o3d.utility.Vector3dVector(np.zeros((len(pcd.points), 3)))

    return pcd

def color_pcd_from_frame(
    pcd: o3d.geometry.PointCloud,
    frame_rgb: np.ndarray,
    frame_depth: np.ndarray,
    camera_pose: np.ndarray,
    camera_intrinsics: np.ndarray,
    depth_scale: float = 1000.0,
    epsilon: float = 0.01
) -> o3d.geometry.PointCloud:
    """
    Colors the point cloud by projecting the frame onto the mesh and assigning the colors to the corresponding points.

    Parameters:
    pcd (o3d.geometry.PointCloud): Open3D point cloud.
    frame_rgb (np.ndarray): RGB frame.
    frame_depth (np.ndarray): Depth frame.
    camera_pose (np.ndarray): 4x4 camera pose matrix.
    camera_intrinsics (np.ndarray): 4x4 camera intrinsics matrix.
    depth_scale (float): Depth scaling factor.
    epsilon (float): Depth tolerance for point projection in meters.

    Returns:
    o3d.geometry.PointCloud: Open3D point cloud with colors assigned.
    """

    # Invert the camera pose to get the extrinsic matrix (world to camera)
    extrinsic = np.linalg.inv(camera_pose)  # Shape: (4, 4)

    # Get the point cloud points as numpy array
    pcd_points = np.asarray(pcd.points)  # Shape: (N, 3)

    # Convert to homogeneous coordinates
    ones = np.ones((pcd_points.shape[0], 1))
    points_world_hom = np.hstack((pcd_points, ones))  # Shape: (N, 4)

    # Transform the points to the camera frame
    points_camera_hom = (extrinsic @ points_world_hom.T).T  # Shape: (N, 4)
    points_camera = points_camera_hom[:, :3]  # Shape: (N, 3)

    # Keep only the points in front of the camera
    valid_mask = points_camera[:, 2] > 0  # Boolean array of shape (N,)
    points_camera = points_camera[valid_mask]
    
    # Project the points to the image plane
    points_camera_T = points_camera.T  # Shape: (3, N_valid)
    pixels_hom = (camera_intrinsics[:3, :3] @ points_camera_T).T  # Shape: (N_valid, 3)

    # Convert to pixel coordinates by normalizing
    pixels = pixels_hom[:, :2] / pixels_hom[:, 2][:, np.newaxis]  # Shape: (N_valid, 2)
    pixels = pixels.astype(int)

    # Get indices of valid points in the original point cloud
    valid_indices = np.where(valid_mask)[0]  # Shape: (N_valid,)

    # Initialize colors array with the color of the point cloud
    colors = np.asarray(pcd.colors)  # Shape: (N, 3)

    # Image dimensions
    height, width = frame_rgb.shape[:2]

    # Loop over the valid points
    for idx_in_valid, (u, v) in enumerate(pixels):
        
        if 0 <= u < width and 0 <= v < height:
            idx_in_pcd = valid_indices[idx_in_valid]
            # Retrieve depth from depth image
            depth_from_image = frame_depth[v, u] / depth_scale  # Convert to meters if necessary
            # Depth from point in camera coordinates
            depth_from_point = points_camera[idx_in_valid, 2]
            # Visibility check
            if abs(depth_from_image - depth_from_point) < epsilon:
                # Get color from RGB image
                colors[idx_in_pcd] = frame_rgb[v, u] / 255.0  # Normalize RGB to [0, 1]
            else:
                # Occluded or mismatched depth; keep color from point cloud
                pass
        else:
            # Point projects outside the image; keep color from point cloud
            pass

    # Assign colors to the point cloud
    pcd.colors = o3d.utility.Vector3dVector(colors)

    return pcd


def render_depth_image(
    mesh: o3d.geometry.TriangleMesh,
    width: int,
    height: int,
    intrinsic: np.ndarray,
    camera_pose: np.ndarray,
    depth_scale: float = 1000.0
) -> np.ndarray:
    """
    Renders a depth image by raycasting from a given camera pose into a mesh.

    Parameters:
    mesh (o3d.geometry.TriangleMesh): The input mesh (legacy Open3D format).
    width (int): The width of the depth image.
    height (int): The height of the depth image.
    intrinsic (np.ndarray): 4x4 intrinsic matrix.
    camera_pose (np.ndarray): 4x4 camera pose matrix (camera-to-world).
    depth_scale (float): Scaling factor for depth values (default: 1000.0).

    Returns:
    np.ndarray: The rendered depth image as a NumPy array (uint16).
    """

    # if not mesh.has_triangle_normals():
    #     print("What the hell")

    # Step 1: Convert the mesh to tensor format
    mesh_t = o3d.t.geometry.TriangleMesh.from_legacy(mesh)

    # Step 2: Extract the intrinsic matrix and convert to Open3D tensor
    # Extract the top-left 3x3 portion
    intrinsic_3x3 = intrinsic[:3, :3].astype(np.float32)
    intrinsic_t = o3c.Tensor(intrinsic_3x3, dtype=o3c.float32)

    # Step 3: Camera pose in world frame
    # Ensure camera_pose is of shape (4, 4) and dtype float32

    # NOTE: In Open3D, the z and y axes are inverted compared to other libraries

    camera_pose[:3, 2] *= -1  # Invert Z-axis
    camera_pose[:3, 1] *= -1  # Invert Y-axis

    camera_pose_inv = np.linalg.inv(camera_pose)
    extrinsic_t = o3c.Tensor(camera_pose_inv, dtype=o3c.float32)

    # Step 4: Set up camera parameters (width and height are already provided)

    # Step 5: Generate rays and perform raycasting
    scene = o3d.t.geometry.RaycastingScene()
    scene.add_triangles(mesh_t)

    # Generate rays using Open3D's utility function
    rays = o3d.t.geometry.RaycastingScene.create_rays_pinhole(
        intrinsic_matrix=intrinsic_t,
        extrinsic_matrix=extrinsic_t,
        width_px=width,
        height_px=height,
    )

    # Cast rays
    raycasting_results = scene.cast_rays(rays)

    # Step 6: Process depth values
    # Extract 't_hit' which contains the depth values
    t_hit = raycasting_results['t_hit'].numpy()  # Shape: (width * height,)

    # Reshape to image dimensions
    depth_image = t_hit.reshape((height, width))

    # Handle missing depth values (set 'inf' to zero)
    depth_image[np.isinf(depth_image)] = 0

    # Scale depth values
    depth_image_scaled = depth_image * depth_scale

    # Convert to uint16
    depth_image_scaled = depth_image_scaled.astype(np.uint16)

    # Step 7: Return the depth image
    return depth_image_scaled

def fill_outlier_colors(pcd: o3d.geometry.PointCloud, k: int = 100, outlier_threshold: float = 0.5) -> o3d.geometry.PointCloud:
    """
    Fills in colors that are identified as outliers with respect to their k-nearest neighbors.

    Parameters:
    pcd (o3d.geometry.PointCloud): Input point cloud with possible outlier colored points.
    k (int): Number of nearest neighbors to consider for identifying outliers.
    outlier_threshold (float): Threshold factor to determine outliers based on color distance from neighbors.

    Returns:
    o3d.geometry.PointCloud: Point cloud with outlier colors filled.
    """
    # Get the point cloud points and colors as numpy arrays
    points = np.asarray(pcd.points)  # Shape: (N, 3)
    colors = np.asarray(pcd.colors)  # Shape: (N, 3)

    # Build KD-tree using all points for neighbor search
    nbrs = NearestNeighbors(n_neighbors=k + 1, algorithm='auto').fit(points)  # k + 1 to exclude the point itself

    # Iterate over all points to identify outliers and fill their colors
    for idx in range(len(points)):
        query_point = points[idx].reshape(1, -1)
        distances, indices = nbrs.kneighbors(query_point)

        # Exclude the point itself from neighbors
        neighbor_indices = indices[0][1:]
        neighbor_colors = colors[neighbor_indices]

        # Compute the average color of the neighbors
        averaged_color = np.mean(neighbor_colors, axis=0)

        # Compute the distance between the point's color and the average color of neighbors
        color_distance = np.linalg.norm(colors[idx] - averaged_color)

        # If the color distance is greater than the outlier threshold, update the color
        if color_distance > outlier_threshold:
            colors[idx] = averaged_color

    # Update the point cloud colors
    pcd.colors = o3d.utility.Vector3dVector(colors)
    return pcd