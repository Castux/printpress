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
        rotate([0, 90, 0])
            linear_extrude(h*2, center= true)
                profile(h, z, z/7 * 3);

        linear_extrude(w*2, center= true)
            profile(w, z, z / 7 * 3);
    }
}



sheetW = 150;

baseW = sheetW + 2 * 50;
baseH = 200;

h = 70;
plateHeight = 15;
weightHeight = 40;
plateMargin = 20;

difference() {

    
    base(baseW, baseH, h);
    translate([0, h - plateHeight/2 + 0.1, 0])
        cube([sheetW, plateHeight, baseH], center = true);
    translate([0, h - plateHeight - weightHeight/2 + 0.2, 0])
        cube([sheetW - plateMargin, weightHeight, baseH - plateMargin], center = true);
}

lidThickness = 5;

    #translate([0, h - plateHeight + lidThickness / 2, 0])
        cube([baseW, lidThickness, baseH], center = true);