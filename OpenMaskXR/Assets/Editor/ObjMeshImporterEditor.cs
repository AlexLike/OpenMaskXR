using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(ObjMeshImporter))]
public class ObjMeshImporterEditor : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector(); // Draw the default Inspector UI

        ObjMeshImporter objMeshImporter = (ObjMeshImporter)target;

        // Add buttons labeled "Import and Create New Mesh" and "Create Instance Meshes" in the Inspector
        if (GUILayout.Button("Import and Create New Mesh"))
        {
            objMeshImporter.ImportAndCreateMesh();
        }
        if (GUILayout.Button("Create Instance Meshes"))
        {
            objMeshImporter.CreateInstanceMeshes();
        }
    }
}
