include <BOSL/transforms.scad>

$fa = 1;
$fs = 1;

module profile(w, h, smallr) {
	lowerScale = 0.35;
	xflip_copy()
	back_half(s = w * 2, planar = true)
		union() {
			square([w/2, h]);
			square([w/2 + smallr, h - smallr]);
			square([w/2 + smallr + lowerScale * (h - smallr) + 2, 10]);

			right(w/2) back(h - smallr) circle(smallr);
			right(w/2 + smallr) scale([lowerScale, 1]) circle(h - smallr);
		}
}

module base(w, h, z) {
	intersection() {
		zrot(90) xrot(90)
			linear_extrude(h*3, center=true)
				profile(h, z, z/7 * 1.5);

		xrot(90)
			linear_extrude(w*3, center=true)
				profile(w, z, z / 7 * 1.5);
	}
}

module main() {

	tolerance = 0.2;

	sheetW = 130;
	supportW = 40;

	baseW = sheetW + 2 * supportW;
	baseH = 180;

	h = 40;
	plateHeight = 10;
	weightHeight = 25;
	plateMargin = 20;

	supportHeight = 120;
	supportSlotSize = 30;
	supportOffset = sheetW/2 + supportW/2;
	supportRadius = 10;

	difference() {
		base(baseW, baseH, h);
		up(h - plateHeight/2 + 0.1)
			cube([sheetW, baseH, plateHeight], center = true);
		up(h - plateHeight - weightHeight/2 + 0.2)
			cube([sheetW - plateMargin, baseH - plateMargin, weightHeight], center = true);
		left(supportOffset) up(h) support(supportHeight, supportSlotSize, supportRadius + tolerance);
		right(supportOffset) up(h) support(supportHeight, supportSlotSize, supportRadius + tolerance);
	}

	lidThickness = 5;
	up(h - plateHeight + lidThickness / 2 + 20)
		cube([sheetW, baseH, lidThickness], center = true);
	
	left(supportOffset) up(h*2) support(supportHeight, supportSlotSize, supportRadius);
	right(supportOffset) up(h*2) support(supportHeight, supportSlotSize, supportRadius);
}

module support(height, slotHeight, rad) {
	union() {
		down(slotHeight)
		linear_extrude(height + slotHeight, twist = 2.6 * 360)
		union() {
			right(0.8 * rad) circle(rad);
			left(0.8 * rad) circle(rad);
			back(0.8 * rad) circle(rad/3);
			forward(0.8 * rad) circle(rad/3);
		}
	}
}

main();
