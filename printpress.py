from build123d import *
from ocp_vscode import show

# Support

supportRadius = 10
supportHeight = 130

supportSketch = Pos(0.8 * supportRadius, 0, 0) * Circle(supportRadius)
supportSketch += Pos(-0.8 * supportRadius, 0, 0) * Circle(supportRadius)
supportSketch += Pos(0, 0.8 * supportRadius, 0) * Circle(supportRadius / 3)
supportSketch += Pos(0, -0.8 * supportRadius, 0) * Circle(supportRadius / 3)

support = Solid.extrude_linear_with_rotation(supportSketch, (0,0), (0, 0, supportHeight), 3 * 180)
support = fillet(support.edges().group_by(Axis.Z)[1], radius=1)

# Base profile

def baseProfile(baseH = 40, baseW = 120):
    ln = Line((0, 0), (baseW/2, 0))
    ln += Line(ln @ 1, ln @ 1 + (0, baseH/10))
    ln += Line(ln @ 1, ln @ 1 + (-3, 0))
    ln += RadiusArc(ln @ 1, ln @ 1 + (-4, baseH/3), -baseH/4)
    ln += Line(ln @ 1, ln @ 1 + (0, baseH/10))
    ln += RadiusArc(ln @ 1, ln @ 1 + (-4, baseH/3), baseH/4)
    ln += Line(ln @ 1, ln @ 1 + (-2, 0))
    ln += Line(ln @ 1, ((ln @ 1).X, baseH))
    ln += Line(ln @ 1, (0, baseH))
    ln += mirror(ln, Plane.YZ)

    return ln

# Base construction

baseThickness = 40
baseW = 120
baseH = 180

tmp1 = make_face(Plane.XZ.offset(-baseH) * baseProfile(baseThickness, baseW))
tmp1 = extrude(tmp1, baseH * 2)
tmp2 = make_face(Plane.YZ.offset(-baseW) * baseProfile(baseThickness, baseH))
tmp2 = extrude(tmp2, baseW * 2)

base = tmp1 & tmp2

show(base)
