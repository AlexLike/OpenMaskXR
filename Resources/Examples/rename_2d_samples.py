import os
import glob

# Pattern to match the .pth files inside subfolders (e.g., 0000_02-*/*_vh_clean_2.pth)
file_pattern = os.path.join(".", "*", "scene*_vh_clean_2.pth")

# Loop through each .pth file that matches the pattern
for pth_file in glob.glob(file_pattern):
    try:
        scenePath = os.path.dirname(pth_file)
        print(f"Renaming 2D samples of {os.path.basename(scenePath)}...")

        colorPath = os.path.join(scenePath, "color")
        depthPath = os.path.join(scenePath, "depth")
        posePath = os.path.join(scenePath, "pose")

        idxs = sorted(
            [os.path.splitext(os.path.basename(f))[0] for f in os.listdir(colorPath)],
            key=lambda x: int(x),
        )

        for i, idx in enumerate(idxs):
            for folder, ext in [("color", "jpg"), ("depth", "png"), ("pose", "txt")]:
                path = os.path.join(scenePath, folder)
                os.rename(
                    os.path.join(path, f"{idx}.{ext}"), os.path.join(path, f"{i}.{ext}")
                )

    except Exception as e:
        print(f"Failed to process {pth_file}: {e}")
