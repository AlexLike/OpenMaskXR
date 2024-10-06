from flask import Flask, request, jsonify
import os

# Initialize the Flask application
app = Flask(__name__)

# Define the home route
@app.route('/')
def home():
    return "Hello, Flask!"

# Configure the folder to save reconstruction mesh
MESH_UPLOAD_FOLDER = 'meshes'
app.config['MESH_UPLOAD_FOLDER'] = MESH_UPLOAD_FOLDER

# Ensure the meshes upload folder exists
if not os.path.exists(MESH_UPLOAD_FOLDER):
    os.makedirs(MESH_UPLOAD_FOLDER)

# Configure the folder to save RGB frames
FRAMES_UPLOAD_FOLDER = 'frames'
app.config['FRAMES_UPLOAD_FOLDER'] = FRAMES_UPLOAD_FOLDER

# Ensure the frames upload folder exists
if not os.path.exists(FRAMES_UPLOAD_FOLDER):
    os.makedirs(FRAMES_UPLOAD_FOLDER)

# Route for receiving reconstruction mesh and camera intrinsics
@app.route('/reconstruct', methods=['POST'])
def reconstruct():
     # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request', 'status': 'error'}), 400

    file = request.files['file']

    # Check if the file has a valid name
    if file.filename == '':
        return jsonify({'message': 'No selected file', 'status': 'error'}), 400

    # Check if the uploaded file is an OBJ file
    if file and file.filename.endswith('.obj'):
        file_path = os.path.join(app.config['MESH_UPLOAD_FOLDER'], file.filename)
        file.save(file_path)  # Save the file
  
        # Get JSON data from the request body
        data = request.get_json()

        # Check if JSON is present and process it
        if data:
            # Accessing fields from the JSON
            if 'camera_intrinsics' in data:
                camera_intrinsics = data['camera_intrinsics']
            else:
                return jsonify({"error": "Invalid JSON format, required key: 'camera_intrinsics'"}), 400
        else:
            return jsonify({"error": "No JSON data found"}), 400

        # Return a success response
        return jsonify({
            "message": f"File {file.filename} uploaded successfully!",
            "json_data": {
                "camera_intrinsics": camera_intrinsics
            }
        }), 200

    else:
        return jsonify({'message': 'Invalid file format. Please upload a .obj file.', 'status': 'error'}), 400

# Route for receiving posed RGB frames
@app.route('/register-frame', methods=['POST'])
def register_frame():
     # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request', 'status': 'error'}), 400

    file = request.files['file']

    # Check if the file has a valid name
    if file.filename == '':
        return jsonify({'message': 'No selected file', 'status': 'error'}), 400

    # Check if the uploaded file is a JPEG file
    if file and file.filename.endswith('.jpg'):
        file_path = os.path.join(app.config['FRAMES_UPLOAD_FOLDER'], file.filename)
        file.save(file_path)  # Save the file

        # Get JSON data from the request body
        data = request.get_json()

        # Check if JSON is present and process it
        if data:
            # Accessing fields from the JSON
            if 'poses' in data:
                poses = data['poses']
            else:
                return jsonify({"error": "Invalid JSON format, required key: 'poses'"}), 400
        else:
            return jsonify({"error": "No JSON data found"}), 400

        # Return a success response
        return jsonify({
            "message": f"File {file.filename} uploaded successfully!",
            "json_data": {
                "poses": poses
            }
        }), 200
    else:
        return jsonify({'message': 'Invalid file format. Please upload a .jpg file.', 'status': 'error'}), 400

# Error handling example
@app.errorhandler(404)
def route_not_found(e):
    return "Route not found!", 404

# Run the application
if __name__ == '__main__':
    app.run(debug=True)