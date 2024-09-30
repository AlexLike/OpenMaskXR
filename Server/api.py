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

# Ensure the upload folder exists
if not os.path.exists(MESH_UPLOAD_FOLDER):
    os.makedirs(MESH_UPLOAD_FOLDER)

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

        return jsonify({'message': f"File '{file.filename}' uploaded successfully!", 'status': 'success'}), 200
    else:
        return jsonify({'message': 'Invalid file format. Please upload a .obj file.', 'status': 'error'}), 400

    # # Get JSON data from the request body
    # data = request.get_json()

    # # Process the data (Example: Access specific keys from the JSON)
    # if 'name' in data and 'age' in data:
    #     name = data['name']
    #     age = data['age']
    #     response = {
    #         'message': f"Hello {name}, you are {age} years old!",
    #         'status': 'success'
    #     }
    # else:
    #     response = {
    #         'message': 'Invalid data received!',
    #         'status': 'error'
    #     }

    # # Return a JSON response
    # return jsonify(response)

# Route for receiving posed RGB frames
@app.route('/register-frame', methods=['POST'])
def register_frame():
    # Get JSON data from the request body
    data = request.get_json()

    # Process the data (Example: Access specific keys from the JSON)
    if 'name' in data and 'age' in data:
        name = data['name']
        age = data['age']
        response = {
            'message': f"Hello {name}, you are {age} years old!",
            'status': 'success'
        }
    else:
        response = {
            'message': 'Invalid data received!',
            'status': 'error'
        }

    # Return a JSON response
    return jsonify(response)

# Error handling example
@app.errorhandler(404)
def route_not_found(e):
    return "Route not found!", 404

# Run the application
if __name__ == '__main__':
    app.run(debug=True)