Mesh Repair for 3D Printing
============

**Deprecated** - Rolled into to Blender's `3D Printing Toolbox` as `Clean Up Non-Manifolds` [Patch T41093](https://developer.blender.org/rBAa88a2e646018b3f9b8d1f818f0a08370b2a0dd67).

------------
A [Blender](http://www.blender.org/) add-on to repair meshes for 3D printing.

[![Mesh Repair]
(http://i1115.photobucket.com/albums/k552/caretdashcaret/2014-07/Screenshot2014-07-13at74220PM_zpsbfbe4047.png)]
(https://github.com/caretdashcaret/MeshRepairFor3DPrinting/blob/master/add_on/repair.py)

It's an attempt at repair of non-manifolds.

The algorithm selects non-manifold vertices (assumes they are holes) and fills them in.
Since the fill can generate new non-manifold vertices, it checks if there are any non-manifold vertices after the fill,
and deletes them. Since the deletion can create new holes,
this algorithm loops until there are no more non-manifold vertices.

I assume convergence to a repaired mesh. The repair will terminate if in one iteration of the repair,
it could not repair anything and the same non-manifold vertices remain. It will also terminate
if the number of iterations exceed the `max_interation`.

This works well for models with dense polygons but may not work for all models. Read my [blog article](https://caretdashcaret.wordpress.com/2014/12/04/lets-talk-mesh-repair/) to learn about complexities of mesh repair.

To Run
-------------

Download the script and install the add-on in [Blender](http://www.blender.org/)
(or run the script as it will self-install).
The add-on is not rolled into the official Blender release, and must be self installed.

In `OBJECT` mode, select the mesh object and run the add-on
(shortcut: press `spacebar` and type `Mesh Repair for 3D Printing`)

There are three parameters you can set. `threshold` determines how far away vertices are away from each other before
the are counted as duplicates. `sides` is the default number of sides for repairing holes. `max_iteration` is
the maximum iteration the internal `fix_non_manifold` loop will run before it decides the mesh is unrepairable.

License
-------------

Mesh Repair for 3D Printing is under [GPLv3](http://opensource.org/licenses/gpl-3.0.html).

A copy of GPLv3 can be found at [http://opensource.org/licenses/gpl-3.0.html](http://opensource.org/licenses/gpl-3.0.html).

Credits
-------------

Created by Jenny - [CaretDashCaret](http://caretdashcaret.wordpress.com/)

[![Jenny](http://i1115.photobucket.com/albums/k552/caretdashcaret/2014-03/About5_zps7f79c497.jpg)](http://caretdashcaret.wordpress.com/)
