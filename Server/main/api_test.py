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
    def test_query_VLM_with_all_parameters(self):
        # Define the request payload
        payload = {
            "text": "What is in this image?",
            "instance_id": "0",
            "folder_name": "ScanNet/0000_02-apartment"
        }

        # Make a POST request with JSON data
        response = self.client.post("/query-VLM", json=payload)

        # Check that the request was successful
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("parsed_query", data)

    # Test for /query_VLM route with no text
    def test_query_VLM_missing_text(self):
        # Define the request payload without the "text" field
        payload = {
            "instance_id": "0",
            "folder_name": "ScanNet/0000_02-apartment"
        }

        # Make a POST request with JSON data
        response = self.client.post("/query-VLM", json=payload)

        # Check that the request failed due to missing "text" field
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["message"], "No text part in the request")
        self.assertEqual(data["status"], "error")

    # Test for /query_VLM route with no instance_id
    def test_query_VLM_missing_instance_id(self):
        # Define the request payload without the "instance_id" field
        payload = {
            "text": "What is in this image?",
            "folder_name": "ScanNet/0000_02-apartment"
        }

        # Make a POST request with JSON data
        response = self.client.post("/query-VLM", json=payload)

        # Check that the request failed due to missing "instance_id" field
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["message"], "No instance_id part in the request")
        self.assertEqual(data["status"], "error")

    # Test for /query_VLM route with no folder_name
    def test_query_VLM_missing_folder_name(self):
        # Define the request payload without the "folder_name" field
        payload = {
            "text": "What is in this image?",
            "instance_id": "0",
        }

        # Make a POST request with JSON data
        response = self.client.post("/query-VLM", json=payload)

        # Check that the request failed due to missing "folder_name" field
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["message"], "No folder_name part in the request")
        self.assertEqual(data["status"], "error")

if __name__ == "__main__":
    unittest.main()
