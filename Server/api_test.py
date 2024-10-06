import unittest
import os
from io import BytesIO
from api import app

class FlaskAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['MESH_UPLOAD_FOLDER'] = 'test_meshes'
        app.config['FRAMES_UPLOAD_FOLDER'] = 'test_frames'
        cls.client = app.test_client()

        if not os.path.exists(app.config['MESH_UPLOAD_FOLDER']):
            os.makedirs(app.config['MESH_UPLOAD_FOLDER'])
        if not os.path.exists(app.config['FRAMES_UPLOAD_FOLDER']):
            os.makedirs(app.config['FRAMES_UPLOAD_FOLDER'])

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(app.config['MESH_UPLOAD_FOLDER']):
            for f in os.listdir(app.config['MESH_UPLOAD_FOLDER']):
                os.remove(os.path.join(app.config['MESH_UPLOAD_FOLDER'], f))
            os.rmdir(app.config['MESH_UPLOAD_FOLDER'])
        if os.path.exists(app.config['FRAMES_UPLOAD_FOLDER']):
            for f in os.listdir(app.config['FRAMES_UPLOAD_FOLDER']):
                os.remove(os.path.join(app.config['FRAMES_UPLOAD_FOLDER'], f))
            os.rmdir(app.config['FRAMES_UPLOAD_FOLDER'])

    # Test reconstruct route without file
    def test_reconstruct_no_file(self):
        response = self.client.post('/reconstruct', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('No file part in the request', response.json['message'])

    # Test reconstruct route with file but missing JSON field (camera_intrinsics)
    def test_reconstruct_missing_json_key(self):
        data = {
            'file': (BytesIO(b'mock obj content'), 'test.obj')
        }
        response = self.client.post('/reconstruct', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid JSON format, required key: 'camera_intrinsics'", response.json['error'])

    # Test reconstruct route with file and valid JSON
    def test_reconstruct_with_file_and_json(self):
        data = {
            'file': (BytesIO(b'mock obj content'), 'test.obj'),
            'camera_intrinsics': 'mock_intrinsics'
        }
        response = self.client.post('/reconstruct', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('File test.obj uploaded successfully!', response.json['message'])
        self.assertEqual(response.json['json_data']['camera_intrinsics'], 'mock_intrinsics')

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
