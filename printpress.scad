include <BOSL/transforms.scad>

$fa = 1;
$fs = 1;

module profile(w, h, smallr) {
	lowerScale = 0.5;
	difference() {
		union() {
			left(w/2) square([w, h]);
			left((w+smallr)/2) square([w + smallr, h - smallr]);

			right(w/2) back(h - smallr) circle(smallr);
			right(w/2 + smallr) scale([lowerScale, 1]) circle(h - smallr);

			left(w/2) back(h - smallr) circle(smallr);
			left(w/2 + smallr) scale([lowerScale, 1]) circle(h - smallr);
		}
		translate([-w, -2*h]) square([2*w, 2*h]);
	}
}

module base(w, h, z) {
	intersection() {
		zrot(90) xrot(90)
			linear_extrude(h*3,  center=true)
				profile(h, z, z/7 * 1.5);

		xrot(90)
			linear_extrude(w*3, center= true)
				profile(w, z, z / 7 * 1.5);
	}
}

module main() {

	sheetW = 150;
	supportW = 40;

	baseW = sheetW + 2 * supportW;
	baseH = 200;

	h = 40;
	plateHeight = 15;
	weightHeight = 20;
	plateMargin = 20;

	difference() {
		base(baseW, baseH, h);
		up(h - plateHeight/2 + 0.1)
			cube([sheetW, baseH, plateHeight], center = true);
		up(h - plateHeight - weightHeight/2 + 0.2)
			cube([sheetW - plateMargin, baseH - plateMargin, weightHeight], center = true);
	}

	lidThickness = 5;
	#up(h - plateHeight + lidThickness / 2)
		cube([baseW, baseH, lidThickness], center = true);
}

main();