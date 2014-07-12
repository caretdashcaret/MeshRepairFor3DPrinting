"""
A plugin to repair mesh for 3D printing.

It's a naive attempt at mesh repair, by relying a lot on Blender's built-in functionalities.
The algorithm finds non-manifold vertices (possibly bordering holes) and fills them in.
Since the fill can generate new non-manifold vertices, it checks if there are any non-manifold vertices after the fill,
and deletes them. Since the deletion can create new holes,
this algorithm loops until there are no more non-manifold vertices.
I assume convergence to a repaired mesh. Please email me if this is not the case.

I created functionality to remove multiple shells, through boolean intersection,
but due to Blender's use of the Carve library, it sometimes will crash when intersecting certain objects
(or will fail silently unless you inspect the terminal console). I've disabled it for now.
It definitely works for with simple meshes but fails the complex test.
This is not a huge problem, as the repair will produce a mesh that passes standard checks like netfabb.

I've also disabled reduction of polygons, through decimation.
Still deciding if this should be left up to the user or have it be a part of mesh repair.
Polygon reduction is important if there's a polygon cap on the slicer, or in general,
increases the speed which the slicer generates G-code for 3D printers.

TODO:
1. Patch Boolean intersection to not crash.
2. Handle thiness constraints for 3D printability
3. If rolling in decimation, implement a true density-based approach for determining a vertex-dense mesh
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

    original_object = context.scene.objects.active

    #separate loose mesh
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.separate(type="LOOSE")

    #find all mesh objects in scene
    bpy.ops.object.mode_set(mode="OBJECT")
    mesh_objects = [obj for obj in context.scene.objects if type(obj.data) == bpy.types.Mesh]
    bpy.ops.object.select_all(action="DESELECT")

    #boolean union all
    final_mesh_object = mesh_objects[0]
    original_object.select = False


    for mesh_object in mesh_objects[1:]:
        print(mesh_object)
        input("mesh boolean: ")

        context.scene.objects.active = final_mesh_object
        final_mesh_object.select = True
        #mode_set needs to come after setting an active object
        bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.object.modifier_add(type="BOOLEAN")
        final_mesh_object.modifiers["Boolean"].operation = "UNION"
        final_mesh_object.modifiers["Boolean"].object = mesh_object
        bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Boolean")

        bpy.ops.object.modifier_add(type="BOOLEAN")
        final_mesh_object.modifiers["Boolean"].operation = "UNION"
        final_mesh_object.modifiers["Boolean"].object = mesh_object
        bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Boolean")
        
        #delete after union-ed
        final_mesh_object.select = False
        context.scene.objects.active = mesh_object
        mesh_object.select = True
        bpy.ops.object.delete()

    #select the final mesh object
    context.scene.objects.active = final_mesh_object
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
    """determine if the vertex density is high"""
    max_faces = 500000

    if len(mesh_object.data.polygons) > max_faces:
        return True

    return False


def fix_non_manifold(context):
    """naive iterate-until-no-more approach for fixing manifolds"""
    bpy.ops.object.mode_set(mode="EDIT")
    mesh = context.scene.objects.active.data

    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_non_manifold()

    non_manifold_vertices = mesh.total_vert_sel

    while non_manifold_vertices > 0:
        print("Non-manifold vertices: " + str(non_manifold_vertices))

        #fix non-manifold
        bpy.ops.mesh.fill_holes()

        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.fill()

        #have all normals face outwards
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent()

        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.select_non_manifold()

        bpy.ops.mesh.delete(type='VERT')

        bpy.ops.mesh.select_non_manifold()
        non_manifold_vertices = mesh.total_vert_sel


class MeshRepairFor3DP(bpy.types.Operator):
    """Script for a naive mesh repair for 3D printing"""
    bl_idname = "mesh.mesh_repair_for_3dp"
    bl_label = "Mesh Repair for 3D Printing"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        #remove duplicate vertices
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(use_unselected=True)

        #delete loose vertices/edges/faces
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.delete_loose()

        #dissolve zero area faces and zero length edges
        bpy.ops.mesh.dissolve_degenerate()

        fix_non_manifold(context)

        #have all normals face outwards
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent()

        ##boolean union all mesh to remove shells and self intersections
        #deshelled_mesh_object = remove_shells(context)

        ##decimate to reduce polygons
        #if has_dense_vertices(deshelled_mesh_object):
        #    decimate(context, deshelled_mesh_object)

        #end in object mode
        bpy.ops.object.mode_set(mode="OBJECT")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MeshRepairFor3DP)


def unregister():
    bpy.utils.unregister_class(MeshRepairFor3DP)


if __name__ == "__main__":
    register()