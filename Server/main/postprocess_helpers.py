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

def create_mesh_from_pcd(pcd: o3d.geometry.PointCloud, depth: int = 8, voxel_size: float = 0.04, radius:float = 0.1, max_nn:int = 30) -> o3d.geometry.TriangleMesh:
    """Create a mesh from a point cloud
    Args:
        pcd (o3d.geometry.PointCloud): Point cloud to create the mesh
        depth (int, optional): Depth of the Poisson reconstruction.
        voxel_size (float, optional): Voxel size for the voxel down sampling
        radius (float, optional): Radius for the normal estimation
        max_nn (int, optional): Maximum number of nearest neighbors for the normal estimation
    Returns:
        o3d.geometry.TriangleMesh: Mesh created from the point cloud
    """
    down_pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    down_pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn))
    mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(down_pcd, depth=depth)
    return mesh

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