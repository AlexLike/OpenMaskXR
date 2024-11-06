import torch
import pandas as pd
import open3d as o3d
import os
import glob
import numpy as np
import pymeshlab as pml


# Pattern to match the .pth files inside subfolders (e.g., 0000_02-*/*_vh_clean_2.pth)
file_pattern = os.path.join(".", "*", "scene*_vh_clean_2.pth")

print(file_pattern)

# Loop through each .pth file that matches the pattern
for pth_file in glob.glob(file_pattern):
    try:
        scenePath, pthFileName = os.path.split(pth_file)
        print(f"Processing {os.path.basename(scenePath)}...")

        # Load the point position and color data.
        x = torch.load(pth_file, weights_only=False)
        point_data = x[0]
        color_data = (x[1] + 1) / 2  # undo [-1, 1] normalization to [0, 1]

        # Save as an Open3D point cloud.
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(point_data)
        pcd.colors = o3d.utility.Vector3dVector(color_data)
        pcd_file = os.path.join(scenePath, f"scene.ply")
        o3d.io.write_point_cloud(pcd_file, pcd)

        # Load into MeshLab for further synthesis.
        ms = pml.MeshSet()
        ms.load_new_mesh(pcd_file)

        # Downsample the point cloud.
        ms.generate_simplified_point_cloud(
            samplenum=np.int32(point_data.shape[0] * 0.3)
        )

        # Compute normals based on the visual center.
        center = (point_data.max(axis=0) - point_data.min(axis=0)) / 2
        ms.compute_normal_for_point_clouds(viewpos=center, flipflag=True)

        # Reconstruct a mesh.
        ms.generate_surface_reconstruction_ball_pivoting(
            ballradius=pml.PureValue(0.1), deletefaces=True
        )
        mesh_file = os.path.join(scenePath, f"reconstruction.obj")
        ms.save_current_mesh(mesh_file)

        # Bake vertex color to textures.
        texture_size = 8192
        ms.compute_texcoord_parametrization_triangle_trivial_per_wedge(
            sidedim=0, textdim=texture_size
        )
        ms.transfer_attributes_to_texture_per_vertex(
            sourcemesh=1,
            targetmesh=1,
            textw=texture_size,
            texth=texture_size,
            textname="reconstruction-textured.png",
        )

        mesh_file = os.path.join(scenePath, f"reconstruction-textured.obj")
        ms.save_current_mesh(mesh_file)

    except Exception as e:
        print(f"Failed to process {pth_file}: {e}")
