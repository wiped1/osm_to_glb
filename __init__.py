bl_info = {
    "name": "OSM to GLB",
    "description": "Export GLB hierarchy from OSM data",
    "warning": "",
    "author": "Mateusz Dudek",
    "version": (0, 1),
    "blender": (2, 7, 8),
    "tracker_url": "https://github.com/wiped1/osm_to_glb",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

import bpy
import os
import json
import sys

from .lib import Bounds

class ExportGLBFromOSMProperties(bpy.types.PropertyGroup):
    output = bpy.props.StringProperty(
        name = "Output",
        subtype = "FILE_PATH",
        description = "Path where GLB hierarchy will be exported"
    )

    rootObject = bpy.props.StringProperty(
        name = "Root",
        description = "Root hierarchy object. Must not be a mesh"
    )

    geometricError = bpy.props.FloatProperty(
        name = "Geometric error",
        description = "Root geometric error in meters. See cesium 3d-tiles documentation."
    )

class ExportGLBFromOSMPanel(bpy.types.Panel):
    bl_label = "Export GLB hierarchy from OSM data"
    bl_idname = "OBJECT_PT_export_glb_hierarchy"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "osm"

    def draw(self, context):
        props = context.scene.glb_from_osm
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.prop(props, "output")
        row = box.row()
        row.prop_search(props, "rootObject", context.scene, "objects")
        row = box.row()
        row.prop(props, "geometricError")

        row = layout.row()
        row.operator("object.export_glb_from_osm")

class ExportGLBFromOSM(bpy.types.Operator):
    bl_idname = "object.export_glb_from_osm"
    bl_label = "Export GLB hierarchy from OSM data"

    def saveLocRotScale_(self, obj):
        return {'loc': obj.location.copy(),
                'rot': obj.rotation_quaternion.copy(),
                'scale': obj.scale.copy() }

    def clearLocRotScale_(self, obj):
        obj.location = (0, 0, 0)
        obj.rotation_quaternion = (0, 0, 0, 0)
        obj.scale = (1, 1, 1)

    def restoreLocRotScale_(self, obj, saved):
        obj.location = saved['loc']
        obj.rotation_quaternion = saved['rot']
        obj.scale = saved['scale']

    def clear_selections_(self):
        for obj in bpy.data.objects:
            obj.select = False

    def execute(self, context):
        properties = context.scene.glb_from_osm

        if not properties.output:
            self.report({'ERROR'}, 'Output not set!')
            return {'CANCELLED'}

        if not properties.rootObject:
            self.report({'ERROR'}, 'Root not set!')
            return {'CANCELLED'}

        self.root_name = properties.rootObject
        self.root = bpy.data.objects[self.root_name]
        self.output = properties.output
        self.clear_selections_()
        self.create_hierarchy(context, self.root, self.output)
        return {'FINISHED'}

    def create_hierarchy(self, context, obj, path):
        properties = context.scene.glb_from_osm

        name = obj.name.replace(" ", "_")
        path = bpy.path.abspath(os.path.join(path, name))
        if not os.path.exists(path):
            os.makedirs(path)

        def open_meta(path, name):
            return open(os.path.join(path, name + '.meta'), 'w')

        def serialize_mat4(mat4):
            result = []
            for col in mat4.col:
                result.append(col[0])
                result.append(col[1])
                result.append(col[2])
                result.append(col[3])
            return result

        def add_geo_location(data):
            data['lon'] = bpy.context.scene['lon'];
            data['lat'] = bpy.context.scene['lat'];

        def add_geometric_error(data):
            data['geometricError'] = properties.geometricError

        def add_transform(data, mat4):
            data['transform'] = mat4;

        def add_bounds(data, obj):
            obj_bounds = Bounds.bounds(obj)
            result = {}
            result['x'] = {'min': obj_bounds.x.min, 'max': obj_bounds.x.max, 'distance': obj_bounds.x.distance}
            result['y'] = {'min': obj_bounds.y.min, 'max': obj_bounds.y.max, 'distance': obj_bounds.y.distance}
            result['z'] = {'min': obj_bounds.z.min, 'max': obj_bounds.z.max, 'distance': obj_bounds.z.distance}
            data['bounds'] = result

        def write(f, data):
            json.dump(data, f)

        f = open_meta(path, name)
        data = {}
        # initial meta object with lon and lat properties
        if obj.name == self.root_name:
            add_geo_location(data)
            add_geometric_error(data)

        add_transform(data, serialize_mat4(obj.matrix_local))

        if obj.type == 'MESH':
            # set current object as active
            bpy.context.scene.objects.active = obj
            obj.select = True

            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY', center='BOUNDS')

            add_transform(data, serialize_mat4(obj.matrix_local))

            savedLocRotScale = self.saveLocRotScale_(obj)
            self.clearLocRotScale_(obj)

            add_bounds(data, obj)

            bpy.ops.export_scene.gltf(
                filepath=os.path.join(path, name + '.glb'),
                nodes_selected_only = True,
                buffers_embed_data = True,
                gltf_export_binary = True
            )

            self.restoreLocRotScale_(obj, savedLocRotScale)
            obj.select = False

        write(f, data)
        for child in obj.children:
            self.create_hierarchy(context, child, path)

def register():
    bpy.utils.register_class(ExportGLBFromOSMProperties)
    bpy.types.Scene.glb_from_osm = bpy.props.PointerProperty(type=ExportGLBFromOSMProperties)
    bpy.utils.register_class(ExportGLBFromOSM)
    bpy.utils.register_class(ExportGLBFromOSMPanel)

def unregister():
    del bpy.types.Scene.glb_from_osm
    bpy.utils.unregister_class(ExportGLBFromOSMProperties)
    bpy.utils.unregister_class(ExportGLBFromOSM)
    bpy.utils.unregister_class(ExportGLBFromOSMPanel)

if __name__ == "__main__":
    register()
