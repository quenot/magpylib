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

```{note}
This method is restricted to 2D (planar) fields with $B_z = 0$ and $\partial B_z / \partial z = 0$.
```

In this example, we show the B-field streamlines, complete and unbroken, with given starting points, and without using matplotlib streamplot as in {ref}`gallery_vis_mpl_streamplot`.

Work in progress.

$$
\psi(x,y) = \int_C \mathbf{B}.\mathbf{n} dl  = \int_C B_x \ dy - B_y \ dx
$$

## Cuboid magnet example

Code to be improved, including specifying starting points as sets of (x,y) coordinates. It will also be clearer to choose the same x and y axes for the figure and for the "real world" x and y axes.

```{code-cell} ipython3
import numpy as np
import matplotlib.pyplot as plt
import magpylib as magpy
from scipy.interpolate import RegularGridInterpolator

nx, ny = 500, 400    # grid size
wx, wy = 10, 8       # window size (scale 1 mm ~ 1 inch)
mx, my, mz = 2.4, 1.8, 10 # magnet size

# Create a Matplotlib figure
fig, ax = plt.subplots(figsize=(wx, wy))
ax.set_xlim([-wx/2, wx/2])
ax.set_ylim([-wy/2, wy/2])

# Create an observer grid in the xz-symmetry plane
tsx = -wx/2+wx*(np.arange(nx)+0.5)/nx
tsy = -wy/2+wy*(np.arange(ny)+0.5)/ny
# grid = np.array([[(x,y,0) for x in tsx] for y in tsy]) # slow Python loop
grid = np.moveaxis(np.array(np.meshgrid(tsx, tsy, [0]))[:,:,:,0], 0, -1)

# Compute the B-field of a cube magnet on the grid
cube = magpy.magnet.Cuboid(magnetization=(0, -1000, 0), dimension=(mx, my, mz))
B = cube.getB(grid)
x, y, u, v = grid[:,:,0], grid[:,:,1], B[:, :, 0], B[:, :, 1]

# Build the stream function
dx, dy = x[0,1]-x[0,0], y[1,0]-y[0,0]
psi = np.cumsum(u,axis=0)*dy-np.cumsum(v[0:1,:],axis=1)*dx

# Define starting points
xp, yp = np.linspace(-mx/2, mx/2, 31), np.zeros(31)
plt.plot(xp, yp, 'bo', markersize=2.5)

# Turn starting points into levels
def levelsFromXY(psi, xp, yp):
    ip, jp = (xp+wx/2)*nx/wx-0.5, (yp+wy/2)*ny/wy-0.5
    interp = RegularGridInterpolator((range(ny), range(nx)), psi)
    return interp((jp, ip))

# Plot isolines
levels = levelsFromXY(psi, xp, yp)
plt.contour(x, y, psi, levels=levels, colors='blue', linewidths=1.0, negative_linestyles='solid')

# Outline magnet boundary
ax.plot([mx/2, mx/2, -mx/2, -mx/2, mx/2], [my/2, -my/2, -my/2, my/2, my/2], "k-", lw=2)

# Figure styling
ax.set(xlabel="x-position (mm)", ylabel="y-position (mm)",)

plt.tight_layout()
plt.show()
```
