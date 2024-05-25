import bpy
from mathutils import Vector
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
import mathutils
from mathutils import(
    Vector,
    Matrix,
    Quaternion
)
from bpy.types import (
    Action,
    Armature,
    Mesh,
    Operator
)


separator = " "
decimals=4

def formatDigit(digit):
    result = ""
    result += str(round(digit, decimals))
    return result

def vecStr(vec, ):

    result = ""
    for i in vec:
        result += str(round(i, decimals)) + separator
    return result

outputSting = ""

def printOut(input):
    global outputSting
    if(isinstance(input, str)):
        outputSting += input + "\n"
    else:
        outputSting += str(input) + "\n"


obj = bpy.context.active_object

vertsQty = len(obj.data.vertices)
polygonsQty = len(obj.data.polygons)

uvlayer = obj.data.uv_layers.active
hasUv = uvlayer is not None
vertlists = [[] if hasUv else [Vector((0,0))] for i in range(vertsQty)]

vertices = obj.data.vertices
polygons = obj.data.polygons


faceSub = [[-1, -1, -1] for i in range(polygonsQty)]

for fn, face in enumerate(polygons):
    for vn, vid, loop in zip(range(3), face.vertices, face.loop_indices):
        uv = uvlayer.data[loop].uv
        i = 0
        while i < len(vertlists[vid]):
            if (vertlists[vid][i] == uv):
                break
            i+=1
                
        if i == len(vertlists[vid]):
            vertlists[vid].append(uv)
                
        faceSub[fn][vn] = i

vertstart = [0 for i in range(vertsQty+1)]
datastr = "" ## Vertices:\n

printOut("vnt")
printOut("verts:xyz,bones:xzy")

for vn, vert in enumerate(obj.data.vertices):
    vertstart[vn+1] = vertstart[vn] + len(vertlists[vn])

    for uv in vertlists[vn]:
        datastr += vecStr(vert.co)
        datastr += vecStr(vert.normal)
        datastr += vecStr(uv)
        datastr += str(vert.groups[0].group)
        datastr += "\n"

printOut(datastr)

printOut("indices")
datastr = ""

for fn, face in enumerate(obj.data.polygons):
    for i in range(3):
        vn = face.vertices[i]
        datastr += str(vertstart[vn] + faceSub[fn][i]) + separator
        
    datastr += "\n"

printOut(datastr)




def convert_armature(armature: Armature):
    coord_tf = Matrix([(1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0)]).to_4x4()
    num_roots = 0
    bones = []
    for bone in armature.bones:
        if bone.parent == None:
            num_roots += 1
            arma_loc, arma_rot, arma_scale = (bone.matrix_local).decompose()
            arma_axis, arma_angle = arma_rot.to_axis_angle()
            bones.append((bone.name, coord_tf @ arma_loc, Quaternion(coord_tf @ arma_axis, arma_angle), None))
        else:
            parent_index = next(idx for (idx, p_bone) in enumerate(armature.bones) if p_bone == bone.parent)
            arma_loc, arma_rot, arma_scale = (bone.parent.matrix_local.inverted() @ bone.matrix_local).decompose()
            arma_axis, arma_angle = arma_rot.to_axis_angle()
            bones.append( ( bone.name, coord_tf @ arma_loc, Quaternion(coord_tf @ arma_axis, arma_angle), parent_index  ) )
    if num_roots > 1:
        bones.insert(0, ('root', Vector(), Quaternion(), None))
        for bone in bones:
            bone = (bone[0], bone[1], bone[2], 0 if bone[3] == None else bone[3] + 1)
    return bones


def action_in_armature(action: Action, armature: Armature) -> bool:
    return set([curve.data_path.split('\"')[1] for curve in action.fcurves]).issubset(set([bone.name for bone in armature.bones]))

XLOC = 'xloc'
YLOC = 'yloc'
ZLOC = 'zloc'

WROT = 'wrot'
XROT = 'xrot'
YROT = 'yrot'
ZROT = 'zrot'

XSCALE = 'xscale'
YSCALE = 'yscale'
ZSCALE = 'zscale'

KEY_TABLE = {'location': [XLOC, YLOC, ZLOC], 'rotation_quaternion': [WROT, XROT, YROT, ZROT], 'scale': [XSCALE, YSCALE, ZSCALE]}
LOC_INDEX_TABLE = [XLOC, YLOC, ZLOC]
ROT_INDEX_TABLE = [XROT, YROT, ZROT]
SCALE_INDEX_TABLE = [XSCALE, YSCALE, ZSCALE]
WRITE_KEY_TABLE = [XLOC, YLOC, ZLOC, XROT, YROT, ZROT, WROT, XSCALE, YSCALE, ZSCALE]
coord_tf = Matrix([(1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0)])

armature = next(mod for mod in obj.modifiers if mod.type == 'ARMATURE').object.data
bone_names = [bone[0] for bone in convert_armature(armature)]
groups = [group.name for group in obj.vertex_groups]


def filterTransRot(item):
    importantChannels = ['a', 'e', 'i', 'o', 'u']
    if (item in importantChannels):
        return True
    else:
        return False


anim_tracks = {}
for action in bpy.data.actions:
    if action_in_armature(action, armature):
        clip = []
        for bone in armature.bones:
            bone_tracks = {}
            min_frame = 65535
            max_frame = 0

            for channel in action.groups[bone.name].channels:
                track = [(int(keyframe.co[0]), keyframe.co[1]) for keyframe in channel.keyframe_points]
                max_frame = max([max_frame] + [f[0] for f in track] )
                min_frame = min([min_frame] + [f[0] for f in track] )
                key_list = KEY_TABLE.get(channel.data_path.split('.')[-1])
                key = None if key_list == None or channel.array_index > len(key_list) else key_list[channel.array_index]
                if key != None:
                        bone_tracks[key] = track
            clip.append(bone_tracks)
        anim_tracks[action.name] = (clip, int(action.frame_start) if action.use_frame_range else min_frame, int(action.frame_end) if action.use_frame_range else max_frame)

tf_map = {}
for r, row in enumerate(coord_tf.row):
    for c, v in enumerate(row):
        if v != 0.0:
            tf_map[LOC_INDEX_TABLE[r]] = (LOC_INDEX_TABLE[c], -1.0 if v < 0.0 else 1.0)
            tf_map[ROT_INDEX_TABLE[r]] = (ROT_INDEX_TABLE[c], -1.0 if v < 0.0 else 1.0)
            tf_map[SCALE_INDEX_TABLE[r]] = (SCALE_INDEX_TABLE[c], 1.0)



for clip_name in anim_tracks:
    clip, start, end = anim_tracks[clip_name]

    printOut( "bones_qty: "+ str(len( clip )) )

    for i, bone in enumerate(clip):

        printOut( "bone_name: " + armature.bones[i].name )
        for track_key in bone:

            adj_key = tf_map[track_key][0] if track_key in tf_map else track_key
            adj_scale = tf_map[track_key][1] if track_key in tf_map else 1.0

            datastr = ""

            for keyframe in bone[adj_key]:
                datastr += adj_key
                datastr += " "
                datastr += formatDigit(adj_scale * keyframe[1])
                datastr += " "
            printOut(datastr)


coord_tf = Matrix([(1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0)]).to_4x4()
num_roots = 0
datastr = ""

for bone in armature.bones:
    if bone.parent == None:
        num_roots += 1
        arma_loc, arma_rot, arma_scale = (bone.matrix_local).decompose()
        arma_axis, arma_angle = arma_rot.to_axis_angle()
        datastr += bone.name
        datastr += " pos: "
        datastr += formatDigit((coord_tf @ arma_loc).x) + " " + formatDigit((coord_tf @ arma_loc).y) + " " + formatDigit((coord_tf @ arma_loc).z) 
        datastr += " quaternion: "
        datastr += formatDigit(Quaternion(coord_tf @ arma_axis, arma_angle).w) + " " + formatDigit(Quaternion(coord_tf @ arma_axis, arma_angle).x) + " " + formatDigit(Quaternion(coord_tf @ arma_axis, arma_angle).y) + " " + formatDigit(Quaternion(coord_tf @ arma_axis, arma_angle).z)
        datastr += " "
        datastr += "parent: None\n"
    else:
        parent_index = next(idx for (idx, p_bone) in enumerate(armature.bones) if p_bone == bone.parent)
        arma_loc, arma_rot, arma_scale = (bone.parent.matrix_local.inverted() @ bone.matrix_local).decompose()
        arma_axis, arma_angle = arma_rot.to_axis_angle()

        datastr += bone.name
        datastr += " pos: "
        datastr += formatDigit((coord_tf @ arma_loc).x) + " " + formatDigit((coord_tf @ arma_loc).y) + " " + formatDigit((coord_tf @ arma_loc).z) 
        datastr += " quaternion: "
        datastr += formatDigit(Quaternion(coord_tf @ arma_axis, arma_angle).w) + " " + formatDigit(Quaternion(coord_tf @ arma_axis, arma_angle).x) + " " + formatDigit(Quaternion(coord_tf @ arma_axis, arma_angle).y) + " " + formatDigit(Quaternion(coord_tf @ arma_axis, arma_angle).z)
        datastr += " "
        datastr += "parent: "+str(armature.bones[parent_index].name) + "\n"

printOut(datastr)


filepath = bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend", ".txt")
with open(filepath, 'w') as file:
    file.write(outputSting)
    file.close()
    print(outputSting)