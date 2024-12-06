#     ____                   __  ___           __  _  __ ____
#    / __ \____  ___  ____  /  |/  /___ ______/ /_| |/ // __ \
#   / / / / __ \/ _ \/ __ \/ /|_/ / __ `/ ___/ //_/   // /_/ /
#  / /_/ / /_/ /  __/ / / / /  / / /_/ (__  ) ,< /   |/ _, _/
#  \____/ .___/\___/_/ /_/_/  /_/\__,_/____/_/|_/_/|_/_/ |_|
#      /_/
#
#  Created by Hanqiu Li Cai, Michael Siebenmann, Omar Majzoub, and Alexander Zank
#  and available under the MIT License. (See <ProjectRoot>/LICENSE.)

import unittest
import os
from io import BytesIO
from api import app
import zipfile
import json

class FlaskAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up resources needed for all tests, such as initializing test client"""
        cls.client = app.test_client()
        cls.client.testing = True
        cls.test_uid = "12345"

        # Create temporary test directories
        cls.test_mesh_folder = "test_meshes"
        cls.test_frames_folder = "test_frames"

        # Paths for additional folders
        TRIANGLE_ID_FOLDER = 'test_triangle_id_to_object_id'
        CLIP_FOLDER = 'test_object_id_to_CLIP'

        cls.test_triangle_folder = TRIANGLE_ID_FOLDER
        cls.test_clip_folder = CLIP_FOLDER

        # Update the app configuration to use the test folders
        app.config["MESH_UPLOAD_FOLDER"] = cls.test_mesh_folder
        app.config["FRAMES_UPLOAD_FOLDER"] = cls.test_frames_folder
        app.config["TRIANGLE_TO_OBJECT_FOLDER"] = cls.test_triangle_folder
        app.config["OBJECT_TO_CLIP_FOLDER"] = cls.test_clip_folder

        # Ensure test mesh folder exists before tests run
        if not os.path.exists(cls.test_mesh_folder):
            os.makedirs(cls.test_mesh_folder)

        # Ensure test frames folder exists
        if not os.path.exists(cls.test_frames_folder):
            os.makedirs(cls.test_frames_folder)

        os.makedirs(cls.test_triangle_folder, exist_ok=True)
        os.makedirs(cls.test_clip_folder, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # Clean up the test folders
        for folder in [cls.test_mesh_folder, cls.test_triangle_folder, cls.test_clip_folder, cls.test_frames_folder]:
            for uid_folder in os.listdir(folder):
                uid_folder_path = os.path.join(folder, uid_folder)
                if os.path.isdir(uid_folder_path):
                    for file in os.listdir(uid_folder_path):
                        os.remove(os.path.join(uid_folder_path, file))
                    os.rmdir(uid_folder_path)
            os.rmdir(folder)

    # Test for reconstruct route with multiple valid .obj files and valid JSON (success case)
    def test_reconstruct_with_uid(self):
        # Mock data with two .obj files and valid JSON form data
        data = {
            "file": [
                (BytesIO(b"mock obj content 1"), "test1.obj"),
                (BytesIO(b"mock obj content 2"), "test2.obj"),
            ],
            "camera_intrinsics": "mock_intrinsics",
        }
        uid = self.test_uid

        # Send the POST request to the /reconstruct/uid route
        response = self.client.post(
            f"/reconstruct/{uid}", data=data, content_type="multipart/form-data"
        )

        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the success message
        self.assertIn("Files uploaded successfully!", response.json["message"])
        # Assert that the sub-folder matches the provided UID
        self.assertIn(uid, response.json["sub_folder"])
        # Assert that two files were uploaded
        self.assertEqual(len(response.json["uploaded_files"]), 2)
        self.assertIn("test1.obj", response.json["uploaded_files"])
        self.assertIn("test2.obj", response.json["uploaded_files"])

    # Test for reconstruct route with no file part in request (error case)
    def test_reconstruct_no_file(self):
        uid = self.test_uid
        data = {"camera_intrinsics": "mock_intrinsics"}

        # Send the POST request without a file
        response = self.client.post(
            f"/reconstruct/{uid}", data=data, content_type="multipart/form-data"
        )

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn("No file part in the request", response.json["message"])

    # Test for reconstruct route with file but no JSON (error case)
    def test_reconstruct_no_json(self):
        uid = self.test_uid
        data = {"file": (BytesIO(b"mock obj content"), "test.obj")}

        # Send the POST request without JSON data (camera_intrinsics)
        response = self.client.post(
            f"/reconstruct/{uid}", data=data, content_type="multipart/form-data"
        )

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn(
            "Invalid JSON format, required key: 'camera_intrinsics'",
            response.json["error"],
        )

    # Test for reconstruct route with invalid file type (error case)
    def test_reconstruct_invalid_file_type(self):
        uid = self.test_uid
        data = {
            "file": (BytesIO(b"mock content"), "test.txt"),  # Invalid file type
            "camera_intrinsics": "mock_intrinsics",
        }

        # Send the POST request with an invalid file type
        response = self.client.post(
            f"/reconstruct/{uid}", data=data, content_type="multipart/form-data"
        )

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn("Invalid file format for test.txt", response.json["message"])

    # Test for reconstruct route with no files and no JSON (error case)
    def test_reconstruct_no_file_no_json(self):
        uid = self.test_uid

        # Send the POST request with no files and no JSON data
        response = self.client.post(
            f"/reconstruct/{uid}", content_type="multipart/form-data"
        )

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn("No file part in the request", response.json["message"])

    def test_register_frame_with_file_and_poses(self):
        frame_number = "001"
        data = {
            "file": (BytesIO(b"mock jpg content"), "test_frame.jpg"),
            "poses": '{"pose1": [1,0,0], "pose2": [0,1,0]}',  # Poses as form data
        }

        # Send the POST request using data=data
        response = self.client.post(
            f"/register-frame/{self.test_uid}?frame_number={frame_number}",
            data=data,
            content_type="multipart/form-data",
        )

        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the success message
        self.assertIn(
            f"File {frame_number}.jpg uploaded successfully!", response.json["message"]
        )
        # Assert that the 'poses' key is included in the response
        self.assertIn("poses", response.json["json_data"])

        # Assert that the file was saved correctly
        saved_file_path = os.path.join(
            app.config["FRAMES_UPLOAD_FOLDER"], self.test_uid, f"{frame_number}.jpg"
        )
        self.assertTrue(os.path.exists(saved_file_path))

    # Test for /register-frame/<uid> route with no file part in request (error case)
    def test_register_frame_no_file(self):
        frame_number = "001"
        data = {}

        # Send the POST request without a file
        response = self.client.post(
            f"/register-frame/{self.test_uid}?frame_number={frame_number}",
            data=data,
            content_type="multipart/form-data",
        )

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn("No file part in the request", response.json["message"])

    # Test for /register-frame/<uid> route with file but no frame_number (error case)
    def test_register_frame_no_frame_number(self):
        data = {"file": (BytesIO(b"mock jpg content"), "test_frame.jpg")}

        # Send the POST request without the frame_number query parameter
        response = self.client.post(
            f"/register-frame/{self.test_uid}",
            data=data,
            content_type="multipart/form-data",
        )

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn("Frame number is required", response.json["message"])

    # Test for /register-frame/<uid> route with invalid file type (error case)
    def test_register_frame_invalid_file_type(self):
        frame_number = "001"
        data = {
            "file": (BytesIO(b"mock content"), "test_frame.txt")  # Invalid file type
        }

        # Send the POST request with an invalid file type
        response = self.client.post(
            f"/register-frame/{self.test_uid}?frame_number={frame_number}",
            data=data,
            content_type="multipart/form-data",
        )

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn(
            "Invalid file format. Please upload a .jpg file.", response.json["message"]
        )

    # Test the /register-frame/<uid> route when 'poses' is missing in the form data
    def test_register_frame_no_poses(self):
        frame_number = "001"
        data = {
            "file": (BytesIO(b"mock jpg content"), "test_frame.jpg")
            # No 'poses' key in form data
        }

        # Send the POST request
        response = self.client.post(
            f"/register-frame/{self.test_uid}?frame_number={frame_number}",
            data=data,
            content_type="multipart/form-data",
        )

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message indicates the missing 'poses' key
        self.assertIn(
            "Invalid JSON format, required key: 'poses'", response.json["error"]
        )

    # Test the /recall/<uid> route with a valid UID containing .obj files in the subfolder
    def test_recall_with_valid_uid(self):
        # Specify the test UID and its mesh folder
        test_uid = "test_uid"
        test_mesh_folder = os.path.join(self.test_mesh_folder, test_uid)

        # Ensure the test folder for the UID exists and create a mock .obj file in it
        os.makedirs(test_mesh_folder, exist_ok=True)
        with open(os.path.join(test_mesh_folder, "test_file.obj"), "w") as f:
            f.write("mock content")

        # Send the GET request to the /recall/<uid> route
        response = self.client.get(f"/recall/{test_uid}")

        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the response is a zip file
        self.assertEqual(response.mimetype, 'application/zip')

        # Open the zip file from the response and check its contents
        zip_content = BytesIO(response.data)
        with zipfile.ZipFile(zip_content, 'r') as zip_file:
            self.assertIn('test_file.obj', zip_file.namelist())

    
    # Test the /recall/<uid> route with valid .obj and corresponding JSON files
    def test_recall_with_valid_uid(self):
        test_uid = 'test_uid'
        test_mesh_folder = os.path.join(self.test_mesh_folder, test_uid)
        test_triangle_folder = os.path.join(self.test_triangle_folder, test_uid)
        test_clip_folder = os.path.join(self.test_clip_folder, test_uid)

        # Create necessary subfolders
        os.makedirs(test_mesh_folder, exist_ok=True)
        os.makedirs(test_triangle_folder, exist_ok=True)
        os.makedirs(test_clip_folder, exist_ok=True)

        # Create mock .obj file
        obj_file = 'test_file.obj'
        with open(os.path.join(test_mesh_folder, obj_file), 'w') as f:
            f.write('mock content')

        # Create corresponding triangle_id_to_object_id JSON
        triangle_json = {'data': [[1, 100], [2, 101]]}
        with open(os.path.join(test_triangle_folder, 'test_file.json'), 'w') as f:
            json.dump(triangle_json, f)

        # Create corresponding object_id_to_CLIP JSON
        clip_json = {'data': [[100, [0.1, 0.2]], [101, [0.3, 0.4]]]}
        with open(os.path.join(test_clip_folder, 'test_file.json'), 'w') as f:
            json.dump(clip_json, f)

        # Send the GET request to /recall/<uid>
        response = self.client.get(f'/recall/{test_uid}')
        
        # Assert the response is a zip file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/zip')

        # Check contents of the zip file
        zip_content = BytesIO(response.data)
        with zipfile.ZipFile(zip_content, 'r') as zip_file:
            self.assertIn(f'{test_uid}/test_file.obj', zip_file.namelist())
            self.assertIn(f'{test_uid}/test_file.json', zip_file.namelist())

    # Test the /recall/<uid> route with valid .obj but missing JSON files
    def test_recall_with_missing_json(self):
        test_uid = 'test_uid'
        test_mesh_folder = os.path.join(self.test_mesh_folder, test_uid)
        test_triangle_folder = os.path.join(self.test_triangle_folder, test_uid)
        test_clip_folder = os.path.join(self.test_clip_folder, test_uid)

        # Create necessary subfolders
        os.makedirs(test_mesh_folder, exist_ok=True)
        os.makedirs(test_triangle_folder, exist_ok=True)
        os.makedirs(test_clip_folder, exist_ok=True)

        # Create mock .obj file
        obj_file = 'test_file.obj'
        with open(os.path.join(test_mesh_folder, obj_file), 'w') as f:
            f.write('mock content')

        # Do not create corresponding JSON files to simulate missing files

        # Send the GET request to /recall/<uid>
        response = self.client.get(f'/recall/{test_uid}')

        # Assert the response is a 404 due to missing JSON files
        self.assertEqual(response.status_code, 404)
        self.assertIn('Missing triangle ID mapping for test_file.obj', response.json['message'])

    # Test for /text-to-CLIP route
    def test_text_to_CLIP_with_text(self):
        data = {"text": (BytesIO(b"mock jpg content"), "test_frame.jpg")}

        # Define the request payload
        payload = {
            "text": "Sample text to encode"
        }

        # Make a POST request with JSON data
        response = self.client.post("/text-to-CLIP", json=payload)

        # Check that the request was successful
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("CLIP_embedding", data)

    # Test for /text-to-CLIP route with no text
    def test_text_to_CLIP_missing_text(self):
        # Define the request payload without the "text" field
        payload = {}

        # Make a POST request with JSON data
        response = self.client.post("/text-to-CLIP", json=payload)

        # Check that the request failed due to missing "text" field
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["message"], "No text part in the request")
        self.assertEqual(data["status"], "error")

    # Test for /parse-with-LLM route
    def test_parse_with_LLM_with_text(self):
        # Define the request payload
        payload = {
            "text": "I'm looking for a small chair in this room"
        }

        # Make a POST request with JSON data
        response = self.client.post("/parse-with-LLM", json=payload)

        # Check that the request was successful
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("parsed_query", data)

    # Test for /parse-with-LLM route with no text
    def test_parse_with_LLM_missing_text(self):
        # Define the request payload without the "text" field
        payload = {}

        # Make a POST request with JSON data
        response = self.client.post("/parse-with-LLM", json=payload)

        # Check that the request failed due to missing "text" field
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["message"], "No text part in the request")
        self.assertEqual(data["status"], "error")

    # Test for /query-VLM route
    def test_query_VLM_with_text_and_image(self):
        # Define the request payload
        payload = {
            "text": "What is in this image?",
            "images": ["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"]
        }

        # Make a POST request with JSON data
        response = self.client.post("/query-VLM", json=payload)

        # Check that the request was successful
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("parsed_query", data)

    # Test for /query_VLM route with no image
    def test_query_VLM_missing_image(self):
        # Define the request payload without the "images" field
        payload = {
            "text": "What is in this image?",
        }

        # Make a POST request with JSON data
        response = self.client.post("/query-VLM", json=payload)

        # Check that the request failed due to missing "images" field
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["message"], "No images part in the request")
        self.assertEqual(data["status"], "error")

    # Test for /query_VLM route with no text
    def test_query_VLM_missing_text(self):
        # Define the request payload without the "text" field
        payload = {
            "images": ["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"]
        }

        # Make a POST request with JSON data
        response = self.client.post("/query-VLM", json=payload)

        # Check that the request failed due to missing "text" field
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["message"], "No text part in the request")
        self.assertEqual(data["status"], "error")

    

if __name__ == "__main__":
    unittest.main()
