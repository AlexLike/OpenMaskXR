#if UNITY_EDITOR

using Leguar.TotalJSON;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

public class ObjMeshImporter : MonoBehaviour
{
    public string jsonFolder; // Folder containing triangle_ids.json file, also instances will be saved here
    public Material highlightMaterial;
    private Dictionary<int, int[]> instances;
    private Mesh importedMesh;

    public void CreateInstanceMeshes()
    {
        importedMesh = GetComponent<MeshFilter>().sharedMesh;
        ParseJson();
        //GameObject parent = new GameObject("Instances");
        // Make Instances folder if it doesn't exist
        if (!AssetDatabase.IsValidFolder(Path.Combine("Assets", jsonFolder, "Instances")))
        {
            AssetDatabase.CreateFolder(Path.Combine("Assets", jsonFolder), "Instances");
        }

        if (importedMesh != null)
        {
            foreach (int id in instances.Keys)
            {
                List<int> ids = instances[id].ToList();
                //Debug.Log("id: " + id);
                //Debug.Log("Triangle ids: " + string.Join(", ", ids));
                Mesh newMesh = CreateMeshFromTriangles(importedMesh, ids);

                AssetDatabase.CreateAsset(newMesh, Path.Combine(new string[] { "Assets", jsonFolder, "Instances", id + ".asset" }));
                AssetDatabase.SaveAssets();

                //GameObject newInstance = AssignNewMesh(newMesh, id.ToString());
                //newInstance.GetComponent<MeshRenderer>().material = highlightMaterial;
                //newInstance.transform.SetParent(parent.transform);
            }
        }
    }


    // Function to create a new mesh using only selected triangles and preserve colors
    public Mesh CreateMeshFromTriangles(Mesh originalMesh, List<int> triangleIDs)
    {
        List<Vector3> newVertices = new List<Vector3>();
        List<Color> newColors = new List<Color>();
        List<int> newTriangles = new List<int>();
        Dictionary<int, int> vertexMap = new Dictionary<int, int>();

        int[] triangles = originalMesh.triangles;
        Vector3[] vertices = originalMesh.vertices;
        //Color[] colors = originalMesh.colors;

        foreach (int id in triangleIDs)
        {
            if (id * 3 + 2 < triangles.Length)
            {
                for (int i = 0; i < 3; i++)
                {
                    int originalVertexIndex = triangles[id * 3 + i];

                    if (!vertexMap.ContainsKey(originalVertexIndex))
                    {
                        vertexMap[originalVertexIndex] = newVertices.Count;
                        newVertices.Add(vertices[originalVertexIndex]);
                        //newColors.Add(colors[originalVertexIndex]); // Preserve color
                    }

                    newTriangles.Add(vertexMap[originalVertexIndex]);
                }
            }
            else
            {
                Debug.LogWarning("Triangle ID " + id + " is out of bounds.");
            }
        }

        Mesh newMesh = new Mesh();
        newMesh.SetVertices(newVertices);
        newMesh.SetTriangles(newTriangles, 0);
        //newMesh.colors = newColors.ToArray(); // Set colors on the new mesh
        newMesh.RecalculateNormals();

        return newMesh;
    }

    // Function to assign the new mesh to a MeshFilter or create a new GameObject
    private GameObject AssignNewMesh(Mesh newMesh, string name = "SelectedTrianglesMesh")
    {
        GameObject newObject = new GameObject(name);
        newObject.AddComponent<MeshFilter>().mesh = newMesh;

        // Use sharedMaterial in Edit Mode to prevent material instantiation
        if (Application.isEditor && !Application.isPlaying)
        {
            newObject.AddComponent<MeshRenderer>().sharedMaterial = GetComponent<MeshRenderer>().sharedMaterial;
        }
        else
        {
            newObject.AddComponent<MeshRenderer>().material = GetComponent<MeshRenderer>().material;
        }

        return newObject;
    }

    private void ParseJson()
    {
        // Load a dummy file for now
        instances = new Dictionary<int, int[]>();
        string path = Path.Combine(new string[] { Application.dataPath, jsonFolder, "triangle_ids.json" });
        if (File.Exists(path))
        {
            string json = File.ReadAllText(path);
            JSON jsonObject = JSON.ParseString(json);
            foreach (string key in jsonObject.Keys)
            {
                int[] vec = jsonObject.GetJArray(key).AsIntArray();
                instances.Add(int.Parse(key), vec);
            }
        }
        else
        {
            Debug.LogError("Cannot find JSON file at path: " + path);
        }
    }

    // UNUSED
    /*
    public Mesh ImportObjFile(string path)
    {
        if (!File.Exists(path))
        {
            Debug.LogError("File not found: " + path);
            return null;
        }

        List<Vector3> vertices = new List<Vector3>();
        List<Color> colors = new List<Color>();
        List<int> triangles = new List<int>();

        foreach (string line in File.ReadAllLines(path))
        {
            if (line.StartsWith("v "))
            {
                string[] parts = line.Split(' ');
                float x = float.Parse(parts[1]);
                float y = float.Parse(parts[2]);
                float z = float.Parse(parts[3]);
                vertices.Add(new Vector3(x, y, z));

                // If RGB values are specified, parse them; otherwise, add a default color
                if (parts.Length >= 7)
                {
                    float r = float.Parse(parts[4]);
                    float g = float.Parse(parts[5]);
                    float b = float.Parse(parts[6]);
                    colors.Add(new Color(r, g, b));
                }
                else
                {
                    colors.Add(Color.white); // Default color if no color information is provided
                }
            }
            else if (line.StartsWith("f "))
            {
                string[] parts = line.Split(' ');
                foreach (string part in parts.Skip(1)) // Skip "f"
                {
                    string[] indices = part.Split('/');
                    int vertexIndex = int.Parse(indices[0]) - 1;
                    triangles.Add(vertexIndex);
                }
            }
        }

        Mesh mesh = new Mesh();
        mesh.SetVertices(vertices);
        mesh.SetTriangles(triangles, 0);
        mesh.colors = colors.ToArray(); // Assign vertex colors if available
        mesh.RecalculateNormals();

        GetComponent<MeshFilter>().mesh = mesh;

        return mesh;
    }
    */
}

#endif