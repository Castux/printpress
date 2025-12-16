from build123d import *
from ocp_vscode import *
from bd_warehouse.thread import IsoThread
set_defaults(reset_camera=Camera.CENTER, helper_scale=5)

eps = 0.2

# Supports

supportRadius = 10
supportHeight = 100
supportThreadRadius = 10
supportThreadDepth = 30
threadEps = 0.4

supportSketch = Pos(0.8 * supportRadius, 0, 0) * Circle(supportRadius)
supportSketch += Pos(-0.8 * supportRadius, 0, 0) * Circle(supportRadius)
supportSketch += Pos(0, 0.8 * supportRadius, 0) * Circle(supportRadius / 3)
supportSketch += Pos(0, -0.8 * supportRadius, 0) * Circle(supportRadius / 3)

support = Solid.extrude_linear_with_rotation(supportSketch, (0,0), (0, 0, supportHeight), 3 * 180)
#support = fillet(support.edges().group_by(Axis.Z)[1], radius=0.5)

# Supports threads

thread = IsoThread(major_diameter = supportThreadRadius * 2, pitch = 8, length = supportThreadDepth, external = True, end_finishes=("square", "chamfer"))
threadSocket = IsoThread(major_diameter = supportThreadRadius * 2 + threadEps * 2, pitch = 8, length = supportThreadDepth, external = False, end_finishes=("square", "chamfer"))
thread += Cylinder(radius=thread.min_radius, height= supportThreadDepth, align=(Align.CENTER, Align.CENTER, Align.MIN))
support += Rot(180, 0, 0) * thread

# Support top

supportTopRadius = 10
supportTopHeight = 32

support += extrude(Plane(support.faces().sort_by().last) * Circle(supportTopRadius), supportTopHeight)
support = fillet(support.edges().sort_by().last, radius = 2)

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

sheetW = 120
sheetH = 180
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

# Sockets for supports

base -= extrude(Plane(topFace) * Pos(supportOffset, 0) * Circle(supportThreadRadius + threadEps), -supportThreadDepth - 1)
base -= extrude(Plane(topFace) * Pos(-supportOffset, 0) * Circle(supportThreadRadius + threadEps), -supportThreadDepth - 1)

base += Plane(topFace) * Pos(supportOffset, 0) * Rot(180, 0, 180) * threadSocket
base += Plane(topFace) * Pos(-supportOffset, 0) * Rot(180, 0, 180) * threadSocket

# Cavity under ("balast" will be filled with rice or something :D)

balastDepth = 25
balastW = baseW - 2*sheetMargin
balastH = baseH - 2*sheetMargin
reinforcementW = 20

balastSketch = Rectangle(balastW, balastH)
balastSketch -= [
	Pos(supportOffset, 0) * Circle(supportThreadRadius * 1.5),
    Pos(-supportOffset, 0) * Circle(supportThreadRadius * 1.5),
    Rectangle(balastW, reinforcementW),
    Rectangle(reinforcementW, balastH)
]

bottomFace = base.faces().sort_by().first
base -= extrude(Plane(bottomFace) * balastSketch, -balastDepth)

# Feet

footH = 30

footProfile = Line((0, footH), (10, footH))
footProfile += SagittaArc(footProfile @ 1, footProfile @ 1 + (0, -5), 1)
footProfile += EllipticalCenterArc(footProfile @ 1 + (0, -5), 12, 5, start_angle= -90, end_angle=90)
footProfile += RadiusArc(footProfile @ 1, (4, 0), 15)
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

# Beam

beamThickness = 20

def beamProfile(w):
    h = beamThickness
    ln = Line((0, h), (w/2 + 8, h))
    ln += Line(ln @ 1, ln @ 1 + (0, -4))
    ln += Line(ln @ 1, ln @ 1 + (-4, 0))
    ln += RadiusArc(ln @ 1, ln @ 1 + (-4, -12), 12)
    ln += Line(ln @ 1, ln @ 1 + (0, -4))
    ln += Line(ln @ 1, (0,0))
    ln += mirror(ln, Plane.YZ)

    return ln

beamW = baseW
beamH = 60

beamTmp1 = make_face(Plane.XZ.offset(beamH) * beamProfile(beamW))
beamTmp1 = extrude(beamTmp1, beamH * 2)
beamTmp2 = make_face(Plane.YZ.offset(beamW) * beamProfile(beamH))
beamTmp2 = extrude(beamTmp2, baseW * 2)

beam = beamTmp1 & beamTmp2

beamTopFace = beam.faces().sort_by().last
beam -= extrude(Plane(beamTopFace) * Pos(supportOffset, 0) * Circle(supportTopRadius + eps), -beamThickness)
beam -= extrude(Plane(beamTopFace) * Pos(-supportOffset, 0) * Circle(supportTopRadius + eps), -beamThickness)
beam.label = "beam"

beamPeg = Box(10, supportTopRadius*2 + 20, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
beamPeg.label = "beamPeg"

support -= Pos(0, 0, supportHeight + beamThickness) * scale(beamPeg, 1.05)
pegs = [
	Pos( supportOffset, 0, baseThickness + supportHeight + beamThickness) * beamPeg,
	Pos(-supportOffset, 0, baseThickness + supportHeight + beamThickness) * beamPeg,
]

# Final assembly

assem = Compound(children = [
    base,
    Pos(0, 0, baseThickness + supportHeight) * beam,
    Pos(supportOffset, 0, baseThickness) * support,
    Pos(-supportOffset, 0, baseThickness) * support,
] + feet + pegs)

show(assem)
#export_step(assem, "print.step")
