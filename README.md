Mesh Repair for 3D Printing
============

A [Blender](http://www.blender.org/) add-on to repair meshes for 3D printing.

It's a naive attempt at mesh repair, by relying a lot on Blender's built-in functionalities.

The algorithm finds non-manifold vertices (possibly bordering holes) and fills them in.
Since the fill can generate new non-manifold vertices, it checks if there are any non-manifold vertices after the fill,
and deletes them. Since the deletion can create new holes,
this algorithm loops until there are no more non-manifold vertices.

I assume convergence to a repaired mesh.
Please email me if this is not the case.
I'd love to find a non-converging case.

I created functionality to remove multiple shells, through boolean intersection,
but due to Blender's use of the Carve library, it sometimes will crash when intersecting certain objects
(or will fail silently unless you inspect the terminal console). I've disabled it for now.
It definitely works for with simple meshes but fails my complex mesh test.
This is not a huge problem, as the repair will produce a mesh that passes standard checks like netfabb.

I've also disabled reduction of polygons, through decimation.
Still deciding if this should be left up to the user or have it be a part of mesh repair.
Polygon reduction is important if there's a polygon cap on the slicer, or in general,
increases the speed which the slicer generates G-code for 3D printers.

To Run
-------------

Download the script and install the add-on in [Blender](http://www.blender.org/)
(or run the script as it will self-install).
The add-on is not rolled into the official Blender release, and must be self installed.

In `OBJECT` mode, select the mesh object and run the add-on
(shortcut: press `spacebar` and type `Mesh Repair for 3D Printing`)

It may take a while depending on the complexity of the mesh.
You can uncomment out the `print` in `fix_non_manifold` to track the progress.

You can uncomment `remove_shells` in `execute` to remove multiple shells. This is unstable for complex meshes.

To Do
-------------

* Patch Boolean intersection to not crash.
* Handle thiness constraints for 3D printability
* If rolling in decimation, implement a true density-based approach for determining a vertex-dense mesh
* Roll into Blender's 3D Printing Toolbox

License
-------------

Mesh Repair for 3D Printing is under [GPLv3](http://opensource.org/licenses/gpl-3.0.html).

A copy of GPLv3 can be found at [http://opensource.org/licenses/gpl-3.0.html](http://opensource.org/licenses/gpl-3.0.html).

Credits
-------------

Created by Jenny - [CaretDashCaret](http://caretdashcaret.wordpress.com/)

[![Jenny](http://i1115.photobucket.com/albums/k552/caretdashcaret/2014-03/About5_zps7f79c497.jpg)](http://caretdashcaret.wordpress.com/)