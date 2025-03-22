Python script for blender, exports mesh, and armature animation data to text format.
Output goes to blender folder
Example file (vertex normal texcoord):

vnt
verts:xyz,bones:xzy
-1.0 -1.0 0.0 0.0 0.0 1.0 0.0716 0.0325
1.0 -1.0 0.0 0.0 0.0 1.0 0.6706 0.0325
1.0 -1.0 0.0 0.0 0.0 1.0 0.8972 0.3372
-1.0 1.0 0.0 0.0 0.0 1.0 0.0716 0.6315
-1.0 1.0 0.0 0.0 0.0 1.0 0.2982 0.9362
1.0 1.0 0.0 0.0 0.0 1.0 0.8972 0.9362

indices
1 3 0
2 5 4

frames_qty: 2
bone_name: bottom
xloc 0.0 xloc 0.0
zloc 0.0 zloc 0.0
yloc -0.0 yloc -0.0
wrot 1.0 wrot 0.995
xrot 0.0 xrot 0.0
zrot 0.0 zrot -0.0998
yrot -0.0 yrot 0.0007
xscale 1.0 xscale 1.0
zscale 1.0 zscale 1.0
yscale 1.0 yscale 1.0
bone_name: top
xloc 0.0 xloc 0.0
zloc 0.0 zloc 0.0
yloc -0.0 yloc -0.0
wrot 0.9333 wrot 1.0
xrot -0.0 xrot 0.0
zrot 0.3591 zrot 0.0
yrot 0.0 yrot -0.0
xscale 1.0 xscale 1.0
zscale 1.0 zscale 1.0
yscale 1.0 yscale 1.0
bottom pos: -0.0 0.0069 0.8732 quaternion: 1.0 0.0035 0.0 -0.0 parent: None
top pos: -0.0 -0.0 -0.8367 quaternion: 1.0 -0.0035 -0.0 -0.0 parent name: bottom
