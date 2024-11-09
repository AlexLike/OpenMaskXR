using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(MeshExporter))]
public class MeshExporterEditor : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();

        MeshExporter meshExporter = (MeshExporter)target;
        if (GUILayout.Button("Export Mesh"))
        {
            meshExporter.ExportMesh();
        }
    }
}