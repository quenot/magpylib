import numpy as np
import pytest
from scipy.spatial.transform import Rotation as R

import magpylib
from magpylib import getB
from magpylib import getH
from magpylib._src.exceptions import MagpylibBadUserInput
from magpylib.magnet import Cuboid
from magpylib.magnet import Cylinder
from magpylib.magnet import Sphere


def test_getB_dict1():
    """test field wrapper functions"""
    pos_obs = (11, 2, 2)
    mag = [111, 222, 333]
    dim = [3, 3]

    pm = Cylinder(mag, dim)
    pm.move(np.linspace((0.5, 0, 0), (7.5, 0, 0), 15), start=-1)
    pm.rotate_from_angax(np.linspace(0, 666, 25), "y", anchor=0)
    pm.move([(0, x, 0) for x in np.linspace(0, 5, 5)], start=-1)
    B2 = pm.getB(pos_obs)

    pos = pm.position
    rot = pm.orientation

    dic = {"magnetization": mag, "dimension": dim, "position": pos, "orientation": rot}
    B1 = getB("Cylinder", pos_obs, **dic)

    assert np.allclose(B1, B2, rtol=1e-12, atol=1e-12)


def test_getB_dict2():
    """test field wrapper functions"""
    pos_obs = (11, 2, 2)
    mag = [111, 222, 333]
    dim = [3, 3]
    pos = [(1, 1, 1), (2, 2, 2), (3, 3, 3), (5, 5, 5)]

    dic = {"magnetization": mag, "dimension": dim, "position": pos}
    B1 = getB("Cylinder", pos_obs, **dic)

    pm = Cylinder(mag, dim, position=pos)
    B2 = getB([pm], pos_obs)

    assert np.allclose(B1, B2, rtol=1e-12, atol=1e-12)


def test_getH_dict1():
    """test field wrapper functions"""
    pos_obs = (11, 2, 2)
    mag = [111, 222, 333]
    dim = [3, 3]

    dic = {
        "magnetization": mag,
        "dimension": dim,
    }
    B1 = getH("Cylinder", pos_obs, **dic)

    pm = Cylinder(mag, dim)
    B2 = pm.getH(pos_obs)

    assert np.allclose(B1, B2, rtol=1e-12, atol=1e-12)


def test_getB_dict3():
    """test field wrapper functions"""
    n = 25
    pos_obs = np.array([1, 2, 2])
    mag = [
        [111, 222, 333],
    ] * n
    dim = [3, 3, 3]
    pos = np.array([0, 0, 0])
    rot = R.from_quat([(t, 0.2, 0.3, 0.4) for t in np.linspace(0, 0.1, n)])

    dic = {"magnetization": mag, "dimension": dim, "position": pos, "orientation": rot}
    B1 = getB("Cuboid", pos_obs, **dic)

    B2 = []
    for i in range(n):
        pm = Cuboid(mag[i], dim, pos, rot[i])
        B2 += [pm.getB(pos_obs)]
    B2 = np.array(B2)
    print(B1 - B2)
    assert np.allclose(B1, B2, rtol=1e-12, atol=1e-12)


def test_getH_dict3():
    """test field wrapper functions"""
    pos_obs = (1, 2, 2)
    mag = [[111, 222, 333], [22, 2, 2], [22, -33, -44]]
    dim = 3

    dic = {"magnetization": mag, "diameter": dim}
    B1 = getH("Sphere", pos_obs, **dic)

    B2 = []
    for i in range(3):
        pm = Sphere(mag[i], dim)
        B2 += [getH([pm], pos_obs)]
    B2 = np.array(B2)

    assert np.allclose(B1, B2, rtol=1e-12, atol=1e-12)


def test_getB_dict4():
    """test field wrapper functions"""
    n = 25
    pos_obs = np.array([1, 2, 2])
    mag = [
        [111, 222, 333],
    ] * n
    dim = 3
    pos = np.array([0, 0, 0])
    rot = R.from_quat([(t, 0.2, 0.3, 0.4) for t in np.linspace(0, 0.1, n)])

    dic = {"magnetization": mag, "diameter": dim, "position": pos, "orientation": rot}
    B1 = getB("Sphere", pos_obs, **dic)

    B2 = []
    for i in range(n):
        pm = Sphere(mag[i], dim, pos, rot[i])
        B2 += [pm.getB(pos_obs)]
    B2 = np.array(B2)
    print(B1 - B2)
    assert np.allclose(B1, B2, rtol=1e-12, atol=1e-12)


def test_geBHv_dipole():
    """test if Dipole implementation gives correct output"""
    B = getB("Dipole", (1, 1, 1), moment=(1, 2, 3))
    Btest = np.array([0.07657346, 0.06125877, 0.04594407])
    assert np.allclose(B, Btest)

    H = getH("Dipole", (1, 1, 1), moment=(1, 2, 3))
    Htest = np.array([0.06093522, 0.04874818, 0.03656113])
    assert np.allclose(H, Htest)


def test_geBHv_circular():
    """test if Loop implementation gives correct output"""
    B = getB("Loop", (0, 0, 0), current=1, diameter=2)
    Btest = np.array([0, 0, 0.6283185307179586])
    assert np.allclose(B, Btest)

    H = getH("Loop", (0, 0, 0), current=1, diameter=2)
    Htest = np.array([0, 0, 0.6283185307179586 * 10 / 4 / np.pi])
    assert np.allclose(H, Htest)


def test_getBHv_squeeze():
    """test if squeeze works"""
    B1 = getB("Loop", (0, 0, 0), current=1, diameter=2)
    B2 = getB("Loop", [(0, 0, 0)], current=1, diameter=2)
    B3 = getB("Loop", [(0, 0, 0)], current=1, diameter=2, squeeze=False)
    B4 = getB("Loop", [(0, 0, 0)] * 2, current=1, diameter=2)

    assert B1.ndim == 1
    assert B2.ndim == 1
    assert B3.ndim == 2
    assert B4.ndim == 2


def test_getBHv_line():
    """test getBHv with Line"""
    H = getH(
        "Line",
        [(1, 1, 1), (1, 2, 3), (2, 2, 2)],
        current=1,
        segment_start=(0, 0, 0),
        segment_end=[(0, 0, 0), (2, 2, 2), (2, 2, 2)],
    )
    x = (
        np.array([[0, 0, 0], [0.02672612, -0.05345225, 0.02672612], [0, 0, 0]])
        * 10
        / 4
        / np.pi
    )
    assert np.allclose(x, H)


def test_getBHv_line2():
    """test line with pos and rot arguments"""
    x = 0.14142136

    # z-line on x=1
    B1 = getB(
        "Line", (0, 0, 0), current=1, segment_start=(1, 0, -1), segment_end=(1, 0, 1)
    )
    assert np.allclose(B1, np.array([0, -x, 0]))

    # move z-line to x=-1
    B2 = getB(
        "Line",
        (0, 0, 0),
        position=(-2, 0, 0),
        current=1,
        segment_start=(1, 0, -1),
        segment_end=(1, 0, 1),
    )
    assert np.allclose(B2, np.array([0, x, 0]))

    # rotate 1
    rot = R.from_euler("z", 90, degrees=True)
    B3 = getB(
        "Line",
        (0, 0, 0),
        orientation=rot,
        current=1,
        segment_start=(1, 0, -1),
        segment_end=(1, 0, 1),
    )
    assert np.allclose(B3, np.array([x, 0, 0]))

    # rotate 2
    rot = R.from_euler("x", 90, degrees=True)
    B4 = getB(
        "Line",
        (0, 0, 0),
        orientation=rot,
        current=1,
        segment_start=(1, 0, -1),
        segment_end=(1, 0, 1),
    )
    assert np.allclose(B4, np.array([0, 0, -x]))

    # rotate 3
    rot = R.from_euler("y", 90, degrees=True)
    B5 = getB(
        "Line",
        (0, 0, 0),
        orientation=rot,
        current=1,
        segment_start=(1, 0, -1),
        segment_end=(1, 0, 1),
    )
    assert np.allclose(B5, np.array([0, -x, 0]))

    # "scalar" vertices tiling
    B = getB(
        "Line",
        observers=[(0, 0, 0)] * 5,
        current=1,
        vertices=np.linspace((0, 5, 5), (5, 5, 5), 6),
    )
    np.testing.assert_allclose(
        B, np.array([[0.0, 0.0057735, -0.0057735]] * 5), rtol=1e-6
    )

    # ragged sequence of vertices
    observers = (1, 1, 1)
    current = 1
    vertices = [
        [(0, 0, 0), (1, 1, 1), (2, 2, 2), (3, 3, 3), (1, 2, 3), (-3, 4, -5)],
        [(0, 0, 0), (3, 3, 3), (-3, 4, -5)],
        [(1, 2, 3), (-2, -3, 3), (3, 2, 1), (3, 3, 3)],
    ]
    B1 = getB(
        "Line",
        observers=observers,
        current=current,
        vertices=vertices,
    )
    B2 = np.array(
        [
            getB(
                "Line",
                observers=observers,
                current=current,
                vertices=v,
            )
            for v in vertices
        ]
    )

    np.testing.assert_allclose(B1, B2)


def test_BHv_Cylinder_FEM():
    """test against FEM"""
    ts = np.linspace(0, 2, 31)
    obsp = [(t, t, t) for t in ts]

    Bfem = np.array(
        [
            (-0.0300346254954609, -0.00567085248536589, -0.0980899423563197),
            (-0.0283398999697276, -0.00136726650574628, -0.10058277210005),
            (-0.0279636086648847, 0.00191033319772333, -0.102068667474779),
            (-0.0287959403346942, 0.00385627171155148, -0.102086609934239),
            (-0.0298064414078247, 0.00502298395545467, -0.101395051504575),
            (-0.0309138327020785, 0.00585315159763698, -0.0994210978208941),
            (-0.0304478836262897, 0.00637062970240076, -0.0956959733446996),
            (-0.0294756102340511, 0.00796586777139283, -0.0909716586168481),
            (-0.0257014555198541, 0.00901347002514088, -0.0839378050637996),
            (-0.0203392379411272, 0.0113401710780434, -0.0758447872526493),
            (-0.0141186721748514, 0.014275060463367, -0.0666447793887049),
            (-0.00715638330645336, 0.0169990957749629, -0.0567988806666027),
            (-0.000315107745706201, 0.0196025044167515, -0.0471345331233655),
            (0.00570680487262037, 0.0216935664564627, -0.0379802748006986),
            (0.0106937560983821, 0.0229598553802506, -0.029816827145783),
            (0.0147153251512036, 0.0237740278061223, -0.0226247514391129),
            (0.0173457909761498, 0.0240321714861875, -0.0167312828159773),
            (0.0193755103218335, 0.023674091804632, -0.0119446813034152),
            (0.0204291390948416, 0.0230735973599725, -0.00805340729977855),
            (0.0207908036651642, 0.0221875600164857, -0.00496582571560478),
            (0.020692112773328, 0.0211419193131436, -0.00269563642259977),
            (0.0202607525969918, 0.0199897027578393, -0.000891130303443818),
            (0.0195698099586468, 0.0187793271229261, 0.000332964123866357),
            (0.0187342589014612, 0.0175395229794614, 0.00128198337775133),
            (0.0178090320514157, 0.0163998590430951, 0.00196979345612218),
            (0.0168069297247124, 0.0152418998801328, 0.00243910426847474),
            (0.0158127817011691, 0.0141524929704775, 0.00274664013462767),
            (0.0148149313600427, 0.013148844940711, 0.00293212192295656),
            (0.013878964772737, 0.0121841676914905, 0.00302995618189322),
            (0.0129803941608119, 0.0113011353152514, 0.00305232762136824),
            (0.0121250819870128, 0.0104894041620816, 0.00303690098080925),
        ]
    )

    # compare against FEM
    B = getB(
        "CylinderSegment",
        obsp,
        dimension=(1, 2, 1, 90, 360),
        magnetization=np.array((1, 2, 3)) * 1000 / np.sqrt(14),
        position=(0, 0, 0.5),
    )

    err = np.linalg.norm(B - Bfem * 1000, axis=1) / np.linalg.norm(B, axis=1)
    assert np.amax(err) < 0.01


def test_BHv_solid_cylinder():
    """compare multiple solid-cylinder solutions against each other"""
    # combine multiple slices to one big Cylinder
    B1 = getB(
        "CylinderSegment",
        (1, 2, 3),
        dimension=[(0, 1, 2, 20, 120), (0, 1, 2, 120, 220), (0, 1, 2, 220, 380)],
        magnetization=(22, 33, 44),
    )
    B1 = np.sum(B1, axis=0)

    # one big cylinder
    B2 = getB(
        "CylinderSegment",
        (1, 2, 3),
        dimension=(0, 1, 2, 0, 360),
        magnetization=(22, 33, 44),
    )

    # compute with solid cylinder code
    B3 = getB(
        "Cylinder",
        (1, 2, 3),
        dimension=(2, 2),
        magnetization=(22, 33, 44),
    )

    assert np.allclose(B1, B2)
    assert np.allclose(B1, B3)


def test_getB_dict_over_getB():
    """test field wrapper functions"""
    pos_obs = (11, 2, 2)
    mag = [111, 222, 333]
    dim = [3, 3]

    pm = Cylinder(mag, dim)
    pm.move(np.linspace((0.5, 0, 0), (7.5, 0, 0), 15))
    pm.rotate_from_angax(np.linspace(0, 666, 25), "y", anchor=0)
    pm.move([(0, x, 0) for x in np.linspace(0, 5, 5)])
    B2 = pm.getB(pos_obs)

    pos = pm.position
    rot = pm.orientation

    dic = {
        "sources": "Cylinder",
        "observers": pos_obs,
        "magnetization": mag,
        "dimension": dim,
        "position": pos,
        "orientation": rot,
    }
    B1 = magpylib.getB(**dic)

    assert np.allclose(B1, B2, rtol=1e-12, atol=1e-12)

    # test for kwargs if sources is not a string
    dic["sources"] = pm
    with pytest.raises(MagpylibBadUserInput):
        magpylib.getB(**dic)


def test_subclassing():
    """Test side effects of suclasssing a source"""

    # pylint: disable=unused-variable
    class MyCuboid(magpylib.magnet.Cuboid):
        """Test subclass"""

    B1 = magpylib.getB(
        "Cuboid", (0, 0, 0), magnetization=(1, 1, 1), dimension=(1, 1, 1)
    )
    B2 = magpylib.getB(
        "MyCuboid", (0, 0, 0), magnetization=(1, 1, 1), dimension=(1, 1, 1)
    )

    np.testing.assert_allclose(B1, B2)
