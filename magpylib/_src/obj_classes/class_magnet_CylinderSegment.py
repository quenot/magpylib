"""Magnet Cylinder class code"""
import numpy as np

from magpylib._src.display.traces_core import make_CylinderSegment
from magpylib._src.fields.field_BH_cylinder_segment import (
    magnet_cylinder_segment_field_internal,
)
from magpylib._src.input_checks import check_format_input_cylinder_segment
from magpylib._src.obj_classes.class_BaseExcitations import BaseMagnet
from magpylib._src.utility import unit_prefix


class CylinderSegment(BaseMagnet):
    """Cylinder segment (ring-section) magnet with homogeneous magnetization.

    Can be used as `sources` input for magnetic field computation.

    When `position=(0,0,0)` and `orientation=None` the geometric center of the
    cylinder lies in the origin of the global coordinate system and
    the cylinder axis coincides with the global z-axis. Section angle 0
    corresponds to an x-z plane section of the cylinder.

    Parameters
    ----------
    magnetization: array_like, shape (3,), default=`None`
        Magnetization vector (mu0*M, remanence field) in units of mT given in
        the local object coordinates (rotates with object).

    dimension: array_like, shape (5,), default=`None`
        Dimension/Size of the cylinder segment of the form (r1, r2, h, phi1, phi2)
        where r1<r2 denote inner and outer radii in units of mm, phi1<phi2 denote
        the cylinder section angles in units of deg and h is the cylinder height
        in units of mm.

    position: array_like, shape (3,) or (m,3), default=`(0,0,0)`
        Object position(s) in the global coordinates in units of mm. For m>1, the
        `position` and `orientation` attributes together represent an object path.

    barycenter: array_like, shape (3,)
        Read only property that returns the geometric barycenter (=center of mass)
        of the object.

    orientation: scipy `Rotation` object with length 1 or m, default=`None`
        Object orientation(s) in the global coordinates. `None` corresponds to
        a unit-rotation. For m>1, the `position` and `orientation` attributes
        together represent an object path.

    parent: `Collection` object or `None`
        The object is a child of it's parent collection.

    style: dict
        Object style inputs must be in dictionary form, e.g. `{'color':'red'}` or
        using style underscore magic, e.g. `style_color='red'`.

    Returns
    -------
    magnet source: `CylinderSegment` object

    Examples
    --------
    `CylinderSegment` magnets are magnetic field sources. In this example we compute the
    H-field kA/m of such a cylinder segment magnet with magnetization (100,200,300)
    in units of mT, inner radius 1 mm, outer radius 2 mm, height 1 mm, and
    section angles 0 and 45 deg at the observer position (2,2,2) in units of mm:

    >>> import magpylib as magpy
    >>> src = magpy.magnet.CylinderSegment(magnetization=(100,200,300), dimension=(1,2,1,0,45))
    >>> H = src.getH((2,2,2))
    >>> print(H)
    [0.80784692 1.93422813 2.74116805]

    We rotate the source object, and compute the B-field, this time at a set of observer positions:

    >>> src.rotate_from_angax(45, 'x')
    CylinderSegment(id=...)
    >>> B = src.getB([(1,1,1), (2,2,2), (3,3,3)])
    >>> print(B)
    [[-32.82849635  30.15882073 -16.32885658]
     [  0.62876075   3.97579164   0.73297829]
     [  0.25439493   0.74331628   0.11682542]]

    The same result is obtained when the rotated source moves along a path away from an
    observer at position (1,1,1). Here we use a `Sensor` object as observer.

    >>> sens = magpy.Sensor(position=(1,1,1))
    >>> src.move([(-1,-1,-1), (-2,-2,-2)])
    CylinderSegment(id=...)
    >>> B = src.getB(sens)
    >>> print(B)
    [[-32.82849635  30.15882073 -16.32885658]
     [  0.62876075   3.97579164   0.73297829]
     [  0.25439493   0.74331628   0.11682542]]
    """

    _field_func = staticmethod(magnet_cylinder_segment_field_internal)
    _field_func_kwargs_ndim = {"magnetization": 2, "dimension": 2}
    get_trace = make_CylinderSegment

    def __init__(
        self,
        magnetization=None,
        dimension=None,
        position=(0, 0, 0),
        orientation=None,
        style=None,
        **kwargs,
    ):
        # instance attributes
        self.dimension = dimension

        # init inheritance
        super().__init__(position, orientation, magnetization, style, **kwargs)

    # property getters and setters
    @property
    def dimension(self):
        """
        Dimension/Size of the cylinder segment of the form (r1, r2, h, phi1, phi2)
        where r1<r2 denote inner and outer radii in units of mm, phi1<phi2 denote
        the cylinder section angles in units of deg and h is the cylinder height
        in units of mm.
        """
        return self._dimension

    @dimension.setter
    def dimension(self, dim):
        """Set Cylinder dimension (r1,r2,h,phi1,phi2), shape (5,), (mm, deg)."""
        self._dimension = check_format_input_cylinder_segment(dim)

    @property
    def _barycenter(self):
        """Object barycenter."""
        return self._get_barycenter(self._position, self._orientation, self.dimension)

    @property
    def barycenter(self):
        """Object barycenter."""
        return np.squeeze(self._barycenter)

    @staticmethod
    def _get_barycenter(position, orientation, dimension):
        """Returns the barycenter of a cylinder segment.
        Input checks should make sure:
            -360 < phi1 < phi2 < 360 and 0 < r1 < r2
        """
        if dimension is None:
            centroid = np.array([0.0, 0.0, 0.0])
        else:
            r1, r2, _, phi1, phi2 = dimension
            alpha = np.deg2rad((phi2 - phi1) / 2)
            phi = np.deg2rad((phi1 + phi2) / 2)
            # get centroid x for unrotated annular sector
            centroid_x = (
                2
                / 3
                * np.sin(alpha)
                / alpha
                * (r2**3 - r1**3)
                / (r2**2 - r1**2)
            )
            # get centroid for rotated annular sector
            x, y, z = centroid_x * np.cos(phi), centroid_x * np.sin(phi), 0
            centroid = np.array([x, y, z])
        barycenter = orientation.apply(centroid) + position
        return barycenter

    @property
    def _default_style_description(self):
        """Default style description text"""
        if self.dimension is None:
            return "no dimension"
        d = [
            unit_prefix(d / (1000 if i < 3 else 1))
            for i, d in enumerate(self.dimension)
        ]
        return f"r={d[0]}m|{d[1]}m, h={d[2]}m, φ={d[3]}°|{d[4]}°"
