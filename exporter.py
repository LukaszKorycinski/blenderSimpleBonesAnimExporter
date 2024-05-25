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


filepath = bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend", ".txt")
with open(filepath, 'w') as file:
    file.write(outputSting)
    file.close()
    print(outputSting)