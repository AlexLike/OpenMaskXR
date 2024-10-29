# Preprocessing Scenes

In [Meshlab](https://www.meshlab.net/),

1. Import PLY as Mesh
2. Filters -> Texture -> Parameterization: Trivial per triangle. Choose a texture size of 4096px.
3. Filters -> Texture -> Transfer: Vertex Attributes to Texture.
4. Export to OBJ w/ texture.

In [Blender](https://www.blender.org/),

1. Import OBJ w/ texture.
2. Set zero rotation.
3. Eye-ball align origin with center-bottom of model.
