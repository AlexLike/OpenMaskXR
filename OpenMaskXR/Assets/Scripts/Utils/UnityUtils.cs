using UnityEngine;

public static class UnityUtils
{
    // Find a child GameObject by name
    public static GameObject FindChild(Transform parent, string childName)
    {
        foreach (Transform child in parent)
        {
            if (child.name == childName)
            {
                return child.gameObject;
            }

            GameObject found = FindChild(child, childName);
            if (found != null)
            {
                return found;
            }
        }

        return null;
    }
}
