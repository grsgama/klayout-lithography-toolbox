import pya
import math
import cnst_extended_pcells as cep

# =====================================================================
# LITHOGRAPHY & NANOPHOTONICS CELLS
# =====================================================================

# 1. Grating
class GratingPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(GratingPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("period", self.TypeDouble, "Grating Period (um)", default = 1.0)
        self.param("fill_factor", self.TypeDouble, "Fill Factor (0 to 1)", default = 0.5)
        self.param("length", self.TypeDouble, "Grating Length (um)", default = 50.0)
        self.param("width", self.TypeDouble, "Grating Width (um)", default = 20.0)

    def display_text_impl(self):
        return f"Grating(Period={self.period:.2f}um, Length={self.length:.1f}um)"

    def coerce_parameters_impl(self):
        if self.period <= 0: self.period = 0.1
        if self.fill_factor <= 0.01: self.fill_factor = 0.01
        elif self.fill_factor >= 0.99: self.fill_factor = 0.99
        if self.length <= 0: self.length = 1.0
        if self.width <= 0: self.width = 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        finger_width = self.period * self.fill_factor
        num_periods = int(self.length / self.period)
        
        for i in range(num_periods):
            x_start = i * self.period
            x_end = x_start + finger_width
            box = pya.Box(
                int(x_start / dbu),
                int(-self.width / 2.0 / dbu),
                int(x_end / dbu),
                int(self.width / 2.0 / dbu)
            )
            self.cell.shapes(layer_idx).insert(box)

# 2. Ring / Disk
class RingPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(RingPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("r_outer", self.TypeDouble, "Outer Radius (um)", default = 10.0)
        self.param("r_inner", self.TypeDouble, "Inner Radius (um) [0 for Disk]", default = 8.0)
        self.param("npoints", self.TypeInt, "Number of Vertices", default = 64)

    def display_text_impl(self):
        return f"Ring(Ro={self.r_outer:.2f}um, Ri={self.r_inner:.2f}um)"

    def coerce_parameters_impl(self):
        if self.r_outer <= 0: self.r_outer = 1.0
        if self.r_inner < 0: self.r_inner = 0.0
        if self.r_inner >= self.r_outer: self.r_inner = self.r_outer - 0.1
        if self.npoints < 3: self.npoints = 3

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        outer_pts = []
        inner_pts = []
        
        for i in range(self.npoints):
            angle = i * 2 * math.pi / self.npoints
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            outer_pts.append(pya.Point(int(self.r_outer * cos_a / dbu), int(self.r_outer * sin_a / dbu)))
            if self.r_inner > 0:
                inner_pts.append(pya.Point(int(self.r_inner * cos_a / dbu), int(self.r_inner * sin_a / dbu)))
                
        if self.r_inner > 0:
            poly = pya.Polygon(outer_pts)
            poly.insert_hole(inner_pts)
            self.cell.shapes(layer_idx).insert(poly)
        else:
            poly = pya.Polygon(outer_pts)
            self.cell.shapes(layer_idx).insert(poly)

# 3. Bezier Taper
class BezierTaperPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(BezierTaperPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("w_start", self.TypeDouble, "Start Width (um)", default = 0.5)
        self.param("w_end", self.TypeDouble, "End Width (um)", default = 5.0)
        self.param("length", self.TypeDouble, "Taper Length (um)", default = 20.0)
        self.param("npoints", self.TypeInt, "Number of segments", default = 30)

    def display_text_impl(self):
        return f"BezierTaper(W={self.w_start:.1f}->{self.w_end:.1f}um, L={self.length:.1f}um)"

    def coerce_parameters_impl(self):
        if self.w_start <= 0: self.w_start = 0.1
        if self.w_end <= 0: self.w_end = 0.1
        if self.length <= 0: self.length = 1.0
        if self.npoints < 2: self.npoints = 2

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        pts = []
        
        for i in range(self.npoints + 1):
            t = i / self.npoints
            s = 3 * t**2 - 2 * t**3
            w = self.w_start * (1.0 - s) + self.w_end * s
            x = t * self.length
            pts.append(pya.Point(int(x / dbu), int(w / 2.0 / dbu)))
            
        for i in range(self.npoints, -1, -1):
            t = i / self.npoints
            s = 3 * t**2 - 2 * t**3
            w = self.w_start * (1.0 - s) + self.w_end * s
            x = t * self.length
            pts.append(pya.Point(int(x / dbu), int(-w / 2.0 / dbu)))
            
        poly = pya.Polygon(pts)
        self.cell.shapes(layer_idx).insert(poly)

# 4. Alignment Mark
class AlignmentMarkPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(AlignmentMarkPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("style", self.TypeString, "Style (Cross, Box, Both)", default = "Cross")
        self.param("cross_w", self.TypeDouble, "Cross bar width (um)", default = 2.0)
        self.param("cross_l", self.TypeDouble, "Cross length (um)", default = 40.0)
        self.param("box_size", self.TypeDouble, "Box Outer size (um)", default = 50.0)
        self.param("box_w", self.TypeDouble, "Box frame thickness (um)", default = 4.0)

    def display_text_impl(self):
        return f"AlignMark({self.style})"

    def coerce_parameters_impl(self):
        if self.cross_w <= 0: self.cross_w = 0.5
        if self.cross_l <= self.cross_w: self.cross_l = self.cross_w + 2.0
        if self.box_size <= 0: self.box_size = 10.0
        if self.box_w <= 0: self.box_w = 1.0
        if self.box_w >= self.box_size/2.0: self.box_w = self.box_size/4.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        region = pya.Region()
        
        if self.style in ["Cross", "Both"]:
            horiz_box = pya.Box(
                int(-self.cross_l / 2.0 / dbu), int(-self.cross_w / 2.0 / dbu),
                int(self.cross_l / 2.0 / dbu), int(self.cross_w / 2.0 / dbu)
            )
            vert_box = pya.Box(
                int(-self.cross_w / 2.0 / dbu), int(-self.cross_l / 2.0 / dbu),
                int(self.cross_w / 2.0 / dbu), int(self.cross_l / 2.0 / dbu)
            )
            region.insert(horiz_box)
            region.insert(vert_box)
            
        if self.style in ["Box", "Both"]:
            outer_box = pya.Box(
                int(-self.box_size / 2.0 / dbu), int(-self.box_size / 2.0 / dbu),
                int(self.box_size / 2.0 / dbu), int(self.box_size / 2.0 / dbu)
            )
            inner_size = self.box_size - 2.0 * self.box_w
            inner_box = pya.Box(
                int(-inner_size / 2.0 / dbu), int(-inner_size / 2.0 / dbu),
                int(inner_size / 2.0 / dbu), int(inner_size / 2.0 / dbu)
            )
            box_region = pya.Region(outer_box) - pya.Region(inner_box)
            region.insert(box_region)
            
        self.cell.shapes(layer_idx).insert(region)

# 5. Vernier Caliper
class VernierCaliperPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(VernierCaliperPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("num_ticks", self.TypeInt, "Number of ticks", default = 11)
        self.param("main_pitch", self.TypeDouble, "Main scale pitch (um)", default = 1.0)
        self.param("vernier_pitch", self.TypeDouble, "Vernier scale pitch (um)", default = 0.9)
        self.param("tick_w", self.TypeDouble, "Tick width (um)", default = 0.1)
        self.param("tick_l", self.TypeDouble, "Tick length (um)", default = 8.0)
        self.param("spacing", self.TypeDouble, "Separation between scales (um)", default = 1.0)

    def display_text_impl(self):
        return f"Vernier(P1={self.main_pitch:.2f}um, P2={self.vernier_pitch:.2f}um)"

    def coerce_parameters_impl(self):
        if self.num_ticks < 2: self.num_ticks = 2
        if self.main_pitch <= 0: self.main_pitch = 0.2
        if self.vernier_pitch <= 0: self.vernier_pitch = 0.2
        if self.tick_w <= 0: self.tick_w = 0.05
        if self.tick_l <= 0: self.tick_l = 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        main_total_w = (self.num_ticks - 1) * self.main_pitch
        vernier_total_w = (self.num_ticks - 1) * self.vernier_pitch
        
        for i in range(self.num_ticks):
            x = -main_total_w / 2.0 + i * self.main_pitch
            box = pya.Box(
                int((x - self.tick_w / 2.0) / dbu),
                int(self.spacing / 2.0 / dbu),
                int((x + self.tick_w / 2.0) / dbu),
                int((self.spacing / 2.0 + self.tick_l) / dbu)
            )
            self.cell.shapes(layer_idx).insert(box)
            
        for i in range(self.num_ticks):
            x = -vernier_total_w / 2.0 + i * self.vernier_pitch
            box = pya.Box(
                int((x - self.tick_w / 2.0) / dbu),
                int((-self.spacing / 2.0 - self.tick_l) / dbu),
                int((x + self.tick_w / 2.0) / dbu),
                int(-self.spacing / 2.0 / dbu)
            )
            self.cell.shapes(layer_idx).insert(box)

# 6. Photonic Crystal
class PhotonicCrystalPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(PhotonicCrystalPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("lattice", self.TypeString, "Lattice (Square, Hexagonal)", default = "Square")
        self.param("pitch", self.TypeDouble, "Pitch (um)", default = 1.0)
        self.param("radius", self.TypeDouble, "Radius of pillars/holes (um)", default = 0.3)
        self.param("nx", self.TypeInt, "Number of columns (X)", default = 10)
        self.param("ny", self.TypeInt, "Number of rows (Y)", default = 10)
        self.param("npoints", self.TypeInt, "Number of vertices for circle", default = 32)
        self.param("draw_slab", self.TypeBoolean, "Draw background slab (Holes)", default = True)
        self.param("margin", self.TypeDouble, "Slab margin (um)", default = 1.0)

    def display_text_impl(self):
        return f"PhC_{self.lattice}(Pitch={self.pitch:.2f}um, R={self.radius:.2f}um)"

    def coerce_parameters_impl(self):
        if self.pitch <= 0: self.pitch = 0.1
        if self.radius <= 0: self.radius = 0.01
        if self.radius >= self.pitch/2.0: self.radius = self.pitch/2.0 - 0.01
        if self.nx < 1: self.nx = 1
        if self.ny < 1: self.ny = 1
        if self.npoints < 3: self.npoints = 3
        if self.margin < 0: self.margin = 0.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        centers = []
        for ix in range(self.nx):
            for iy in range(self.ny):
                if self.lattice == "Square":
                    cx = ix * self.pitch
                    cy = iy * self.pitch
                else:
                    cx = (ix + 0.5 * (iy % 2)) * self.pitch
                    cy = iy * self.pitch * math.sqrt(3) / 2.0
                centers.append((cx, cy))
                
        xs = [c[0] for c in centers]
        ys = [c[1] for c in centers]
        mid_x = (max(xs) + min(xs)) / 2.0
        mid_y = (max(ys) + min(ys)) / 2.0
        
        circles_region = pya.Region()
        for cx, cy in centers:
            ccx = cx - mid_x
            ccy = cy - mid_y
            circle_pts = []
            for i in range(self.npoints):
                angle = i * 2 * math.pi / self.npoints
                px = ccx + self.radius * math.cos(angle)
                py = ccy + self.radius * math.sin(angle)
                circle_pts.append(pya.Point(int(px / dbu), int(py / dbu)))
            circles_region.insert(pya.Polygon(circle_pts))
            
        if self.draw_slab:
            min_x = min(xs) - mid_x - self.radius - self.margin
            max_x = max(xs) - mid_x + self.radius + self.margin
            min_y = min(ys) - mid_y - self.radius - self.margin
            max_y = max(ys) - mid_y + self.radius + self.margin
            slab_box = pya.Box(
                int(min_x / dbu), int(min_y / dbu),
                int(max_x / dbu), int(max_y / dbu)
            )
            slab_region = pya.Region(slab_box) - circles_region
            self.cell.shapes(layer_idx).insert(slab_region)
        else:
            self.cell.shapes(layer_idx).insert(circles_region)

# 7. Y-Splitter Waveguide
class YSplitterPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(YSplitterPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("w_in", self.TypeDouble, "Input width (um)", default = 0.5)
        self.param("w_out", self.TypeDouble, "Output width (um)", default = 0.5)
        self.param("length", self.TypeDouble, "Length (um)", default = 15.0)
        self.param("branch_sep", self.TypeDouble, "Output branch separation (um)", default = 4.0)
        self.param("npoints", self.TypeInt, "Number of points per curve", default = 30)

    def display_text_impl(self):
        return f"YSplitter(Length={self.length:.1f}um, Sep={self.branch_sep:.1f}um)"

    def coerce_parameters_impl(self):
        if self.w_in <= 0: self.w_in = 0.1
        if self.w_out <= 0: self.w_out = 0.1
        if self.length <= 0: self.length = 1.0
        if self.branch_sep <= self.w_out: self.branch_sep = self.w_out + 0.1
        if self.npoints < 3: self.npoints = 3

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        
        # Draw Top Branch
        top_pts = []
        for i in range(self.npoints + 1):
            t = i / self.npoints
            x = t * self.length
            y_center = (self.branch_sep / 4.0) * (1.0 - math.cos(math.pi * t))
            w = self.w_in * (1.0 - t) + self.w_out * t
            y = y_center + w / 2.0
            top_pts.append(pya.Point(int(x / dbu), int(y / dbu)))
            
        for i in range(self.npoints, -1, -1):
            t = i / self.npoints
            x = t * self.length
            y_center = (self.branch_sep / 4.0) * (1.0 - math.cos(math.pi * t))
            w = self.w_in * (1.0 - t) + self.w_out * t
            y = y_center - w / 2.0
            top_pts.append(pya.Point(int(x / dbu), int(y / dbu)))
        top_poly = pya.Polygon(top_pts)
        
        # Draw Bottom Branch
        bottom_pts = []
        for i in range(self.npoints + 1):
            t = i / self.npoints
            x = t * self.length
            y_center = -(self.branch_sep / 4.0) * (1.0 - math.cos(math.pi * t))
            w = self.w_in * (1.0 - t) + self.w_out * t
            y = y_center + w / 2.0
            bottom_pts.append(pya.Point(int(x / dbu), int(y / dbu)))
            
        for i in range(self.npoints, -1, -1):
            t = i / self.npoints
            x = t * self.length
            y_center = -(self.branch_sep / 4.0) * (1.0 - math.cos(math.pi * t))
            w = self.w_in * (1.0 - t) + self.w_out * t
            y = y_center - w / 2.0
            bottom_pts.append(pya.Point(int(x / dbu), int(y / dbu)))
        bottom_poly = pya.Polygon(bottom_pts)
        
        self.cell.shapes(layer_idx).insert(top_poly)
        self.cell.shapes(layer_idx).insert(bottom_poly)

# 8. Star Shape
class StarPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(StarPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("r_outer", self.TypeDouble, "Outer Radius (um)", default = 10.0)
        self.param("r_inner", self.TypeDouble, "Inner Radius (um)", default = 4.0)
        self.param("n_points", self.TypeInt, "Number of star points", default = 5)
        self.param("rotation", self.TypeDouble, "Rotation Angle (deg)", default = 0.0)

    def display_text_impl(self):
        return f"Star(Ro={self.r_outer:.1f}um, Points={self.n_points})"

    def coerce_parameters_impl(self):
        if self.r_outer <= 0: self.r_outer = 1.0
        if self.r_inner <= 0: self.r_inner = 0.5
        if self.r_inner >= self.r_outer: self.r_inner = self.r_outer / 2.0
        if self.n_points < 3: self.n_points = 3

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        pts = []
        total_vertices = 2 * self.n_points
        
        for i in range(total_vertices):
            angle = i * math.pi / self.n_points + math.radians(self.rotation)
            r = self.r_outer if i % 2 == 0 else self.r_inner
            pts.append(pya.Point(int(r * math.cos(angle) / dbu), int(r * math.sin(angle) / dbu)))
            
        poly = pya.Polygon(pts)
        self.cell.shapes(layer_idx).insert(poly)

# 9. L-Shape
class LShapePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(LShapePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("l1", self.TypeDouble, "Horizontal Length (um)", default = 20.0)
        self.param("w1", self.TypeDouble, "Horizontal Width (um)", default = 5.0)
        self.param("l2", self.TypeDouble, "Vertical Length (um)", default = 20.0)
        self.param("w2", self.TypeDouble, "Vertical Width (um)", default = 5.0)

    def display_text_impl(self):
        return f"LShape(L1={self.l1:.1f}um, L2={self.l2:.1f}um)"

    def coerce_parameters_impl(self):
        if self.l1 <= 0: self.l1 = 1.0
        if self.w1 <= 0: self.w1 = 0.5
        if self.l2 <= 0: self.l2 = 1.0
        if self.w2 <= 0: self.w2 = 0.5
        if self.w2 >= self.l1: self.w2 = self.l1 - 0.1

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        
        pts = [
            pya.Point(0, 0),
            pya.Point(int(self.l1 / dbu), 0),
            pya.Point(int(self.l1 / dbu), int(self.w1 / dbu)),
            pya.Point(int(self.w2 / dbu), int(self.w1 / dbu)),
            pya.Point(int(self.w2 / dbu), int((self.w1 + self.l2) / dbu)),
            pya.Point(0, int((self.w1 + self.l2) / dbu))
        ]
        
        poly = pya.Polygon(pts)
        self.cell.shapes(layer_idx).insert(poly)

# 10. Rounded Rectangle
class RoundedRectanglePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(RoundedRectanglePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("length", self.TypeDouble, "Length X (um)", default = 30.0)
        self.param("width", self.TypeDouble, "Width Y (um)", default = 15.0)
        self.param("r_corner", self.TypeDouble, "Corner Radius (um)", default = 3.0)
        self.param("npoints", self.TypeInt, "Points per corner", default = 16)

    def display_text_impl(self):
        return f"RoundRect(L={self.length:.1f}um, W={self.width:.1f}um)"

    def coerce_parameters_impl(self):
        if self.length <= 0: self.length = 1.0
        if self.width <= 0: self.width = 1.0
        if self.r_corner < 0: self.r_corner = 0.0
        max_r = min(self.length, self.width) / 2.0
        if self.r_corner >= max_r: self.r_corner = max_r - 0.05
        if self.npoints < 2: self.npoints = 2

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        
        if self.r_corner == 0:
            box = pya.Box(
                int(-self.length / 2.0 / dbu), int(-self.width / 2.0 / dbu),
                int(self.length / 2.0 / dbu), int(self.width / 2.0 / dbu)
            )
            self.cell.shapes(layer_idx).insert(box)
            return
            
        pts = []
        cx = self.length / 2.0 - self.r_corner
        cy = self.width / 2.0 - self.r_corner
        
        for i in range(self.npoints + 1):
            angle = i * (math.pi / 2.0) / self.npoints
            x = cx + self.r_corner * math.cos(angle)
            y = cy + self.r_corner * math.sin(angle)
            pts.append(pya.Point(int(x / dbu), int(y / dbu)))
            
        for i in range(self.npoints + 1):
            angle = math.pi / 2.0 + i * (math.pi / 2.0) / self.npoints
            x = -cx + self.r_corner * math.cos(angle)
            y = cy + self.r_corner * math.sin(angle)
            pts.append(pya.Point(int(x / dbu), int(y / dbu)))
            
        for i in range(self.npoints + 1):
            angle = math.pi + i * (math.pi / 2.0) / self.npoints
            x = -cx + self.r_corner * math.cos(angle)
            y = -cy + self.r_corner * math.sin(angle)
            pts.append(pya.Point(int(x / dbu), int(y / dbu)))
            
        for i in range(self.npoints + 1):
            angle = 1.5 * math.pi + i * (math.pi / 2.0) / self.npoints
            x = cx + self.r_corner * math.cos(angle)
            y = -cy + self.r_corner * math.sin(angle)
            pts.append(pya.Point(int(x / dbu), int(y / dbu)))
            
        poly = pya.Polygon(pts)
        self.cell.shapes(layer_idx).insert(poly)

# 11. Torus / Ring Arc
class TorusPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(TorusPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("r_outer", self.TypeDouble, "Outer Radius (um)", default = 10.0)
        self.param("r_inner", self.TypeDouble, "Inner Radius (um)", default = 7.0)
        self.param("start_angle", self.TypeDouble, "Start Angle (deg)", default = 0.0)
        self.param("end_angle", self.TypeDouble, "End Angle (deg)", default = 90.0)
        self.param("npoints", self.TypeInt, "Number of segments", default = 32)

    def display_text_impl(self):
        return f"Torus(Ro={self.r_outer:.1f}um, Ri={self.r_inner:.1f}um, Sweep={self.end_angle-self.start_angle:.1f}deg)"

    def coerce_parameters_impl(self):
        if self.r_outer <= 0: self.r_outer = 1.0
        if self.r_inner <= 0: self.r_inner = 0.5
        if self.r_inner >= self.r_outer: self.r_inner = self.r_outer - 0.1
        if self.npoints < 3: self.npoints = 3
        if self.start_angle > self.end_angle:
            self.start_angle, self.end_angle = self.end_angle, self.start_angle

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        pts = []
        
        start_rad = math.radians(self.start_angle)
        end_rad = math.radians(self.end_angle)
        sweep_rad = end_rad - start_rad
        
        for i in range(self.npoints + 1):
            angle = start_rad + (i / self.npoints) * sweep_rad
            x = self.r_outer * math.cos(angle)
            y = self.r_outer * math.sin(angle)
            pts.append(pya.Point(int(x / dbu), int(y / dbu)))
            
        for i in range(self.npoints, -1, -1):
            angle = start_rad + (i / self.npoints) * sweep_rad
            x = self.r_inner * math.cos(angle)
            y = self.r_inner * math.sin(angle)
            pts.append(pya.Point(int(x / dbu), int(y / dbu)))
            
        poly = pya.Polygon(pts)
        self.cell.shapes(layer_idx).insert(poly)


# =====================================================================
# MEMS & NEMS MECHANICAL CELLS
# =====================================================================

# 1. Cantilever Beam
class CantileverPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CantileverPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("length", self.TypeDouble, "Beam Length (um)", default = 100.0)
        self.param("width", self.TypeDouble, "Beam Width (um)", default = 10.0)
        self.param("anchor_l", self.TypeDouble, "Anchor Length (um)", default = 10.0)
        self.param("anchor_w", self.TypeDouble, "Anchor Width (um)", default = 20.0)
        self.param("release_holes", self.TypeBoolean, "Enable Release Holes", default = False)
        self.param("hole_size", self.TypeDouble, "Hole Size (um)", default = 2.0)
        self.param("hole_pitch", self.TypeDouble, "Hole Pitch (um)", default = 10.0)

    def display_text_impl(self):
        return f"Cantilever(L={self.length:.1f}um, W={self.width:.1f}um)"

    def coerce_parameters_impl(self):
        if self.length <= 0: self.length = 10.0
        if self.width <= 0: self.width = 1.0
        if self.anchor_l <= 0: self.anchor_l = 1.0
        if self.anchor_w <= 0: self.anchor_w = self.width
        if self.hole_size <= 0: self.hole_size = 0.5
        if self.hole_pitch <= self.hole_size: self.hole_pitch = self.hole_size + 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        
        anchor_box = pya.Box(
            int(-self.anchor_l / dbu), int(-self.anchor_w / 2.0 / dbu),
            0, int(self.anchor_w / 2.0 / dbu)
        )
        beam_box = pya.Box(
            0, int(-self.width / 2.0 / dbu),
            int(self.length / dbu), int(self.width / 2.0 / dbu)
        )
        
        region = pya.Region(anchor_box)
        region.insert(beam_box)
        
        if self.release_holes:
            margin = 2.0
            x_start = margin + self.hole_size/2.0
            x_end = self.length - margin - self.hole_size/2.0
            y_start = -self.width/2.0 + margin + self.hole_size/2.0
            y_end = self.width/2.0 - margin - self.hole_size/2.0
            
            if x_end > x_start and y_end > y_start:
                nx = int((x_end - x_start) / self.hole_pitch) + 1
                ny = int((y_end - y_start) / self.hole_pitch) + 1
                x_offset = (self.length - (nx - 1) * self.hole_pitch) / 2.0
                y_offset = - ((ny - 1) * self.hole_pitch) / 2.0
                
                holes_region = pya.Region()
                for ix in range(nx):
                    for iy in range(ny):
                        cx = x_offset + ix * self.hole_pitch
                        cy = y_offset + iy * self.hole_pitch
                        hole_box = pya.Box(
                            int((cx - self.hole_size/2.0) / dbu),
                            int((cy - self.hole_size/2.0) / dbu),
                            int((cx + self.hole_size/2.0) / dbu),
                            int((cy + self.hole_size/2.0) / dbu)
                        )
                        holes_region.insert(hole_box)
                region -= holes_region
                
        self.cell.shapes(layer_idx).insert(region)

# 2. Bent Beam Actuator
class BentBeamPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(BentBeamPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("w", self.TypeDouble, "Beam Width (um)", default = 2.0)
        self.param("l", self.TypeDouble, "Beam Length (um)", default = 100.0)
        self.param("tilt", self.TypeDouble, "Tilt Angle (degrees)", default = 2.0)
        self.param("anchor_l", self.TypeDouble, "Anchor Length (um)", default = 10.0)
        self.param("anchor_w", self.TypeDouble, "Anchor Width (um)", default = 20.0)

    def display_text_impl(self):
        return f"BentBeam(L={self.l:.1f}um, Tilt={self.tilt:.1f}deg)"

    def coerce_parameters_impl(self):
        if self.w <= 0: self.w = 0.5
        if self.l <= 10.0: self.l = 10.0
        if self.tilt < 0: self.tilt = 0.0
        elif self.tilt > 45: self.tilt = 45.0
        if self.anchor_l <= 0: self.anchor_l = 1.0
        if self.anchor_w <= 0: self.anchor_w = 2.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        tilt_rad = math.radians(self.tilt)
        apex_y = (self.l / 2.0) * math.tan(tilt_rad)
        
        left_anchor = pya.Box(
            int((-self.l/2.0 - self.anchor_l) / dbu), int(-self.anchor_w / 2.0 / dbu),
            int(-self.l/2.0 / dbu), int(self.anchor_w / 2.0 / dbu)
        )
        right_anchor = pya.Box(
            int(self.l/2.0 / dbu), int(-self.anchor_w / 2.0 / dbu),
            int((self.l/2.0 + self.anchor_l) / dbu), int(self.anchor_w / 2.0 / dbu)
        )
        
        path_l = pya.Path([pya.Point(int(-self.l/2.0 / dbu), 0), pya.Point(0, int(apex_y / dbu))], int(self.w / dbu))
        path_r = pya.Path([pya.Point(0, int(apex_y / dbu)), pya.Point(int(self.l/2.0 / dbu), 0)], int(self.w / dbu))
        
        region = pya.Region()
        region.insert(left_anchor)
        region.insert(right_anchor)
        region.insert(path_l.simple_polygon())
        region.insert(path_r.simple_polygon())
        
        self.cell.shapes(layer_idx).insert(region)

# 3. Comb Drive
class CombDrivePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CombDrivePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("n_fingers", self.TypeInt, "Number of fingers", default = 10)
        self.param("finger_l", self.TypeDouble, "Finger Length (um)", default = 20.0)
        self.param("finger_w", self.TypeDouble, "Finger Width (um)", default = 2.0)
        self.param("finger_g", self.TypeDouble, "Finger Gap (um)", default = 2.0)
        self.param("spine_w", self.TypeDouble, "Spine Width (um)", default = 4.0)
        self.param("overlap", self.TypeDouble, "Initial Overlap (um)", default = 5.0)

    def display_text_impl(self):
        return f"CombDrive(N={self.n_fingers}, Overlap={self.overlap:.1f}um)"

    def coerce_parameters_impl(self):
        if self.n_fingers < 1: self.n_fingers = 1
        if self.finger_l <= 0: self.finger_l = 1.0
        if self.finger_w <= 0: self.finger_w = 0.1
        if self.finger_g <= 0: self.finger_g = 0.1
        if self.spine_w <= 0: self.spine_w = 0.5
        if self.overlap < 0: self.overlap = 0.0
        elif self.overlap >= self.finger_l: self.overlap = self.finger_l - 0.5

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        pitch = self.finger_w + self.finger_g
        comb_h = self.n_fingers * pitch
        region = pya.Region()
        
        stator_spine = pya.Box(
            int(-self.spine_w / dbu), int(-comb_h / 2.0 / dbu),
            0, int(comb_h / 2.0 / dbu)
        )
        region.insert(stator_spine)
        
        for i in range(self.n_fingers):
            y_center = -comb_h / 2.0 + (i + 0.25) * pitch
            finger = pya.Box(
                0, int((y_center - self.finger_w/2.0) / dbu),
                int(self.finger_l / dbu), int((y_center + self.finger_w/2.0) / dbu)
            )
            region.insert(finger)
            
        x_rotor_start = self.finger_l - self.overlap
        rotor_spine = pya.Box(
            int(x_rotor_start / dbu), int(-comb_h / 2.0 / dbu),
            int((x_rotor_start + self.spine_w) / dbu), int(comb_h / 2.0 / dbu)
        )
        region.insert(rotor_spine)
        
        for i in range(self.n_fingers):
            y_center = -comb_h / 2.0 + (i + 0.75) * pitch
            finger = pya.Box(
                int((x_rotor_start - self.finger_l) / dbu), int((y_center - self.finger_w/2.0) / dbu),
                int(x_rotor_start / dbu), int((y_center + self.finger_w/2.0) / dbu)
            )
            region.insert(finger)
            
        self.cell.shapes(layer_idx).insert(region)

# 4. Folded Spring
class FoldedSpringPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(FoldedSpringPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("w", self.TypeDouble, "Beam Width (um)", default = 1.5)
        self.param("l", self.TypeDouble, "Beam Length (um)", default = 80.0)
        self.param("spacing", self.TypeDouble, "Fold Spacing (um)", default = 4.0)
        self.param("anchor_s", self.TypeDouble, "Anchor Size (um)", default = 10.0)

    def display_text_impl(self):
        return f"FoldedSpring(L={self.l:.1f}um)"

    def coerce_parameters_impl(self):
        if self.w <= 0: self.w = 0.1
        if self.l <= 0: self.l = 5.0
        if self.spacing <= self.w: self.spacing = self.w + 1.0
        if self.anchor_s <= 0: self.anchor_s = 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        region = pya.Region()
        
        b1 = pya.Box(
            int(-self.w/2.0 / dbu), 0,
            int(self.w/2.0 / dbu), int(self.l / dbu)
        )
        b2 = pya.Box(
            int((self.spacing - self.w/2.0) / dbu), 0,
            int((self.spacing + self.w/2.0) / dbu), int(self.l / dbu)
        )
        conn = pya.Box(
            int(-self.w/2.0 / dbu), int((self.l - self.w/2.0) / dbu),
            int((self.spacing + self.w/2.0) / dbu), int((self.l + self.w/2.0) / dbu)
        )
        anchor_fixed = pya.Box(
            int(-self.anchor_s/2.0 / dbu), int(-self.anchor_s / dbu),
            int(self.anchor_s/2.0 / dbu), 0
        )
        anchor_movable = pya.Box(
            int((self.spacing - self.anchor_s/2.0) / dbu), int(-self.anchor_s / dbu),
            int((self.spacing + self.anchor_s/2.0) / dbu), 0
        )
        
        region.insert(b1)
        region.insert(b2)
        region.insert(conn)
        region.insert(anchor_fixed)
        region.insert(anchor_movable)
        
        self.cell.shapes(layer_idx).insert(region)

# 5. Gear
class GearPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(GearPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("r_outer", self.TypeDouble, "Outer Radius (um)", default = 20.0)
        self.param("r_inner", self.TypeDouble, "Inner Hole Radius (um)", default = 5.0)
        self.param("n_teeth", self.TypeInt, "Number of Teeth", default = 20)
        self.param("tooth_depth", self.TypeDouble, "Tooth Depth (um)", default = 3.0)

    def display_text_impl(self):
        return f"Gear(R={self.r_outer:.1f}um, Teeth={self.n_teeth})"

    def coerce_parameters_impl(self):
        if self.r_outer <= 0: self.r_outer = 2.0
        if self.r_inner < 0: self.r_inner = 0.0
        elif self.r_inner >= self.r_outer: self.r_inner = self.r_outer - 1.0
        if self.n_teeth < 3: self.n_teeth = 3
        if self.tooth_depth < 0: self.tooth_depth = 0.0
        elif self.tooth_depth >= self.r_outer: self.tooth_depth = self.r_outer / 2.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        pts = []
        
        for i in range(self.n_teeth):
            angle_start = i * 2.0 * math.pi / self.n_teeth
            angle_mid1 = angle_start + 0.25 * 2.0 * math.pi / self.n_teeth
            angle_mid2 = angle_start + 0.5 * 2.0 * math.pi / self.n_teeth
            angle_end = angle_start + 0.75 * 2.0 * math.pi / self.n_teeth
            
            r_top = self.r_outer
            r_bottom = self.r_outer - self.tooth_depth
            
            pts.append(pya.Point(int(r_top * math.cos(angle_start) / dbu), int(r_top * math.sin(angle_start) / dbu)))
            pts.append(pya.Point(int(r_top * math.cos(angle_mid1) / dbu), int(r_top * math.sin(angle_mid1) / dbu)))
            pts.append(pya.Point(int(r_bottom * math.cos(angle_mid2) / dbu), int(r_bottom * math.sin(angle_mid2) / dbu)))
            pts.append(pya.Point(int(r_bottom * math.cos(angle_end) / dbu), int(r_bottom * math.sin(angle_end) / dbu)))
            
        poly = pya.Polygon(pts)
        
        if self.r_inner > 0:
            hole_pts = []
            npoints_hole = 64
            for i in range(npoints_hole):
                angle = i * 2.0 * math.pi / npoints_hole
                hole_pts.append(pya.Point(int(self.r_inner * math.cos(angle) / dbu), int(self.r_inner * math.sin(angle) / dbu)))
            poly.insert_hole(hole_pts)
            
        self.cell.shapes(layer_idx).insert(poly)

# 6. Radial Comb Drive (Helper Functions and Class)
def make_rotated_rect(dbu, start_r, end_r, angle_rad, width):
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    ax, ay = start_r * cos_a, start_r * sin_a
    bx, by = end_r * cos_a, end_r * sin_a
    nx, ny = -sin_a * (width / 2.0), cos_a * (width / 2.0)
    
    pts = [
        pya.Point(int((ax + nx) / dbu), int((ay + ny) / dbu)),
        pya.Point(int((ax - nx) / dbu), int((ay - ny) / dbu)),
        pya.Point(int((bx - nx) / dbu), int((by - ny) / dbu)),
        pya.Point(int((bx + nx) / dbu), int((by + ny) / dbu))
    ]
    return pya.Polygon(pts)

def draw_torus_arc(dbu, r_center, width, start_deg, end_deg, num_sides):
    r_out = r_center + width / 2.0
    r_in = r_center - width / 2.0
    
    angle_span_deg = abs(end_deg - start_deg)
    num_pts = max(4, int(num_sides * angle_span_deg / 360.0))
    
    start_rad = math.radians(start_deg)
    end_rad = math.radians(end_deg)
    sweep_rad = end_rad - start_rad
    
    pts = []
    for i in range(num_pts + 1):
        angle = start_rad + (i / num_pts) * sweep_rad
        pts.append(pya.Point(int(r_out * math.cos(angle) / dbu), int(r_out * math.sin(angle) / dbu)))
        
    for i in range(num_pts, -1, -1):
        angle = start_rad + (i / num_pts) * sweep_rad
        pts.append(pya.Point(int(r_in * math.cos(angle) / dbu), int(r_in * math.sin(angle) / dbu)))
        
    return pya.Polygon(pts)

def draw_radial_comb_v1_shapes(layout, w1, r1, w2, r2, wc, gap, numElements, numSides, thetaALL, thetaOverlap, anchorDistance):
    dbu = layout.dbu
    region = pya.Region()
    anchor_region = pya.Region()
    
    thetaPrime = abs(thetaALL - thetaOverlap) / 2.0
    totalLengthUpper = (2 * numElements - 1) * wc + 2 * (numElements - 1) * gap
    totalLengthLower = 2 * (numElements - 1) * wc + 2 * (numElements - 1) * gap
    
    # 1. Lower horizontal spine (at angle 0)
    x_start = int(r2 / dbu)
    x_end = int((r1 + totalLengthLower - gap) / dbu)
    y_half = int((w2 / 2.0) / dbu)
    region.insert(pya.Box(x_start, -y_half, x_end, y_half))
    
    # 2. Upper arm (at angle thetaALL)
    theta_rad = math.radians(thetaALL)
    upper_arm = make_rotated_rect(dbu, r1, r1 + totalLengthUpper, theta_rad, w1)
    region.insert(upper_arm)
    
    # 3. Stator fingers (attached to upper arm)
    start_deg_stator = thetaALL - thetaPrime - thetaOverlap
    end_deg_stator = thetaALL
    for i in range(numElements):
        r_finger = r1 + wc / 2.0 + i * (2.0 * wc + 2.0 * gap)
        finger_poly = draw_torus_arc(dbu, r_finger, wc, start_deg_stator, end_deg_stator, numSides)
        region.insert(finger_poly)
        
    # 4. Rotor fingers (attached to lower spine)
    start_deg_rotor = 0.0
    end_deg_rotor = thetaPrime + thetaOverlap
    for i in range(numElements - 1):
        r_finger = r1 + wc / 2.0 + gap + wc + i * (2.0 * wc + 2.0 * gap)
        finger_poly = draw_torus_arc(dbu, r_finger, wc, start_deg_rotor, end_deg_rotor, numSides)
        region.insert(finger_poly)
        
    # 5. Upper arm anchor
    anchor_width = w1 - 2.0 * anchorDistance
    if anchor_width > 0:
        anchor_poly = make_rotated_rect(dbu, r1 + anchorDistance, r1 + totalLengthUpper - anchorDistance, theta_rad, anchor_width)
        anchor_region.insert(anchor_poly)
        
    return region, anchor_region

def draw_radial_comb_v2_shapes(layout, w1, r1, w2, r2, wc, gap, numElements, numSides, thetaALL, thetaOverlap, anchorDistance):
    # Base V1 shapes
    region, anchor_region = draw_radial_comb_v1_shapes(
        layout, w1, r1, w2, r2, wc, gap, numElements, numSides, thetaALL, thetaOverlap, anchorDistance
    )
    
    # Mirror across x-axis
    mirror_trans = pya.Trans(pya.Trans.M0)
    
    region_mirrored = region.dup()
    region_mirrored.transform(mirror_trans)
    region.insert(region_mirrored)
    
    anchor_mirrored = anchor_region.dup()
    anchor_mirrored.transform(mirror_trans)
    anchor_region.insert(anchor_mirrored)
    
    return region, anchor_region

def draw_circular_spring(layout, layer_idx, anchor_layer_idx, width, radiusCenterHub, widthRing, radiusRing, numSides, numElements, anchorDistance):
    dbu = layout.dbu
    region = pya.Region()
    
    # 1. Inner Hub disk
    hub_pts = []
    for i in range(numSides):
        angle = i * 2.0 * math.pi / numSides
        hub_pts.append(pya.Point(int(radiusCenterHub * math.cos(angle) / dbu), int(radiusCenterHub * math.sin(angle) / dbu)))
    region.insert(pya.Polygon(hub_pts))
    
    # 2. Outer Ring Torus
    r_outer_ring_in = radiusRing - widthRing / 2.0
    r_outer_ring_out = radiusRing + widthRing / 2.0
    ring_pts = []
    for i in range(numSides):
        angle = i * 2.0 * math.pi / numSides
        ring_pts.append(pya.Point(int(r_outer_ring_out * math.cos(angle) / dbu), int(r_outer_ring_out * math.sin(angle) / dbu)))
    ring_poly = pya.Polygon(ring_pts)
    
    ring_hole_pts = []
    for i in range(numSides):
        angle = i * 2.0 * math.pi / numSides
        ring_hole_pts.append(pya.Point(int(r_outer_ring_in * math.cos(angle) / dbu), int(r_outer_ring_in * math.sin(angle) / dbu)))
    ring_poly.insert_hole(ring_hole_pts)
    region.insert(ring_poly)
    
    # 3. Curved Spokes
    rad_beam = (radiusRing - (radiusCenterHub - width / 2.0)) / 2.0
    r_beam_in = rad_beam - width / 2.0
    r_beam_out = rad_beam + width / 2.0
    
    # Semicircle torus segment (0 to 180 degrees)
    beam_pts = []
    n_beam_pts = numSides // 2
    for i in range(n_beam_pts + 1):
        angle = i * math.pi / n_beam_pts
        beam_pts.append(pya.Point(int(r_beam_out * math.cos(angle) / dbu), int(r_beam_out * math.sin(angle) / dbu)))
    for i in range(n_beam_pts, -1, -1):
        angle = i * math.pi / n_beam_pts
        beam_pts.append(pya.Point(int(r_beam_in * math.cos(angle) / dbu), int(r_beam_in * math.sin(angle) / dbu)))
        
    shift_x = int((radiusRing - rad_beam) / dbu)
    shifted_beam_pts = [pya.Point(pt.x + shift_x, pt.y) for pt in beam_pts]
    
    for i in range(numElements):
        rot_angle = (i * 2.0) * math.pi / numElements
        cos_a = math.cos(rot_angle)
        sin_a = math.sin(rot_angle)
        
        rotated_pts = []
        for pt in shifted_beam_pts:
            rx = pt.x * cos_a - pt.y * sin_a
            ry = pt.x * sin_a + pt.y * cos_a
            rotated_pts.append(pya.Point(int(rx), int(ry)))
        region.insert(pya.Polygon(rotated_pts))
        
    # 4. Anchor disk
    anchor_region = pya.Region()
    r_anchor = radiusCenterHub - anchorDistance
    anchor_pts = []
    for i in range(numSides):
        angle = i * 2.0 * math.pi / numSides
        anchor_pts.append(pya.Point(int(r_anchor * math.cos(angle) / dbu), int(r_anchor * math.sin(angle) / dbu)))
    anchor_region.insert(pya.Polygon(anchor_pts))
    
    return region, anchor_region

def draw_radial_comb_hub(layout, layer_idx, anchor_layer_idx,
                           spring_w, spring_r_hub, spring_w_ring, spring_r_ring, spring_n_sides, spring_n_spokes, spring_anchor_dist,
                           comb_w1, comb_r1, comb_w2, comb_r2, comb_wc, comb_gap, comb_n_fingers, comb_n_sides, comb_theta_comb, comb_theta_overlap, comb_anchor_dist):
    dbu = layout.dbu
    # 1. Circular spring at origin
    region, anchor_region = draw_circular_spring(
        layout, layer_idx, anchor_layer_idx,
        spring_w, spring_r_hub, spring_w_ring, spring_r_ring,
        spring_n_sides, spring_n_spokes, spring_anchor_dist
    )
    
    # 2. Base comb at origin
    comb_reg, comb_anc = draw_radial_comb_v2_shapes(
        layout, comb_w1, comb_r1, comb_w2, comb_r2, comb_wc, comb_gap,
        comb_n_fingers, comb_n_sides, comb_theta_comb, comb_theta_overlap,
        comb_anchor_dist
    )
    
    # Place 4 mirrored radial combs at 0, 90, 180, 270 degrees
    comb_offset = spring_r_ring - comb_r2
    
    for angle_deg in [0, 90, 180, 270]:
        angle_rad = math.radians(angle_deg)
        tx = comb_offset * math.cos(angle_rad)
        ty = comb_offset * math.sin(angle_rad)
        
        rot_map = {0: pya.Trans.R0, 90: pya.Trans.R90, 180: pya.Trans.R180, 270: pya.Trans.R270}
        trans = pya.Trans(rot_map[angle_deg], int(tx / dbu), int(ty / dbu))
        
        c_reg = comb_reg.dup()
        c_reg.transform(trans)
        region.insert(c_reg)
        
        c_anc = comb_anc.dup()
        c_anc.transform(trans)
        anchor_region.insert(c_anc)
        
    return region, anchor_region

class RadialCombDrivePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(RadialCombDrivePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(4, 0))
        self.param("w1", self.TypeDouble, "Upper Arm Width (um)", default = 4.0)
        self.param("r1", self.TypeDouble, "Upper Arm Start Radius (um)", default = 40.0)
        self.param("w2", self.TypeDouble, "Lower Spine Width (um)", default = 1.0)
        self.param("r2", self.TypeDouble, "Lower Spine Start Radius (um)", default = 30.0)
        self.param("wc", self.TypeDouble, "Finger Width (um)", default = 1.1)
        self.param("gap", self.TypeDouble, "Finger Gap (um)", default = 2.2)
        self.param("n_fingers", self.TypeInt, "Number of fingers", default = 10)
        self.param("n_sides", self.TypeInt, "Rendering Resolution", default = 32)
        self.param("theta_comb", self.TypeDouble, "Arm Angle Span (deg)", default = 40.0)
        self.param("theta_overlap", self.TypeDouble, "Finger Overlap Angle (deg)", default = 20.0)
        self.param("anchor_dist", self.TypeDouble, "Anchor Inset (um)", default = 1.0)
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(7, 0))

    def display_text_impl(self):
        return f"RadialComb(r1={self.r1:.1f}um, r2={self.r2:.1f}um, N={self.n_fingers})"

    def coerce_parameters_impl(self):
        if self.w1 < 0.1: self.w1 = 0.1
        if self.r1 < 1.0: self.r1 = 1.0
        if self.w2 < 0.1: self.w2 = 0.1
        if self.r2 < 1.0: self.r2 = 1.0
        if self.wc < 0.1: self.wc = 0.1
        if self.gap < 0.1: self.gap = 0.1
        if self.n_fingers < 1: self.n_fingers = 1
        if self.n_sides < 4: self.n_sides = 4
        if self.theta_comb < 1.0: self.theta_comb = 1.0
        elif self.theta_comb > 179.0: self.theta_comb = 179.0
        if self.theta_overlap < 0.0: self.theta_overlap = 0.0
        elif self.theta_overlap >= self.theta_comb: self.theta_overlap = self.theta_comb - 1.0
        if self.anchor_dist < 0.0: self.anchor_dist = 0.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        anchor_layer_idx = self.layout.layer(self.anchor_layer)
        
        region, anchor_region = draw_radial_comb_v2_shapes(
            self.layout, self.w1, self.r1, self.w2, self.r2, self.wc, self.gap,
            self.n_fingers, self.n_sides, self.theta_comb, self.theta_overlap,
            self.anchor_dist
        )
        
        self.cell.shapes(layer_idx).insert(region)
        self.cell.shapes(anchor_layer_idx).insert(anchor_region)

class CircularSpringPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CircularSpringPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(4, 0))
        self.param("w", self.TypeDouble, "Spoke/Beam Width (um)", default = 1.0)
        self.param("r_hub", self.TypeDouble, "Inner Hub Radius (um)", default = 4.0)
        self.param("w_ring", self.TypeDouble, "Outer Ring Width (um)", default = 3.4)
        self.param("r_ring", self.TypeDouble, "Outer Ring Radius (um)", default = 40.0)
        self.param("n_sides", self.TypeInt, "Rendering Resolution", default = 128)
        self.param("n_spokes", self.TypeInt, "Number of Spokes", default = 18)
        self.param("anchor_dist", self.TypeDouble, "Anchor Inset (um)", default = 0.2)
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(7, 0))

    def display_text_impl(self):
        return f"CircSpring(R={self.r_ring:.1f}um, Spokes={self.n_spokes})"

    def coerce_parameters_impl(self):
        if self.w < 0.1: self.w = 0.1
        if self.r_hub < 1.0: self.r_hub = 1.0
        if self.w_ring < 0.1: self.w_ring = 0.1
        if self.r_ring <= self.r_hub + self.w_ring: self.r_ring = self.r_hub + self.w_ring + 5.0
        if self.n_sides < 8: self.n_sides = 8
        if self.n_spokes < 2: self.n_spokes = 2
        if self.anchor_dist < 0.0: self.anchor_dist = 0.0
        elif self.anchor_dist >= self.r_hub: self.anchor_dist = self.r_hub - 0.5

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        anchor_layer_idx = self.layout.layer(self.anchor_layer)
        
        region, anchor_region = draw_circular_spring(
            self.layout, layer_idx, anchor_layer_idx,
            self.w, self.r_hub, self.w_ring, self.r_ring,
            self.n_sides, self.n_spokes, self.anchor_dist
        )
        
        self.cell.shapes(layer_idx).insert(region)
        self.cell.shapes(anchor_layer_idx).insert(anchor_region)

class RadialCombDriveHubPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(RadialCombDriveHubPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(4, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(7, 0))
        
        # Spring parameters
        self.param("spring_w", self.TypeDouble, "Spring Spoke Width (um)", default = 1.0)
        self.param("spring_r_hub", self.TypeDouble, "Spring Inner Hub Radius (um)", default = 4.0)
        self.param("spring_w_ring", self.TypeDouble, "Spring Outer Ring Width (um)", default = 3.4)
        self.param("spring_r_ring", self.TypeDouble, "Spring Outer Ring Radius (um)", default = 40.0)
        self.param("spring_n_sides", self.TypeInt, "Spring Resolution", default = 128)
        self.param("spring_n_spokes", self.TypeInt, "Spring Spokes Count", default = 18)
        self.param("spring_anchor_dist", self.TypeDouble, "Spring Anchor Inset (um)", default = 0.2)
        
        # Comb parameters
        self.param("comb_w1", self.TypeDouble, "Comb Upper Arm Width (um)", default = 4.0)
        self.param("comb_r1", self.TypeDouble, "Comb Upper Arm Start Rad (um)", default = 40.0)
        self.param("comb_w2", self.TypeDouble, "Comb Lower Spine Width (um)", default = 1.0)
        self.param("comb_r2", self.TypeDouble, "Comb Lower Spine Start Rad (um)", default = 30.0)
        self.param("comb_wc", self.TypeDouble, "Comb Finger Width (um)", default = 1.1)
        self.param("comb_gap", self.TypeDouble, "Comb Finger Gap (um)", default = 2.2)
        self.param("comb_n_fingers", self.TypeInt, "Comb Fingers Count", default = 10)
        self.param("comb_n_sides", self.TypeInt, "Comb Resolution", default = 32)
        self.param("comb_theta_comb", self.TypeDouble, "Comb Arm Angle Span (deg)", default = 40.0)
        self.param("comb_theta_overlap", self.TypeDouble, "Comb Overlap Angle (deg)", default = 20.0)
        self.param("comb_anchor_dist", self.TypeDouble, "Comb Anchor Inset (um)", default = 1.0)

    def display_text_impl(self):
        return f"CombDriveHub(R={self.spring_r_ring:.1f}um, Fingers={self.comb_n_fingers})"

    def coerce_parameters_impl(self):
        # Coerce spring parameters
        if self.spring_w < 0.1: self.spring_w = 0.1
        if self.spring_r_hub < 1.0: self.spring_r_hub = 1.0
        if self.spring_w_ring < 0.1: self.spring_w_ring = 0.1
        if self.spring_r_ring <= self.spring_r_hub + self.spring_w_ring: self.spring_r_ring = self.spring_r_hub + self.spring_w_ring + 5.0
        if self.spring_n_sides < 8: self.spring_n_sides = 8
        if self.spring_n_spokes < 2: self.spring_n_spokes = 2
        if self.spring_anchor_dist < 0.0: self.spring_anchor_dist = 0.0
        elif self.spring_anchor_dist >= self.spring_r_hub: self.spring_anchor_dist = self.spring_r_hub - 0.5
        
        # Coerce comb parameters
        if self.comb_w1 < 0.1: self.comb_w1 = 0.1
        if self.comb_r1 < 1.0: self.comb_r1 = 1.0
        if self.comb_w2 < 0.1: self.comb_w2 = 0.1
        if self.comb_r2 < 1.0: self.comb_r2 = 1.0
        if self.comb_wc < 0.1: self.comb_wc = 0.1
        if self.comb_gap < 0.1: self.comb_gap = 0.1
        if self.comb_n_fingers < 1: self.comb_n_fingers = 1
        if self.comb_n_sides < 4: self.comb_n_sides = 4
        if self.comb_theta_comb < 1.0: self.comb_theta_comb = 1.0
        elif self.comb_theta_comb > 179.0: self.comb_theta_comb = 179.0
        if self.comb_theta_overlap < 0.0: self.comb_theta_overlap = 0.0
        elif self.comb_theta_overlap >= self.comb_theta_comb: self.comb_theta_overlap = self.comb_theta_comb - 1.0
        if self.comb_anchor_dist < 0.0: self.comb_anchor_dist = 0.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        anchor_layer_idx = self.layout.layer(self.anchor_layer)
        
        region, anchor_region = draw_radial_comb_hub(
            self.layout, layer_idx, anchor_layer_idx,
            self.spring_w, self.spring_r_hub, self.spring_w_ring, self.spring_r_ring, self.spring_n_sides, self.spring_n_spokes, self.spring_anchor_dist,
            self.comb_w1, self.comb_r1, self.comb_w2, self.comb_r2, self.comb_wc, self.comb_gap, self.comb_n_fingers, self.comb_n_sides,
            self.comb_theta_comb, self.comb_theta_overlap, self.comb_anchor_dist
        )
        
        self.cell.shapes(layer_idx).insert(region)
        self.cell.shapes(anchor_layer_idx).insert(anchor_region)


# =====================================================================
# LIBRARY REGISTRATION
# =====================================================================

# 1. Register NIST_LithoToolbox
class NISTLithoToolboxLibrary(pya.Library):
    def __init__(self):
        self.description = "NIST Lithography and Nanophotonics PCells"
        
        self.layout().register_pcell("1_Grating", GratingPCell())
        self.layout().register_pcell("2_Ring_Disk", RingPCell())
        self.layout().register_pcell("3_Bezier_Taper", BezierTaperPCell())
        self.layout().register_pcell("4_Alignment_Mark", AlignmentMarkPCell())
        self.layout().register_pcell("5_Vernier_Caliper", VernierCaliperPCell())
        self.layout().register_pcell("6_Photonic_Crystal", PhotonicCrystalPCell())
        self.layout().register_pcell("7_Y_Splitter", YSplitterPCell())
        self.layout().register_pcell("8_Star", StarPCell())
        self.layout().register_pcell("9_L_Shape", LShapePCell())
        self.layout().register_pcell("9a_Rounded_Rectangle", RoundedRectanglePCell())
        self.layout().register_pcell("9b_Torus_Arc", TorusPCell())
        
        # Extended Lithography PCells from cnst_extended_pcells
        self.layout().register_pcell("9c_Torus_Wave", cep.TorusWavePCell())
        self.layout().register_pcell("10_Rectangular_Array", cep.RectangularArrayPCell())
        self.layout().register_pcell("11_Hexagonal_Array", cep.HexagonalArrayPCell())
        self.layout().register_pcell("12_Polar_Array", cep.PolarArrayPCell())
        self.layout().register_pcell("13_Fractals", cep.FractalPCell())
        self.layout().register_pcell("14_Grayscale", cep.GrayscalePCell())
        self.layout().register_pcell("15_Interdigitated_Electrodes", cep.InterdigitatedElectrodesPCell())
        self.layout().register_pcell("16_Resolution_Test_Pattern", cep.ResolutionTestPatternPCell())
        self.layout().register_pcell("17_Spirals", cep.SpiralsPCell())
        self.layout().register_pcell("18_Rectangular_Spiral", cep.RectangularSpiralPCell())
        self.layout().register_pcell("19_Alignment_Marks_Custom", cep.AlignmentMarksCustomPCell())
        self.layout().register_pcell("20_Reticle_Barcode_Frame", cep.ReticleBarcodeFramePCell())
        self.layout().register_pcell("21_Vernier", cep.VernierPCell())
        self.layout().register_pcell("22_Vernier_With_Labels", cep.VernierWithLabelsPCell())
        self.layout().register_pcell("23_Exponential_Taper", cep.ExponentialTaperPCell())
        self.layout().register_pcell("24_S_Bend_Funnel", cep.SBendFunnelPCell())
        self.layout().register_pcell("25_Bend_180_Degree_Inverse", cep.Bend180DegreeInversePCell())
        self.layout().register_pcell("26_Racetrack", cep.RacetrackPCell())
        self.layout().register_pcell("27_Spiral_Delay_Line", cep.SpiralDelayLinePCell())
        self.layout().register_pcell("28_Inverse_Spiral_Delay_Line", cep.InverseSpiralDelayLinePCell())
        self.layout().register_pcell("29_Apodized_Grating", cep.ApodizedGratingPCell())
        self.layout().register_pcell("30_Grating_Coupler", cep.GratingCouplerPCell())
        self.layout().register_pcell("31_Grating_Coupler_With_Waveguide", cep.GratingCouplerWithWaveguidePCell())
        
        self.register("NIST_LithoToolbox")

# 2. Register NIST_MEMS_NEMS
class NISTMEMSNEMSLibrary(pya.Library):
    def __init__(self):
        self.description = "NIST MEMS and NEMS PCells"
        
        self.layout().register_pcell("1_Cantilever", CantileverPCell())
        self.layout().register_pcell("2_Bent_Beam_Actuator", BentBeamPCell())
        self.layout().register_pcell("3_Comb_Drive", CombDrivePCell())
        self.layout().register_pcell("4_Folded_Spring", FoldedSpringPCell())
        self.layout().register_pcell("5_Gear", GearPCell())
        self.layout().register_pcell("6_Radial_Comb_Drive", RadialCombDrivePCell())
        self.layout().register_pcell("7_Circular_Spring", CircularSpringPCell())
        self.layout().register_pcell("8_Radial_Comb_Drive_Hub", RadialCombDriveHubPCell())
        
        # New MEMS/NEMS PCells from cnst_extended_pcells
        self.layout().register_pcell("9_BiMorph_Thermal_Actuator", cep.BiMorphThermalActuatorPCell())
        self.layout().register_pcell("10_Bolometer", cep.BolometerPCell())
        self.layout().register_pcell("11_Anchored_Flexures", cep.AnchoredFlexuresPCell())
        self.layout().register_pcell("12_Cantilever_CE_Paddle", cep.CantileverCEPaddlePCell())
        self.layout().register_pcell("13_dcBeam_Rectangular", cep.dcBeamRPCell())
        self.layout().register_pcell("14_dcBeam_Torsional", cep.dcBeamTorsionalPCell())
        self.layout().register_pcell("15_dcBeam_Coupled_Array", cep.dcBeamCoupledBeamsPCell())
        self.layout().register_pcell("16_dcBeam_Corner_Fillets", cep.dcBeamCPCell())
        self.layout().register_pcell("17_Guckel_Rings", cep.GuckelRingPCell())
        self.layout().register_pcell("18_Diamond_Ring", cep.DiamondRingPCell())
        self.layout().register_pcell("19_Suspended_Fluid_Cell", cep.SuspendedFluidCellPCell())
        
        self.register("NIST_MEMS_NEMS")

# Instantiate libraries to load them on KLayout startup
NISTLithoToolboxLibrary()
NISTMEMSNEMSLibrary()
