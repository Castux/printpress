from bd_warehouse.thread import IsoThread
from build123d import *
from ocp_vscode import *

set_defaults(reset_camera=Camera.CENTER, helper_scale=5)

eps = 0.2

supportRadius = 10
supportHeight = 100
supportThreadRadius = 10
supportThreadDepth = 30
threadEps = 0.4

sheetW = 120
sheetH = 180
sheetMargin = 6
sheetDepth = 10

supportMargin = 40
supportOffset = (sheetW + sheetMargin + supportMargin) / 2

baseThickness = 40
baseW = sheetW + 2 * supportMargin + 2 * sheetMargin
baseH = sheetH + 2 * sheetMargin

supportTopRadius = 10
supportTopHeight = 32

beamThickness = 20

shaftRadius = 20
hingeHeight = 30
shaftHeight = 100

def make_support_thread(external, eps):
	return IsoThread(
		major_diameter=supportThreadRadius * 2 + eps * 2,
		pitch=8,
		length=supportThreadDepth,
		external=external,
		end_finishes=("square", "chamfer"),
	)


def make_beam_peg(withEps=False):
	margin = eps if withEps else 0.0
	return Box(
		10 + 2 * margin,
		supportTopRadius * 2 + 20,
		6 + 2 * margin,
		align=(Align.CENTER, Align.CENTER, Align.MIN),
	)


def make_supports():
	supportSketch = Pos(0.8 * supportRadius, 0, 0) * Circle(supportRadius)
	supportSketch += Pos(-0.8 * supportRadius, 0, 0) * Circle(supportRadius)
	supportSketch += Pos(0, 0.8 * supportRadius, 0) * Circle(supportRadius / 3)
	supportSketch += Pos(0, -0.8 * supportRadius, 0) * Circle(supportRadius / 3)
	supportSketch = Rot(0, 0, 90) * supportSketch

	support = Solid.extrude_linear_with_rotation(
		supportSketch, (0, 0), (0, 0, supportHeight), 3 * 180
	)
	support = fillet(support.edges().group_by(Axis.Z)[1], radius=1)

	# Supports threads

	thread = make_support_thread(external=True, eps=0.0)
	thread = IsoThread(
		major_diameter=supportThreadRadius * 2,
		pitch=8,
		length=supportThreadDepth,
		external=True,
		end_finishes=("square", "chamfer"),
	)
	thread += Cylinder(
		radius=thread.min_radius,
		height=supportThreadDepth,
		align=(Align.CENTER, Align.CENTER, Align.MIN),
	)
	support += Rot(180, 0, 0) * thread

	# Support top

	support += extrude(
		Plane(support.faces().sort_by().last) * Circle(supportTopRadius),
		supportTopHeight,
	)
	support = fillet(support.edges().sort_by().last, radius=2)
	support -= Pos(0, 0, supportHeight + beamThickness) * make_beam_peg(withEps=True)

	support.label = "support"
	return [
		Pos(supportOffset, 0, baseThickness) * support,
		Pos(-supportOffset, 0, baseThickness) * support,
	]


def make_base():

	def baseProfile(baseH=40, baseW=120):
		short = baseH / 9
		tall = baseH * 3 / 9

		ln = Line((0, baseH), (baseW / 2, baseH))
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

	tmp1 = make_face(Plane.XZ.offset(baseH) * baseProfile(baseThickness, baseW))
	tmp1 = extrude(tmp1, baseH * 2)
	tmp2 = make_face(Plane.YZ.offset(baseW) * baseProfile(baseThickness, baseH))
	tmp2 = extrude(tmp2, baseW * 2)

	base = tmp1 & tmp2

	topFace = base.faces().sort_by().last

	plateIndent = Plane(topFace) * Rectangle(sheetW, sheetH)
	base -= extrude(plateIndent, -sheetDepth)

	# Sockets for supports

	base -= extrude(
		Plane(topFace)
		* Pos(supportOffset, 0)
		* Circle(supportThreadRadius + threadEps),
		-supportThreadDepth - 1,
	)
	base -= extrude(
		Plane(topFace)
		* Pos(-supportOffset, 0)
		* Circle(supportThreadRadius + threadEps),
		-supportThreadDepth - 1,
	)

	threadSocket = make_support_thread(external=False, eps=threadEps)
	base += Plane(topFace) * Pos(supportOffset, 0) * Rot(180, 0, 180) * threadSocket
	base += Plane(topFace) * Pos(-supportOffset, 0) * Rot(180, 0, 180) * threadSocket

	# Cavity under ("balast" will be filled with rice or something :D)

	balastDepth = 25
	balastW = baseW - 2 * sheetMargin
	balastH = baseH - 2 * sheetMargin
	reinforcementW = 20

	balastSketch = Rectangle(balastW, balastH)
	balastSketch -= [
		Pos(supportOffset, 0) * Circle(supportThreadRadius * 1.5),
		Pos(-supportOffset, 0) * Circle(supportThreadRadius * 1.5),
		Rectangle(balastW, reinforcementW),
		Rectangle(reinforcementW, balastH),
	]

	bottomFace = base.faces().sort_by().first
	base -= extrude(Plane(bottomFace) * balastSketch, -balastDepth)
	base.label = "base"

	return base


def make_feet(base):
	footH = 30

	footProfile = Line((0, footH), (10, footH))
	footProfile += SagittaArc(footProfile @ 1, footProfile @ 1 + (0, -5), 1)
	footProfile += EllipticalCenterArc(
		footProfile @ 1 + (0, -5), 12, 5, start_angle=-90, end_angle=90
	)
	footProfile += RadiusArc(footProfile @ 1, (4, 0), 15)
	footProfile += Line(footProfile @ 1, (0, 0))

	footProfile = Pos(0, -footH) * footProfile

	foot = revolve(make_face(Plane.XZ * footProfile), axis=Axis.Z)
	foot.label = "foot"

	baseBottomVertices = base.faces().sort_by().first.vertices().group_by(Axis.X)
	feetPosLeft = baseBottomVertices[1].sort_by(Axis.Y)
	feetPosRight = baseBottomVertices[-2].sort_by(Axis.Y)

	feetPos = [
		feetPosLeft.first,
		feetPosLeft.last,
		feetPosRight.first,
		feetPosRight.last,
	]

	feet = [Pos(vert.X, vert.Y) * foot for vert in feetPos]

	return feet


def make_beam():
	def beamProfile(w):
		h = beamThickness
		ln = Line((0, h), (w / 2 + 8, h))
		ln += Line(ln @ 1, ln @ 1 + (0, -4))
		ln += Line(ln @ 1, ln @ 1 + (-4, 0))
		ln += RadiusArc(ln @ 1, ln @ 1 + (-4, -12), 12)
		ln += Line(ln @ 1, ln @ 1 + (0, -4))
		ln += Line(ln @ 1, (0, 0))
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
	beam -= extrude(
		Plane(beamTopFace) * Pos(supportOffset, 0) * Circle(supportTopRadius + eps),
		-beamThickness,
	)
	beam -= extrude(
		Plane(beamTopFace) * Pos(-supportOffset, 0) * Circle(supportTopRadius + eps),
		-beamThickness,
	)

	beam -= Cylinder(radius=shaftRadius + threadEps, height = beamThickness*2)
	beam += Rot(0, 0, 180) * make_shaft_thread(height=beamThickness, external=False, eps=threadEps)

	beam.label = "beam"

	beamPeg = make_beam_peg()
	beamPeg.label = "beamPeg"

	return [
		Pos(0, 0, baseThickness + supportHeight) * beam,
		Pos(supportOffset, 0, baseThickness + supportHeight + beamThickness) * beamPeg,
		Pos(-supportOffset, 0, baseThickness + supportHeight + beamThickness) * beamPeg,
	]

def make_shaft_joint(withEps=False):
	margin = eps if withEps else 0.0
	return Box(shaftRadius + 2*margin, shaftRadius + 2*margin, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))

def make_shaft_hinge(withEps=False):
	emptyThickness = 5
	dy = hingeHeight / 4

	radius = shaftRadius
	innerRadius = 12

	if withEps:
		radius += eps
		innerRadius += eps

	sk = Line((0, emptyThickness), (radius, emptyThickness))
	sk += Line(sk @ 1, sk @ 1 + (0, dy - emptyThickness))
	sk += Line(sk @ 1, sk @ 1 + (-(radius-innerRadius), dy))
	sk += Line(sk @ 1, sk @ 1 + (0, dy))
	sk += Line(sk @ 1, sk @ 1 + (radius-innerRadius, dy))
	sk += Line(sk @ 1, sk @ 1 + (-radius, 0))

	return revolve(make_face(Plane.XZ * sk), axis=Axis.Z)

def make_shaft_thread(height, external, eps):
	return IsoThread(
		major_diameter=shaftRadius * 2 + eps * 2,
		pitch=10,
		length=height,
		external=external,
		end_finishes=("square", "square"),
	)

def make_shaft():
	thread = make_shaft_thread(height=shaftHeight, external=True, eps=0.0)
	thread += Cylinder(
		radius=thread.min_radius,
		height=shaftHeight,
		align=(Align.CENTER, Align.CENTER, Align.MIN),
	)

	joint = make_shaft_joint()
	hinge = make_shaft_hinge()

	shaft = Pos(0, 0, hingeHeight + shaftHeight) * joint + Pos(0, 0, hingeHeight) * thread + hinge
	shaft.label = "shaft"

	return [Pos(0, 0, baseThickness) * shaft]

def make_press():

	straightThickness = 5

	plate = Box(sheetW, sheetH, straightThickness, align=(Align.CENTER, Align.CENTER, Align.MIN))
	plate += extrude(
		Plane(plate.faces().sort_by().last) * Rectangle(sheetW - 20, sheetH - 20),
		amount=hingeHeight - straightThickness,
		taper=45
	)
	plate = fillet(plate.edges().group_by()[-3:], radius=straightThickness-1)

	hinge = make_shaft_hinge(withEps=True)
	hinge += extrude(hinge.faces().sort_by().first, 50)
	plate -= hinge

	plate.label = "plate"

	return [Pos(0, 0, baseThickness) * plate]

# Final assembly

parts = []

parts += make_supports()
base = make_base()
parts.append(base)
parts += make_feet(base)
parts += make_beam()
parts += make_shaft()
parts += make_press()

assem = Compound(children=parts)
show(assem)
# export_step(assem, "print.step")
