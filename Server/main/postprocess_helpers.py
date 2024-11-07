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
from scipy.spatial import KDTree
import open3d as o3d

def get_triangle_ids(mesh: o3d.geometry.TriangleMesh, point_cloud: o3d.geometry.PointCloud, point_mask: np.ndarray, object_k: int, assigned_triangles: set[int], k_neighbors: int=10) -> list[int]:
    """
    Returns a list of unique triangle indices that are assigned to object_k based on the majority of their nearest neighbors,
    while ensuring no duplicate assignments across instances.

    Parameters:
    mesh (o3d.geometry.TriangleMesh): Open3D triangle mesh.
    point_cloud (o3d.geometry.PointCloud): Open3D point cloud.
    point_mask (np.ndarray): PxK binary mask, where point_mask[i][k] = 1 if point i belongs to object k.
    object_k (int): Index of the object (0-based).
    assigned_triangles (set[int]): Set of triangle indices that are already assigned to other instances.
    k_neighbors (int): Number of nearest neighbors to consider.

    Returns:
    list[int]: List of unique triangle indices assigned to object_k.
    """

    # Extract vertices and faces
    mesh_vertices = np.asarray(mesh.vertices)  # Nx3 array
    mesh_faces = np.asarray(mesh.triangles)    # Mx3 array of indices

    # Convert point cloud to Px3 array
    point_cloud_np = np.asarray(point_cloud.points)

    # Build KDTree from point cloud
    tree = KDTree(point_cloud_np)
    
    # Prepare output list to store triangle IDs assigned to object_k
    triangle_ids = []
    
    for i, mesh_face in enumerate(mesh_faces):
        # Skip if this triangle is already assigned to another instance
        if i in assigned_triangles:
            continue

        # Get triangle vertex indices
        idx0, idx1, idx2 = mesh_face
        # Get vertex positions
        v0 = mesh_vertices[idx0]
        v1 = mesh_vertices[idx1]
        v2 = mesh_vertices[idx2]
        # Compute centroid of the triangle
        centroid = (v0 + v1 + v2) / 3.0
        # Find k nearest neighbors to centroid
        _, indices = tree.query(centroid, k=k_neighbors)
        # Get the object assignments of the nearest points
        neighbor_mask = point_mask[indices, object_k]
        # Count how many neighbors belong to object_k
        count = np.sum(neighbor_mask)
        # If majority of neighbors belong to object_k, assign triangle to object_k
        if count >= k_neighbors // 2:
            triangle_ids.append(i)
    
    return triangle_ids