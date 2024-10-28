#     ____                   __  ___           __  _  __ ____
#    / __ \____  ___  ____  /  |/  /___ ______/ /_| |/ // __ \
#   / / / / __ \/ _ \/ __ \/ /|_/ / __ `/ ___/ //_/   // /_/ /
#  / /_/ / /_/ /  __/ / / / /  / / /_/ (__  ) ,< /   |/ _, _/
#  \____/ .___/\___/_/ /_/_/  /_/\__,_/____/_/|_/_/|_/_/ |_|
#      /_/
#
#  Created by Hanqiu Li Cai, Michael Siebenmann, Omar Majzoub, and Alexander Zank
#  and available under the MIT License. (See <ProjectRoot>/LICENSE.)

from flask import Flask, request
from os import path, listdir, getcwd
from subprocess import run
from sys import stdout, stderr
from threading import Lock

SCENE_DIR = f"{getcwd()}/input"
SCENE_POSE_DIR = f"{SCENE_DIR}/pose"
SCENE_INTRINSIC_PATH = f"{SCENE_DIR}/intrinsic/intrinsic_color.txt"
SCENE_PLY_PATH = f"{SCENE_DIR}/scene.ply"
SCENE_COLOR_IMG_DIR = f"{SCENE_DIR}/color"
SCENE_DEPTH_IMG_DIR = f"{SCENE_DIR}/depth"
MASK_MODULE_CKPT_PATH = "/third_party/checkpoints/scannet200_model.ckpt"
SAM_CKPT_PATH = "/third_party/checkpoints/sam_vit_h_4b8939.pth"
OUTPUT_DIR = f"{getcwd()}/output"
SAVE_VISUALIZATIONS = False
SAVE_CROPS = False
OPTIMIZE_GPU_USAGE = False

app = Flask(__name__)
lock = Lock()


@app.route("/", methods=["GET"])
def run_openmask3d():
    if not lock.acquire(blocking=False):
        return "Busy handling another request.", 503

    try:
        print("[INFO] OpenMask3D request received.")

        intrinsic_resolution = request.args.get(
            "intrinsicResolution", default="[968,1296]"
        )
        depth_scale = request.args.get("depthScale", default=1000)

        try:
            compute_masks()
        except:
            return f"Mask computation failed.", 500

        try:
            compute_features(intrinsic_resolution, depth_scale)
        except:
            return f"Feature computation failed.", 500

        return f"Success! Find the results in {OUTPUT_DIR}", 200

    finally:
        lock.release()


def compute_masks():
    run(
        cwd="/third_party/openmask3d/openmask3d",
        args=[
            "python",
            "class_agnostic_mask_computation/get_masks_single_scene.py",
            f"general.experiment_name=experiment",
            f"general.checkpoint={MASK_MODULE_CKPT_PATH}",
            "general.train_mode=false",
            "data.test_mode=test",
            "model.num_queries=120",
            "general.use_dbscan=true",
            "general.dbscan_eps=0.95",
            f"general.save_visualizations={SAVE_VISUALIZATIONS}",
            f"general.scene_path={SCENE_PLY_PATH}",
            f"general.mask_save_dir={OUTPUT_DIR}",
            f"hydra.run.dir={OUTPUT_DIR}/hydra_outputs/class_agnostic_mask_computation",
        ],
        stdout=stdout,
        stderr=stderr,
        check=True,
    )

    app.logger.info("Masks computed.")


def compute_features(intrinsic_resolution, depth_scale):
    run(
        cwd="/third_party/openmask3d/openmask3d",
        args=[
            "python",
            "compute_features_single_scene.py",
            f"data.masks.masks_path={OUTPUT_DIR}/{path.splitext(path.basename(SCENE_PLY_PATH))[0]}_masks.pt",
            f"data.camera.poses_path={SCENE_POSE_DIR}",
            f"data.camera.intrinsic_path={SCENE_INTRINSIC_PATH}",
            f"data.camera.intrinsic_resolution={intrinsic_resolution}",
            f"data.depths.depths_path={SCENE_DEPTH_IMG_DIR}",
            f"data.depths.depth_scale={depth_scale}",
            f"data.depths.depths_ext={path.splitext(listdir(SCENE_DEPTH_IMG_DIR)[0])[1]}",
            f"data.images.images_path={SCENE_COLOR_IMG_DIR}",
            f"data.images.images_ext={path.splitext(listdir(SCENE_COLOR_IMG_DIR)[0])[1]}",
            f"data.point_cloud_path={SCENE_PLY_PATH}",
            f"output.output_directory={OUTPUT_DIR}",
            f"output.save_crops={SAVE_CROPS}",
            f"hydra.run.dir={OUTPUT_DIR}/hydra_outputs/mask_features_computation",
            f"external.sam_checkpoint={SAM_CKPT_PATH}",
            f"gpu.optimize_gpu_usage={OPTIMIZE_GPU_USAGE}",
        ],
        stdout=stdout,
        stderr=stderr,
        check=True,
    )
    app.logger.info("Features computed.")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80, threaded=False)
