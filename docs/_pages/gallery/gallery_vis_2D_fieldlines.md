---
orphan: true
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

(gallery-vis-2D-fieldlines)=

# Visualizing 2D streamlines using contours on a stream function

In this example, we show the B-field streamlines, complete and unbroken, with given starting points, and without using matplotlib streamplot as in {ref}`gallery_vis_mpl_streamplot`. This method is restricted to 2D (planar) fields with $B_z = 0$ and $\partial B_z / \partial z = 0$.

Work in progress.

$$
\psi(x,y) = \int_C \mathbf{B}.\mathbf{n} dl  = \int_C B_x \ dy - B_y \ dx
$$

```{caution}
This method is restricted to 2D (planar) fields with $B_z = 0$ and $\partial B_z / \partial z = 0$.
```

## Cuboid magnet example

Code to be improved, including specifying starting points as sets of (x,y) coordinates.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np
import magpylib as magpy

# Create a Matplotlib figure
fig, ax = plt.subplots(figsize=(10, 10))

# Create an observer grid in the xz-symmetry plane
ts = -5+10*(np.arange(201)+0.5)/201
grid = np.array([[(x,0,z) for x in ts] for z in ts]) # slow Python loop

# Compute the B-field of a cube magnet on the grid
cube = magpy.magnet.Cuboid(magnetization=(0, 0, -1000), dimension=(2, 2, 2))
B = cube.getB(grid)
x, y, u, v = grid[:,:,0], grid[:,:,2], B[:, :, 0], B[:, :, 2],

# Build the stream function and plot its isolines
dx, dy = x[0,1]-x[0,0], y[1,0]-y[0,0]
psi = np.cumsum(u,axis=0)*dy-np.cumsum(v[0:1,:],axis=1)*dx
psi -= np.min(psi)
levels = np.linspace(psi[101,81], psi[101,119], 31)
plt.contour(x, y, psi, levels=levels, colors='blue', linewidths=1.0)

# Outline magnet boundary
ax.plot([1, 1, -1, -1, 1], [1, -1, -1, 1, 1], "k-", lw=2)
ax.set_xlim([-5, 5])
ax.set_ylim([-5, 5])

# Figure styling
ax.set(
    xlabel="x-position (mm)",
    ylabel="z-position (mm)",
)

plt.tight_layout()
plt.show()
```
