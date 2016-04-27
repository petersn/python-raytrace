A simple Python raytracer I challenged myself to write in an hour.
The following two images are from a version that was committed 59 minutes and 54 seconds after I started the timer (although their actual renders took longer).
The images thereafter have additional changes in the code.

An 800x800 render done in about 10 minutes, with four objects and three lights, with a recursion limit of 2:

![Simple render](https://raw.githubusercontent.com/petersn/python-raytrace/master/demos/render.png)

Another render of the same scene with 16 depth-of-field samples per pixel, that took 2.2 hours to render:

![Depth of field render](https://raw.githubusercontent.com/petersn/python-raytrace/master/demos/dof_render.png)

I didn't like how bad the DOF effect looked on the above image, but it was the last render I started before my hour was up.
These images have a texture and more carefully tuned DOF.

![Textured render](https://raw.githubusercontent.com/petersn/python-raytrace/master/demos/texture_render.png)

![Textured and DOF render](https://raw.githubusercontent.com/petersn/python-raytrace/master/demos/texture_dof_render.png)

