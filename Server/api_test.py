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

        # Update the app configuration to use the test folders
        app.config["MESH_UPLOAD_FOLDER"] = cls.test_mesh_folder
        app.config["FRAMES_UPLOAD_FOLDER"] = cls.test_frames_folder

        # Ensure test mesh folder exists before tests run
        if not os.path.exists(cls.test_mesh_folder):
            os.makedirs(cls.test_mesh_folder)

        # Ensure test frames folder exists
        if not os.path.exists(cls.test_frames_folder):
            os.makedirs(cls.test_frames_folder)

    @classmethod
    def tearDownClass(cls):
        """Clean up resources after all tests have run"""
        # Clean up by removing the test mesh folder and its contents
        if os.path.exists(cls.test_mesh_folder):
            for root, dirs, files in os.walk(cls.test_mesh_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(cls.test_mesh_folder)

        # Clean up any frames uploaded during the test
        if os.path.exists(cls.test_frames_folder):
            for root, dirs, files in os.walk(cls.test_frames_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(cls.test_frames_folder)

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
        # Assert that the response contains the list of .obj files
        self.assertIn("test_file.obj", response.json["files"])
        # Assert that the success message is correct
        self.assertIn(
            f"Mesh files for UID {test_uid} retrieved successfully",
            response.json["message"],
        )

    # Test the /recall/<uid> route with a valid UID but no .obj files in the subfolder
    def test_recall_with_valid_uid_no_obj_files(self):
        # Specify the test UID and its mesh folder
        test_uid = "test_uid"
        test_mesh_folder = os.path.join(self.test_mesh_folder, test_uid)

        # Ensure the test folder for the UID exists and it's empty
        os.makedirs(test_mesh_folder, exist_ok=True)

        # Remove any existing files to ensure the folder is empty
        for file in os.listdir(test_mesh_folder):
            os.remove(os.path.join(test_mesh_folder, file))

        # Send the GET request to the /recall/<uid> route
        response = self.client.get(f"/recall/{test_uid}")

        # Assert that the response status code is 404
        self.assertEqual(response.status_code, 404)
        # Assert that the error message indicates no .obj files found
        self.assertIn(
            f"No .obj files found in folder for UID {test_uid}",
            response.json["message"],
        )

    # Test the /recall/<uid> route with an invalid (non-existent) UID
    def test_recall_with_invalid_uid(self):
        # Send the GET request to the /recall/<uid> route with a non-existent UID
        response = self.client.get(f"/recall/non_existent_uid")

        # Assert that the response status code is 404
        self.assertEqual(response.status_code, 404)
        # Assert that the error message indicates no mesh files found for the invalid UID
        self.assertIn(
            "No mesh files found for UID non_existent_uid", response.json["message"]
        )


if __name__ == "__main__":
    unittest.main()
