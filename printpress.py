# %%

from build123d import *
from ocp_vscode import show
# %%
# Supports

supportRadius = 10
supportHeight = 130

supportSketch = Pos(0.8 * supportRadius, 0, 0) * Circle(supportRadius)
supportSketch += Pos(-0.8 * supportRadius, 0, 0) * Circle(supportRadius)
supportSketch += Pos(0, 0.8 * supportRadius, 0) * Circle(supportRadius / 3)
supportSketch += Pos(0, -0.8 * supportRadius, 0) * Circle(supportRadius / 3)

support = Solid.extrude_linear_with_rotation(supportSketch, (0,0), (0, 0, supportHeight), 3 * 180)
support = fillet(support.edges().group_by(Axis.Z)[1], radius=0.5)
support.label = "support"

# Base profile

def baseProfile(baseH = 40, baseW = 120):

    short = baseH / 9
    tall = baseH * 3 / 9

    ln = Line((0, baseH), (baseW/2, baseH))
    ln += Line(ln @ 1, ln @ 1 + (0, -short))
    ln += Line(ln @ 1, ln @ 1 + (2, 0))
    ln += RadiusArc(ln @ 1, ln @ 1 + (4, -tall), -tall)
    ln += Line(ln @ 1, ln @ 1 + (0, -short))
    ln += RadiusArc(ln @ 1, ln @ 1 + (4, -tall), tall)
    ln += Line(ln @ 1, ln @ 1 + (3, 0))
    ln += Line(ln @ 1, ln @ 1 + (0, -short))
    ln += Line(ln @ 1, (0, 0))
    ln += mirror(ln, Plane.YZ)

    return ln

# Base construction

sheetW = 140
sheetH = 200
sheetMargin = 6
sheetDepth = 10

supportMargin = 40
supportOffset = (sheetW + sheetMargin + supportMargin) / 2

baseThickness = 40
baseW = sheetW + 2*supportMargin + 2*sheetMargin
baseH = sheetH + 2*sheetMargin

tmp1 = make_face(Plane.XZ.offset(baseH) * baseProfile(baseThickness, baseW))
tmp1 = extrude(tmp1, baseH * 2)
tmp2 = make_face(Plane.YZ.offset(baseW) * baseProfile(baseThickness, baseH))
tmp2 = extrude(tmp2, baseW * 2)

base = tmp1 & tmp2

topFace = base.faces().sort_by().last

plateIndent = Plane(topFace) * Rectangle(sheetW, sheetH)
base -= extrude(plateIndent, -sheetDepth)

# Cavity under ("balast" will be filled with rice or something :D)

balastDepth = 25
balastW = baseW - 2*sheetMargin
balastH = baseH - 2*sheetMargin
reinforcementW = 20

bottomFace = base.faces().sort_by().first
balastSketch = Rectangle(balastW, balastH)
balastSketch -= [
	Pos(supportOffset, 0) * Circle(supportMargin * 0.5),
    Pos(-supportOffset, 0) * Circle(supportMargin * 0.5),
    Rectangle(balastW, reinforcementW),
    Rectangle(reinforcementW, balastH)
]

base -= extrude(Plane(bottomFace) * balastSketch, -balastDepth)

# Feet

footH = 30

footProfile = Line((0, footH), (10, footH))
footProfile += SagittaArc(footProfile @ 1, footProfile @ 1 + (0, -5), 1)
footProfile += EllipticalCenterArc(footProfile @ 1 + (0, -5), 14, 5, start_angle= -90, end_angle=90)
footProfile += RadiusArc(footProfile @ 1, (3, 0), 15)
footProfile += Line(footProfile @ 1, (0, 0))

footProfile = Pos(0, -footH) * footProfile

foot = revolve(make_face(Plane.XZ * footProfile), axis=Axis.Z)
footJoint = extrude(Plane(foot.faces().sort_by().last) * Rectangle(15, 15), 10)
foot += footJoint
foot.label = "foot"

feetPosLeft = base.faces().sort_by().first.vertices().group_by(Axis.X)[1].sort_by(Axis.Y)
feetPosRight = base.faces().sort_by().first.vertices().group_by(Axis.X)[-2].sort_by(Axis.Y)
feetPos = [feetPosLeft.first, feetPosLeft.last, feetPosRight.first, feetPosRight.last]

feet = [Pos(vert.X, vert.Y) * foot for vert in feetPos]

base -= [Pos(vert.X, vert.Y) * scale(footJoint, 1.05) for vert in feetPos]
base.label = "base"

# Final assembly

assem = Compound(children = [
    base,
    Pos(supportOffset, 0, baseThickness) * support,
    Pos(-supportOffset, 0, baseThickness) * support,
] + feet)

show(assem)
