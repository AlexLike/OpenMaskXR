using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(ObjMeshImporter))]
public class ObjMeshImporterEditor : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector(); // Draw the default Inspector UI

        ObjMeshImporter objMeshImporter = (ObjMeshImporter)target;

        if (GUILayout.Button("Create Instance Meshes"))
        {
            objMeshImporter.CreateInstanceMeshes();
        }
    }
}
