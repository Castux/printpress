$fa = 1;
$fs = 1;

module profile(w, h, smallr) {
	lowerScale = 0.5;
	difference() {
		union() {
			translate([-w/2, 0]) square([w, h]);
			translate([-(w+smallr)/2, 0]) square([w + smallr, h - smallr]);

			translate([w/2, h - smallr]) circle(smallr);
			translate([w/2 + smallr, 0]) scale([lowerScale, 1]) circle(h - smallr);

			translate([-w/2, h - smallr]) circle(smallr);
			translate([-w/2 - smallr, 0]) scale([lowerScale, 1]) circle(h - smallr);
		}
		translate([-w, -2*h]) square([2*w, 2*h]);
	}
}

module base(w, h, z) {
	intersection() {
		rotate([90, 0, 90])
			linear_extrude(h*3,  center=true)
				profile(h, z, z/7 * 1.5);

		rotate([90, 0, 0])
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
		translate([0, 0, h - plateHeight/2 + 0.1])
			cube([sheetW, baseH, plateHeight], center = true);
		translate([0, 0, h - plateHeight - weightHeight/2 + 0.2])
			cube([sheetW - plateMargin, baseH - plateMargin, weightHeight], center = true);
	}

	lidThickness = 5;
	#translate([0, 0, h - plateHeight + lidThickness / 2])
		cube([baseW, baseH, lidThickness], center = true);
}

main();
