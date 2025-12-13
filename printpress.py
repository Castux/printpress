from build123d import *
from ocp_vscode import show
#from yacv_server import show

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

    short = baseH / 9
    tall = baseH * 3 / 9
    margin = 13

    ln = Line((0, 0), (baseW/2 + margin, 0))
    ln += Line(ln @ 1, ln @ 1 + (0, short))
    ln += Line(ln @ 1, ln @ 1 + (-3, 0))
    ln += RadiusArc(ln @ 1, ln @ 1 + (-4, tall), -tall)
    ln += Line(ln @ 1, ln @ 1 + (0, short))
    ln += RadiusArc(ln @ 1, ln @ 1 + (-4, tall), tall)
    ln += Line(ln @ 1, ln @ 1 + (-2, 0))
    ln += Line(ln @ 1, ((ln @ 1).X, baseH))
    ln += Line(ln @ 1, (0, baseH))
    ln += mirror(ln, Plane.YZ)

    return ln

# Base construction

sheetW = 120
sheetH = 180
sheetMargin = 6
sheetDepth = 10
balastDepth = 25

supportMargin = 40
supportOffset = sheetW / 2 + sheetMargin + supportMargin / 2

baseThickness = 40
baseW = sheetW + 2*supportMargin + 2*sheetMargin
baseH = sheetH + 2*sheetMargin

tmp1 = make_face(Plane.XZ.offset(-baseH) * baseProfile(baseThickness, baseW))
tmp1 = extrude(tmp1, baseH * 2)
tmp2 = make_face(Plane.YZ.offset(-baseW) * baseProfile(baseThickness, baseH))
tmp2 = extrude(tmp2, baseW * 2)

base = tmp1 & tmp2
topFace = base.faces().sort_by().last

plateIndent = Plane(topFace) * Rectangle(sheetW, sheetH)
balastIndent = Plane(topFace) * Rectangle(sheetW - 2*sheetMargin, sheetH - 2*sheetMargin)
base -= extrude(plateIndent, -sheetDepth)
base -= extrude(balastIndent, -sheetDepth-balastDepth)

base += Pos(supportOffset, 0, baseThickness) * support
base += Pos(-supportOffset, 0, baseThickness) * support

show(base)
