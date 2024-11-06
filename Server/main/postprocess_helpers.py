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

def mask_point_cloud(pcd: o3d.geometry.PointCloud, masks_output: np.ndarray, instance_id: int) -> o3d.geometry.PointCloud:
    """Function to query the point cloud with the mask output of OpenMask3D
    Args:
        pcd (o3d.geometry.PointCloud): Original point cloud
        masks_output (np.ndarray): Output of the OpenMask3D model
        instance_id (int): Instance to query
    Returns:
        o3d.geometry.PointCloud: Point cloud with only the queried instance
    """
    assert instance_id < masks_output.shape[1], "Instance ID is out of range"

    mask_instance = masks_output.T[instance_id]
    points_in_mask = np.where(mask_instance == 1)[0]
    queried_pcd = pcd.select_by_index(points_in_mask)

    return queried_pcd

def mesh_to_dict(mesh: o3d.geometry.TriangleMesh, key_name: str) -> dict:
    """Export the mesh to a JSON file
    Args:
        mesh (o3d.geometry.TriangleMesh): Mesh to export
        output_path (str): Path to save the JSON file
    """
    vertices = np.asarray(mesh.vertices).tolist()
    faces = np.asarray(mesh.triangles).tolist()
    normals = np.asarray(mesh.vertex_normals).tolist() if mesh.has_vertex_normals() else None
    colors = np.asarray(mesh.vertex_colors).tolist() if mesh.has_vertex_colors() else None

    mesh_dict = {
        "verices": vertices,
        "faces": faces,
    }

    if normals:
        mesh_dict["normals"] = normals

    if colors:
        mesh_dict["colors"] = colors # Colors are in RGB format and correspond to the vertex

    return {key_name: mesh_dict}

# TODO: Function given a mesh, point cloud, masks, and instance ID, return the triangle ids from the mesh that correspond to the instance.

# def get_instance_triangles(mesh: o3d.geometry.TriangleMesh, pcd: o3d.geometry.PointCloud, masks_output: np.ndarray, instance_id: int) -> np.ndarray: