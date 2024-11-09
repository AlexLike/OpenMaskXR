# How to import a new pre-processed scan
1. Create a new folder in Scans/ with the scene name
2. Add the meshes and triangle_ids.json files into this folder
	IMPORTANT: change import settings of models: set Optimize Mesh to "Nothing" (we need to preserve ordering) and weld vertices to False
3. Rename the clip.json file to the scene name and put it into the StreamingAssets folder
4. Extract material from textured mesh and set it to two-sided
5. Drag reconstruction mesh (can be uncolored) into scene, add a ObjMeshImporter component to where the MeshFilter is (so likely in default child of object) and set JsonFolder to Scans/<scene_name> (replace with scene name)
6. Click "Create Instance Meshes" in inspector of ObjMeshImporter
7. Drag all created instance meshes (inside Scans/<scene_name>/Instances into scene, parent them to an object called "Instances", then parent this object together with textured reconstruction mesh to an object called <scene_name>
8. Fix scaling and rotation (scale of 0.08 and -90 rotation in x seems reasonable) INSIDE the two children, don't set them in parent
9. Create a prefab in Scans/<scene_name>