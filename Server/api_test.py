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
        cls.test_uid = '12345'

        # Create temporary test directories
        cls.test_mesh_folder = 'test_meshes'
        cls.test_frames_folder = 'test_frames'

        # Update the app configuration to use the test folders
        app.config['MESH_UPLOAD_FOLDER'] = cls.test_mesh_folder
        app.config['FRAMES_UPLOAD_FOLDER'] = cls.test_frames_folder

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
            for file in os.listdir(cls.test_frames_folder):
                os.remove(os.path.join(cls.test_frames_folder, file))
            os.rmdir(cls.test_frames_folder)

    # Test for reconstruct route with multiple valid .obj files and valid JSON (success case)
    def test_reconstruct_with_uid(self):
        # Mock data with two .obj files and valid JSON form data
        data = {
            'file': [
                (BytesIO(b'mock obj content 1'), 'test1.obj'),
                (BytesIO(b'mock obj content 2'), 'test2.obj')
            ],
            'camera_intrinsics': 'mock_intrinsics'
        }
        uid = self.test_uid
        
        # Send the POST request to the /reconstruct/uid route
        response = self.client.post(f'/reconstruct/{uid}', data=data, content_type='multipart/form-data')
        
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the success message
        self.assertIn('Files uploaded successfully!', response.json['message'])
        # Assert that the sub-folder matches the provided UID
        self.assertIn(uid, response.json['sub_folder'])
        # Assert that two files were uploaded
        self.assertEqual(len(response.json['uploaded_files']), 2)
        self.assertIn('test1.obj', response.json['uploaded_files'])
        self.assertIn('test2.obj', response.json['uploaded_files'])

    # Test for reconstruct route with no file part in request (error case)
    def test_reconstruct_no_file(self):
        uid = self.test_uid
        data = {'camera_intrinsics': 'mock_intrinsics'}
        
        # Send the POST request without a file
        response = self.client.post(f'/reconstruct/{uid}', data=data, content_type='multipart/form-data')
        
        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn('No file part in the request', response.json['message'])

    # Test for reconstruct route with file but no JSON (error case)
    def test_reconstruct_no_json(self):
        uid = self.test_uid
        data = {
            'file': (BytesIO(b'mock obj content'), 'test.obj')
        }
        
        # Send the POST request without JSON data (camera_intrinsics)
        response = self.client.post(f'/reconstruct/{uid}', data=data, content_type='multipart/form-data')
        
        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn("Invalid JSON format, required key: 'camera_intrinsics'", response.json['error'])

    # Test for reconstruct route with invalid file type (error case)
    def test_reconstruct_invalid_file_type(self):
        uid = self.test_uid
        data = {
            'file': (BytesIO(b'mock content'), 'test.txt'),  # Invalid file type
            'camera_intrinsics': 'mock_intrinsics'
        }
        
        # Send the POST request with an invalid file type
        response = self.client.post(f'/reconstruct/{uid}', data=data, content_type='multipart/form-data')
        
        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn('Invalid file format for test.txt', response.json['message'])

    # Test for reconstruct route with no files and no JSON (error case)
    def test_reconstruct_no_file_no_json(self):
        uid = self.test_uid
        
        # Send the POST request with no files and no JSON data
        response = self.client.post(f'/reconstruct/{uid}', content_type='multipart/form-data')
        
        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        # Assert that the error message is correct
        self.assertIn('No file part in the request', response.json['message'])

    # Test register-frame route without file
    def test_register_frame_no_file(self):
        response = self.client.post('/register-frame', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('No file part in the request', response.json['message'])

    # Test register-frame route with file but missing JSON field (poses)
    def test_register_frame_missing_json_key(self):
        data = {
            'file': (BytesIO(b'mock jpg content'), 'test.jpg')
        }
        response = self.client.post('/register-frame', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid JSON format, required key: 'poses'", response.json['error'])

    # Test register-frame route with file and valid JSON
    def test_register_frame_with_file_and_json(self):
        data = {
            'file': (BytesIO(b'mock jpg content'), 'test.jpg'),
            'poses': 'mock_poses'
        }
        response = self.client.post('/register-frame', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('File test.jpg uploaded successfully!', response.json['message'])
        self.assertEqual(response.json['json_data']['poses'], 'mock_poses')

    # Test register-frame route with invalid file format
    def test_register_frame_invalid_file(self):
        data = {
            'file': (BytesIO(b'mock jpg content'), 'test.png')
        }
        response = self.client.post('/register-frame', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid file format', response.json['message'])

if __name__ == '__main__':
    unittest.main()
