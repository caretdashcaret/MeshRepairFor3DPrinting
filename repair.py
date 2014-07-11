"""
A plugin to repair mesh for 3D printing.

It's a naive attempt at mesh repair:

1. unioning all meshes within an object to remove shells
2. remove duplicate vertices (and weld sides together)
3. reduce the number of polygons if the object has high number of polygons
4. remove loose vertices / edges / faces
5. remove degenerate edges / faces
6. fill holes
7. make all normals face outwards

TODO:
1. reduce polygons based on vertex density rather than vertex count
2. thicken thin areas
"""

bl_info = {
    "name": "Mesh Repair for 3D Printing",
    "category": "OBJECT",
}

import bpy


def remove_shells(context):
    """
    separate each loose mesh into a new object, then boolean merge them all together
    """

    #separate loose mesh
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.separate(type="LOOSE")

    #find all mesh objects in scene
    mesh_objects = [obj for obj in context.scene.objects if type(obj.data) == bpy.types.Mesh]

    #boolean union all
    final_mesh_object = mesh_objects[0]

    for mesh_object in mesh_objects[1:]:

        bpy.ops.object.mode_set(mode="OBJECT")
        final_mesh_object.select = True

        bpy.ops.object.modifier_add(type="BOOLEAN")
        final_mesh_object.modifiers["Boolean"].operation = "UNION"
        final_mesh_object.modifiers["Boolean"].object = mesh_object
        bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Boolean")

        #delete after unioned
        final_mesh_object.select = False
        mesh_object.select = True
        bpy.ops.object.delete()

    final_mesh_object.select = True
    return final_mesh_object


def decimate(context, deshelled_mesh_object):
    """decimate to reduce polygons"""
    bpy.ops.object.mode_set(mode="OBJECT")
    context.scene.objects.active = deshelled_mesh_object

    bpy.ops.object.modifier_add(type="DECIMATE")
    deshelled_mesh_object.modifiers["Decimate"].ratio = 0.5
    bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Decimate")


def has_dense_vertices(mesh_object):
    """compute if the vertex density is high"""
    max_faces = 500000

    if len(mesh_object.data.polygons) > max_faces:
        return True

    return False


class MeshRepairFor3DP(bpy.types.Operator):
    """Script for a naive mesh repair for 3D printing"""
    bl_idname = "mesh.mesh_repair_for_3dp"
    bl_label = "Mesh Repair for 3D Printing"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        #boolean union all mesh to remove shells and self intersections
        deshelled_mesh_object = remove_shells(context)

        #remove duplicate vertices
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(use_unselected=True)

        #decimate to reduce polygons
        if has_dense_vertices(deshelled_mesh_object):
            decimate(context, deshelled_mesh_object)

        bpy.ops.object.mode_set(mode="EDIT")
        #delete loose vertices/edges/faces
        bpy.ops.mesh.delete_loose()

        #dissolve zero area faces and zero length edges
        bpy.ops.mesh.dissolve_degenerate()

        #fix non-manifold
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.fill_holes(0) #fill_grid?

        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.fill()

        #have all normals face outwards
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MeshRepairFor3DP)


def unregister():
    bpy.utils.unregister_class(MeshRepairFor3DP)


if __name__ == "__main__":
    register()