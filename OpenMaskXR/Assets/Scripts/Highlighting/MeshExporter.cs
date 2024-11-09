using System.IO;
using UnityEngine;

public class MeshExporter : MonoBehaviour
{
    public GameObject objectToExport;

    public void ExportMesh()
    {
        if (objectToExport == null)
        {
            Debug.LogError("No object assigned to export.");
            return;
        }

        MeshFilter meshFilter = objectToExport.GetComponent<MeshFilter>();
        if (meshFilter == null)
        {
            Debug.LogError("The selected object has no mesh to export.");
            return;
        }

        Mesh mesh = meshFilter.sharedMesh;
        string objData = MeshToString(mesh);

        string filePath = Application.dataPath + "/ExportedMesh.obj";
        File.WriteAllText(filePath, objData);
        Debug.Log("Mesh exported to " + filePath);
    }

    private string MeshToString(Mesh mesh)
    {
        System.Text.StringBuilder sb = new System.Text.StringBuilder();

        // Write vertices
        foreach (Vector3 v in mesh.vertices)
        {
            sb.AppendFormat("v {0} {1} {2}\n", v.x, v.y, v.z);
        }

        // Write normals
        foreach (Vector3 n in mesh.normals)
        {
            sb.AppendFormat("vn {0} {1} {2}\n", n.x, n.y, n.z);
        }

        // Write UVs
        foreach (Vector2 uv in mesh.uv)
        {
            sb.AppendFormat("vt {0} {1}\n", uv.x, uv.y);
        }

        // Write faces
        for (int i = 0; i < mesh.triangles.Length; i += 3)
        {
            sb.AppendFormat("f {0}/{0}/{0} {1}/{1}/{1} {2}/{2}/{2}\n",
                mesh.triangles[i] + 1, mesh.triangles[i + 1] + 1, mesh.triangles[i + 2] + 1);
        }

        return sb.ToString();
    }
}
