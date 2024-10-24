#     ____                   __  ___           __  _  __ ____
#    / __ \____  ___  ____  /  |/  /___ ______/ /_| |/ // __ \
#   / / / / __ \/ _ \/ __ \/ /|_/ / __ `/ ___/ //_/   // /_/ /
#  / /_/ / /_/ /  __/ / / / /  / / /_/ (__  ) ,< /   |/ _, _/
#  \____/ .___/\___/_/ /_/_/  /_/\__,_/____/_/|_/_/|_/_/ |_|
#      /_/
#
#  Created by Hanqiu Li Cai, Michael Siebenmann, Omar Majzoub, and Alexander Zank
#  and available under the MIT License. (See <ProjectRoot>/LICENSE.)

from flask import Flask, request, jsonify
import os
import zipfile
import io
from flask import send_file
import json

# Initialize the Flask application
app = Flask(__name__)


# Define the home route
@app.route("/")
def home():
    return "Hello, Flask!"


# Configure the folder to save reconstruction mesh
MESH_UPLOAD_FOLDER = "meshes"
app.config["MESH_UPLOAD_FOLDER"] = MESH_UPLOAD_FOLDER

# Ensure the meshes upload folder exists
if not os.path.exists(MESH_UPLOAD_FOLDER):
    os.makedirs(MESH_UPLOAD_FOLDER)

# Configure the folder to save RGB frames
FRAMES_UPLOAD_FOLDER = "frames"
app.config["FRAMES_UPLOAD_FOLDER"] = FRAMES_UPLOAD_FOLDER

# Ensure the frames upload folder exists
if not os.path.exists(FRAMES_UPLOAD_FOLDER):
    os.makedirs(FRAMES_UPLOAD_FOLDER)


# Folders for additional mappings
TRIANGLE_TO_OBJECT_FOLDER = 'triangle_id_to_object_id'
OBJECT_TO_CLIP_FOLDER = 'object_id_to_CLIP'

app.config['TRIANGLE_TO_OBJECT_FOLDER'] = TRIANGLE_TO_OBJECT_FOLDER

# Ensure the triangle to object folder exists
if not os.path.exists(TRIANGLE_TO_OBJECT_FOLDER):
    os.makedirs(TRIANGLE_TO_OBJECT_FOLDER)

app.config['OBJECT_TO_CLIP_FOLDER'] = OBJECT_TO_CLIP_FOLDER

# Ensure the object to clip folder exists
if not os.path.exists(OBJECT_TO_CLIP_FOLDER):
    os.makedirs(OBJECT_TO_CLIP_FOLDER)

@app.route("/reconstruct/<uid>", methods=["POST"])
def reconstruct(uid):
    # Ensure the sub-folder for the given UID exists
    folder_path = os.path.join(app.config["MESH_UPLOAD_FOLDER"], uid)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Check if there are files in the request
    if "file" not in request.files:
        return (
            jsonify({"message": "No file part in the request", "status": "error"}),
            400,
        )

    # Get the list of files
    files = request.files.getlist("file")

    # Validate that there are files
    if not files or all(f.filename == "" for f in files):
        return jsonify({"message": "No selected file", "status": "error"}), 400

    saved_files = []

    # Process each file
    for file in files:
        # Check if the uploaded file is an OBJ file
        if file and file.filename.endswith(".obj"):
            file_path = os.path.join(folder_path, file.filename)
            file.save(file_path)  # Save the file
            saved_files.append(file.filename)
        else:
            return (
                jsonify(
                    {
                        "message": f"Invalid file format for {file.filename}. Please upload .obj files.",
                        "status": "error",
                    }
                ),
                400,
            )

    # Get JSON data from the request form
    if "camera_intrinsics" in request.form:
        camera_intrinsics = request.form["camera_intrinsics"]
    else:
        return (
            jsonify(
                {"error": "Invalid JSON format, required key: 'camera_intrinsics'"}
            ),
            400,
        )

    # Return a success response
    return (
        jsonify(
            {
                "message": "Files uploaded successfully!",
                "uploaded_files": saved_files,
                "sub_folder": uid,
                "json_data": {"camera_intrinsics": camera_intrinsics},
            }
        ),
        200,
    )


# Route for receiving posed RGB frames
@app.route("/register-frame/<uid>", methods=["POST"])
def register_frame(uid):
    if "file" not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files["file"]
    frame_number = request.args.get("frame_number")

    if not frame_number:
        return jsonify({"message": "Frame number is required"}), 400

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    # Only allow jpg files
    if not file.filename.endswith(".jpg"):
        return (
            jsonify({"message": "Invalid file format. Please upload a .jpg file."}),
            400,
        )

    # Create the sub-folder if it doesn't exist
    uid_folder = os.path.join(app.config["FRAMES_UPLOAD_FOLDER"], uid)
    os.makedirs(uid_folder, exist_ok=True)

    # Save the file
    file_path = os.path.join(uid_folder, f"{frame_number}.jpg")
    file.save(file_path)

    # Get JSON data from the request form
    if "poses" in request.form:
        poses = request.form["poses"]
    else:
        return jsonify({"error": "Invalid JSON format, required key: 'poses'"}), 400

    # Return a success response
    return (
        jsonify(
            {
                "message": f"File {frame_number}.jpg uploaded successfully!",
                "json_data": {"poses": poses},
            }
        ),
        200,
    )


# Route to recall mesh files and return them in a zip folder along with the corresponding JSON mappings
@app.route('/recall/<uid>', methods=['GET'])
def recall(uid):
    # Get the folder paths for the given UID
    mesh_folder = os.path.join(app.config['MESH_UPLOAD_FOLDER'], uid)
    triangle_folder = os.path.join(app.config['TRIANGLE_TO_OBJECT_FOLDER'], uid)
    clip_folder = os.path.join(app.config['OBJECT_TO_CLIP_FOLDER'], uid)
    
    # Check if the mesh folder exists
    if not os.path.exists(mesh_folder):
        return jsonify({'message': f'No mesh files found for UID {uid}'}), 404
    
    # Find all .obj files in the mesh folder
    obj_files = [f for f in os.listdir(mesh_folder) if f.endswith('.obj')]
    
    # If no .obj files are found, return a 404 response
    if not obj_files:
        return jsonify({'message': f'No .obj files found in folder for UID {uid}'}), 404

    # Check if triangle_id_to_object_id and object_id_to_CLIP folders exist for the UID
    if not os.path.exists(triangle_folder):
        return jsonify({'message': f'Triangle ID mappings not found for UID {uid}'}), 404
    if not os.path.exists(clip_folder):
        return jsonify({'message': f'Object ID to CLIP mappings not found for UID {uid}'}), 404

    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add each .obj file and corresponding JSON mappings
        for obj_file in obj_files:
            obj_file_path = os.path.join(mesh_folder, obj_file)
            zip_file.write(obj_file_path, os.path.join(uid, obj_file))  # Add the .obj file
            
            # Add the corresponding triangle_id_to_object_id JSON file
            triangle_file = obj_file.replace('.obj', '.json')
            triangle_file_path = os.path.join(triangle_folder, triangle_file)
            if os.path.exists(triangle_file_path):
                zip_file.write(triangle_file_path, os.path.join(uid, triangle_file))
            else:
                return jsonify({'message': f'Missing triangle ID mapping for {obj_file}'}), 404
            
            # Add the corresponding object_id_to_CLIP JSON file
            clip_file_path = os.path.join(clip_folder, triangle_file)
            if os.path.exists(clip_file_path):
                zip_file.write(clip_file_path, os.path.join(uid, triangle_file))
            else:
                return jsonify({'message': f'Missing CLIP mapping for {obj_file}'}), 404

    # Move the buffer's position to the beginning
    zip_buffer.seek(0)

    # Send the zip file as a downloadable response
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'mesh_files_and_mappings_{uid}.zip'
    )

# Error handling example
@app.errorhandler(404)
def route_not_found(e):
    return "Route not found!", 404


# Run the application
if __name__ == "__main__":
    app.run(debug=True)
