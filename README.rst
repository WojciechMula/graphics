================================================================================
                            Graphics algorithms
================================================================================

Various graphics algorithms I learned. Python program using either Tkinter
or Python Imaging Library (PIL), or Javascript embedded in SVG files.

There are following library modules used by demo applications:

* ``utils2D.py`` --- different procedures work with segments, polygons etc.;
* ``aabb2D.py`` --- axis-aligned bounding boxes;
* ``isconvex.py`` --- procedures work with convex polygons;
* ``cbezier2D.py`` --- procedures work with cubic Bezier curves;
* convex hull algorithms: ``jarvis.py``, ``graham.py`` and ``quickhull.py``.


.. contents::


Tkinter events serializer
--------------------------------------------------

Most Tkinter-based scripts relie on ``tkes.py``, it's my attempt to express
interactive tasks in an imperative way. File ``tkes-demo.py`` is a simple
drawing program which use this approach.


BSP tree demo (tkinter)
--------------------------------------------------------------------------------

**BSP-tree-tkdemo.py** allows to edit a polygon and represents it as
a BSP tree. Then a user may check if a point lies inside or outside
the drawn polygon using the tree.

.. image:: img/BSP-tree-tkdemo.png


Approximation of a Bezier curve (tkinter)
--------------------------------------------------------------------------------

**cbezier-as-tkdemo.py** use different metrics to approximate
a Bezier curve with polyline.

.. image:: img/cbezier-as-tkdemo.png


Intersection of Bezier curves (tkinter)
--------------------------------------------------------------------------------

**cbezier-cc-tkdemo.py** approximates curves with polylines,
then check intersection of polylines.

.. image:: img/cbezier-cc-tkdemo.png


Find a convex hull using Graham algorithm (tkinter)
--------------------------------------------------------------------------------

**graham-tkdemo.py** calculates convex hull of point using Graham algorithm.

.. image:: img/graham-tkdemo.png


Sutherland-Hodgman --- clip a polygon against a convex polygon (tkinter)
--------------------------------------------------------------------------------

**polyintersect-tkdemo.py** allows to define two or more polygons and clip
them using Sutherland-Hodgman algorithm.

.. image:: img/polyintersect-tkdemo.png


Exact bounding box of Tkinter "smooth curve" (tkinter)
--------------------------------------------------------------------------------

**tk_ebbox-demo.py** --- Tkinter uses Bezier splines to represent "smoothed
curves", however its method bbox returns the bounding box of control points.
This demo shows how to calculate an exact bounding box.

.. image:: img/tk_ebbox-demo.png


Clipping segment using Cohen-Sutherland algorithm (JavaScript + SVG)
--------------------------------------------------------------------------------

**Cohen_Sutherland-demo.svg** demonstrates the algorithm.

.. image:: img/Cohen_Sutherland-demo.png


Bounding box of an elliptical arc (JavaScript + SVG)
--------------------------------------------------------------------------------

**elarc_aabb-demo.svg** shows how to find the bounding-box of a rotated
elliptical arc using basic math properties.

There's `an article`__ in Polish which describes the algorithm.

__ http://0x80.pl/articles/elarc-aabb.html

.. image:: img/elarc_aabb-demo.png


Segment-circle intersection (JavaScript + SVG)
--------------------------------------------------------------------------------

**segment-circle-intersection-test.svg** show an algorithm to check whether
a segment crosses a circle or not.
