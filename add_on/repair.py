"""
A plugin to repair mesh for 3D printing.
"""

bl_info = {
    "name": "Mesh Repair for 3D Printing",
    "category": "OBJECT",
}

import bpy


class MeshRepairFor3DP(bpy.types.Operator):
    """Script for a non-manifold mesh repair for 3D printing"""
    bl_idname = "mesh.mesh_repair_for_3dp"
    bl_label = "Mesh Repair for 3D Printing"
    bl_options = {"REGISTER", "UNDO"}

    threshold = bpy.props.FloatProperty(name="threshold",
                                        description="Minimum distance between elements to merge",
                                        default=0.0001)

    sides = bpy.props.IntProperty(name="sides",
                                  description="Number of sides in hole required to fill",
                                  default=4)

    max_iterations = bpy.props.IntProperty(name="max_iterations",
                                           description="Max number of iterations to run the internal repair",
                                           default=200)

    selected_mesh = None

    def execute(self, context):

        self.setup_environment()
        self.remove_doubles()
        self.dissolve_degenerate()
        self.set_selected_mesh(context)

        try:
            self.fix_non_manifold()
        except RuntimeError as e:
            print("RuntimeError:", e)
            return {"CANCELLED"}

        self.make_normals_consistently_outwards()

        #end in object mode
        bpy.ops.object.mode_set(mode="OBJECT")

        return {"FINISHED"}

    def setup_environment(self):
        """set the mode as edit, select mode as vertices, and reveal hidden vertices"""
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.reveal()

    def remove_doubles(self):
        """remove duplicate vertices"""
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=self.threshold)

    def delete_loose(self):
        """delete loose vertices/edges/faces"""
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.delete_loose()

    def dissolve_degenerate(self):
        """dissolve zero area faces and zero length edges"""
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.dissolve_degenerate(threshold=self.threshold)

    def make_normals_consistently_outwards(self):
        """have all normals face outwards"""
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent()

    def fix_non_manifold(self):
        """naive iterate-until-no-more approach for fixing manifolds"""
        non_manifold_vertices = self.get_non_manifold_vertices()
        current_iteration = 0

        while len(non_manifold_vertices) > 0:

            if current_iteration > self.max_iterations:
                raise RuntimeError("Exceeded maximum iterations, terminated early")

            self.fill_non_manifold()

            self.make_normals_consistently_outwards()

            self.delete_newly_generated_non_manifold_vertices()

            new_non_manifold_vertices = self.get_non_manifold_vertices()
            if new_non_manifold_vertices == non_manifold_vertices:
                raise RuntimeError("Not possible to repair, non-ending loop occurred")
            else:
                non_manifold_vertices = new_non_manifold_vertices
                current_iteration += 1

    def set_selected_mesh(self, context):
        """set the selected mesh from context data"""
        self.selected_mesh = context.scene.objects.active.data

    def select_non_manifold_vertices(self):
        """select non-manifold vertices"""
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.select_non_manifold()

    def selected_vertices_to_coords(self):
        """returns a set of the coordinates of selected vertices"""
        #Have to toggle mode for select vertices to work
        bpy.ops.object.mode_set(mode="OBJECT")
        selected_vertices = {(v.co[0], v.co[1], v.co[2]) for v in self.selected_mesh.vertices if v.select}
        bpy.ops.object.mode_set(mode="EDIT")

        return selected_vertices

    def get_non_manifold_vertices(self):
        """return a set of coordinates of non-manifold vertices"""
        self.select_non_manifold_vertices()

        print("Non-manifold remaining:", self.selected_mesh.total_vert_sel)

        return self.selected_vertices_to_coords()

    def fill_non_manifold(self):
        """fill holes and then fill in any remnant non-manifolds"""
        bpy.ops.mesh.fill_holes(sides=self.sides)

        #fill selected edge faces, which could be additional holes
        self.select_non_manifold_vertices()
        bpy.ops.mesh.fill()

    def delete_newly_generated_non_manifold_vertices(self):
        """delete any newly generated vertices from the filling repair"""
        self.select_non_manifold_vertices()
        bpy.ops.mesh.delete(type="VERT")


def register():
    bpy.utils.register_class(MeshRepairFor3DP)


def unregister():
    bpy.utils.unregister_class(MeshRepairFor3DP)


if __name__ == "__main__":
    register()
