#     ____                   __  ___           __  _  __ ____
#    / __ \____  ___  ____  /  |/  /___ ______/ /_| |/ // __ \
#   / / / / __ \/ _ \/ __ \/ /|_/ / __ `/ ___/ //_/   // /_/ /
#  / /_/ / /_/ /  __/ / / / /  / / /_/ (__  ) ,< /   |/ _, _/
#  \____/ .___/\___/_/ /_/_/  /_/\__,_/____/_/|_/_/|_/_/ |_|
#      /_/
#
#  Created by Hanqiu Li Cai, Michael Siebenmann, Omar Majzoub, and Alexander Zank
#  and available under the MIT License. (See <ProjectRoot>/LICENSE.)

import open3d as o3d

# Load the colored PLY point cloud.
input_file = "/root/input/scene.ply"
point_cloud = o3d.io.read_point_cloud(input_file)

# Calculate the number of points and determine the downsample factor.
target_points = 30000
current_points = len(point_cloud.points)
downsample_factor = current_points / target_points

# Uniformly downsample the point cloud.
downsampled_pc = point_cloud.uniform_down_sample(int(downsample_factor + 1))
assert downsampled_pc.has_colors()

# Save the downsampled point cloud to a new PLY file.
output_file = "/root/input/downsampled_scene.ply"
o3d.io.write_point_cloud(output_file, downsampled_pc)

print(
    f"Downsampled point cloud saved to {output_file} with {len(downsampled_pc.points)} points."
)
