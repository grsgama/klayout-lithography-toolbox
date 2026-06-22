import pya
import math
import cnst_extended as ex

# =====================================================================
# PCell Declarations for NIST Extended Library
# =====================================================================

# 1. Torus with a Wave Boundary
class TorusWavePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(TorusWavePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("rad_in", self.TypeDouble, "Inner Radius (um)", default = 10.0)
        self.param("rad_out", self.TypeDouble, "Outer Radius (um)", default = 15.0)
        self.param("n", self.TypeInt, "Number of waves", default = 8)
        self.param("amp", self.TypeDouble, "Wave Amplitude (um)", default = 1.0)
        self.param("num_sides", self.TypeInt, "Rendering Resolution", default = 128)
        self.param("out_of_phase", self.TypeBoolean, "Out of phase (pi/2)", default = False)

    def display_text_impl(self):
        return f"TorusWave(R_in={self.rad_in:.1f}, R_out={self.rad_out:.1f})"

    def coerce_parameters_impl(self):
        if self.rad_in <= 0: self.rad_in = 0.5
        if self.rad_out <= self.rad_in: self.rad_out = self.rad_in + 1.0
        if self.n < 1: self.n = 1
        if self.amp < 0: self.amp = 0.0
        if self.num_sides < 8: self.num_sides = 8

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        poly = ex.draw_torus_wave(self.layout, self.rad_in, self.rad_out, self.n, self.amp, self.num_sides, self.out_of_phase)
        self.cell.shapes(layer_idx).insert(poly)

# 2. Rectangular Arrays
class RectangularArrayPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(RectangularArrayPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("cell_name", self.TypeString, "Cell Name to Array", default = "target_cell")
        self.param("nx", self.TypeInt, "Columns (X)", default = 5)
        self.param("ny", self.TypeInt, "Rows (Y)", default = 5)
        self.param("dx", self.TypeDouble, "Pitch X (um)", default = 10.0)
        self.param("dy", self.TypeDouble, "Pitch Y (um)", default = 10.0)
        self.param("x_offset", self.TypeDouble, "Offset X (um)", default = 0.0)
        self.param("y_offset", self.TypeDouble, "Offset Y (um)", default = 0.0)
        self.param("fallback_shape", self.TypeString, "Fallback Shape", default = "Square", choices = [["Square", "Square"], ["Circle", "Circle"], ["Cross", "Cross"], ["None", "None"]])
        self.param("fallback_w", self.TypeDouble, "Fallback Width (um)", default = 1.0)
        self.param("fallback_h", self.TypeDouble, "Fallback Height (um)", default = 1.0)

    def display_text_impl(self):
        return f"RectArray({self.cell_name}, {self.nx}x{self.ny})"

    def coerce_parameters_impl(self):
        if self.nx < 1: self.nx = 1
        if self.ny < 1: self.ny = 1
        if self.fallback_w < 0.01: self.fallback_w = 0.01
        if self.fallback_h < 0.01: self.fallback_h = 0.01

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        target = self.layout.cell(self.cell_name)
        if target:
            inst = pya.CellInstArray(target.cell_index(), pya.Trans(int(self.x_offset/dbu), int(self.y_offset/dbu)), 
                                      pya.Vector(int(self.dx/dbu), 0), pya.Vector(0, int(self.dy/dbu)), self.nx, self.ny)
            self.cell.insert(inst)
        elif self.fallback_shape != "None":
            # Fallback marker
            for ix in range(self.nx):
                for iy in range(self.ny):
                    cx = self.x_offset + ix * self.dx
                    cy = self.y_offset + iy * self.dy
                    if self.fallback_shape == "Square":
                        box = pya.Box(int((cx - self.fallback_w/2.0)/dbu), int((cy - self.fallback_h/2.0)/dbu),
                                      int((cx + self.fallback_w/2.0)/dbu), int((cy + self.fallback_h/2.0)/dbu))
                        self.cell.shapes(layer_idx).insert(box)
                    elif self.fallback_shape == "Circle":
                        poly = ex.draw_ellipse(dbu, cx, cy, self.fallback_w/2.0, self.fallback_h/2.0, 32)
                        self.cell.shapes(layer_idx).insert(poly)
                    elif self.fallback_shape == "Cross":
                        horiz = pya.Box(int((cx - self.fallback_w/2.0)/dbu), int((cy - self.fallback_h/10.0)/dbu),
                                        int((cx + self.fallback_w/2.0)/dbu), int((cy + self.fallback_h/10.0)/dbu))
                        vert = pya.Box(int((cx - self.fallback_w/10.0)/dbu), int((cy - self.fallback_h/2.0)/dbu),
                                       int((cx + self.fallback_w/10.0)/dbu), int((cy + self.fallback_h/2.0)/dbu))
                        self.cell.shapes(layer_idx).insert(horiz)
                        self.cell.shapes(layer_idx).insert(vert)

# 3. Hexagonal Arrays
class HexagonalArrayPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(HexagonalArrayPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("cell_name", self.TypeString, "Cell Name to Array", default = "target_cell")
        self.param("nx", self.TypeInt, "Columns (X)", default = 5)
        self.param("ny", self.TypeInt, "Rows (Y)", default = 5)
        self.param("dx", self.TypeDouble, "Pitch X (um)", default = 10.0)
        self.param("x_offset", self.TypeDouble, "Offset X (um)", default = 0.0)
        self.param("y_offset", self.TypeDouble, "Offset Y (um)", default = 0.0)
        self.param("fallback_shape", self.TypeString, "Fallback Shape", default = "Square", choices = [["Square", "Square"], ["Circle", "Circle"], ["Cross", "Cross"], ["None", "None"]])
        self.param("fallback_w", self.TypeDouble, "Fallback Width (um)", default = 1.0)
        self.param("fallback_h", self.TypeDouble, "Fallback Height (um)", default = 1.0)

    def display_text_impl(self):
        return f"HexArray({self.cell_name}, {self.nx}x{self.ny})"

    def coerce_parameters_impl(self):
        if self.nx < 1: self.nx = 1
        if self.ny < 1: self.ny = 1
        if self.dx <= 0: self.dx = 1.0
        if self.fallback_w < 0.01: self.fallback_w = 0.01
        if self.fallback_h < 0.01: self.fallback_h = 0.01

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        target = self.layout.cell(self.cell_name)
        dy = 2.0 * self.dx * math.cos(math.radians(30.0))
        
        for iy in range(self.ny):
            y_coord = self.y_offset + iy * dy
            x_shift = (self.dx / 2.0) if (iy % 2 == 1) else 0.0
            for ix in range(self.nx):
                x_coord = self.x_offset + ix * self.dx + x_shift
                if target:
                    inst = pya.CellInstArray(target.cell_index(), pya.Trans(int(x_coord/dbu), int(y_coord/dbu)))
                    self.cell.insert(inst)
                elif self.fallback_shape != "None":
                    cx, cy = x_coord, y_coord
                    if self.fallback_shape == "Square":
                        box = pya.Box(int((cx - self.fallback_w/2.0)/dbu), int((cy - self.fallback_h/2.0)/dbu),
                                      int((cx + self.fallback_w/2.0)/dbu), int((cy + self.fallback_h/2.0)/dbu))
                        self.cell.shapes(layer_idx).insert(box)
                    elif self.fallback_shape == "Circle":
                        poly = ex.draw_ellipse(dbu, cx, cy, self.fallback_w/2.0, self.fallback_h/2.0, 32)
                        self.cell.shapes(layer_idx).insert(poly)
                    elif self.fallback_shape == "Cross":
                        horiz = pya.Box(int((cx - self.fallback_w/2.0)/dbu), int((cy - self.fallback_h/10.0)/dbu),
                                        int((cx + self.fallback_w/2.0)/dbu), int((cy + self.fallback_h/10.0)/dbu))
                        vert = pya.Box(int((cx - self.fallback_w/10.0)/dbu), int((cy - self.fallback_h/2.0)/dbu),
                                       int((cx + self.fallback_w/10.0)/dbu), int((cy + self.fallback_h/2.0)/dbu))
                        self.cell.shapes(layer_idx).insert(horiz)
                        self.cell.shapes(layer_idx).insert(vert)


# 4. Polar Arrays
class PolarArrayPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(PolarArrayPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("cell_name", self.TypeString, "Cell Name to Array", default = "target_cell")
        self.param("radius_start", self.TypeDouble, "Radius Start (um)", default = 20.0)
        self.param("radius_end", self.TypeDouble, "Radius End (um)", default = 50.0)
        self.param("radius_inc", self.TypeDouble, "Radius Increment (um)", default = 10.0)
        self.param("angle_start", self.TypeDouble, "Angle Start (deg)", default = 0.0)
        self.param("angle_end", self.TypeDouble, "Angle End (deg)", default = 360.0)
        self.param("angle_inc", self.TypeDouble, "Angle Increment (deg)", default = 30.0)
        self.param("rotate_instance", self.TypeBoolean, "Rotate Instances", default = True)

    def display_text_impl(self):
        return f"PolarArray({self.cell_name})"

    def coerce_parameters_impl(self):
        if self.radius_start < 0: self.radius_start = 0.0
        if self.radius_end < self.radius_start: self.radius_end = self.radius_start
        if self.radius_inc <= 0: self.radius_inc = 1.0
        if self.angle_inc <= 0: self.angle_inc = 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        target = self.layout.cell(self.cell_name)
        
        num_radii = int((self.radius_end - self.radius_start) / self.radius_inc) + 1
        num_angles = int((self.angle_end - self.angle_start) / self.angle_inc) + 1
        
        for ir in range(num_radii):
            r = self.radius_start + ir * self.radius_inc
            for ia in range(num_angles):
                ang_deg = self.angle_start + ia * self.angle_inc
                ang_rad = math.radians(ang_deg)
                x = r * math.cos(ang_rad)
                y = r * math.sin(ang_rad)
                
                if target:
                    if self.rotate_instance:
                        # KLayout Trans handles rotations of 90/180/270 degrees natively.
                        # For arbitrary angles, we use pya.ICTrans.
                        trans = pya.ICTrans(1.0, ang_deg, False, int(x/dbu), int(y/dbu))
                        self.cell.insert(pya.CellInstArray(target.cell_index(), trans))
                    else:
                        inst = pya.CellInstArray(target.cell_index(), pya.Trans(int(x/dbu), int(y/dbu)))
                        self.cell.insert(inst)
                else:
                    box = pya.Box(int((x - 0.5)/dbu), int((y - 0.5)/dbu), int((x + 0.5)/dbu), int((y + 0.5)/dbu))
                    self.cell.shapes(layer_idx).insert(box)

# 5. Fractals (Sierpinski / Vicsek)
class FractalPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(FractalPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("style", self.TypeString, "Style (Sierpinski Carpet, Sierpinski Triangle, Vicsek Saltire, Vicsek Cross)", default = "Sierpinski Carpet")
        self.param("length", self.TypeDouble, "Length (um)", default = 50.0)
        self.param("iterations", self.TypeInt, "Iterations", default = 3)

    def display_text_impl(self):
        return f"Fractal({self.style}, Iter={self.iterations})"

    def coerce_parameters_impl(self):
        if self.length <= 0: self.length = 1.0
        if self.iterations < 0: self.iterations = 0
        elif self.iterations > 5: self.iterations = 5 # Avoid crash from exponential growth

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        region = pya.Region()
        
        if self.style == "Sierpinski Carpet":
            ex.draw_sierpinski_carpet(dbu, 0.0, 0.0, self.length, self.iterations, region)
        elif self.style == "Sierpinski Triangle":
            ex.draw_sierpinski_triangle(dbu, -self.length/2.0, -self.length/2.0, self.length, self.iterations, region)
        elif self.style == "Vicsek Saltire":
            ex.draw_vicsek_saltire(dbu, 0.0, 0.0, self.length, self.iterations, region)
        elif self.style == "Vicsek Cross":
            ex.draw_vicsek_cross(dbu, 0.0, 0.0, self.length, self.iterations, region)
            
        self.cell.shapes(layer_idx).insert(region)

# 6. Grayscale
class GrayscalePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(GrayscalePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Base Layer", default = pya.LayerInfo(1, 0))
        self.param("style", self.TypeString, "Style (Linear N-GON, Linear RECT, Ramp Up/Down, Ramp)", default = "Linear N-GON")
        self.param("rad_x", self.TypeDouble, "Radius X (um) / Length", default = 20.0)
        self.param("rad_y", self.TypeDouble, "Radius Y (um) / Height", default = 20.0)
        self.param("segments", self.TypeInt, "Number of Segments", default = 8)
        self.param("num_sides", self.TypeInt, "N-GON sides", default = 64)
        self.param("output_mode", self.TypeString, "Output Mode (Datatypes, Layers)", default = "Datatypes")

    def display_text_impl(self):
        return f"Grayscale({self.style}, Segments={self.segments})"

    def coerce_parameters_impl(self):
        if self.rad_x <= 0: self.rad_x = 1.0
        if self.rad_y <= 0: self.rad_y = 1.0
        if self.segments < 1: self.segments = 1
        elif self.segments > 256: self.segments = 256
        if self.num_sides < 3: self.num_sides = 3

    def produce_impl(self):
        dbu = self.layout.dbu
        base_layer = self.layer.layer
        base_datatype = self.layer.datatype
        
        for i in range(self.segments):
            # Calculate layer or datatype
            lyr_num = base_layer + (i if self.output_mode == "Layers" else 0)
            dt_num = base_datatype + (0 if self.output_mode == "Layers" else i)
            layer_idx = self.layout.layer(pya.LayerInfo(lyr_num, dt_num))
            
            region = pya.Region()
            if self.style == "Linear N-GON":
                # Concentric ellipses
                rx_outer = self.rad_x - i * (self.rad_x / self.segments)
                ry_outer = self.rad_y - i * (self.rad_y / self.segments)
                rx_inner = self.rad_x - (i + 1) * (self.rad_x / self.segments)
                ry_inner = self.rad_y - (i + 1) * (self.rad_y / self.segments)
                
                outer_pts = []
                for s in range(self.num_sides):
                    a = s * 2.0 * math.pi / self.num_sides
                    outer_pts.append(pya.Point(int(rx_outer * math.cos(a) / dbu), int(ry_outer * math.sin(a) / dbu)))
                poly = pya.Polygon(outer_pts)
                
                if rx_inner > 0 and ry_inner > 0:
                    inner_pts = []
                    for s in range(self.num_sides):
                        a = s * 2.0 * math.pi / self.num_sides
                        inner_pts.append(pya.Point(int(rx_inner * math.cos(a) / dbu), int(ry_inner * math.sin(a) / dbu)))
                    poly.insert_hole(inner_pts)
                region.insert(poly)
                
            elif self.style == "Linear RECT":
                lx_outer = self.rad_x - i * (self.rad_x / self.segments)
                ly_outer = self.rad_y - i * (self.rad_y / self.segments)
                lx_inner = self.rad_x - (i + 1) * (self.rad_x / self.segments)
                ly_inner = self.rad_y - (i + 1) * (self.rad_y / self.segments)
                
                box_outer = pya.Box(int(-lx_outer/dbu), int(-ly_outer/dbu), int(lx_outer/dbu), int(ly_outer/dbu))
                region.insert(box_outer)
                if lx_inner > 0 and ly_inner > 0:
                    box_inner = pya.Box(int(-lx_inner/dbu), int(-ly_inner/dbu), int(lx_inner/dbu), int(ly_inner/dbu))
                    region -= pya.Region(box_inner)
                    
            elif self.style == "Ramp Up/Down":
                delta_l = self.rad_x / self.segments
                # Strip i is drawn
                rx1 = i * delta_l
                rx2 = (i + 1) * delta_l
                region.insert(pya.Box(int(rx1/dbu), 0, int(rx2/dbu), int(self.rad_y/dbu)))
                
            elif self.style == "Ramp":
                delta_l = self.rad_x / self.segments
                # Symmetric ramp layers: layer is abs(N/2 - i)
                rx1 = i * delta_l
                rx2 = (i + 1) * delta_l
                region.insert(pya.Box(int(rx1/dbu), 0, int(rx2/dbu), int(self.rad_y/dbu)))
                # Adjust layer/datatype to be symmetric
                lyr_sym = base_layer + (abs(self.segments // 2 - i) if self.output_mode == "Layers" else 0)
                dt_sym = base_datatype + (0 if self.output_mode == "Layers" else abs(self.segments // 2 - i))
                layer_idx = self.layout.layer(pya.LayerInfo(lyr_sym, dt_sym))
                
            self.cell.shapes(layer_idx).insert(region)

# 7. Interdigitated Electrodes
class InterdigitatedElectrodesPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(InterdigitatedElectrodesPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("type", self.TypeInt, "Type (1 to 5)", default = 1)
        self.param("width1", self.TypeDouble, "Finger Width (um)", default = 2.0)
        self.param("width2", self.TypeDouble, "Spine Width (um)", default = 4.0)
        self.param("length1", self.TypeDouble, "Finger Length (um)", default = 40.0)
        self.param("length2", self.TypeDouble, "Connector Spine Length (um)", default = 10.0)
        self.param("overlap", self.TypeDouble, "Overlap (um)", default = 30.0)
        self.param("num_elec", self.TypeInt, "Number of fingers", default = 10)
        self.param("pitch", self.TypeDouble, "Pitch (um)", default = 8.0)
        self.param("base_h", self.TypeDouble, "Base Height (um)", default = 50.0)
        self.param("base_w", self.TypeDouble, "Base Width (um)", default = 50.0)

    def display_text_impl(self):
        return f"IntElectrodes(Type={self.type}, N={self.num_elec})"

    def coerce_parameters_impl(self):
        if self.type < 1: self.type = 1
        elif self.type > 5: self.type = 5
        if self.width1 <= 0: self.width1 = 0.5
        if self.width2 <= 0: self.width2 = 0.5
        if self.length1 <= 0: self.length1 = 1.0
        if self.pitch <= self.width1: self.pitch = self.width1 + 1.0
        if self.overlap > self.length1: self.overlap = self.length1
        if self.num_elec < 1: self.num_elec = 1

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_interdigitated_electrodes(
            self.layout, self.type, self.width1, self.width2, self.length1, self.length2,
            self.overlap, self.num_elec, self.pitch, self.base_h, self.base_w
        )
        self.cell.shapes(layer_idx).insert(region)

# 8. Resolution Test Pattern
class ResolutionTestPatternPCell(pya.PCellDeclarationHelper):
    def __init__(self, default_style="RS"):
        super(ResolutionTestPatternPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("style", self.TypeString, "Style", default = default_style, choices = [["RS", "RS"], ["LS", "LS"], ["RSA", "RSA"], ["LSA", "LSA"], ["Star", "Star"], ["PiStar", "PiStar"]])
        self.param("width", self.TypeDouble, "Line Width W (um) [RS/LS/Star]", default = 1.0)
        self.param("height", self.TypeDouble, "Height H (um) [RS/LS/RSA/LSA]", default = 20.0)
        self.param("num_lines", self.TypeInt, "Number of lines", default = 5)
        self.param("rad", self.TypeDouble, "Outer Radius (um) [Star/PiStar]", default = 50.0)
        self.param("start_w", self.TypeDouble, "Start Width (um) [RSA/LSA]", default = 0.1)
        self.param("end_w", self.TypeDouble, "End Width (um) [RSA/LSA]", default = 1.0)
        self.param("delta_w", self.TypeDouble, "Delta Width (um) [RSA/LSA]", default = 0.1)
        self.param("space", self.TypeDouble, "Space (um) [RSA/LSA]", default = 2.0)
        self.param("n", self.TypeInt, "Cycles N [PiStar]", default = 12)

    def display_text_impl(self):
        return f"ResolutionPattern({self.style}, W={self.width:.2f}um)"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.05
        if self.height <= 0: self.height = 1.0
        if self.num_lines < 1: self.num_lines = 1
        if self.rad <= 0: self.rad = 1.0
        if self.start_w <= 0: self.start_w = 0.01
        if self.end_w < self.start_w: self.end_w = self.start_w + 0.1
        if self.delta_w <= 0: self.delta_w = 0.01
        if self.space < 0: self.space = 0.0
        if self.n < 1: self.n = 1

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        region = pya.Region()
        
        if self.style == "RS":
            for i in range(self.num_lines):
                # Bottom vertical bar
                region.insert(pya.Box(int((2 * i * self.width)/dbu), 0, int(((2 * i + 1) * self.width)/dbu), int(self.height/dbu)))
                # Top vertical bar
                region.insert(pya.Box(int(((2 * i + 1) * self.width)/dbu), int(self.height/dbu), int(((2 * i + 2) * self.width)/dbu), int((2 * self.height)/dbu)))
            ex.draw_text(self.layout, self.cell, self.layer, f"{self.width:.3g}", 0.0, 2.5 * self.height, 2.0 * self.height)
            
        elif self.style == "LS":
            height = self.height
            for i in range(self.num_lines):
                if self.width < height:
                    # Vertical bar
                    v_box = pya.Box(0, 0, int(self.width/dbu), int(height/dbu))
                    # Horizontal bar
                    h_box = pya.Box(0, 0, int(height/dbu), int(self.width/dbu))
                    
                    l_shape = pya.Region(v_box).join(pya.Region(h_box))
                    l_shape.transform(pya.Trans(int((2 * i * self.width)/dbu), int((2 * i * self.width)/dbu)))
                    region.insert(l_shape)
                    height -= 2.0 * self.width
                else:
                    break
            ex.draw_text(self.layout, self.cell, self.layer, f"{self.width:.3g}", 0.0, 1.5 * self.height, self.height)
            
        elif self.style == "RSA":
            curr_x = 0.0
            w = self.start_w
            while w <= self.end_w + 1e-9:
                for i in range(self.num_lines):
                    region.insert(pya.Box(int((curr_x + 2 * i * w)/dbu), 0, int((curr_x + (2 * i + 1) * w)/dbu), int(self.height/dbu)))
                    region.insert(pya.Box(int((curr_x + (2 * i + 1) * w)/dbu), int(self.height/dbu), int((curr_x + (2 * i + 2) * w)/dbu), int((2 * self.height)/dbu)))
                ex.draw_text(self.layout, self.cell, self.layer, f"{w:.3g}", curr_x, 2.5 * self.height, 2.0 * self.height)
                curr_x += 2.0 * self.num_lines * w + self.space
                w += self.delta_w
                
        elif self.style == "LSA":
            curr_x = 0.0
            w = self.start_w
            while w <= self.end_w + 1e-9:
                h = self.height
                for i in range(self.num_lines):
                    if w < h:
                        v_box = pya.Box(0, 0, int(w/dbu), int(h/dbu))
                        h_box = pya.Box(0, 0, int(h/dbu), int(w/dbu))
                        l_shape = pya.Region(v_box).join(pya.Region(h_box))
                        l_shape.transform(pya.Trans(int((curr_x + 2 * i * w)/dbu), int((2 * i * w)/dbu)))
                        region.insert(l_shape)
                        h -= 2.0 * w
                    else:
                        break
                ex.draw_text(self.layout, self.cell, self.layer, f"{w:.3g}", curr_x, 1.5 * self.height, self.height)
                curr_x += self.height + self.space
                w += self.delta_w
                
        elif self.style in ["Star", "PiStar"]:
            is_pi = (self.style == "PiStar")
            w = (self.n * math.pi) if is_pi else self.width
            num_elements = int((math.pi * 2.0 * self.rad) / (2.0 * w))
            if num_elements < 2:
                num_elements = 2
            d_theta = math.pi * 2.0 / num_elements
            for i in range(num_elements):
                theta = i * d_theta
                pts = [
                    pya.Point(0, 0),
                    pya.Point(int((self.rad * math.cos(theta) - (-w/2.0) * math.sin(theta))/dbu),
                              int((self.rad * math.sin(theta) + (-w/2.0) * math.cos(theta))/dbu)),
                    pya.Point(int((self.rad * math.cos(theta) - (w/2.0) * math.sin(theta))/dbu),
                              int((self.rad * math.sin(theta) + (w/2.0) * math.cos(theta))/dbu))
                ]
                region.insert(pya.Polygon(pts))
                
        self.cell.shapes(layer_idx).insert(region)


# 9. Spirals
class SpiralsPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralsPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("style", self.TypeString, "Style (Archimedean, Fermat, Logarithmic)", default = "Archimedean")
        self.param("turns", self.TypeInt, "Number of turns", default = 5)
        self.param("width", self.TypeDouble, "Waveguide Width (um)", default = 1.0)
        self.param("separation", self.TypeDouble, "Separation (um) [Archimedean]", default = 2.0)
        self.param("a", self.TypeDouble, "Coefficient a [Fermat/Log]", default = 2.0)
        self.param("b", self.TypeDouble, "Growth Factor b [Logarithmic]", default = 0.1)
        self.param("resolution", self.TypeInt, "Points per turn", default = 64)

    def display_text_impl(self):
        return f"Spiral({self.style}, Turns={self.turns})"

    def coerce_parameters_impl(self):
        if self.turns < 1: self.turns = 1
        if self.width <= 0: self.width = 0.1
        if self.separation < 0: self.separation = 0.0
        if self.a <= 0: self.a = 0.1
        if self.resolution < 8: self.resolution = 8

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        pts = []
        
        inc = 2.0 * math.pi / self.resolution
        upper_lim = 2.0 * math.pi * self.turns
        
        if self.style == "Archimedean":
            factor = (self.separation + self.width) / (2.0 * math.pi)
            for i in range(int(upper_lim / inc) + 1):
                theta = i * inc
                r = factor * theta + self.width / 2.0
                pts.append(pya.Point(int(r * math.cos(theta) / dbu), int(r * math.sin(theta) / dbu)))
        elif self.style == "Fermat":
            for i in range(int(upper_lim / inc) + 1):
                theta = i * inc
                r = math.sqrt(self.a * self.a * theta) + self.width / 2.0
                pts.append(pya.Point(int(r * math.cos(theta) / dbu), int(r * math.sin(theta) / dbu)))
        elif self.style == "Logarithmic":
            for i in range(int(upper_lim / inc) + 1):
                theta = i * inc
                r = self.a * math.exp(self.b * theta) + self.width / 2.0
                pts.append(pya.Point(int(r * math.cos(theta) / dbu), int(r * math.sin(theta) / dbu)))
                
        path = pya.Path(pts, int(self.width/dbu))
        self.cell.shapes(layer_idx).insert(path.simple_polygon())

# 10. Spiral - Rectangular
class RectangularSpiralPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(RectangularSpiralPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("turns", self.TypeInt, "Number of turns", default = 5)
        self.param("width", self.TypeDouble, "Line Width (um)", default = 1.0)
        self.param("pitch", self.TypeDouble, "Pitch between turns (um)", default = 3.0)
        self.param("start_length", self.TypeDouble, "Start Length (um)", default = 5.0)

    def display_text_impl(self):
        return f"RectSpiral(Turns={self.turns}, W={self.width:.1f}um)"

    def coerce_parameters_impl(self):
        if self.turns < 1: self.turns = 1
        if self.width <= 0: self.width = 0.1
        if self.pitch <= self.width: self.pitch = self.width + 0.5
        if self.start_length <= 0: self.start_length = 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        pts = [pya.Point(0, 0)]
        
        x = 0.0
        y = 0.0
        length = self.start_length
        for i in range(self.turns):
            # Line right
            pts.append(pya.Point(int((x + length)/dbu), int(y/dbu)))
            x += length
            # Line up
            pts.append(pya.Point(int(x/dbu), int((y + length)/dbu)))
            y += length
            length += self.pitch
            # Line left
            pts.append(pya.Point(int((x - length)/dbu), int(y/dbu)))
            x -= length
            # Line down
            pts.append(pya.Point(int(x/dbu), int((y - length)/dbu)))
            y -= length
            length += self.pitch
            
        path = pya.Path(pts, int(self.width/dbu))
        self.cell.shapes(layer_idx).insert(path.simple_polygon())

# 11. Alignment Marks - Custom
class AlignmentMarksCustomPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(AlignmentMarksCustomPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("type", self.TypeInt, "Type (1 to 4)", default = 1)
        self.param("L1", self.TypeDouble, "Cross Horiz Length L1 (um)", default = 100.0)
        self.param("W1", self.TypeDouble, "Cross Horiz Width W1 (um)", default = 10.0)
        self.param("L2", self.TypeDouble, "Cross Vert Length L2 (um)", default = 100.0)
        self.param("PL", self.TypeDouble, "Pad Length PL (um)", default = 20.0)
        self.param("PW", self.TypeDouble, "Pad Width PW (um)", default = 20.0)
        self.param("LX", self.TypeDouble, "Ext Length LX (um) [Type 3]", default = 20.0)
        self.param("d", self.TypeDouble, "Offset Distance d (um) [Type 4]", default = 40.0)
        self.param("BL", self.TypeDouble, "Box Length BL (um) [Type 4]", default = 30.0)
        self.param("BW", self.TypeDouble, "Box Width BW (um) [Type 4]", default = 30.0)
        self.param("inverse", self.TypeBoolean, "Inverse (Cladding)", default = False)
        self.param("IL", self.TypeDouble, "Inverse Box Length IL (um)", default = 300.0)
        self.param("IW", self.TypeDouble, "Inverse Box Width IW (um)", default = 300.0)

    def display_text_impl(self):
        return f"AlignMarkCustom(Type={self.type})"

    def coerce_parameters_impl(self):
        if self.type < 1: self.type = 1
        elif self.type > 4: self.type = 4
        if self.L1 <= 0: self.L1 = 1.0
        if self.W1 <= 0: self.W1 = 0.5
        if self.L2 <= 0: self.L2 = 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        region = pya.Region()
        
        # 1. Base cross
        gH = pya.Box(int(-self.L1/dbu), int(-self.W1/2.0/dbu), int(self.L1/dbu), int(self.W1/2.0/dbu))
        gV = pya.Box(int(-self.W1/2.0/dbu), int(-self.L2/dbu), int(self.W1/2.0/dbu), int(self.L2/dbu))
        region.insert(gH)
        region.insert(gV)
        
        if self.type == 2:
            pad = pya.Box(int(self.L1/dbu), int(-self.PW/2.0/dbu), int((self.L1 + self.PL)/dbu), int(self.PW/2.0/dbu))
            r_pad = pya.Region(pad)
            for i in [90, 180, 270]:
                temp = r_pad.dup()
                temp.transform(pya.Trans(pya.Trans.R90 if i==90 else (pya.Trans.R180 if i==180 else pya.Trans.R270)))
                region.insert(temp)
            region.insert(r_pad)
        elif self.type == 3:
            pad = pya.Box(int(self.L1/dbu), int(-self.PW/2.0/dbu), int((self.L1 + self.PL)/dbu), int(self.PW/2.0/dbu))
            ext = pya.Box(int((self.L1 + self.PL)/dbu), int(-self.W1/2.0/dbu), int((self.L1 + self.PL + self.LX)/dbu), int(self.W1/2.0/dbu))
            r_comb = pya.Region(pad).join(pya.Region(ext))
            for i in [0, 90, 180, 270]:
                temp = r_comb.dup()
                if i > 0:
                    temp.transform(pya.Trans(pya.Trans.R90 if i==90 else (pya.Trans.R180 if i==180 else pya.Trans.R270)))
                region.insert(temp)
        elif self.type == 4:
            offset = self.d + self.W1/2.0
            region.insert(pya.Box(int(offset/dbu), int(offset/dbu), int((offset + self.BL)/dbu), int((offset + self.BW)/dbu)))
            region.insert(pya.Box(int((-offset - self.BL)/dbu), int(offset/dbu), int(-offset/dbu), int((offset + self.BW)/dbu)))
            region.insert(pya.Box(int((-offset - self.BL)/dbu), int((-offset - self.BW)/dbu), int(-offset/dbu), int(-offset/dbu)))
            region.insert(pya.Box(int(offset/dbu), int((-offset - self.BW)/dbu), int((offset + self.BL)/dbu), int(-offset/dbu)))
            
        if self.inverse:
            outer_box = pya.Box(int(-self.IL/2.0/dbu), int(-self.IW/2.0/dbu), int(self.IL/2.0/dbu), int(self.IW/2.0/dbu))
            region = pya.Region(outer_box) - region
            
        self.cell.shapes(layer_idx).insert(region)

# 12. Reticle Barcode and Label Frames
class ReticleBarcodeFramePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(ReticleBarcodeFramePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("tool", self.TypeString, "Tool (ASML, Contact 5-Inch, Contact 7-Inch)", default = "ASML")
        self.param("barcode_text", self.TypeString, "Barcode Text", default = "123456")
        self.param("label_text", self.TypeString, "Label Text", default = "SAMPLE-01")
        self.param("bar_w", self.TypeDouble, "Thin Bar Width (um)", default = 100.0)
        self.param("bar_h", self.TypeDouble, "Bar Height (um)", default = 3000.0)

    def display_text_impl(self):
        return f"ReticleFrame({self.tool}, {self.label_text})"

    def coerce_parameters_impl(self):
        if self.bar_w <= 0: self.bar_w = 1.0
        if self.bar_h <= 0: self.bar_h = 10.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        region = pya.Region()
        
        if self.tool == "ASML":
            # Outer frame corner marks
            # ASML PAS5500 frame has marks at: (-67750, 69500) and (67750, 69500)
            # Center mark cross:
            cross_l = 1750.0
            cross_w = 300.0
            c_cross = pya.Region(pya.Box(int(-cross_l/dbu), int(-cross_w/dbu), int(cross_l/dbu), int(cross_w/dbu)))
            c_cross.insert(pya.Box(int(-cross_w/dbu), int(-cross_l/dbu), int(cross_w/dbu), int(cross_l/dbu)))
            
            # Place left mark
            m_left = c_cross.dup()
            m_left.transform(pya.Trans(int(-67750.0/dbu), int(69500.0/dbu)))
            region.insert(m_left)
            # Place right mark
            m_right = c_cross.dup()
            m_right.transform(pya.Trans(int(67750.0/dbu), int(69500.0/dbu)))
            region.insert(m_right)
            
            # Draw barcode at (69000, 29150) rotated 90
            bc_reg = ex.draw_barcode_39(self.layout, self.barcode_text, 0, 0, self.bar_h, self.bar_w)
            bc_reg.transform(pya.Trans(pya.Trans.R90, int(69000.0/dbu), int(29150.0/dbu)))
            region.insert(bc_reg)
            
        elif self.tool in ["Contact 5-Inch", "Contact 7-Inch"]:
            # Simple frame for contact printing masks
            y_pad = -58000.0 if self.tool == "Contact 5-Inch" else -83900.0
            # Draw label box representing the placement of label
            region.insert(pya.Box(int(-10000.0/dbu), int((y_pad - 1000.0)/dbu), int(10000.0/dbu), int((y_pad + 1000.0)/dbu)))
            
        self.cell.shapes(layer_idx).insert(region)

# 13. Vernier
class VernierPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(VernierPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer 1", default = pya.LayerInfo(1, 0))
        self.param("layer2", self.TypeLayer, "Layer 2", default = pya.LayerInfo(2, 0))
        self.param("ticks", self.TypeInt, "Number of ticks", default = 11)
        self.param("pitch", self.TypeDouble, "Pitch (um)", default = 10.0)
        self.param("vernierReso", self.TypeDouble, "Vernier resolution (um)", default = 0.5)
        self.param("lineWidth", self.TypeDouble, "Tick Line Width (um)", default = 1.0)
        self.param("lineLength", self.TypeDouble, "Tick Line Length (um)", default = 15.0)

    def display_text_impl(self):
        return f"Vernier(Res={self.vernierReso:.2f}um)"

    def coerce_parameters_impl(self):
        if self.ticks < 1: self.ticks = 1
        if self.pitch <= 0: self.pitch = 1.0
        if self.lineWidth <= 0: self.lineWidth = 0.1
        if self.lineLength <= 0: self.lineLength = 1.0

    def produce_impl(self):
        lyr1 = self.layout.layer(self.layer)
        lyr2 = self.layout.layer(self.layer2)
        dbu = self.layout.dbu
        
        # Center ticks
        self.cell.shapes(lyr1).insert(pya.Box(int(-self.lineWidth/2.0/dbu), 0, int(self.lineWidth/2.0/dbu), int(self.lineLength/dbu)))
        self.cell.shapes(lyr2).insert(pya.Box(int(-self.lineWidth/2.0/dbu), int(-self.lineLength/dbu), int(self.lineWidth/2.0/dbu), 0))
        
        for i in range(1, self.ticks + 1):
            offset = self.lineLength / 3.0 if (i % 10 == 0) else (self.lineLength / 7.0 if (i % 5 == 0) else 0.0)
            
            # Scale 1 (layer 1) positive and negative
            self.cell.shapes(lyr1).insert(pya.Box(int((-self.lineWidth/2.0 + i * self.pitch)/dbu), 0, int((self.lineWidth/2.0 + i * self.pitch)/dbu), int((self.lineLength/3.0 + offset)/dbu)))
            self.cell.shapes(lyr1).insert(pya.Box(int((-self.lineWidth/2.0 - i * self.pitch)/dbu), 0, int((self.lineWidth/2.0 - i * self.pitch)/dbu), int((self.lineLength/3.0 + offset)/dbu)))
            
            # Scale 2 (layer 2) positive and negative
            pitch2_p = i * self.pitch + i * self.vernierReso
            pitch2_n = -i * self.pitch - i * self.vernierReso
            self.cell.shapes(lyr2).insert(pya.Box(int((-self.lineWidth/2.0 + pitch2_p)/dbu), int((-self.lineLength/3.0 - offset)/dbu), int((self.lineWidth/2.0 + pitch2_p)/dbu), 0))
            self.cell.shapes(lyr2).insert(pya.Box(int((-self.lineWidth/2.0 + pitch2_n)/dbu), int((-self.lineLength/3.0 - offset)/dbu), int((self.lineWidth/2.0 + pitch2_n)/dbu), 0))

# 14. Vernier With Labels
class VernierWithLabelsPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(VernierWithLabelsPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer 1", default = pya.LayerInfo(1, 0))
        self.param("layer2", self.TypeLayer, "Layer 2", default = pya.LayerInfo(2, 0))
        self.param("ticks", self.TypeInt, "Number of ticks", default = 11)
        self.param("pitch", self.TypeDouble, "Pitch (um)", default = 10.0)
        self.param("vernierReso", self.TypeDouble, "Vernier resolution (um)", default = 0.5)
        self.param("lineWidth", self.TypeDouble, "Tick Line Width (um)", default = 1.0)
        self.param("lineLength", self.TypeDouble, "Tick Line Length (um)", default = 15.0)
        self.param("label1", self.TypeString, "Label 1", default = "L1")
        self.param("label2", self.TypeString, "Label 2", default = "L2")

    def display_text_impl(self):
        return f"VernierLabeled(Res={self.vernierReso:.2f}um)"

    def coerce_parameters_impl(self):
        if self.ticks < 1: self.ticks = 1
        if self.pitch <= 0: self.pitch = 1.0
        if self.lineWidth <= 0: self.lineWidth = 0.1
        if self.lineLength <= 0: self.lineLength = 1.0

    def produce_impl(self):
        lyr1 = self.layout.layer(self.layer)
        lyr2 = self.layout.layer(self.layer2)
        dbu = self.layout.dbu
        
        # Center ticks
        self.cell.shapes(lyr1).insert(pya.Box(int(-self.lineWidth/2.0/dbu), 0, int(self.lineWidth/2.0/dbu), int(self.lineLength/dbu)))
        self.cell.shapes(lyr2).insert(pya.Box(int(-self.lineWidth/2.0/dbu), int(-self.lineLength/dbu), int(self.lineWidth/2.0/dbu), 0))
        
        for i in range(1, self.ticks + 1):
            offset = self.lineLength / 3.0 if (i % 10 == 0) else (self.lineLength / 7.0 if (i % 5 == 0) else 0.0)
            self.cell.shapes(lyr1).insert(pya.Box(int((-self.lineWidth/2.0 + i * self.pitch)/dbu), 0, int((self.lineWidth/2.0 + i * self.pitch)/dbu), int((self.lineLength/3.0 + offset)/dbu)))
            self.cell.shapes(lyr1).insert(pya.Box(int((-self.lineWidth/2.0 - i * self.pitch)/dbu), 0, int((self.lineWidth/2.0 - i * self.pitch)/dbu), int((self.lineLength/3.0 + offset)/dbu)))
            
            pitch2_p = i * self.pitch + i * self.vernierReso
            pitch2_n = -i * self.pitch - i * self.vernierReso
            self.cell.shapes(lyr2).insert(pya.Box(int((-self.lineWidth/2.0 + pitch2_p)/dbu), int((-self.lineLength/3.0 - offset)/dbu), int((self.lineWidth/2.0 + pitch2_p)/dbu), 0))
            self.cell.shapes(lyr2).insert(pya.Box(int((-self.lineWidth/2.0 + pitch2_n)/dbu), int((-self.lineLength/3.0 - offset)/dbu), int((self.lineWidth/2.0 + pitch2_n)/dbu), 0))
            
        # Draw placeholder label markers (small circles/boxes representing label centers)
        self.cell.shapes(lyr1).insert(pya.Box(int(-self.lineWidth/dbu), int((self.lineLength + 5.0)/dbu), int(self.lineWidth/dbu), int((self.lineLength + 7.0)/dbu)))
        self.cell.shapes(lyr2).insert(pya.Box(int(-self.lineWidth/dbu), int((-self.lineLength - 7.0)/dbu), int(self.lineWidth/dbu), int((-self.lineLength - 5.0)/dbu)))

# 15. Exponential Taper
class ExponentialTaperPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(ExponentialTaperPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("length", self.TypeDouble, "Taper Length (um)", default = 50.0)
        self.param("w_start", self.TypeDouble, "Start Width (um)", default = 0.5)
        self.param("w_end", self.TypeDouble, "End Width (um)", default = 5.0)
        self.param("n_points", self.TypeInt, "Number of points", default = 30)

    def display_text_impl(self):
        return f"ExpTaper({self.w_start:.1f}->{self.w_end:.1f}um, L={self.length:.1f}um)"

    def coerce_parameters_impl(self):
        if self.length <= 0: self.length = 1.0
        if self.w_start <= 0: self.w_start = 0.1
        if self.w_end <= 0: self.w_end = 0.1
        if self.n_points < 2: self.n_points = 2

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        pts = []
        
        for i in range(self.n_points):
            t = i / float(self.n_points - 1)
            x = t * self.length
            w = self.w_start / 2.0 * ((self.w_end / self.w_start) ** t)
            pts.append(pya.Point(int(x/dbu), int(w/dbu)))
            
        for i in range(self.n_points - 1, -1, -1):
            t = i / float(self.n_points - 1)
            x = t * self.length
            w = self.w_start / 2.0 * ((self.w_end / self.w_start) ** t)
            pts.append(pya.Point(int(x/dbu), int(-w/dbu)))
            
        poly = pya.Polygon(pts)
        self.cell.shapes(layer_idx).insert(poly)

# 16. S-Bend Funnel
class SBendFunnelPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SBendFunnelPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("x1", self.TypeDouble, "x1 (um)", default = 0.0)
        self.param("y1", self.TypeDouble, "y1 (um)", default = 0.0)
        self.param("cx1", self.TypeDouble, "cx1 (um)", default = 10.0)
        self.param("cy1", self.TypeDouble, "cy1 (um)", default = 0.0)
        self.param("cx2", self.TypeDouble, "cx2 (um)", default = 10.0)
        self.param("cy2", self.TypeDouble, "cy2 (um)", default = 20.0)
        self.param("x2", self.TypeDouble, "x2 (um)", default = 20.0)
        self.param("y2", self.TypeDouble, "y2 (um)", default = 20.0)
        self.param("w1", self.TypeDouble, "Start Width w1 (um)", default = 10.0)
        self.param("n_points", self.TypeInt, "Number of points", default = 30)

    def display_text_impl(self):
        return f"SBendFunnel(W1={self.w1:.1f}um)"

    def coerce_parameters_impl(self):
        if self.w1 <= 0: self.w1 = 0.1
        if self.n_points < 3: self.n_points = 3

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        
        # S-bend upper curve
        curve_pts = ex.compute_bezier_pts(self.x1, self.y1 + self.w1/2.0, self.cx1, self.cy1 + self.w1/2.0, 
                                          self.cx2, self.cy2 - self.w1/2.0, self.x2, self.y2, self.n_points)
        
        pts = []
        for x, y in curve_pts:
            pts.append(pya.Point(int(x/dbu), int(y/dbu)))
        # Mirror along the x-axis for the bottom edge
        for x, y in reversed(curve_pts):
            pts.append(pya.Point(int(x/dbu), int(-y/dbu)))
            
        poly = pya.Polygon(pts)
        self.cell.shapes(layer_idx).insert(poly)

# 17. 180 Degree Bend Inverse
class Bend180DegreeInversePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(Bend180DegreeInversePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("L1", self.TypeDouble, "Length L1 (um)", default = 20.0)
        self.param("L2", self.TypeDouble, "Length L2 (um)", default = 20.0)
        self.param("D", self.TypeDouble, "Center Distance D (um)", default = 40.0)
        self.param("W", self.TypeDouble, "Waveguide Width W (um)", default = 1.0)
        self.param("We", self.TypeDouble, "Cladding Width We (um)", default = 3.0)
        self.param("gap", self.TypeDouble, "Gap for slot (um)", default = 0.2)
        self.param("num_sides", self.TypeInt, "Sides", default = 32)
        self.param("is_slot", self.TypeBoolean, "Slot Waveguide", default = False)

    def display_text_impl(self):
        return f"Bend180Inverse(D={self.D:.1f}um, W={self.W:.1f}um)"

    def coerce_parameters_impl(self):
        if self.L1 < 0: self.L1 = 0.0
        if self.L2 < 0: self.L2 = 0.0
        if self.D <= 0: self.D = 10.0
        if self.W <= 0: self.W = 0.1
        if self.We <= 0: self.We = 0.1
        if self.num_sides < 4: self.num_sides = 4

    def draw_single_bend(self, width):
        dbu = self.layout.dbu
        region = pya.Region()
        # Straight 1
        region.insert(pya.Box(int(-width/2.0/dbu), 0, int(width/2.0/dbu), int(self.L1/dbu)))
        # Semicircle Torus at (R, L1)
        r_center = self.D / 2.0
        r_out = r_center + width / 2.0
        r_in = r_center - width / 2.0
        
        pts = []
        for i in range(self.num_sides + 1):
            ang = i * math.pi / self.num_sides
            pts.append(pya.Point(int((r_center + r_out * math.cos(ang))/dbu), int((self.L1 + r_out * math.sin(ang))/dbu)))
        for j in range(self.num_sides, -1, -1):
            ang = j * math.pi / self.num_sides
            pts.append(pya.Point(int((r_center + r_in * math.cos(ang))/dbu), int((self.L1 + r_in * math.sin(ang))/dbu)))
            
        region.insert(pya.Polygon(pts))
        # Straight 2
        region.insert(pya.Box(int((self.D - width/2.0)/dbu), int((self.L1 - self.L2)/dbu), int((self.D + width/2.0)/dbu), int(self.L1/dbu)))
        return region

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        
        if self.is_slot:
            # outer cladding
            region = self.draw_single_bend(2.0 * self.We + 2.0 * self.gap + self.W)
            # subtract gap + core
            region -= self.draw_single_bend(2.0 * self.gap + self.W)
            # add core
            region.insert(self.draw_single_bend(self.W))
        else:
            region = self.draw_single_bend(2.0 * self.We + self.W)
            region -= self.draw_single_bend(self.W)
            
        self.cell.shapes(layer_idx).insert(region)

# 18. Racetrack
class RacetrackPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(RacetrackPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("length", self.TypeDouble, "Straight Length (um)", default = 50.0)
        self.param("width", self.TypeDouble, "Waveguide Width (um)", default = 1.0)
        self.param("radius_in", self.TypeDouble, "Inner Radius (um)", default = 10.0)
        self.param("num_sides", self.TypeInt, "Sides", default = 32)

    def display_text_impl(self):
        return f"Racetrack(L={self.length:.1f}um, R_in={self.radius_in:.1f}um)"

    def coerce_parameters_impl(self):
        if self.length <= 0: self.length = 1.0
        if self.width <= 0: self.width = 0.1
        if self.radius_in <= 0: self.radius_in = 0.5
        if self.num_sides < 4: self.num_sides = 4

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        region = pya.Region()
        
        # 1. Straight waveguides (top and bottom)
        dy = self.radius_in + self.width / 2.0
        region.insert(pya.Box(int(-self.length/2.0/dbu), int((dy - self.width/2.0)/dbu), int(self.length/2.0/dbu), int((dy + self.width/2.0)/dbu)))
        region.insert(pya.Box(int(-self.length/2.0/dbu), int((-dy - self.width/2.0)/dbu), int(self.length/2.0/dbu), int((-dy + self.width/2.0)/dbu)))
        
        # 2. Right semicircle torus
        pts_r = []
        for i in range(self.num_sides + 1):
            ang = -math.pi/2.0 + i * math.pi / self.num_sides
            pts_r.append(pya.Point(int((self.length/2.0 + (self.radius_in + self.width) * math.cos(ang))/dbu), int(((self.radius_in + self.width) * math.sin(ang))/dbu)))
        for j in range(self.num_sides, -1, -1):
            ang = -math.pi/2.0 + j * math.pi / self.num_sides
            pts_r.append(pya.Point(int((self.length/2.0 + self.radius_in * math.cos(ang))/dbu), int((self.radius_in * math.sin(ang))/dbu)))
        region.insert(pya.Polygon(pts_r))
        
        # 3. Left semicircle torus
        pts_l = []
        for i in range(self.num_sides + 1):
            ang = math.pi/2.0 + i * math.pi / self.num_sides
            pts_l.append(pya.Point(int((-self.length/2.0 + (self.radius_in + self.width) * math.cos(ang))/dbu), int(((self.radius_in + self.width) * math.sin(ang))/dbu)))
        for j in range(self.num_sides, -1, -1):
            ang = math.pi/2.0 + j * math.pi / self.num_sides
            pts_l.append(pya.Point(int((-self.length/2.0 + self.radius_in * math.cos(ang))/dbu), int((self.radius_in * math.sin(ang))/dbu)))
        region.insert(pya.Polygon(pts_l))
        
        self.cell.shapes(layer_idx).insert(region)

# 19. Spiral Delay Line
class SpiralDelayLinePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralDelayLinePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("turns", self.TypeInt, "Number of turns", default = 5)
        self.param("width", self.TypeDouble, "Waveguide Width (um)", default = 1.0)
        self.param("separation", self.TypeDouble, "Separation (um)", default = 2.0)
        self.param("length", self.TypeDouble, "Straight Extension Length (um)", default = 20.0)
        self.param("resolution", self.TypeInt, "Points per turn", default = 64)

    def display_text_impl(self):
        return f"SpiralDelayLine(Turns={self.turns})"

    def coerce_parameters_impl(self):
        if self.turns < 1: self.turns = 1
        if self.width <= 0: self.width = 0.1
        if self.separation < 0: self.separation = 0.0
        if self.resolution < 8: self.resolution = 8

    def build_spiral_path(self):
        a = (self.separation + self.width) / (2.0 * math.pi)
        pts = []
        inc = 2.0 * math.pi / self.resolution
        upper_lim = 2.0 * self.turns * math.pi
        
        # Spiral 2 (reverse)
        for i in range(int(upper_lim / inc) + 1):
            theta = (upper_lim / inc - i) * inc
            r = -a * theta
            pts.append(pya.Point(int(r * math.cos(theta) / self.layout.dbu), int((r * math.sin(theta) - self.length)/self.layout.dbu)))
            
        # Spiral 1
        for i in range(int(upper_lim / inc) + 1):
            theta = i * inc
            r = a * theta
            pts.append(pya.Point(int(r * math.cos(theta) / self.layout.dbu), int((r * math.sin(theta) + self.length)/self.layout.dbu)))
            
        return pts

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        pts = self.build_spiral_path()
        path = pya.Path(pts, int(self.width/dbu))
        self.cell.shapes(layer_idx).insert(path.simple_polygon())

# 20. Inverse Spiral Delay Line
class InverseSpiralDelayLinePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(InverseSpiralDelayLinePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("turns", self.TypeInt, "Number of turns", default = 5)
        self.param("width", self.TypeDouble, "Waveguide Width (um)", default = 1.0)
        self.param("separation", self.TypeDouble, "Separation (um)", default = 2.0)
        self.param("length", self.TypeDouble, "Straight Extension Length (um)", default = 20.0)
        self.param("sleeveWidth", self.TypeDouble, "Sleeve Width We (um)", default = 3.0)
        self.param("resolution", self.TypeInt, "Points per turn", default = 64)

    def display_text_impl(self):
        return f"InvSpiralDelay(Turns={self.turns})"

    def coerce_parameters_impl(self):
        if self.turns < 1: self.turns = 1
        if self.width <= 0: self.width = 0.1
        if self.sleeveWidth <= 0: self.sleeveWidth = 0.1
        if self.resolution < 8: self.resolution = 8

    def build_spiral_path(self):
        a = (self.separation + self.width) / (2.0 * math.pi)
        pts = []
        inc = 2.0 * math.pi / self.resolution
        upper_lim = 2.0 * self.turns * math.pi
        
        for i in range(int(upper_lim / inc) + 1):
            theta = (upper_lim / inc - i) * inc
            r = -a * theta
            pts.append(pya.Point(int(r * math.cos(theta) / self.layout.dbu), int((r * math.sin(theta) - self.length)/self.layout.dbu)))
            
        for i in range(int(upper_lim / inc) + 1):
            theta = i * inc
            r = a * theta
            pts.append(pya.Point(int(r * math.cos(theta) / self.layout.dbu), int((r * math.sin(theta) + self.length)/self.layout.dbu)))
            
        return pts

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        pts = self.build_spiral_path()
        
        sleeve_p = pya.Path(pts, int((self.width + 2.0 * self.sleeveWidth)/dbu)).simple_polygon()
        core_p = pya.Path(pts, int(self.width/dbu)).simple_polygon()
        
        region = pya.Region(sleeve_p) - pya.Region(core_p)
        self.cell.shapes(layer_idx).insert(region)

# 21. Apodized Grating
class ApodizedGratingPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(ApodizedGratingPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("grating_l", self.TypeDouble, "Grating Length (um)", default = 20.0)
        self.param("increment", self.TypeDouble, "Increment (um)", default = 0.01)
        self.param("height", self.TypeDouble, "Height (um)", default = 300.0)
        self.param("duty_cutoff", self.TypeDouble, "Duty Cycle Cutoff", default = 0.1)
        self.param("p1", self.TypeDouble, "Pitch Coeff p1 (um)", default = 0.6)
        self.param("p2", self.TypeDouble, "Pitch Coeff p2", default = 0.05)
        self.param("p3", self.TypeDouble, "Pitch Coeff p3", default = 0.0)
        self.param("p4", self.TypeDouble, "Pitch Coeff p4", default = 0.0)
        self.param("d1", self.TypeDouble, "Duty Coeff d1", default = 0.5)
        self.param("d2", self.TypeDouble, "Duty Coeff d2", default = -0.2)
        self.param("d3", self.TypeDouble, "Duty Coeff d3", default = 0.0)
        self.param("d4", self.TypeDouble, "Duty Coeff d4", default = 0.0)
        self.param("d5", self.TypeDouble, "Duty Coeff d5", default = 0.0)

    def display_text_impl(self):
        return f"ApodizedGrating(L={self.grating_l:.1f}um)"

    def coerce_parameters_impl(self):
        if self.grating_l <= 0: self.grating_l = 1.0
        if self.increment <= 0: self.increment = 0.001
        if self.height <= 0: self.height = 10.0

    def get_pitch_width(self, x):
        xOverL = x / self.grating_l
        duty = self.d1 + self.d2 * xOverL + self.d3 * xOverL**2 + self.d4 * xOverL**3 + self.d5 * xOverL**4
        if duty < self.duty_cutoff:
            duty = self.duty_cutoff
        pitch = self.p1 * (1.0 + self.p2 * xOverL + self.p3 * xOverL**2 + self.p4 * xOverL**3)
        return pitch, duty * pitch

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        dbu = self.layout.dbu
        region = pya.Region()
        
        # Determine num periods by average pitch
        mid_pitch, _ = self.get_pitch_width(0.0)
        num_periods = int(round(self.grating_l / mid_pitch))
        
        x_ll = -self.grating_l / 2.0
        for i in range(num_periods):
            pitch, w = self.get_pitch_width(x_ll)
            x_ur = x_ll + w
            # Rect
            region.insert(pya.Box(int(x_ll/dbu), 0, int(x_ur/dbu), int(self.height/dbu)))
            x_ll += pitch
            
        self.cell.shapes(layer_idx).insert(region)

# 22. Grating Coupler
class GratingCouplerPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(GratingCouplerPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Grating Layer", default = pya.LayerInfo(1, 0))
        self.param("lambda0", self.TypeDouble, "Design Wavelength (um)", default = 1.55)
        self.param("n_eff", self.TypeDouble, "Effective Index n_eff", default = 2.85)
        self.param("n_clad", self.TypeDouble, "Cladding Index n_clad", default = 1.44)
        self.param("theta_c", self.TypeDouble, "Acceptance Angle thetaC (deg)", default = 40.0)
        self.param("R1", self.TypeDouble, "Inner Radius Offset R1 (um)", default = 20.0)
        self.param("grating_period", self.TypeDouble, "Grating Period (um)", default = 0.6)
        self.param("ratio", self.TypeDouble, "Duty Cycle Fill Factor (0 to 1)", default = 0.5)
        self.param("num_elements", self.TypeInt, "Number of teeth", default = 25)
        self.param("num_sides", self.TypeInt, "Teeth Resolution", default = 64)
        self.param("endcaps", self.TypeBoolean, "Stroked Endcaps", default = True)

    def display_text_impl(self):
        return f"GratingCoupler(Period={self.grating_period:.2f}um)"

    def coerce_parameters_impl(self):
        if self.lambda0 <= 0: self.lambda0 = 0.5
        if self.n_eff <= 0: self.n_eff = 1.0
        if self.theta_c <= 0: self.theta_c = 5.0
        if self.grating_period <= 0: self.grating_period = 0.1
        if self.ratio <= 0.01: self.ratio = 0.01
        elif self.ratio >= 0.99: self.ratio = 0.99
        if self.num_elements < 1: self.num_elements = 1

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        
        Q1 = int(math.ceil(self.n_eff * self.R1 / self.lambda0))
        theta = math.acos(self.n_eff - self.lambda0 / self.grating_period)
        
        region = ex.draw_grating_teeth(
            self.layout, Q1, self.lambda0, self.n_eff, self.n_clad, theta, self.theta_c,
            self.grating_period, self.ratio, self.num_elements, self.num_sides, self.endcaps
        )
        self.cell.shapes(layer_idx).insert(region)

# 22b. Grating Coupler With Waveguide
class GratingCouplerWithWaveguidePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(GratingCouplerWithWaveguidePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Grating Layer", default = pya.LayerInfo(1, 0))
        self.param("wg_layer", self.TypeLayer, "Waveguide Layer", default = pya.LayerInfo(2, 0))
        self.param("wg_width", self.TypeDouble, "Waveguide Width (um)", default = 0.5)
        self.param("length", self.TypeDouble, "S-Bend Length (um)", default = 50.0)
        self.param("height", self.TypeDouble, "S-Bend Height (um)", default = 10.0)
        self.param("sleeve", self.TypeDouble, "Inverse Cladding Sleeve (um)", default = 2.0)
        self.param("lambda0", self.TypeDouble, "Design Wavelength (um)", default = 1.55)
        self.param("n_eff", self.TypeDouble, "Effective Index n_eff", default = 2.85)
        self.param("n_clad", self.TypeDouble, "Cladding Index n_clad", default = 1.44)
        self.param("theta_c", self.TypeDouble, "Acceptance Angle (deg)", default = 40.0)
        self.param("R1", self.TypeDouble, "Inner Radius Offset R1 (um)", default = 20.0)
        self.param("grating_period", self.TypeDouble, "Grating Period (um)", default = 0.6)
        self.param("ratio", self.TypeDouble, "Duty Cycle Fill Factor", default = 0.5)
        self.param("num_elements", self.TypeInt, "Number of teeth", default = 25)
        self.param("num_sides", self.TypeInt, "Teeth Resolution", default = 64)
        self.param("wg_inv", self.TypeBoolean, "Inverse (Cladding) Waveguide", default = False)
        self.param("endcaps", self.TypeBoolean, "Stroked Endcaps", default = True)

    def display_text_impl(self):
        return f"GC_With_WG(W={self.wg_width:.1f}um)"

    def coerce_parameters_impl(self):
        if self.wg_width <= 0: self.wg_width = 0.1
        if self.length <= 0: self.length = 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        wg_lyr_idx = self.layout.layer(self.wg_layer)
        dbu = self.layout.dbu
        
        # 1. Grating Teeth
        Q1 = int(math.ceil(self.n_eff * self.R1 / self.lambda0))
        theta = math.acos(self.n_eff - self.lambda0 / self.grating_period)
        teeth = ex.draw_grating_teeth(
            self.layout, Q1, self.lambda0, self.n_eff, self.n_clad, theta, self.theta_c,
            self.grating_period, self.ratio, self.num_elements, self.num_sides, self.endcaps
        )
        self.cell.shapes(layer_idx).insert(teeth)
        
        # 2. S-Bend Waveguide starting at origin going left and shifting up
        # Bezier S-bend coordinates: (0,0) -> (-L/2, 0) -> (-L/2, H) -> (-L, H)
        bez_pts = ex.compute_bezier_pts(0.0, 0.0, -self.length / 2.0, 0.0, 
                                        -self.length / 2.0, self.height, -self.length, self.height, 30)
        pts = [pya.Point(int(x/dbu), int(y/dbu)) for x, y in bez_pts]
        
        wg_region = pya.Region()
        if self.wg_inv:
            sleeve_p = pya.Path(pts, int((self.wg_width + 2.0 * self.sleeve)/dbu)).simple_polygon()
            core_p = pya.Path(pts, int(self.wg_width/dbu)).simple_polygon()
            wg_region.insert(sleeve_p)
            wg_region -= pya.Region(core_p)
        else:
            wg_p = pya.Path(pts, int(self.wg_width/dbu)).simple_polygon()
            wg_region.insert(wg_p)
            
        self.cell.shapes(wg_lyr_idx).insert(wg_region)
        self.cell.shapes(wg_lyr_idx).insert(wg_region)


# =====================================================================
# MEMS/NEMS Library PCells (Section 2.10)
# =====================================================================

# 23. Bi-Morph Thermal Actuator
class BiMorphThermalActuatorPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(BiMorphThermalActuatorPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("dimple_layer", self.TypeLayer, "Dimple Layer", default = pya.LayerInfo(2, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(3, 0))
        self.param("width1", self.TypeDouble, "Beam Width 1 (um)", default = 2.0)
        self.param("width2", self.TypeDouble, "Beam Width 2 (um)", default = 8.0)
        self.param("width3", self.TypeDouble, "Beam Width 3 (um)", default = 4.0)
        self.param("width4", self.TypeDouble, "Beam Width 4 (um)", default = 8.0)
        self.param("length1", self.TypeDouble, "Beam Length 1 (um)", default = 150.0)
        self.param("length2", self.TypeDouble, "Beam Length 2 (um)", default = 200.0)
        self.param("length3", self.TypeDouble, "Beam Length 3 (um)", default = 40.0)
        self.param("pitch", self.TypeDouble, "Dimple Pitch (um)", default = 20.0)
        self.param("dimple_height", self.TypeDouble, "Dimple Height (um)", default = 2.0)
        self.param("dimple_width", self.TypeDouble, "Dimple Width (um)", default = 4.0)
        self.param("base_height", self.TypeDouble, "Anchor Pad Height (um)", default = 20.0)
        self.param("base_width", self.TypeDouble, "Anchor Pad Width (um)", default = 30.0)
        self.param("anchor_distance", self.TypeDouble, "Anchor Offset Distance (um)", default = 2.0)

    def display_text_impl(self):
        return f"BiMorphThermal(L1={self.length1:.1f}, L2={self.length2:.1f})"

    def coerce_parameters_impl(self):
        if self.width1 <= 0: self.width1 = 0.1
        if self.width2 <= 0: self.width2 = 0.1
        if self.length1 <= 0: self.length1 = 10.0
        if self.length2 <= self.length1: self.length2 = self.length1 + 10.0
        if self.pitch <= 0: self.pitch = 5.0
        if self.anchor_distance < 0: self.anchor_distance = 0.0

    def produce_impl(self):
        dbu = self.layout.dbu
        layer_idx = self.layout.layer(self.layer)
        dimple_idx = self.layout.layer(self.dimple_layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        
        # 1. Structural Layer
        ga = pya.Region()
        ga.insert(pya.Box(0, 0, int(self.base_width/dbu), int(self.base_height/dbu)))
        ga.insert(pya.Box(int(self.base_width/dbu), int((self.base_height - self.width1)/dbu), int((self.base_width + self.length1)/dbu), int(self.base_height/dbu)))
        ga.insert(pya.Box(int((self.base_width + self.length1)/dbu), int((self.base_height - self.width4)/dbu), int((self.base_width + self.length2)/dbu), int(self.base_height/dbu)))
        ga.insert(pya.Box(int((self.base_width + self.length2 - self.length3)/dbu), int(self.base_height/dbu), int((self.base_width + self.length2)/dbu), int((self.base_height + self.width3)/dbu)))
        ga.insert(pya.Box(0, int((self.base_height + self.width3)/dbu), int(self.base_width/dbu), int((2.0 * self.base_height + self.width3)/dbu)))
        ga.insert(pya.Box(int(self.base_width/dbu), int((self.base_height + self.width3)/dbu), int((self.base_width + self.length2)/dbu), int((self.base_height + self.width3 + self.width2)/dbu)))
        
        ga.merge()
        self.cell.shapes(layer_idx).insert(ga)
        
        # 2. Dimple Layer
        distance = self.length2 - self.length1
        if self.pitch > self.dimple_width and self.width4 > self.dimple_height and distance > self.dimple_width:
            numPeriods = int(distance / self.pitch)
            unoccupiedSpace = self.pitch - self.dimple_width
            edgeOffset = (distance - numPeriods * self.pitch + unoccupiedSpace) / 2.0
            
            dimples = pya.Region()
            xOffset = self.base_width + self.length1 + edgeOffset
            yOffset = self.base_height - (self.width4 - self.dimple_height) / 2.0 - self.dimple_height
            
            for i in range(numPeriods):
                cx = xOffset + i * self.pitch
                dimples.insert(pya.Box(int(cx/dbu), int(yOffset/dbu), int((cx + self.dimple_width)/dbu), int((yOffset + self.dimple_height)/dbu)))
            
            dimples.merge()
            self.cell.shapes(dimple_idx).insert(dimples)
            
        # 3. Anchor Layer
        anchors = pya.Region()
        anchors.insert(pya.Box(int(self.anchor_distance/dbu), int(self.anchor_distance/dbu), int((self.base_width - self.anchor_distance)/dbu), int((self.base_height - self.anchor_distance)/dbu)))
        anchors.insert(pya.Box(int(self.anchor_distance/dbu), int((self.base_height + self.width3 + self.anchor_distance)/dbu), int((self.base_width - self.anchor_distance)/dbu), int((2.0 * self.base_height + self.width3 - self.anchor_distance)/dbu)))
        
        anchors.merge()
        self.cell.shapes(anchor_idx).insert(anchors)


# 24. Bolometers (Section 2.10.2)
class BolometerPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(BolometerPCell, self).__init__()
        self.param("type", self.TypeString, "Type", default = "L-shape", choices = [["L-shape", "L-shape"], ["U-shape", "U-shape"]])
        self.param("layer_a", self.TypeLayer, "Layer A (Joule Contacts)", default = pya.LayerInfo(1, 0))
        self.param("layer_b", self.TypeLayer, "Layer B (Metal Pads/Lines)", default = pya.LayerInfo(2, 0))
        self.param("layer_c", self.TypeLayer, "Layer C (Active Area/Spines)", default = pya.LayerInfo(3, 0))
        self.param("layer_d", self.TypeLayer, "Layer D (Support Frame)", default = pya.LayerInfo(4, 0))
        self.param("layer_e", self.TypeLayer, "Layer E (Inner Release Area)", default = pya.LayerInfo(5, 0))
        self.param("layer_f", self.TypeLayer, "Layer F (Thermistor/Active)", default = pya.LayerInfo(6, 0))
        self.param("w1", self.TypeDouble, "Thermistor line width w1 (um)", default = 0.5)
        self.param("w2", self.TypeDouble, "Support beam width w2 (um)", default = 1.0)
        self.param("w3", self.TypeDouble, "Frame boundary width w3 (um)", default = 1.5)
        self.param("g1", self.TypeDouble, "Gap offset g1 (um)", default = 0.5)
        self.param("g2", self.TypeDouble, "Gap offset g2 (um)", default = 1.0)
        self.param("g3", self.TypeDouble, "Gap offset g3 (um)", default = 1.0)
        self.param("L1", self.TypeDouble, "Frame height L1 (um)", default = 15.0)
        self.param("L2", self.TypeDouble, "Frame width L2 (um)", default = 20.0)
        self.param("r", self.TypeDouble, "Meander/Arc Radius r (um)", default = 1.0)
        self.param("ri", self.TypeDouble, "Frame Corner Radius ri (um)", default = 2.0)
        self.param("num_sides", self.TypeInt, "Circle resolution Nsides", default = 32)
        self.param("a", self.TypeDouble, "Pad lead extension a (um)", default = 2.0)
        self.param("b", self.TypeDouble, "Pad alignment offset b (um)", default = 1.0)
        self.param("c", self.TypeDouble, "Taper length c (um)", default = 1.0)
        self.param("d", self.TypeDouble, "Contact pad width d (um)", default = 3.0)
        self.param("e", self.TypeDouble, "Metal contact margin e (um)", default = 0.5)
        self.param("f", self.TypeDouble, "Thermistor frame margin f (um)", default = 0.5)

    def display_text_impl(self):
        return f"Bolometer_{self.type}(L1={self.L1:.1f}, L2={self.L2:.1f})"

    def coerce_parameters_impl(self):
        if self.w1 <= 0: self.w1 = 0.1
        if self.w2 <= 0: self.w2 = 0.1
        if self.num_sides < 8: self.num_sides = 8

    def produce_impl(self):
        dbu = self.layout.dbu
        lyr_a = self.layout.layer(self.layer_a)
        lyr_b = self.layout.layer(self.layer_b)
        lyr_c = self.layout.layer(self.layer_c)
        lyr_d = self.layout.layer(self.layer_d)
        lyr_e = self.layout.layer(self.layer_e)
        lyr_f = self.layout.layer(self.layer_f)
        
        if self.type == "L-shape":
            innerWidth = self.L2 + 2.0 * (self.g1 + self.g2 + self.w2)
            innerHeight = self.L1 + 2.0 * (self.g1 + self.g2 + self.w2)
            
            box_inner = pya.Box(int(-innerWidth/(2.0*dbu)), int(-innerHeight/(2.0*dbu)), int(innerWidth/(2.0*dbu)), int(innerHeight/(2.0*dbu)))
            poly_inner = pya.Polygon(box_inner)
            poly_inner.round_corners(int(self.ri/dbu), int(self.ri/dbu), self.num_sides)
            gaRoundRectInner = pya.Region(poly_inner)
            
            gaRoundRectTemp = gaRoundRectInner.sized(int(self.g3/dbu))
            gaRoundRectOuter = gaRoundRectInner.sized(int((self.g3 + self.w3)/dbu)) - gaRoundRectTemp
            
            # subtract cutouts on left/right for pad connection
            x_min = int((-innerWidth/2.0 - self.g3 - 2.0*self.w3)/dbu)
            x_max = int((-innerWidth/2.0)/dbu)
            y_min = int((innerHeight/2.0 - self.g1 - self.w2/2.0 - self.w1/2.0 - self.b)/dbu)
            y_max = int((innerHeight/2.0 - self.g1 - self.w2/2.0 + self.w1/2.0 + self.b)/dbu)
            gaRoundRectOuter -= pya.Box(x_min, y_min, x_max, y_max)
            
            x_min = int((innerWidth/2.0)/dbu)
            x_max = int((innerWidth/2.0 + self.g3 + 2.0*self.w3)/dbu)
            y_min = int((-innerHeight/2.0 + self.g1 + self.w2/2.0 - self.w1/2.0 - self.b)/dbu)
            y_max = int((-innerHeight/2.0 + self.g1 + self.w2/2.0 + self.w1/2.0 + self.b)/dbu)
            gaRoundRectOuter -= pya.Box(x_min, y_min, x_max, y_max)
            self.cell.shapes(lyr_d).insert(gaRoundRectOuter)
            
            padding = (self.w2 - self.w1) / 2.0
            lf_box = pya.Box(int((-self.L2/2.0 + padding)/dbu), int((-self.L1/2.0 + padding)/dbu), int((self.L2/2.0 - padding)/dbu), int((self.L1/2.0 - padding)/dbu))
            self.cell.shapes(lyr_f).insert(lf_box)
            
            runnerW2 = pya.Region()
            runnerW2.insert(pya.Box(int((-innerWidth/2.0)/dbu), int((innerHeight/2.0 - self.g1 - self.w2)/dbu), int((innerWidth/2.0 - self.g1 - self.w2/2.0 - self.r)/dbu), int((innerHeight/2.0 - self.g1)/dbu)))
            runnerW2.insert(ex.draw_torus_arc(dbu, innerWidth/2.0 - self.g1 - self.w2/2.0 - self.r, innerHeight/2.0 - self.g1 - self.w2/2.0 - self.r, self.r, self.w2, 0.0, 90.0, self.num_sides))
            runnerW2.insert(pya.Box(int((innerWidth/2.0 - self.g1 - self.w2)/dbu), int((-self.L1/2.0 + self.w2/2.0 + self.r)/dbu), int((innerWidth/2.0 - self.g1)/dbu), int((innerHeight/2.0 - self.g1 - self.w2/2.0 - self.r)/dbu)))
            runnerW2.insert(ex.draw_torus_arc(dbu, innerWidth/2.0 - self.g1 - self.w2/2.0 - self.r, -self.L1/2.0 + self.w2/2.0 + self.r, self.r, self.w2, 270.0, 360.0, self.num_sides))
            runnerW2.insert(pya.Box(int((self.L2/2.0)/dbu), int((-self.L1/2.0)/dbu), int((innerWidth/2.0 - self.g1 - self.w2/2.0 - self.r)/dbu), int((-self.L1/2.0 + self.w2)/dbu)))
            
            temp_r2 = runnerW2.dup()
            temp_r2.transform(pya.Trans(pya.Trans.R180, 0, 0))
            runnerW2.insert(temp_r2)
            runnerW2.insert(pya.Box(int((-self.L2/2.0)/dbu), int((-self.L1/2.0)/dbu), int((self.L2/2.0)/dbu), int((self.L1/2.0)/dbu)))
            
            temp_conn = pya.Region(pya.Box(int((-self.ri - self.w2/2.0)/dbu), 0, int((self.ri + self.w2/2.0)/dbu), int(self.ri/dbu)))
            temp_conn -= pya.Region(ex.draw_ellipse(dbu, -self.w2/2.0 - self.ri, self.ri, self.ri, self.ri, self.num_sides))
            temp_conn -= pya.Region(ex.draw_ellipse(dbu, self.w2/2.0 + self.ri, self.ri, self.ri, self.ri, self.num_sides))
            
            temp2 = temp_conn.dup()
            temp2.transform(pya.Trans(pya.Trans.R270, int(-innerWidth/2.0/dbu), int((innerHeight/2.0 - self.g1 - self.w2/2.0)/dbu)))
            runnerW2.insert(temp2)
            
            temp3 = temp_conn.dup()
            temp3.transform(pya.Trans(pya.Trans.R90, int(innerWidth/2.0/dbu), int((-innerHeight/2.0 + self.g1 + self.w2/2.0)/dbu)))
            runnerW2.insert(temp3)
            self.cell.shapes(lyr_c).insert(runnerW2)
            
            gaRoundRectInner -= runnerW2
            self.cell.shapes(lyr_e).insert(gaRoundRectInner)
            
            pts_bp = [
                pya.DPoint(0.0, 0.0),
                pya.DPoint(self.f, 0.0),
                pya.DPoint(self.f + self.c, self.d/2.0 - self.w1/2.0),
                pya.DPoint(self.f + self.c, self.d/2.0 + self.w1/2.0),
                pya.DPoint(self.f, self.d),
                pya.DPoint(0.0, self.d)
            ]
            bondPad = pya.Region(pya.Polygon([pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in pts_bp]))
            
            temp_la = bondPad.sized(int(-self.e/dbu))
            temp_la.insert(pya.Box(0, int(self.e/dbu), int(self.e/dbu), int((self.d - self.e)/dbu)))
            
            dx_bp = -innerWidth/2.0 - self.a - self.c - self.f
            dy_bp = innerHeight/2.0 - self.g1 - self.w2/2.0 - self.d/2.0
            
            temp_la_left = temp_la.dup()
            temp_la_left.transform(pya.Trans(int(dx_bp/dbu), int(dy_bp/dbu)))
            temp_la_right = temp_la_left.dup()
            temp_la_right.transform(pya.Trans(pya.Trans.R180, 0, 0))
            
            self.cell.shapes(lyr_a).insert(temp_la_left + temp_la_right)
            
            runnerW1 = bondPad.dup()
            runnerW1.insert(pya.Box(int((self.f + self.c)/dbu), int((self.d/2.0 - self.w1/2.0)/dbu), int((self.f + self.c + self.a)/dbu), int((self.d/2.0 + self.w1/2.0)/dbu)))
            runnerW1.transform(pya.Trans(int(dx_bp/dbu), int(dy_bp/dbu)))
            
            runnerW1.insert(pya.Box(int((-innerWidth/2.0)/dbu), int((innerHeight/2.0 - self.g1 - self.w2 + padding)/dbu), int((innerWidth/2.0 - self.g1 - self.w2/2.0 - self.r)/dbu), int((innerHeight/2.0 - self.g1 - self.w2 + padding + self.w1)/dbu)))
            runnerW1.insert(ex.draw_torus_arc(dbu, innerWidth/2.0 - self.g1 - self.w2/2.0 - self.r, innerHeight/2.0 - self.g1 - self.w2/2.0 - self.r, self.r, self.w1, 0.0, 90.0, self.num_sides))
            runnerW1.insert(pya.Box(int((innerWidth/2.0 - self.g1 - self.w2 + padding)/dbu), int((-self.L1/2.0 + self.w2/2.0 + self.r)/dbu), int((innerWidth/2.0 - self.g1 - padding)/dbu), int((innerHeight/2.0 - self.g1 - self.w2/2.0 - self.r)/dbu)))
            runnerW1.insert(ex.draw_torus_arc(dbu, innerWidth/2.0 - self.g1 - self.w2/2.0 - self.r, -self.L1/2.0 + self.w2/2.0 + self.r, self.r, self.w1, 270.0, 360.0, self.num_sides))
            runnerW1.insert(pya.Box(int((self.L2/2.0)/dbu), int((-self.L1/2.0 + padding)/dbu), int((innerWidth/2.0 - self.g1 - self.w2/2.0 - self.r)/dbu), int((-self.L1/2.0 + self.w2 - padding)/dbu)))
            
            numPeriods = int(math.floor((self.L2 - 2.0 * self.r) / (4.0 * self.r)))
            extraLengthPerSide = (self.L2 - 2.0 * self.r - numPeriods * 4.0 * self.r) / 2.0
            botL1p = -self.L1 / 2.0 + padding + self.w1 / 2.0 + self.r
            topL1p = self.L1 / 2.0 - padding - self.w1 / 2.0 - self.r
            
            runnerW1.insert(pya.Box(int((-self.L2/2.0)/dbu), int((self.L1/2.0 - padding - self.w1)/dbu), int((-self.L2/2.0 + extraLengthPerSide)/dbu), int((self.L1/2.0 - padding)/dbu)))
            
            temp_r1 = runnerW1.dup()
            temp_r1.transform(pya.Trans(pya.Trans.R180, 0, 0))
            runnerW1.insert(temp_r1)
            
            startX = -self.L2 / 2.0 + extraLengthPerSide
            startY = self.L1 / 2.0 - padding - self.w1
            meander = pya.Region()
            meander.insert(ex.draw_torus_arc(dbu, startX, startY + self.w1 / 2.0 - self.r, self.r, self.w1, 0.0, 90.0, self.num_sides))
            meander.insert(pya.Box(int((startX + self.r - self.w1/2.0)/dbu), int(botL1p/dbu), int((startX + self.r + self.w1/2.0)/dbu), int(topL1p/dbu)))
            meander.insert(ex.draw_torus_arc(dbu, startX + 2.0 * self.r, botL1p, self.r, self.w1, 180.0, 360.0, self.num_sides))
            meander.insert(pya.Box(int((startX + 3.0 * self.r - self.w1/2.0)/dbu), int(botL1p/dbu), int((startX + 3.0 * self.r + self.w1/2.0)/dbu), int(topL1p/dbu)))
            meander.insert(ex.draw_torus_arc(dbu, startX + 4.0 * self.r, topL1p, self.r, self.w1, 90.0, 180.0, self.num_sides))
            
            pitch = 2.0 * self.r
            cnt = 0
            for i in range(numPeriods):
                temp_m = meander.dup()
                temp_m.transform(pya.Trans(int((i * 2.0 * pitch)/dbu), 0))
                runnerW1.insert(temp_m)
                cnt += 1
                
            meanderLast = pya.Region(ex.draw_torus_arc(dbu, startX, startY + self.w1 / 2.0 - self.r, self.r, self.w1, 0.0, 90.0, self.num_sides))
            meanderLast.insert(pya.Box(int((startX + self.r - self.w1/2.0)/dbu), int(botL1p/dbu), int((startX + self.r + self.w1/2.0)/dbu), int(topL1p/dbu)))
            meanderLast.insert(ex.draw_torus_arc(dbu, startX + 2.0 * self.r, botL1p, self.r, self.w1, 180.0, 270.0, self.num_sides))
            meanderLast.transform(pya.Trans(int((cnt * 2.0 * pitch)/dbu), 0))
            runnerW1.insert(meanderLast)
            
            self.cell.shapes(lyr_b).insert(runnerW1)
            
        else: # U-shape
            innerWidth = self.L2 + 2.0 * self.g1
            innerHeight = self.L1 + 2.0 * self.g1 + 4.0 * (self.g2 + self.w2)
            
            box_inner = pya.Box(int(-innerWidth/(2.0*dbu)), int(-innerHeight/(2.0*dbu)), int(innerWidth/(2.0*dbu)), int(innerHeight/(2.0*dbu)))
            poly_inner = pya.Polygon(box_inner)
            poly_inner.round_corners(int(self.ri/dbu), int(self.ri/dbu), self.num_sides)
            gaRoundRectInner = pya.Region(poly_inner)
            
            gaRoundRectTemp = gaRoundRectInner.sized(int(self.g3/dbu))
            gaRoundRectOuter = gaRoundRectInner.sized(int((self.g3 + self.w3)/dbu)) - gaRoundRectTemp
            
            # subtract cutouts on left/right for pad connection
            x_min = int((-innerWidth/2.0 - self.g3 - 2.0*self.w3)/dbu)
            x_max = int((-innerWidth/2.0)/dbu)
            y_min = int((innerHeight/2.0 - self.g1 - self.w2/2.0 - self.w1/2.0 - self.b)/dbu)
            y_max = int((innerHeight/2.0 - self.g1 - self.w2/2.0 + self.w1/2.0 + self.b)/dbu)
            gaRoundRectOuter -= pya.Box(x_min, y_min, x_max, y_max)
            
            x_min = int((innerWidth/2.0)/dbu)
            x_max = int((innerWidth/2.0 + self.g3 + 2.0*self.w3)/dbu)
            y_min = int((-innerHeight/2.0 + self.g1 + self.w2/2.0 - self.w1/2.0 - self.b)/dbu)
            y_max = int((-innerHeight/2.0 + self.g1 + self.w2/2.0 + self.w1/2.0 + self.b)/dbu)
            gaRoundRectOuter -= pya.Box(x_min, y_min, x_max, y_max)
            self.cell.shapes(lyr_d).insert(gaRoundRectOuter)
            
            padding = (self.w2 - self.w1) / 2.0
            lf_box = pya.Box(int((-self.L2/2.0 + padding)/dbu), int((-self.L1/2.0 + padding)/dbu), int((self.L2/2.0 - padding)/dbu), int((self.L1/2.0 - padding)/dbu))
            self.cell.shapes(lyr_f).insert(lf_box)
            
            runnerW2 = pya.Region()
            # Rect(-innerWidth / 2.0, innerHeight / 2.0 - g1 - w2, innerWidth / 2.0 - g1 - w2 - g2 / 2.0, innerHeight / 2.0 - g1)
            runnerW2.insert(pya.Box(int((-innerWidth/2.0)/dbu), int((innerHeight/2.0 - self.g1 - self.w2)/dbu), int((innerWidth/2.0 - self.g1 - self.w2 - self.g2/2.0)/dbu), int((innerHeight/2.0 - self.g1)/dbu)))
            # TorusW(innerWidth / 2.0 - g1 - w2 - g2 / 2.0, innerHeight / 2.0 - g1 - w2 - g2 / 2.0, g2 / 2.0 + w2 / 2.0, w2, 270.0, 90.0, numSides)
            runnerW2.insert(ex.draw_torus_arc(dbu, innerWidth/2.0 - self.g1 - self.w2 - self.g2/2.0, innerHeight/2.0 - self.g1 - self.w2 - self.g2/2.0, self.g2/2.0 + self.w2/2.0, self.w2, 270.0, 90.0, self.num_sides))
            # Rect(-innerWidth / 2.0 + g1 + w2 + g2 / 2.0, innerHeight / 2.0 - g1 - 2.0 * w2 - g2, innerWidth / 2.0 - g1 - w2 - g2 / 2.0, innerHeight / 2.0 - g1 - w2 - g2)
            runnerW2.insert(pya.Box(int((-innerWidth/2.0 + self.g1 + self.w2 + self.g2/2.0)/dbu), int((innerHeight/2.0 - self.g1 - 2.0*self.w2 - self.g2)/dbu), int((innerWidth/2.0 - self.g1 - self.w2 - self.g2/2.0)/dbu), int((innerHeight/2.0 - self.g1 - self.w2 - self.g2)/dbu)))
            # TorusW(-innerWidth / 2.0 + g1 + w2 + g2 / 2.0, innerHeight / 2.0 - g1 - 2.0 * w2 - g2 - g2 / 2.0, g2 / 2.0 + w2 / 2.0, w2, 90.0, 180.0, numSides)
            runnerW2.insert(ex.draw_torus_arc(dbu, -innerWidth/2.0 + self.g1 + self.w2 + self.g2/2.0, innerHeight/2.0 - self.g1 - 2.0*self.w2 - self.g2 - self.g2/2.0, self.g2/2.0 + self.w2/2.0, self.w2, 90.0, 180.0, self.num_sides))
            # Rect(-L2 / 2.0, L1 / 2.0, -L2 / 2.0 + w2, L1 / 2.0 + g2 / 2.0)
            runnerW2.insert(pya.Box(int((-self.L2/2.0)/dbu), int((self.L1/2.0)/dbu), int((-self.L2/2.0 + self.w2)/dbu), int((self.L1/2.0 + self.g2/2.0)/dbu)))
            
            temp_r2 = runnerW2.dup()
            temp_r2.transform(pya.Trans(pya.Trans.R180, 0, 0))
            runnerW2.insert(temp_r2)
            runnerW2.insert(pya.Box(int((-self.L2/2.0)/dbu), int((-self.L1/2.0)/dbu), int((self.L2/2.0)/dbu), int((self.L1/2.0)/dbu)))
            
            temp_conn = pya.Region(pya.Box(int((-self.ri - self.w2/2.0)/dbu), 0, int((self.ri + self.w2/2.0)/dbu), int(self.ri/dbu)))
            temp_conn -= pya.Region(ex.draw_ellipse(dbu, -self.w2/2.0 - self.ri, self.ri, self.ri, self.ri, self.num_sides))
            temp_conn -= pya.Region(ex.draw_ellipse(dbu, self.w2/2.0 + self.ri, self.ri, self.ri, self.ri, self.num_sides))
            
            curvedEnds = temp_conn.dup()
            temp2 = temp_conn.dup()
            temp2.transform(pya.Trans(pya.Trans.R270, int(-innerWidth/2.0/dbu), int((innerHeight/2.0 - self.g1 - self.w2/2.0)/dbu)))
            runnerW2.insert(temp2)
            
            temp3 = temp_conn.dup()
            temp3.transform(pya.Trans(pya.Trans.R90, int(innerWidth/2.0/dbu), int((-innerHeight/2.0 + self.g1 + self.w2/2.0)/dbu)))
            runnerW2.insert(temp3)
            self.cell.shapes(lyr_c).insert(runnerW2)
            
            # subtract loops from gaRoundRectInner
            gaRoundRectInner -= pya.Box(int((-innerWidth/2.0)/dbu), int((innerHeight/2.0 - self.g1 - self.w2)/dbu), int((innerWidth/2.0 - self.g1 - self.w2 - self.g2/2.0)/dbu), int((innerHeight/2.0 - self.g1)/dbu))
            gaRoundRectInner -= pya.Region(ex.draw_torus_arc(dbu, innerWidth/2.0 - self.g1 - self.w2 - self.g2/2.0, innerHeight/2.0 - self.g1 - self.w2 - self.g2/2.0, self.g2/2.0 + self.w2/2.0, self.w2, 270.0, 90.0, self.num_sides))
            gaRoundRectInner -= pya.Box(int((-innerWidth/2.0 + self.g1 + self.w2 + self.g2/2.0)/dbu), int((innerHeight/2.0 - self.g1 - 2.0*self.w2 - self.g2)/dbu), int((innerWidth/2.0 - self.g1 - self.w2 - self.g2/2.0)/dbu), int((innerHeight/2.0 - self.g1 - self.w2 - self.g2)/dbu))
            gaRoundRectInner -= pya.Region(ex.draw_torus_arc(dbu, -innerWidth/2.0 + self.g1 + self.w2 + self.g2/2.0, innerHeight/2.0 - self.g1 - 2.0*self.w2 - self.g2 - self.g2/2.0, self.g2/2.0 + self.w2/2.0, self.w2, 90.0, 180.0, self.num_sides))
            gaRoundRectInner -= pya.Box(int((-self.L2/2.0)/dbu), int((self.L1/2.0)/dbu), int((-self.L2/2.0 + self.w2)/dbu), int((self.L1/2.0 + self.g2/2.0)/dbu))
            gaRoundRectInner -= pya.Box(int((-self.L2/2.0)/dbu), int((-self.L1/2.0)/dbu), int((self.L2/2.0)/dbu), int((self.L1/2.0)/dbu))
            gaRoundRectInner -= pya.Box(int(-innerWidth/dbu), int(-innerHeight/dbu), int(innerWidth/dbu), 0)
            
            curvedEnds_left = curvedEnds.dup()
            curvedEnds_left.transform(pya.Trans(pya.Trans.R270, int(-innerWidth/2.0/dbu), int((innerHeight/2.0 - self.g1 - self.w2/2.0)/dbu)))
            gaRoundRectInner -= curvedEnds_left
            
            gaRoundRectInnerBot = gaRoundRectInner.dup()
            gaRoundRectInner.transform(pya.Trans(pya.Trans.R180, 0, 0))
            
            self.cell.shapes(lyr_e).insert(gaRoundRectInner + gaRoundRectInnerBot)
            
            pts_bp = [
                pya.DPoint(0.0, 0.0),
                pya.DPoint(self.f, 0.0),
                pya.DPoint(self.f + self.c, self.d/2.0 - self.w1/2.0),
                pya.DPoint(self.f + self.c, self.d/2.0 + self.w1/2.0),
                pya.DPoint(self.f, self.d),
                pya.DPoint(0.0, self.d)
            ]
            bondPad = pya.Region(pya.Polygon([pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in pts_bp]))
            
            temp_la = bondPad.sized(int(-self.e/dbu))
            temp_la.insert(pya.Box(0, int(self.e/dbu), int(self.e/dbu), int((self.d - self.e)/dbu)))
            
            dx_bp = -innerWidth/2.0 - self.a - self.c - self.f
            dy_bp = innerHeight/2.0 - self.g1 - self.w2/2.0 - self.d/2.0
            
            temp_la_left = temp_la.dup()
            temp_la_left.transform(pya.Trans(int(dx_bp/dbu), int(dy_bp/dbu)))
            temp_la_right = temp_la_left.dup()
            temp_la_right.transform(pya.Trans(pya.Trans.R180, 0, 0))
            
            self.cell.shapes(lyr_a).insert(temp_la_left + temp_la_right)
            
            runnerW1 = bondPad.dup()
            runnerW1.insert(pya.Box(int((self.f + self.c)/dbu), int((self.d/2.0 - self.w1/2.0)/dbu), int((self.f + self.c + self.a)/dbu), int((self.d/2.0 + self.w1/2.0)/dbu)))
            runnerW1.transform(pya.Trans(int(dx_bp/dbu), int(dy_bp/dbu)))
            
            runnerW1.insert(pya.Box(int((-innerWidth/2.0)/dbu), int((innerHeight/2.0 - self.g1 - self.w2 + padding)/dbu), int((innerWidth/2.0 - self.g1 - self.w2 - self.g2/2.0)/dbu), int((innerHeight/2.0 - self.g1 - self.w2 + padding + self.w1)/dbu)))
            runnerW1.insert(ex.draw_torus_arc(dbu, innerWidth/2.0 - self.g1 - self.w2 - self.g2/2.0, innerHeight/2.0 - self.g1 - self.w2 - self.g2/2.0, self.g2/2.0 + self.w2/2.0, self.w1, 270.0, 90.0, self.num_sides))
            runnerW1.insert(pya.Box(int((-innerWidth/2.0 + self.g1 + self.w2 + self.g2/2.0)/dbu), int((innerHeight/2.0 - self.g1 - 2.0*self.w2 - self.g2 + padding)/dbu), int((innerWidth/2.0 - self.g1 - self.w2 - self.g2/2.0)/dbu), int((innerHeight/2.0 - self.g1 - self.w2 - self.g2 - padding)/dbu)))
            runnerW1.insert(ex.draw_torus_arc(dbu, -innerWidth/2.0 + self.g1 + self.w2 + self.g2/2.0, innerHeight/2.0 - self.g1 - 2.0*self.w2 - self.g2 - self.g2/2.0, self.g2/2.0 + self.w2/2.0, self.w1, 90.0, 180.0, self.num_sides))
            runnerW1.insert(pya.Box(int((-self.L2/2.0 + padding)/dbu), int((self.L1/2.0)/dbu), int((-self.L2/2.0 + self.w2 - padding)/dbu), int((self.L1/2.0 + self.g2/2.0)/dbu)))
            
            numPeriods = int(math.floor((self.L1 - 2.0 * self.r) / (4.0 * self.r)))
            extraLengthPerSide = (self.L1 - 2.0 * self.r - numPeriods * 4.0 * self.r) / 2.0
            negL2p = -self.L2 / 2.0 + padding + self.w1 / 2.0 + self.r
            posL2p = self.L2 / 2.0 - padding - self.w1 / 2.0 - self.r
            
            runnerW1.insert(pya.Box(int((-self.L2/2.0 + padding)/dbu), int((self.L1/2.0 - extraLengthPerSide)/dbu), int((-self.L2/2.0 + padding + self.w1)/dbu), int((self.L1/2.0)/dbu)))
            
            temp_r1 = runnerW1.dup()
            temp_r1.transform(pya.Trans(pya.Trans.R180, 0, 0))
            runnerW1.insert(temp_r1)
            
            startX = -self.L2 / 2.0 + padding + self.w1
            startY = self.L1 / 2.0 - extraLengthPerSide
            meander = pya.Region()
            meander.insert(ex.draw_torus_arc(dbu, startX - self.w1 / 2.0 + self.r, startY, self.r, self.w1, 180.0, 270.0, self.num_sides))
            meander.insert(pya.Box(int(negL2p/dbu), int((startY - self.r - self.w1/2.0)/dbu), int(posL2p/dbu), int((startY - self.r + self.w1/2.0)/dbu)))
            meander.insert(ex.draw_torus_arc(dbu, posL2p, startY - 2.0 * self.r, self.r, self.w1, 270.0, 90.0, self.num_sides))
            meander.insert(pya.Box(int(negL2p/dbu), int((startY - 3.0 * self.r - self.w1/2.0)/dbu), int(posL2p/dbu), int((startY - 3.0 * self.r + self.w1/2.0)/dbu)))
            meander.insert(ex.draw_torus_arc(dbu, negL2p, startY - 4.0 * self.r, self.r, self.w1, 90.0, 180.0, self.num_sides))
            
            pitch = 2.0 * self.r
            cnt = 0
            for i in range(numPeriods):
                temp_m = meander.dup()
                temp_m.transform(pya.Trans(0, int((-i * 2.0 * pitch)/dbu)))
                runnerW1.insert(temp_m)
                cnt += 1
                
            meanderLast = pya.Region(ex.draw_torus_arc(dbu, startX - self.w1 / 2.0 + self.r, startY, self.r, self.w1, 180.0, 270.0, self.num_sides))
            meanderLast.insert(pya.Box(int(negL2p/dbu), int((startY - self.r - self.w1/2.0)/dbu), int(posL2p/dbu), int((startY - self.r + self.w1/2.0)/dbu)))
            meanderLast.insert(ex.draw_torus_arc(dbu, posL2p, startY - 2.0 * self.r, self.r, self.w1, 0.0, 90.0, self.num_sides))
            meanderLast.transform(pya.Trans(0, int((-cnt * 2.0 * pitch)/dbu)))
            runnerW1.insert(meanderLast)
            
            self.cell.shapes(lyr_b).insert(runnerW1)


# 25. Anchored Flexures (Section 2.10.4)
class AnchoredFlexuresPCell(pya.PCellDeclarationHelper):
    def __init__(self, default_type="V4A"):
        super(AnchoredFlexuresPCell, self).__init__()
        self.param("type", self.TypeString, "Type", default = default_type, choices = [["V2A", "V2A"], ["V2B", "V2B"], ["V2C", "V2C"], ["V2D", "V2D"], ["V2E", "V2E"], ["V4A", "V4A"], ["V4B", "V4B"], ["V4C", "V4C"], ["V4D", "V4D"], ["V4E", "V4E"]])
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width1", self.TypeDouble, "Beam Width 1 (um)", default = 2.0)
        self.param("width2", self.TypeDouble, "Beam Width 2 (um)", default = 2.0)
        self.param("width3", self.TypeDouble, "Beam Width 3 (um)", default = 2.0)
        self.param("width4", self.TypeDouble, "Beam Width 4 (um)", default = 2.0)
        self.param("width5", self.TypeDouble, "Beam Width 5 (um)", default = 2.0)
        self.param("length1", self.TypeDouble, "Beam Length 1 (um)", default = 50.0)
        self.param("length2", self.TypeDouble, "Beam Length 2 (um)", default = 40.0)
        self.param("length3", self.TypeDouble, "Beam Length 3 (um)", default = 30.0)
        self.param("length4", self.TypeDouble, "Beam Length 4 (um)", default = 20.0)
        self.param("length5", self.TypeDouble, "Beam Length 5 (um)", default = 10.0)
        self.param("length6", self.TypeDouble, "Beam Length 6 (um)", default = 10.0)
        self.param("width_mass", self.TypeDouble, "Central Mass Width (um)", default = 30.0)
        self.param("length_mass", self.TypeDouble, "Central Mass Length (um)", default = 30.0)
        self.param("gap", self.TypeDouble, "Actuator Gap (um)", default = 5.0)
        self.param("base_height", self.TypeDouble, "Anchor Pad Height (um)", default = 15.0)
        self.param("base_width", self.TypeDouble, "Anchor Pad Width (um)", default = 20.0)
        self.param("base_extent", self.TypeDouble, "Anchor Base Extent (um)", default = 10.0)
        self.param("anchor_distance", self.TypeDouble, "Anchor Offset (um)", default = 1.0)
        self.param("connector_height", self.TypeDouble, "Connector Height (um)", default = 10.0)
        self.param("connector_width", self.TypeDouble, "Connector Width (um)", default = 4.0)
        self.param("square_height", self.TypeDouble, "Square Height (um)", default = 10.0)
        self.param("square_width", self.TypeDouble, "Square Width (um)", default = 10.0)
        self.param("amplitude", self.TypeDouble, "Meander Amplitude (um)", default = 5.0)
        self.param("periods", self.TypeInt, "Meander Periods", default = 4)

    def display_text_impl(self):
        return f"Flexure_{self.type}"

    def coerce_parameters_impl(self):
        if self.width1 <= 0: self.width1 = 0.1
        if self.length1 <= 0: self.length1 = 1.0

    def produce_impl(self):
        dbu = self.layout.dbu
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        
        ga = pya.Region()
        anchors = pya.Region()
        
        if self.type == "V4A":
            ga.insert(pya.Box(int(-self.width_mass/(2.0*dbu)), int(-self.length_mass/(2.0*dbu)), int(self.width_mass/(2.0*dbu)), int(self.length_mass/(2.0*dbu))))
            ga.insert(pya.Box(int(-self.width1/(2.0*dbu)), int(-self.length1/(2.0*dbu)), int(self.width1/(2.0*dbu)), int(self.length1/(2.0*dbu))))
            ga.insert(pya.Box(int(-self.length2/(2.0*dbu)), int(-self.width1/(2.0*dbu)), int(self.length2/(2.0*dbu)), int(self.width1/(2.0*dbu))))
            
            base = pya.Region(pya.Box(int((-self.base_extent - self.width1/2.0)/dbu), int(-self.base_height/(2.0*dbu)), int((self.base_extent + self.width1/2.0)/dbu), int(self.base_height/(2.0*dbu))))
            
            # Translate bases:
            b_top = base.dup().transform(pya.Trans(0, int((self.length1/2.0 + self.base_height/2.0)/dbu)))
            b_bot = base.dup().transform(pya.Trans(0, int((-self.length1/2.0 - self.base_height/2.0)/dbu)))
            b_right = base.dup().transform(pya.Trans(pya.Trans.R90, int((self.length2/2.0 + self.base_height/2.0)/dbu), 0))
            b_left = base.dup().transform(pya.Trans(pya.Trans.R90, int((-self.length2/2.0 - self.base_height/2.0)/dbu), 0))
            ga.insert(b_top).insert(b_bot).insert(b_right).insert(b_left)
            
            if self.anchor_distance < self.base_extent + self.width1/2.0:
                anchor_box = pya.Box(int((-self.base_extent - self.width1/2.0 + self.anchor_distance)/dbu), int((-self.base_height/2.0 + self.anchor_distance)/dbu), int((self.base_extent + self.width1/2.0 - self.anchor_distance)/dbu), int((self.base_height/2.0 - self.anchor_distance)/dbu))
                base_anc = pya.Region(anchor_box)
                
                a_top = base_anc.dup().transform(pya.Trans(0, int((self.length1/2.0 + self.base_height/2.0)/dbu)))
                a_bot = base_anc.dup().transform(pya.Trans(0, int((-self.length1/2.0 - self.base_height/2.0)/dbu)))
                a_right = base_anc.dup().transform(pya.Trans(pya.Trans.R90, int((self.length2/2.0 + self.base_height/2.0)/dbu), 0))
                a_left = base_anc.dup().transform(pya.Trans(pya.Trans.R90, int((-self.length2/2.0 - self.base_height/2.0)/dbu), 0))
                anchors.insert(a_top).insert(a_bot).insert(a_right).insert(a_left)
                
        elif self.type == "V4B":
            lengthMass = 2.0 * self.length2 + 2.0 * self.base_height + self.gap
            ga.insert(pya.Box(int(-self.width_mass/(2.0*dbu)), int(-lengthMass/(2.0*dbu)), int(self.width_mass/(2.0*dbu)), int(lengthMass/(2.0*dbu))))
            ga.insert(pya.Box(int((-self.width_mass/2.0 - self.length1)/dbu), int(-lengthMass/(2.0*dbu)), int((self.width_mass/2.0 + self.length1)/dbu), int((-lengthMass/2.0 + self.width1)/dbu)))
            ga.insert(pya.Box(int((-self.width_mass/2.0 - self.length1)/dbu), int((lengthMass/2.0 - self.width1)/dbu), int((self.width_mass/2.0 + self.length1)/dbu), int(lengthMass/(2.0*dbu))))
            ga.insert(pya.Box(int((-self.width_mass/2.0 - self.length1)/dbu), int(-lengthMass/(2.0*dbu)), int((-self.width_mass/2.0 - self.length1 + self.width1)/dbu), int((-lengthMass/2.0 + self.length2)/dbu)))
            ga.insert(pya.Box(int((self.width_mass/2.0 + self.length1 - self.width1)/dbu), int(-lengthMass/(2.0*dbu)), int((self.width_mass/2.0 + self.length1)/dbu), int((-lengthMass/2.0 + self.length2)/dbu)))
            ga.insert(pya.Box(int((-self.width_mass/2.0 - self.length1)/dbu), int((lengthMass/2.0 - self.length2)/dbu), int((-self.width_mass/2.0 - self.length1 + self.width1)/dbu), int(lengthMass/(2.0*dbu))))
            ga.insert(pya.Box(int((self.width_mass/2.0 + self.length1 - self.width1)/dbu), int((lengthMass/2.0 - self.length2)/dbu), int((self.width_mass/2.0 + self.length1)/dbu), int(lengthMass/(2.0*dbu))))
            
            bondPad = pya.Region(pya.Box(0, 0, int(self.base_width/dbu), int(self.base_height/dbu)))
            
            t1 = bondPad.dup().transform(pya.Trans(int((-self.width_mass/2.0 - self.length1 - self.base_width/2.0 + self.width1/2.0)/dbu), int((-lengthMass/2.0 + self.length2)/dbu)))
            t2 = bondPad.dup().transform(pya.Trans(int((self.width_mass/2.0 + self.length1 - self.base_width/2.0 - self.width1/2.0)/dbu), int((-lengthMass/2.0 + self.length2)/dbu)))
            t3 = bondPad.dup().transform(pya.Trans(int((-self.width_mass/2.0 - self.length1 - self.base_width/2.0 + self.width1/2.0)/dbu), int((lengthMass/2.0 - self.length2 - self.base_height)/dbu)))
            t4 = bondPad.dup().transform(pya.Trans(int((self.width_mass/2.0 + self.length1 - self.base_width/2.0 - self.width1/2.0)/dbu), int((lengthMass/2.0 - self.length2 - self.base_height)/dbu)))
            ga.insert(t1).insert(t2).insert(t3).insert(t4)
            
            if self.anchor_distance < self.base_width/2.0 and self.anchor_distance < self.base_height/2.0:
                anchor_box = pya.Box(int(self.anchor_distance/dbu), int(self.anchor_distance/dbu), int((self.base_width - self.anchor_distance)/dbu), int((self.base_height - self.anchor_distance)/dbu))
                base_anc = pya.Region(anchor_box)
                
                a1 = base_anc.dup().transform(pya.Trans(int((-self.width_mass/2.0 - self.length1 - self.base_width/2.0 + self.width1/2.0)/dbu), int((-lengthMass/2.0 + self.length2)/dbu)))
                a2 = base_anc.dup().transform(pya.Trans(int((self.width_mass/2.0 + self.length1 - self.base_width/2.0 - self.width1/2.0)/dbu), int((-lengthMass/2.0 + self.length2)/dbu)))
                a3 = base_anc.dup().transform(pya.Trans(int((-self.width_mass/2.0 - self.length1 - self.base_width/2.0 + self.width1/2.0)/dbu), int((lengthMass/2.0 - self.length2 - self.base_height)/dbu)))
                a4 = base_anc.dup().transform(pya.Trans(int((self.width_mass/2.0 + self.length1 - self.base_width/2.0 - self.width1/2.0)/dbu), int((lengthMass/2.0 - self.length2 - self.base_height)/dbu)))
                anchors.insert(a1).insert(a2).insert(a3).insert(a4)
                
        elif self.type == "V4C":
            lengthMass = 2.0 * self.base_height + self.gap
            ga.insert(pya.Box(int(-self.width_mass/(2.0*dbu)), int(-lengthMass/(2.0*dbu)), int(self.width_mass/(2.0*dbu)), int(lengthMass/(2.0*dbu))))
            
            # Upper-Right meander:
            # Polyline: (0,0) -> (0, L1 - W/2) -> (-L2 + W, L1 - W/2) -> (-L2 + W, L1 + L3 - 3*W/2)
            # -> (L4 + base_w/2 + W/2, L1 + L3 - 3*W/2) -> (L4 + base_w/2 + W/2, 0)
            pts_poly = [
                pya.DPoint(0.0, 0.0),
                pya.DPoint(0.0, self.length1 - self.width1/2.0),
                pya.DPoint(-self.length2 + self.width1, self.length1 - self.width1/2.0),
                pya.DPoint(-self.length2 + self.width1, self.length1 + self.length3 - 1.5 * self.width1),
                pya.DPoint(self.length4 + self.base_width/2.0 + self.width1/2.0, self.length1 + self.length3 - 1.5 * self.width1),
                pya.DPoint(self.length4 + self.base_width/2.0 + self.width1/2.0, 0.0)
            ]
            path = pya.Path([pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in pts_poly], int(self.width1/dbu))
            meander = pya.Region(path.simple_polygon())
            
            # top-right
            t_tr = meander.dup().transform(pya.Trans(int((self.width_mass/2.0 - self.width1/2.0)/dbu), int(lengthMass/(2.0*dbu))))
            # mirror top-left
            t_tl = t_tr.dup().transform(pya.Trans(pya.Trans.M90, 0, 0)) # reflection about Y axis
            
            # bottom meander (rotated 180):
            t_br = t_tr.dup().transform(pya.Trans(pya.Trans.R180, 0, 0))
            t_bl = t_tl.dup().transform(pya.Trans(pya.Trans.R180, 0, 0))
            
            ga.insert(t_tr).insert(t_tl).insert(t_br).insert(t_bl)
            
            bondPad = pya.Region(pya.Box(0, 0, int(self.base_width/dbu), int(self.base_height/dbu)))
            
            # base pads:
            bp_bl = bondPad.dup().transform(pya.Trans(int((-self.width_mass/2.0 - self.length4 - self.base_width)/dbu), int(-lengthMass/(2.0*dbu))))
            bp_br = bp_bl.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
            bp_tr = bondPad.dup().transform(pya.Trans(int((self.width_mass/2.0 + self.length4)/dbu), int((lengthMass/2.0 - self.base_height)/dbu)))
            bp_tl = bp_tr.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
            
            ga.insert(bp_bl).insert(bp_br).insert(bp_tr).insert(bp_tl)
            
            if self.anchor_distance < self.base_width/2.0 and self.anchor_distance < self.base_height/2.0:
                anchor_box = pya.Box(int(self.anchor_distance/dbu), int(self.anchor_distance/dbu), int((self.base_width - self.anchor_distance)/dbu), int((self.base_height - self.anchor_distance)/dbu))
                base_anc = pya.Region(anchor_box)
                
                a_bl = base_anc.dup().transform(pya.Trans(int((-self.width_mass/2.0 - self.length4 - self.base_width)/dbu), int(-lengthMass/(2.0*dbu))))
                a_br = a_bl.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
                a_tr = base_anc.dup().transform(pya.Trans(int((self.width_mass/2.0 + self.length4)/dbu), int((lengthMass/2.0 - self.base_height)/dbu)))
                a_tl = a_tr.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
                anchors.insert(a_bl).insert(a_br).insert(a_tr).insert(a_tl)
                
        elif self.type == "V4D":
            extraWidth = self.width2 + self.length1 + self.length2 + self.base_width
            ga.insert(pya.Box(int((-self.width_mass/2.0 - extraWidth)/dbu), int(-self.length_mass/(2.0*dbu)), int((self.width_mass/2.0 + extraWidth)/dbu), int(self.length_mass/(2.0*dbu))))
            
            temp_sub = pya.Box(int((-self.width_mass/2.0 - extraWidth + self.width2)/dbu), int((-self.length_mass/2.0 + self.width1)/dbu), int((self.width_mass/2.0 + extraWidth - self.width2)/dbu), int((self.length_mass/2.0 - self.width1)/dbu))
            ga -= pya.Region(temp_sub)
            
            ga.insert(pya.Box(int(-self.width_mass/(2.0*dbu)), int(-self.length_mass/(2.0*dbu)), int(self.width_mass/(2.0*dbu)), int(self.length_mass/(2.0*dbu))))
            
            # horizontal connection bars on left side:
            temp_left = pya.Region(pya.Box(int((-self.width_mass/2.0 - extraWidth + self.width2)/dbu), int((self.base_height/2.0 + self.gap/2.0 - self.width3/2.0)/dbu), int((-self.width_mass/2.0 - extraWidth + self.width2 + self.length2)/dbu), int((self.base_height/2.0 + self.gap/2.0 + self.width3/2.0)/dbu)))
            temp_left.insert(pya.Box(int((-self.width_mass/2.0 - extraWidth + self.width2)/dbu), int((-self.base_height/2.0 - self.gap/2.0 - self.width3/2.0)/dbu), int((-self.width_mass/2.0 - extraWidth + self.width2 + self.length2)/dbu), int((-self.base_height/2.0 - self.gap/2.0 + self.width3/2.0)/dbu)))
            ga.insert(temp_left)
            
            # mirror to right side
            temp_right = temp_left.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
            ga.insert(temp_right)
            
            # pads on left side:
            temp_pads_l = pya.Region(pya.Box(int((-self.width_mass/2.0 - extraWidth + self.width2 + self.length2)/dbu), int((self.gap/2.0)/dbu), int((-self.width_mass/2.0 - extraWidth + self.width2 + self.length2 + self.base_width)/dbu), int((self.gap/2.0 + self.base_height)/dbu)))
            temp_pads_l.insert(pya.Box(int((-self.width_mass/2.0 - extraWidth + self.width2 + self.length2)/dbu), int((-self.gap/2.0 - self.base_height)/dbu), int((-self.width_mass/2.0 - extraWidth + self.width2 + self.length2 + self.base_width)/dbu), int((-self.gap/2.0)/dbu)))
            ga.insert(temp_pads_l)
            
            # mirror pads to right
            temp_pads_r = temp_pads_l.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
            ga.insert(temp_pads_r)
            
            if self.anchor_distance < self.base_width/2.0 and self.anchor_distance < self.base_height/2.0:
                # anchor box templates left
                anc_l = pya.Region(pya.Box(int((-self.width_mass/2.0 - extraWidth + self.width2 + self.length2 + self.anchor_distance)/dbu), int((self.gap/2.0 + self.anchor_distance)/dbu), int((-self.width_mass/2.0 - extraWidth + self.width2 + self.length2 + self.base_width - self.anchor_distance)/dbu), int((self.gap/2.0 + self.base_height - self.anchor_distance)/dbu)))
                anc_l.insert(pya.Box(int((-self.width_mass/2.0 - extraWidth + self.width2 + self.length2 + self.anchor_distance)/dbu), int((-self.gap/2.0 - self.base_height + self.anchor_distance)/dbu), int((-self.width_mass/2.0 - extraWidth + self.width2 + self.length2 + self.base_width - self.anchor_distance)/dbu), int((-self.gap/2.0 - self.anchor_distance)/dbu)))
                # mirror to right
                anc_r = anc_l.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
                anchors.insert(anc_l).insert(anc_r)
                
        elif self.type == "V4E":
            # Rect(-width1 / 2.0, -length1 / 2.0, width1 / 2.0, length1 / 2.0)
            ga.insert(pya.Box(int(-self.width1/(2.0*dbu)), int(-self.length1/(2.0*dbu)), int(self.width1/(2.0*dbu)), int(self.length1/(2.0*dbu))))
            
            startX = -self.width1 / 2.0 - self.length3
            ga.insert(pya.Box(int(startX/dbu), int((-self.length1/2.0 - self.width3)/dbu), int((-startX)/dbu), int((-self.length1/2.0)/dbu)))
            ga.insert(pya.Box(int(startX/dbu), int((self.length1/2.0)/dbu), int((-startX)/dbu), int((self.length1/2.0 + self.width3)/dbu)))
            
            startX = -self.width1 / 2.0 - self.length2
            ga.insert(pya.Box(int(startX/dbu), int((-self.length1/2.0 + self.length4)/dbu), int((-startX)/dbu), int((-self.length1/2.0 + self.length4 + self.width2)/dbu)))
            ga.insert(pya.Box(int(startX/dbu), int((self.length1/2.0 - self.length4 - self.width2)/dbu), int((-startX)/dbu), int((self.length1/2.0 - self.length4)/dbu)))
            
            startY = -self.length1/2.0 + self.length4 - self.length5
            ga.insert(pya.Box(int((startX - self.width4)/dbu), int(startY/dbu), int(startX/dbu), int((startY + self.length5 + self.width2)/dbu)))
            ga.insert(pya.Box(int((-startX)/dbu), int(startY/dbu), int((-startX + self.width4)/dbu), int((startY + self.length5 + self.width2)/dbu)))
            
            startY = self.length1/2.0 - self.length4 - self.width2
            ga.insert(pya.Box(int((startX - self.width4)/dbu), int(startY/dbu), int(startX/dbu), int((startY + self.length5 + self.width2)/dbu)))
            ga.insert(pya.Box(int((-startX)/dbu), int(startY/dbu), int((-startX + self.width4)/dbu), int((startY + self.length5 + self.width2)/dbu)))
            
            # anchor pads templates:
            # startX = startX + width4 / 2.0 - baseWidth / 2.0 (but wait, in Java it updates startX inside the box call!)
            # Let's compute: startX_new = startX - width4 + width4/2.0 - baseWidth/2.0 = startX - width4/2.0 - baseWidth/2.0
            startX_pad = startX - self.width4/2.0 - self.base_width/2.0
            startY_top = self.length1/2.0 - self.length4 + self.length5
            
            ga.insert(pya.Box(int(startX_pad/dbu), int(startY_top/dbu), int((startX_pad + self.base_width)/dbu), int((startY_top + self.base_height)/dbu)))
            ga.insert(pya.Box(int((-startX_pad - self.base_width)/dbu), int(startY_top/dbu), int((-startX_pad)/dbu), int((startY_top + self.base_height)/dbu)))
            
            anchors.insert(pya.Box(int((startX_pad + self.anchor_distance)/dbu), int((startY_top + self.anchor_distance)/dbu), int((startX_pad + self.base_width - self.anchor_distance)/dbu), int((startY_top + self.base_height - self.anchor_distance)/dbu)))
            anchors.insert(pya.Box(int((-startX_pad - self.base_width + self.anchor_distance)/dbu), int((startY_top + self.anchor_distance)/dbu), int((-startX_pad - self.anchor_distance)/dbu), int((startY_top + self.base_height - self.anchor_distance)/dbu)))
            
            startY_bot = -self.length1/2.0 + self.length4 - self.length5 - self.base_height
            ga.insert(pya.Box(int(startX_pad/dbu), int(startY_bot/dbu), int((startX_pad + self.base_width)/dbu), int((startY_bot + self.base_height)/dbu)))
            ga.insert(pya.Box(int((-startX_pad - self.base_width)/dbu), int(startY_bot/dbu), int((-startX_pad)/dbu), int((startY_bot + self.base_height)/dbu)))
            
            anchors.insert(pya.Box(int((startX_pad + self.anchor_distance)/dbu), int((startY_bot + self.anchor_distance)/dbu), int((startX_pad + self.base_width - self.anchor_distance)/dbu), int((startY_bot + self.base_height - self.anchor_distance)/dbu)))
            anchors.insert(pya.Box(int((-startX_pad - self.base_width + self.anchor_distance)/dbu), int((startY_bot + self.anchor_distance)/dbu), int((-startX_pad - self.anchor_distance)/dbu), int((startY_bot + self.base_height - self.anchor_distance)/dbu)))
            
        elif self.type == "V2B":
            ga.insert(pya.Box(int(-self.width_mass/(2.0*dbu)), int(-self.length_mass/(2.0*dbu)), int(self.width_mass/(2.0*dbu)), int(self.length_mass/(2.0*dbu))))
            
            # Polyline: (L1/2 + W/2, -cH/2 + W/2) -> (L1/2 + W/2, cH/2 - W/2) -> (sW/2 - W/2, L2/2 + W/2) -> (-sW/2 + W/2, L2/2 + W/2)
            # -> (-L1/2 - W/2, bH/2 - W/2) -> (-L1/2 - W/2, -bH/2 + W/2) -> (-sW/2 + W/2, -L2/2 - W/2) -> (sW/2 - W/2, -L2/2 - W/2)
            pts_poly = [
                pya.DPoint(self.length1/2.0 + self.width1/2.0, -self.connector_height/2.0 + self.width1/2.0),
                pya.DPoint(self.length1/2.0 + self.width1/2.0, self.connector_height/2.0 - self.width1/2.0),
                pya.DPoint(self.square_width/2.0 - self.width1/2.0, self.length2/2.0 + self.width1/2.0),
                pya.DPoint(-self.square_width/2.0 + self.width1/2.0, self.length2/2.0 + self.width1/2.0),
                pya.DPoint(-self.length1/2.0 - self.width1/2.0, self.base_height/2.0 - self.width1/2.0),
                pya.DPoint(-self.length1/2.0 - self.width1/2.0, -self.base_height/2.0 + self.width1/2.0),
                pya.DPoint(-self.square_width/2.0 + self.width1/2.0, -self.length2/2.0 - self.width1/2.0),
                pya.DPoint(self.square_width/2.0 - self.width1/2.0, -self.length2/2.0 - self.width1/2.0)
            ]
            path = pya.Path([pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in pts_poly], int(self.width1/dbu))
            diamond = pya.Region(path.simple_polygon())
            
            # Union base: Rect(-baseWidth / 2.0, -baseHeight / 2.0, baseWidth / 2.0, baseHeight / 2.0) at (-length1/2 - baseWidth/2, 0)
            bp = pya.Region(pya.Box(int(-self.base_width/(2.0*dbu)), int(-self.base_height/(2.0*dbu)), int(self.base_width/(2.0*dbu)), int(self.base_height/(2.0*dbu))))
            diamond.insert(bp.dup().transform(pya.Trans(int((-self.length1/2.0 - self.base_width/2.0)/dbu), 0)))
            
            # Union connector: Rect(-connectorWidth / 2.0, -connectorHeight / 2.0, connectorWidth / 2.0, connectorHeight / 2.0) at (length1/2 + connectorWidth/2, 0)
            conn = pya.Region(pya.Box(int(-self.connector_width/(2.0*dbu)), int(-self.connector_height/(2.0*dbu)), int(self.connector_width/(2.0*dbu)), int(self.connector_height/(2.0*dbu))))
            diamond.insert(conn.transform(pya.Trans(int((self.length1/2.0 + self.connector_width/2.0)/dbu), 0)))
            
            # Union squares at (0, length2/2 + sH/2) and (0, -length2/2 - sH/2)
            sq = pya.Region(pya.Box(int(-self.square_width/(2.0*dbu)), int(-self.square_height/(2.0*dbu)), int(self.square_width/(2.0*dbu)), int(self.square_height/(2.0*dbu))))
            diamond.insert(sq.dup().transform(pya.Trans(0, int((self.length2/2.0 + self.square_height/2.0)/dbu))))
            diamond.insert(sq.dup().transform(pya.Trans(0, int((-self.length2/2.0 - self.square_height/2.0)/dbu))))
            
            # Place left side:
            left_side = diamond.dup().transform(pya.Trans(int((-self.width_mass/2.0 - self.length1/2.0 - self.connector_width)/dbu), 0))
            # Place mirrored right side:
            right_side = left_side.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
            ga.insert(left_side).insert(right_side)
            
            if self.anchor_distance < self.base_width/2.0 and self.anchor_distance < self.base_height/2.0:
                anc_t = pya.Region(pya.Box(int((-self.base_width/2.0 + self.anchor_distance)/dbu), int((-self.base_height/2.0 + self.anchor_distance)/dbu), int((self.base_width/2.0 - self.anchor_distance)/dbu), int((self.base_height/2.0 - self.anchor_distance)/dbu)))
                a_left = anc_t.dup().transform(pya.Trans(int((-self.width_mass/2.0 - self.length1 - self.connector_width - self.base_width/2.0)/dbu), 0))
                a_right = a_left.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
                anchors.insert(a_left).insert(a_right)
                
        elif self.type == "V2E":
            ga.insert(pya.Box(int(-self.width1/(2.0*dbu)), int(-self.length1/(2.0*dbu)), int(self.width1/(2.0*dbu)), int(self.length1/(2.0*dbu))))
            
            startX = -self.width1/2.0 - self.length3
            startY = -self.length1/2.0 - self.width3
            ga.insert(pya.Box(int(startX/dbu), int(startY/dbu), int((-startX)/dbu), int((startY + self.width3)/dbu)))
            ga.insert(pya.Box(int(startX/dbu), int((-startY - self.width3)/dbu), int((-startX)/dbu), int((-startY)/dbu)))
            
            startX = -self.width1/2.0 - self.gap - self.base_width - self.length2
            startY = -self.length1/2.0 - self.width3/2.0 - self.width4/2.0
            ga.insert(pya.Box(int(startX/dbu), int(startY/dbu), int((-startX)/dbu), int((startY + self.width4)/dbu)))
            ga.insert(pya.Box(int(startX/dbu), int((-startY - self.width4)/dbu), int((-startX)/dbu), int((-startY)/dbu)))
            
            startY = -self.base_width/2.0 + self.base_extent
            ga.insert(pya.Box(int(startX/dbu), int(startY/dbu), int((startX + self.length2)/dbu), int((startY + self.width2)/dbu)))
            ga.insert(pya.Box(int((-startX - self.length2)/dbu), int(startY/dbu), int((-startX)/dbu), int((startY + self.width2)/dbu)))
            ga.insert(pya.Box(int(startX/dbu), int((-startY - self.width2)/dbu), int((startX + self.length2)/dbu), int((-startY)/dbu)))
            ga.insert(pya.Box(int((-startX - self.length2)/dbu), int((-startY - self.width2)/dbu), int((-startX)/dbu), int((-startY)/dbu)))
            
            startX_pad = startX + self.length2
            ga.insert(pya.Box(int(startX_pad/dbu), int(-self.base_height/(2.0*dbu)), int((startX_pad + self.base_width)/dbu), int(self.base_height/(2.0*dbu))))
            ga.insert(pya.Box(int((-startX_pad - self.base_width)/dbu), int(-self.base_height/(2.0*dbu)), int((-startX_pad)/dbu), int(self.base_height/(2.0*dbu))))
            
            anchors.insert(pya.Box(int((startX_pad + self.anchor_distance)/dbu), int((-self.base_height/2.0 + self.anchor_distance)/dbu), int((startX_pad + self.base_width - self.anchor_distance)/dbu), int((self.base_height/2.0 - self.anchor_distance)/dbu)))
            anchors.insert(pya.Box(int((-startX_pad - self.base_width + self.anchor_distance)/dbu), int((-self.base_height/2.0 + self.anchor_distance)/dbu), int((-startX_pad - self.anchor_distance)/dbu), int((self.base_height/2.0 - self.anchor_distance)/dbu)))
            
            startX_side = startX_pad - self.length2 - self.width5
            startY_side = -self.length1/2.0 - self.width3/2.0 - self.width4/2.0 - self.length4
            ga.insert(pya.Box(int(startX_side/dbu), int(startY_side/dbu), int((startX_side + self.width5)/dbu), int((-startY_side)/dbu)))
            ga.insert(pya.Box(int((-startX_side - self.width5)/dbu), int(startY_side/dbu), int((-startX_side)/dbu), int((-startY_side)/dbu)))
        elif self.type == "V2A":
            ga.insert(pya.Box(int(-self.width_mass/(2.0*dbu)), int(-self.length_mass/(2.0*dbu)), int(self.width_mass/(2.0*dbu)), int(self.length_mass/(2.0*dbu))))
            boxW = 1.5 * self.width1 + self.length2 + self.base_width / 2.0
            boxH = 2.0 * self.length1 + self.length_mass
            meander = pya.Region(pya.Box(int(-boxW/(2.0*dbu)), int(-boxH/(2.0*dbu)), int(boxW/(2.0*dbu)), int(boxH/(2.0*dbu))))
            meander -= pya.Region(pya.Box(int((-boxW/2.0 + self.width1)/dbu), int((-boxH/2.0 + self.width1)/dbu), int((boxW/2.0 - self.width1)/dbu), int((boxH/2.0 - self.width1)/dbu)))
            temp = meander.dup().transform(pya.Trans(int((-self.width_mass/2.0 - boxW/2.0 + self.width1)/dbu), 0))
            ga.insert(temp)
            mirror = temp.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
            ga.insert(mirror)
            bp = pya.Region(pya.Box(int(-self.base_width/(2.0*dbu)), int(-self.base_height/(2.0*dbu)), int(self.base_width/(2.0*dbu)), int(self.base_height/(2.0*dbu))))
            bp_left = bp.dup().transform(pya.Trans(int((-self.width_mass/2.0 - self.length2 - self.base_width/2.0)/dbu), 0))
            ga.insert(bp_left)
            bp_right = bp_left.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
            ga.insert(bp_right)
            if self.anchor_distance < self.base_width/2.0 and self.anchor_distance < self.base_height/2.0:
                anc_t = pya.Region(pya.Box(int((-self.base_width/2.0 + self.anchor_distance)/dbu), int((-self.base_height/2.0 + self.anchor_distance)/dbu), int((self.base_width/2.0 - self.anchor_distance)/dbu), int((self.base_height/2.0 - self.anchor_distance)/dbu)))
                a_left = anc_t.dup().transform(pya.Trans(int((-self.width_mass/2.0 - self.length2 - self.base_width/2.0)/dbu), 0))
                a_right = a_left.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
                anchors.insert(a_left).insert(a_right)
        elif self.type == "V2C":
            ga.insert(pya.Box(int(-self.width_mass/(2.0*dbu)), int(-self.length_mass/(2.0*dbu)), int(self.width_mass/(2.0*dbu)), int(self.length_mass/(2.0*dbu))))
            startX = self.base_width / 2.0
            pts_path = [pya.DPoint(startX, 0.0), pya.DPoint(startX + self.length1, 0.0)]
            delta = self.length2 / (float(self.periods) * 2.0)
            i_val = 0.0
            while i_val < self.length2 - 1e-9:
                pts_path.append(pya.DPoint(i_val + startX + self.length1, self.amplitude))
                pts_path.append(pya.DPoint(i_val + delta + startX + self.length1, self.amplitude))
                pts_path.append(pya.DPoint(i_val + delta + startX + self.length1, -self.amplitude))
                pts_path.append(pya.DPoint(i_val + 2.0 * delta + startX + self.length1, -self.amplitude))
                pts_path.append(pya.DPoint(i_val + 2.0 * delta + startX + self.length1, 0.0))
                i_val += 2.0 * delta
            pts_path.append(pya.DPoint(startX + self.length1 + self.length2, 0.0))
            pts_path.append(pya.DPoint(startX + self.length1 + self.length2 + self.length3, 0.0))
            path_pts = [pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in pts_path]
            path = pya.Path(path_pts, int(self.width1/dbu))
            meander = pya.Region(path.simple_polygon())
            bp = pya.Region(pya.Box(int(-self.base_width/(2.0*dbu)), int(-self.base_height/(2.0*dbu)), int(self.base_width/(2.0*dbu)), int(self.base_height/(2.0*dbu))))
            meander.insert(bp)
            dx_m = -self.base_width / 2.0 - self.length1 - self.length2 - self.length3 - self.width_mass / 2.0
            meander.transform(pya.Trans(int(dx_m/dbu), 0))
            mirror = meander.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
            ga.insert(meander).insert(mirror)
            if self.anchor_distance < self.base_width/2.0 and self.anchor_distance < self.base_height/2.0:
                anc_t = pya.Region(pya.Box(int((-self.base_width/2.0 + self.anchor_distance)/dbu), int((-self.base_height/2.0 + self.anchor_distance)/dbu), int((self.base_width/2.0 - self.anchor_distance)/dbu), int((self.base_height/2.0 - self.anchor_distance)/dbu)))
                a_left = anc_t.dup().transform(pya.Trans(int(dx_m/dbu), 0))
                a_right = a_left.dup().transform(pya.Trans(pya.Trans.M90, 0, 0))
                anchors.insert(a_left).insert(a_right)
        elif self.type == "V2D":
            ga.insert(pya.Box(int(-self.width1/(2.0*dbu)), int((-self.length1/2.0 - self.width4)/dbu), int(self.width1/(2.0*dbu)), int((self.length1/2.0 + self.width4)/dbu)))
            w_ext = self.width1 / 2.0 + self.length4 + self.width2 + self.length5
            ga.insert(pya.Box(int(-w_ext/dbu), int((-self.length1/2.0 - self.width4)/dbu), int(w_ext/dbu), int((-self.length1/2.0)/dbu)))
            ga.insert(pya.Box(int(-w_ext/dbu), int((self.length1/2.0)/dbu), int(w_ext/dbu), int((self.length1/2.0 + self.width4)/dbu)))
            startX = -self.width1 / 2.0 - self.length4 - self.width2
            ga.insert(pya.Box(int(startX/dbu), int((self.length1/2.0 - self.length2 - self.width3)/dbu), int((startX + self.width2)/dbu), int((self.length1/2.0)/dbu)))
            ga.insert(pya.Box(int(startX/dbu), int((-self.length1/2.0)/dbu), int((startX + self.width2)/dbu), int((-self.length1/2.0 + self.length2 + self.width3)/dbu)))
            startX = self.width1 / 2.0 + self.length4
            ga.insert(pya.Box(int(startX/dbu), int((self.length1/2.0 - self.length2 - self.width3)/dbu), int((startX + self.width2)/dbu), int((self.length1/2.0)/dbu)))
            ga.insert(pya.Box(int(startX/dbu), int((-self.length1/2.0)/dbu), int((startX + self.width2)/dbu), int((-self.length1/2.0 + self.length2 + self.width3)/dbu)))
            startX = -self.width1 / 2.0 - self.length4 - self.width2 - self.length3
            ga.insert(pya.Box(int(startX/dbu), int((-self.length1/2.0 + self.length2)/dbu), int((startX + self.length3)/dbu), int((-self.length1/2.0 + self.length2 + self.width3)/dbu)))
            ga.insert(pya.Box(int(startX/dbu), int((self.length1/2.0 - self.length2 - self.width3)/dbu), int((startX + self.length3)/dbu), int((self.length1/2.0 - self.length2)/dbu)))
            startX = self.width1 / 2.0 + self.length4 + self.width2
            ga.insert(pya.Box(int(startX/dbu), int((-self.length1/2.0 + self.length2)/dbu), int((startX + self.length3)/dbu), int((-self.length1/2.0 + self.length2 + self.width3)/dbu)))
            ga.insert(pya.Box(int(startX/dbu), int((self.length1/2.0 - self.length2 - self.width3)/dbu), int((startX + self.length3)/dbu), int((self.length1/2.0 - self.length2)/dbu)))
            startX = -self.width1 / 2.0 - self.length4 - self.width2 - self.length3 - self.base_width
            startY = -self.length1 / 2.0 + self.length2 - self.length6
            middleElectrodeHeight = self.length1 - 2.0 * self.length2
            h_base = 2.0 * self.length6 + middleElectrodeHeight
            ga.insert(pya.Box(int(startX/dbu), int(startY/dbu), int((startX + self.base_width)/dbu), int((startY + h_base)/dbu)))
            anchors.insert(pya.Box(int((startX + self.anchor_distance)/dbu), int((startY + self.anchor_distance)/dbu), int((startX + self.base_width - self.anchor_distance)/dbu), int((startY + h_base - self.anchor_distance)/dbu)))
            startX = self.width1 / 2.0 + self.length4 + self.width2 + self.length3
            ga.insert(pya.Box(int(startX/dbu), int(startY/dbu), int((startX + self.base_width)/dbu), int((startY + h_base)/dbu)))
            anchors.insert(pya.Box(int((startX + self.anchor_distance)/dbu), int((startY + self.anchor_distance)/dbu), int((startX + self.base_width - self.anchor_distance)/dbu), int((startY + h_base - self.anchor_distance)/dbu)))
            
        ga.merge()
        anchors.merge()
        
        self.cell.shapes(layer_idx).insert(ga)
        self.cell.shapes(anchor_idx).insert(anchors)


# 26. cantileverCEPaddle Cantilevers (Section 2.10.5)
class CantileverCEPaddlePCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CantileverCEPaddlePCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width", self.TypeDouble, "Beam Width (um)", default = 5.0)
        self.param("length", self.TypeDouble, "Beam Length (um)", default = 100.0)
        self.param("rX1", self.TypeDouble, "Anchor Fillet rX1 (um)", default = 5.0)
        self.param("rY1", self.TypeDouble, "Anchor Fillet rY1 (um)", default = 5.0)
        self.param("rX2", self.TypeDouble, "Paddle Fillet rX2 (um)", default = 5.0)
        self.param("rY2", self.TypeDouble, "Paddle Fillet rY2 (um)", default = 5.0)
        self.param("num_sides", self.TypeInt, "Fillet Resolution", default = 32)
        self.param("paddle_w", self.TypeDouble, "Paddle Extra Width (um)", default = 10.0)
        self.param("paddle_l", self.TypeDouble, "Paddle Length (um)", default = 30.0)
        self.param("base_height", self.TypeDouble, "Anchor Base Height (um)", default = 20.0)
        self.param("base_extent", self.TypeDouble, "Anchor Base Extent (um)", default = 15.0)
        self.param("anchor_distance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"CantileverCEPaddle(W={self.width:.1f}, L={self.length:.1f})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.5
        if self.length <= 0: self.length = 1.0

    def produce_impl(self):
        dbu = self.layout.dbu
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        
        ga = pya.Region()
        w_tot = 2.0 * self.base_extent + self.width + 2.0 * self.rX1
        h_tot = self.base_height + self.rY1
        ga.insert(pya.Box(0, 0, int(w_tot/dbu), int(h_tot/dbu)))
        
        ellipse1 = ex.draw_ellipse(dbu, self.base_extent, self.base_height + self.rY1, self.rX1, self.rY1, self.num_sides * 4)
        ga -= pya.Region(ellipse1)
        ga -= pya.Box(0, int(self.base_height/dbu), int(self.base_extent/dbu), int((self.base_height + self.rY1)/dbu))
        
        ellipse2 = ex.draw_ellipse(dbu, self.base_extent + self.width + 2.0 * self.rX1, self.base_height + self.rY1, self.rX1, self.rY1, self.num_sides * 4)
        ga -= pya.Region(ellipse2)
        x_start = self.base_extent + self.width + 2.0 * self.rX1
        ga -= pya.Box(int(x_start/dbu), int(self.base_height/dbu), int(w_tot/dbu), int((self.base_height + self.rY1)/dbu))
        
        ga.insert(pya.Box(int((self.base_extent + self.rX1)/dbu), int((self.base_height + self.rY1)/dbu), int((self.base_extent + self.rX1 + self.width)/dbu), int((self.base_height + self.rY1 + self.length)/dbu)))
        
        ga.insert(pya.Box(int((self.base_extent + self.rX1 - self.rX2)/dbu), int((self.base_height + self.rY1 + self.length)/dbu), int((self.base_extent + self.rX1 + self.width + self.rX2)/dbu), int((self.base_height + self.rY1 + self.length + self.rY2)/dbu)))
        
        ellipse3 = ex.draw_ellipse(dbu, self.base_extent + self.rX1 - self.rX2, self.base_height + self.rY1 + self.length, self.rX2, self.rY2, self.num_sides * 4)
        ga -= pya.Region(ellipse3)
        
        ellipse4 = ex.draw_ellipse(dbu, self.base_extent + self.rX1 + self.width + self.rX2, self.base_height + self.rY1 + self.length, self.rX2, self.rY2, self.num_sides * 4)
        ga -= pya.Region(ellipse4)
        
        ga.insert(pya.Box(int((self.base_extent + self.rX1 - self.rX2 - self.paddle_w)/dbu), int((self.base_height + self.rY1 + self.length + self.rY2)/dbu), int((self.base_extent + self.rX1 + self.width + self.rX2 + self.paddle_w)/dbu), int((self.base_height + self.rY1 + self.length + self.rY2 + self.paddle_l)/dbu)))
        
        ga.merge()
        self.cell.shapes(layer_idx).insert(ga)
        
        if self.anchor_distance < self.base_extent + (self.width + 2.0 * self.rX1) / 2.0:
            anchor = pya.Box(int(self.anchor_distance/dbu), int(self.anchor_distance/dbu), int((w_tot - self.anchor_distance)/dbu), int((self.base_height - self.anchor_distance)/dbu))
            self.cell.shapes(anchor_idx).insert(anchor)


# 27. dcBeamR (Section 2.10.5)
class dcBeamRPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(dcBeamRPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width", self.TypeDouble, "Beam Width (um)", default = 5.0)
        self.param("length", self.TypeDouble, "Beam Length (um)", default = 100.0)
        self.param("base_height", self.TypeDouble, "Anchor Base Height (um)", default = 20.0)
        self.param("base_extent", self.TypeDouble, "Anchor Base Extent (um)", default = 15.0)
        self.param("anchor_distance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"dcBeamR(W={self.width:.1f}, L={self.length:.1f})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.5
        if self.length <= 0: self.length = 1.0

    def produce_impl(self):
        dbu = self.layout.dbu
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        
        ga = pya.Region()
        w_tot = 2.0 * self.base_extent + self.width
        ga.insert(pya.Box(0, 0, int(w_tot/dbu), int(self.base_height/dbu)))
        ga.insert(pya.Box(int(self.base_extent/dbu), int(self.base_height/dbu), int((self.base_extent + self.width)/dbu), int((self.base_height + self.length)/dbu)))
        ga.insert(pya.Box(0, int((self.base_height + self.length)/dbu), int(w_tot/dbu), int((2.0 * self.base_height + self.length)/dbu)))
        
        ga.merge()
        self.cell.shapes(layer_idx).insert(ga)
        
        if self.anchor_distance < self.base_extent + self.width / 2.0:
            bot_anchor = pya.Box(int(self.anchor_distance/dbu), int(self.anchor_distance/dbu), int((w_tot - self.anchor_distance)/dbu), int((self.base_height - self.anchor_distance)/dbu))
            self.cell.shapes(anchor_idx).insert(bot_anchor)
            top_anchor = bot_anchor.moved(0, int((self.base_height + self.length)/dbu))
            self.cell.shapes(anchor_idx).insert(top_anchor)


# 28. dcBeamT (Section 2.10.5)
class dcBeamTorsionalPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(dcBeamTorsionalPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width1", self.TypeDouble, "Beam Width (um)", default = 5.0)
        self.param("length1", self.TypeDouble, "Beam Length (um)", default = 100.0)
        self.param("width2", self.TypeDouble, "Mirror/Mass Width (um)", default = 20.0)
        self.param("length2", self.TypeDouble, "Mirror/Mass Length (um)", default = 20.0)
        self.param("base_height", self.TypeDouble, "Anchor Base Height (um)", default = 20.0)
        self.param("base_extent", self.TypeDouble, "Anchor Base Extent (um)", default = 15.0)
        self.param("anchor_distance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"dcBeamT(W1={self.width1:.1f}, L1={self.length1:.1f}, W2={self.width2:.1f})"

    def coerce_parameters_impl(self):
        if self.width1 <= 0: self.width1 = 0.5
        if self.length1 <= 0: self.length1 = 1.0

    def produce_impl(self):
        dbu = self.layout.dbu
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        
        ga = pya.Region()
        w_tot = 2.0 * self.base_extent + self.width1
        ga.insert(pya.Box(0, 0, int(w_tot/dbu), int(self.base_height/dbu)))
        ga.insert(pya.Box(int(self.base_extent/dbu), int(self.base_height/dbu), int((self.base_extent + self.width1)/dbu), int((self.base_height + self.length1)/dbu)))
        ga.insert(pya.Box(0, int((self.base_height + self.length1)/dbu), int(w_tot/dbu), int((2.0 * self.base_height + self.length1)/dbu)))
        
        cx = self.base_extent + self.width1 / 2.0
        cy = self.base_height + self.length1 / 2.0
        ga.insert(pya.Box(int((cx - self.width2/2.0)/dbu), int((cy - self.length2/2.0)/dbu), int((cx + self.width2/2.0)/dbu), int((cy + self.length2/2.0)/dbu)))
        
        ga.merge()
        self.cell.shapes(layer_idx).insert(ga)
        
        if self.anchor_distance < self.base_extent + self.width1 / 2.0:
            bot_anchor = pya.Box(int(self.anchor_distance/dbu), int(self.anchor_distance/dbu), int((w_tot - self.anchor_distance)/dbu), int((self.base_height - self.anchor_distance)/dbu))
            self.cell.shapes(anchor_idx).insert(bot_anchor)
            top_anchor = bot_anchor.moved(0, int((self.base_height + self.length1)/dbu))
            self.cell.shapes(anchor_idx).insert(top_anchor)


# 29. Doubly clamped array of N interacting beams (Section 2.10.5)
class dcBeamCoupledBeamsPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(dcBeamCoupledBeamsPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width", self.TypeDouble, "Coupling Beam Width (um)", default = 2.0)
        self.param("length_start", self.TypeDouble, "Start Length Ls (um)", default = 50.0)
        self.param("length_end", self.TypeDouble, "End Length Le (um)", default = 100.0)
        self.param("num_elements", self.TypeInt, "Number of Beams N", default = 5)
        self.param("base_height", self.TypeDouble, "Anchor Pad Height (um)", default = 20.0)
        self.param("base_width", self.TypeDouble, "Anchor Pad Width (um)", default = 10.0)
        self.param("anchor_distance", self.TypeDouble, "Anchor Offset (um)", default = 1.0)

    def display_text_impl(self):
        return f"dcBeamCoupledBeams(N={self.num_elements})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.5
        if self.num_elements < 2: self.num_elements = 2

    def produce_impl(self):
        dbu = self.layout.dbu
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        
        electrodesALL = pya.Region()
        anchorsALL = pya.Region()
        
        electrodesALL.insert(pya.Box(0, 0, int(self.base_width/dbu), int(self.base_height/dbu)))
        anchorsALL.insert(pya.Box(int(self.anchor_distance/dbu), int(self.anchor_distance/dbu), int((self.base_width - self.anchor_distance)/dbu), int((self.base_height - self.anchor_distance)/dbu)))
        
        lengthX = self.length_start + self.base_width
        deltaL = (self.length_end - self.length_start) / float(self.num_elements - 1)
        
        for i in range(1, self.num_elements + 1):
            electrodesALL.insert(pya.Box(int(lengthX/dbu), 0, int((lengthX + self.base_width)/dbu), int(self.base_height/dbu)))
            anchorsALL.insert(pya.Box(int((lengthX + self.anchor_distance)/dbu), int(self.anchor_distance/dbu), int((lengthX + self.base_width - self.anchor_distance)/dbu), int((self.base_height - self.anchor_distance)/dbu)))
            
            if i == self.num_elements:
                continue
            lengthX = lengthX + self.length_start + i * deltaL + self.base_width
            
        electrodesALL.insert(pya.Box(int(self.base_width/dbu), int((self.base_height/2.0 - self.width/2.0)/dbu), int(lengthX/dbu), int((self.base_height/2.0 + self.width/2.0)/dbu)))
        
        electrodesALL.merge()
        anchorsALL.merge()
        
        self.cell.shapes(layer_idx).insert(electrodesALL)
        self.cell.shapes(anchor_idx).insert(anchorsALL)


# 30. dcBeamC (Section 2.10.5)
class dcBeamCPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(dcBeamCPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width", self.TypeDouble, "Beam Width (um)", default = 5.0)
        self.param("length", self.TypeDouble, "Beam Length (um)", default = 100.0)
        self.param("rX1", self.TypeDouble, "Bot Fillet rX1 (um)", default = 5.0)
        self.param("rY1", self.TypeDouble, "Bot Fillet rY1 (um)", default = 5.0)
        self.param("rX2", self.TypeDouble, "Top Fillet rX2 (um)", default = 5.0)
        self.param("rY2", self.TypeDouble, "Top Fillet rY2 (um)", default = 5.0)
        self.param("num_sides", self.TypeInt, "Fillet Resolution", default = 32)
        self.param("base_height", self.TypeDouble, "Anchor Base Height (um)", default = 20.0)
        self.param("base_extent", self.TypeDouble, "Anchor Base Extent (um)", default = 15.0)
        self.param("anchor_distance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"dcBeamC(W={self.width:.1f}, L={self.length:.1f})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.5
        if self.length <= 0: self.length = 1.0

    def produce_impl(self):
        dbu = self.layout.dbu
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        numSides = self.num_sides * 4
        
        ga = pya.Region()
        w_tot_bot = 2.0 * self.base_extent + self.width + 2.0 * self.rX1
        ga.insert(pya.Box(0, 0, int(w_tot_bot/dbu), int((self.base_height + self.rY1)/dbu)))
        ga.insert(pya.Box(int(self.base_extent/dbu), int(self.base_height/dbu), int((self.base_extent + self.width + 2.0 * self.rX1)/dbu), int((self.base_height + self.rY1)/dbu)))
        
        ellipse1 = ex.draw_ellipse(dbu, self.base_extent, self.base_height + self.rY1, self.rX1, self.rY1, numSides)
        ga -= pya.Region(ellipse1)
        ga -= pya.Box(0, int(self.base_height/dbu), int(self.base_extent/dbu), int((self.base_height + self.rY1)/dbu))
        
        ellipse2 = ex.draw_ellipse(dbu, self.base_extent + self.width + 2.0 * self.rX1, self.base_height + self.rY1, self.rX1, self.rY1, numSides)
        ga -= pya.Region(ellipse2)
        ga -= pya.Box(int((self.base_extent + self.width + 2.0 * self.rX1)/dbu), int(self.base_height/dbu), int(w_tot_bot/dbu), int((self.base_height + self.rY1)/dbu))
        
        ga.insert(pya.Box(int((self.base_extent + self.rX1)/dbu), int((self.base_height + self.rY1)/dbu), int((self.base_extent + self.rX1 + self.width)/dbu), int((self.base_height + self.rY1 + self.length)/dbu)))
        ga.insert(pya.Box(int((self.base_extent + self.rX1 - self.rX2)/dbu), int((self.base_height + self.rY1 + self.length)/dbu), int((self.base_extent + self.rX1 + self.width + self.rX2)/dbu), int((self.base_height + self.rY1 + self.length + self.rY2)/dbu)))
        
        ellipse3 = ex.draw_ellipse(dbu, self.base_extent + self.rX1 - self.rX2, self.base_height + self.rY1 + self.length, self.rX2, self.rY2, numSides)
        ga -= pya.Region(ellipse3)
        
        ellipse4 = ex.draw_ellipse(dbu, self.base_extent + self.rX1 + self.width + self.rX2, self.base_height + self.rY1 + self.length, self.rX2, self.rY2, numSides)
        ga -= pya.Region(ellipse4)
        
        w_tot_top = 2.0 * self.base_extent + self.width + 2.0 * self.rX2
        x_min_top = self.base_extent + self.rX1 - self.rX2 - self.base_extent
        ga.insert(pya.Box(int(x_min_top/dbu), int((self.base_height + self.rY1 + self.length + self.rY2)/dbu), int((x_min_top + w_tot_top)/dbu), int((self.base_height + self.rY1 + self.length + self.rY2 + self.base_height)/dbu)))
        
        ga.merge()
        self.cell.shapes(layer_idx).insert(ga)
        
        if self.anchor_distance < self.base_extent + (self.width + 2.0 * self.rX1) / 2.0:
            bot_anchor = pya.Box(int(self.anchor_distance/dbu), int(self.anchor_distance/dbu), int((w_tot_bot - self.anchor_distance)/dbu), int((self.base_height - self.anchor_distance)/dbu))
            self.cell.shapes(anchor_idx).insert(bot_anchor)
            
        if self.anchor_distance < self.base_extent + (self.width + 2.0 * self.rX2) / 2.0:
            top_anchor = pya.Box(int(self.anchor_distance/dbu), int(self.anchor_distance/dbu), int((w_tot_top - self.anchor_distance)/dbu), int((self.base_height - self.anchor_distance)/dbu))
            top_anchor = top_anchor.moved(int((self.rX1 - self.rX2)/dbu), int((self.base_height + self.rY1 + self.length + self.rY2)/dbu))
            self.cell.shapes(anchor_idx).insert(top_anchor)


# 31. Guckel Rings (Section 2.10.8.1)
class GuckelRingPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(GuckelRingPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("ring_width", self.TypeDouble, "Ring Width (um)", default = 2.0)
        self.param("radius_start", self.TypeDouble, "Radius Start (um)", default = 20.0)
        self.param("radius_end", self.TypeDouble, "Radius End (um)", default = 20.0)
        self.param("delta_radius", self.TypeDouble, "Radius Delta/Step (um)", default = 5.0)
        self.param("num_sides", self.TypeInt, "Ring Resolution", default = 64)
        self.param("beam_width", self.TypeDouble, "Cross Beam Width (um)", default = 1.0)
        self.param("base", self.TypeDouble, "Anchor Pad Size (um)", default = 10.0)
        self.param("connector_length", self.TypeDouble, "Connector Leg Length (um)", default = 15.0)
        self.param("connector_width", self.TypeDouble, "Connector Leg Width (um)", default = 2.0)
        self.param("anchor_distance", self.TypeDouble, "Anchor Offset (um)", default = 1.0)

    def display_text_impl(self):
        return f"GuckelRing(R={self.radius_start:.1f}-{self.radius_end:.1f})"

    def coerce_parameters_impl(self):
        if self.ring_width <= 0: self.ring_width = 0.5
        if self.radius_start <= 0: self.radius_start = 5.0
        if self.radius_end < self.radius_start: self.radius_end = self.radius_start

    def produce_impl(self):
        dbu = self.layout.dbu
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        
        radius_start = self.radius_start
        radius_end = self.radius_end
        delta_radius = self.delta_radius
        if radius_end < radius_start:
            radius_end = radius_start
        if delta_radius <= 0:
            delta_radius = 1.0
            
        offsetX = 0.0
        radius = radius_start
        while radius <= radius_end + 1e-9:
            ga = pya.Region(ex.draw_torus_arc(dbu, 0.0, 0.0, radius, self.ring_width, 0.0, 360.0, self.num_sides))
            ga.insert(pya.Box(int(-self.beam_width/(2.0*dbu)), int(-radius/dbu), int(self.beam_width/(2.0*dbu)), int(radius/dbu)))
            
            temp = pya.Region(pya.Box(int(-self.base/(2.0*dbu)), int(-self.base/(2.0*dbu)), int(self.base/(2.0*dbu)), int(self.base/(2.0*dbu))))
            temp.insert(pya.Box(int(self.base/(2.0*dbu)), int(-self.connector_width/(2.0*dbu)), int((self.base/2.0 + self.connector_length + self.ring_width/2.0)/dbu), int(self.connector_width/(2.0*dbu))))
            
            bondPadOffset = -radius - self.base / 2.0 - self.connector_length - self.ring_width / 2.0
            temp.transform(pya.Trans(int(bondPadOffset/dbu), 0))
            ga.insert(temp)
            
            mirror = temp.dup()
            mirror.transform(pya.Trans(pya.Trans.R180, 0, 0))
            ga.insert(mirror)
            
            ga.transform(pya.Trans(int(offsetX/dbu), 0))
            ga.merge()
            self.cell.shapes(layer_idx).insert(ga)
            
            bondpads = pya.Region(pya.Box(int((-self.base/2.0 + self.anchor_distance)/dbu), int((-self.base/2.0 + self.anchor_distance)/dbu), int((self.base/2.0 - self.anchor_distance)/dbu), int((self.base/2.0 - self.anchor_distance)/dbu)))
            bondpads.transform(pya.Trans(int(bondPadOffset/dbu), 0))
            
            mirror_anc = bondpads.dup()
            mirror_anc.transform(pya.Trans(pya.Trans.R180, 0, 0))
            bondpads.insert(mirror_anc)
            
            bondpads.transform(pya.Trans(int(offsetX/dbu), 0))
            bondpads.merge()
            self.cell.shapes(anchor_idx).insert(bondpads)
            
            offsetX += 2.0 * abs(bondPadOffset) + delta_radius
            if radius_end == radius_start:
                break
            radius += delta_radius


# 32. Diamond Ring (Section 2.10.8.2)
class DiamondRingPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(DiamondRingPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width1", self.TypeDouble, "Ring Width 1 (um)", default = 2.0)
        self.param("width2", self.TypeDouble, "Support Width 2 (um)", default = 2.0)
        self.param("width3", self.TypeDouble, "Coupled Beam Width 3 (um)", default = 1.0)
        self.param("length1", self.TypeDouble, "Coupled Beam Ext length1 (um)", default = 20.0)
        self.param("length2", self.TypeDouble, "Vertical Support length2 (um)", default = 20.0)
        self.param("length3", self.TypeDouble, "Diamond Inner length3 (um)", default = 30.0)
        self.param("base_height", self.TypeDouble, "Anchor Pad Height (um)", default = 20.0)
        self.param("base_width", self.TypeDouble, "Anchor Pad Width (um)", default = 20.0)
        self.param("anchor_distance", self.TypeDouble, "Anchor Offset (um)", default = 1.0)

    def display_text_impl(self):
        return f"DiamondRing(L3={self.length3:.1f})"

    def coerce_parameters_impl(self):
        if self.width1 <= 0: self.width1 = 0.5
        if self.length3 <= 0: self.length3 = 5.0

    def produce_impl(self):
        dbu = self.layout.dbu
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        
        innerBoxX = math.sqrt(2.0) * self.length3 / 2.0
        outerBoxX = innerBoxX + 2.0 * self.width1
        width1Prime = math.sqrt(2.0) * self.width1 / 2.0
        middleBar = self.length3 + 2.0 * width1Prime + 2.0 * self.length1
        
        diamond = pya.Region(pya.Box(int(-outerBoxX/(2.0*dbu)), int(-outerBoxX/(2.0*dbu)), int(outerBoxX/(2.0*dbu)), int(outerBoxX/(2.0*dbu))))
        diamond -= pya.Region(pya.Box(int(-innerBoxX/(2.0*dbu)), int(-innerBoxX/(2.0*dbu)), int(innerBoxX/(2.0*dbu)), int(innerBoxX/(2.0*dbu))))
        
        # 45 deg complex rotation
        diamond.transform(pya.ICplxTrans(1.0, 45.0, False, 0, 0))
        
        diamond.insert(pya.Box(int(-middleBar/(2.0*dbu)), int(-self.width3/(2.0*dbu)), int(middleBar/(2.0*dbu)), int(self.width3/(2.0*dbu))))
        diamond.insert(pya.Box(int(-self.width2/(2.0*dbu)), int((self.length3/2.0)/dbu), int(self.width2/(2.0*dbu)), int((self.length3/2.0 + self.length2)/dbu)))
        diamond.insert(pya.Box(int(-self.width2/(2.0*dbu)), int((-self.length3/2.0 - self.length2)/dbu), int(self.width2/(2.0*dbu)), int((-self.length3/2.0)/dbu)))
        
        dy_tb = self.length2 + self.length3 / 2.0 + self.base_height / 2.0
        diamond.insert(pya.Box(int(-self.base_width/(2.0*dbu)), int((dy_tb - self.base_height/2.0)/dbu), int(self.base_width/(2.0*dbu)), int((dy_tb + self.base_height/2.0)/dbu)))
        diamond.insert(pya.Box(int(-self.base_width/(2.0*dbu)), int((-dy_tb - self.base_height/2.0)/dbu), int(self.base_width/(2.0*dbu)), int((-dy_tb + self.base_height/2.0)/dbu)))
        
        dx_lr = middleBar / 2.0 + self.base_width / 2.0
        diamond.insert(pya.Box(int((-dx_lr - self.base_width/2.0)/dbu), int(-self.base_height/(2.0*dbu)), int((-dx_lr + self.base_width/2.0)/dbu), int(self.base_height/(2.0*dbu))))
        diamond.insert(pya.Box(int((dx_lr - self.base_width/2.0)/dbu), int(-self.base_height/(2.0*dbu)), int((dx_lr + self.base_width/2.0)/dbu), int(self.base_height/(2.0*dbu))))
        
        diamond.merge()
        self.cell.shapes(layer_idx).insert(diamond)
        
        anchors = pya.Region()
        anc_template = pya.Box(int((-self.base_width/2.0 + self.anchor_distance)/dbu), int((-self.base_height/2.0 + self.anchor_distance)/dbu), int((self.base_width/2.0 - self.anchor_distance)/dbu), int((self.base_height/2.0 - self.anchor_distance)/dbu))
        
        anchors.insert(anc_template.moved(0, int(dy_tb/dbu)))
        anchors.insert(anc_template.moved(0, int(-dy_tb/dbu)))
        anchors.insert(anc_template.moved(int(-dx_lr/dbu), 0))
        anchors.insert(anc_template.moved(int(dx_lr/dbu), 0))
        
        anchors.merge()
        self.cell.shapes(anchor_idx).insert(anchors)


# 33. Suspended Fluid Cell (Section 2.10.9)
class SuspendedFluidCellPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SuspendedFluidCellPCell, self).__init__()
        self.param("layer_a", self.TypeLayer, "Layer A (Gold Pad)", default = pya.LayerInfo(1, 0))
        self.param("layer_b", self.TypeLayer, "Layer B (Waveguides/Spirals)", default = pya.LayerInfo(2, 0))
        self.param("layer_c", self.TypeLayer, "Layer C (Fluid Channel)", default = pya.LayerInfo(3, 0))
        self.param("layer_d", self.TypeLayer, "Layer D (Release Hole)", default = pya.LayerInfo(4, 0))
        self.param("layer_e", self.TypeLayer, "Layer E (Trenches/Funnels)", default = pya.LayerInfo(5, 0))
        self.param("layer_f", self.TypeLayer, "Layer F (Sensors)", default = pya.LayerInfo(6, 0))
        self.param("w1", self.TypeDouble, "Waveguide Width w1 (um)", default = 0.5)
        self.param("w2", self.TypeDouble, "Channel Entry Width w2 (um)", default = 2.0)
        self.param("w2T", self.TypeDouble, "Channel Center Width w2T (um)", default = 1.0)
        self.param("w3", self.TypeDouble, "Trench Width w3 (um)", default = 2.0)
        self.param("w4", self.TypeDouble, "Trench Spacing w4 (um)", default = 2.0)
        self.param("L1", self.TypeDouble, "Bridge Extension L1 (um)", default = 20.0)
        self.param("L2", self.TypeDouble, "S-Bend Length L2 (um)", default = 30.0)
        self.param("r", self.TypeDouble, "Torus Radius r (um)", default = 2.0)
        self.param("r1", self.TypeDouble, "Gold Pad Radius r1 (um)", default = 10.0)
        self.param("r2", self.TypeDouble, "Channel Outer Radius r2 (um)", default = 8.0)
        self.param("r3", self.TypeDouble, "Release Hole Radius r3 (um)", default = 12.0)
        self.param("num_sides", self.TypeInt, "Geometry resolution", default = 64)
        self.param("a", self.TypeDouble, "Bridge span a (um)", default = 20.0)
        self.param("b", self.TypeDouble, "Trench offset b (um)", default = 2.0)
        self.param("c", self.TypeDouble, "Taper length c (um)", default = 10.0)
        self.param("d", self.TypeDouble, "Contact pad length d (um)", default = 5.0)
        self.param("e", self.TypeDouble, "Contact pad width e (um)", default = 2.0)
        self.param("f", self.TypeDouble, "Inner contact padding f (um)", default = 0.5)
        self.param("g", self.TypeDouble, "Extension pad g (um)", default = 5.0)
        self.param("h", self.TypeDouble, "Release ring spacing h (um)", default = 2.0)
        self.param("i", self.TypeDouble, "Release gap spacing i (um)", default = 1.0)

    def display_text_impl(self):
        return f"FluidCell(R3={self.r3:.1f}, W2={self.w2:.1f})"

    def coerce_parameters_impl(self):
        if self.w1 <= 0: self.w1 = 0.1
        if self.num_sides < 8: self.num_sides = 8

    def produce_impl(self):
        dbu = self.layout.dbu
        lyr_a = self.layout.layer(self.layer_a)
        lyr_b = self.layout.layer(self.layer_b)
        lyr_c = self.layout.layer(self.layer_c)
        lyr_d = self.layout.layer(self.layer_d)
        lyr_e = self.layout.layer(self.layer_e)
        lyr_f = self.layout.layer(self.layer_f)
        
        # 1. Gold pad (layer La)
        goldPad = pya.Region(ex.draw_ellipse(dbu, 0.0, 0.0, self.r1, self.r1, self.num_sides))
        self.cell.shapes(lyr_a).insert(goldPad)
        
        # 2. Fluid channel (layer Lc)
        fluidChannel = pya.Region(ex.draw_ellipse(dbu, 0.0, 0.0, self.r2, self.r2, self.num_sides))
        fluidChannel.insert(pya.Box(int((self.r2 - self.w2)/dbu), 0, int(self.r2/dbu), int(self.L1/dbu)))
        
        funnel = pya.Region(ex.draw_sbend_funnel(dbu, self.L2, self.w2T / 2.0, self.w2, self.num_sides))
        funnel.transform(pya.ICplxTrans(1.0, 90.0, False, int((self.r2 - self.w2 / 2.0)/dbu), int(self.L1/dbu)))
        fluidChannel.insert(funnel)
        
        temp_fc = fluidChannel.dup()
        temp_fc.transform(pya.Trans(pya.Trans.R180, 0, 0))
        fluidChannel.insert(temp_fc)
        fluidChannel.merge()
        self.cell.shapes(lyr_c).insert(fluidChannel)
        
        # 3. Release (layer Ld)
        release = pya.Region(ex.draw_ellipse(dbu, 0.0, 0.0, self.r3, self.r3, self.num_sides))
        releaseGap = pya.Region(ex.draw_ellipse(dbu, 0.0, 0.0, self.r2 + self.i, self.r2 + self.i, self.num_sides))
        releaseGap.insert(pya.Box(int((self.r2 - self.w2 - self.i)/dbu), 0, int((self.r2 + self.i)/dbu), int(self.L1/dbu)))
        releaseGap.insert(pya.Box(int((-self.r2 - self.i)/dbu), int(-self.L1/dbu), int((-self.r2 + self.w2 + self.i)/dbu), 0))
        release -= releaseGap
        self.cell.shapes(lyr_d).insert(release)
        
        # 4. Trench (layer Le)
        trenchWtot = 2.0 * self.w3 + 3.0 * self.w4
        trenchRin = self.r3 + self.h
        trench = pya.Region(ex.draw_torus_arc(dbu, 0.0, 0.0, trenchRin + trenchWtot/2.0, trenchWtot, 0.0, 360.0, self.num_sides))
        
        ring1 = pya.Region(ex.draw_torus_arc(dbu, 0.0, 0.0, trenchRin + self.w4 + self.w3/2.0, self.w3, 0.0, 360.0, self.num_sides))
        trench -= ring1
        
        ring2 = pya.Region(ex.draw_torus_arc(dbu, 0.0, 0.0, trenchRin + 2.0 * self.w4 + 1.5 * self.w3, self.w3, 0.0, 360.0, self.num_sides))
        trench -= ring2
        
        trenchRectSub = pya.Region(pya.Box(int((self.r2 - self.w2 - self.b)/dbu), 0, int((self.r2 + self.b)/dbu), int((trenchRin + trenchWtot)/dbu)))
        trench -= trenchRectSub
        
        temp_trs = trenchRectSub.dup()
        temp_trs.transform(pya.Trans(pya.Trans.R180, 0, 0))
        trench -= temp_trs
        
        xR = self.r2 + self.b
        yRbot = math.sqrt(max(0.0, (self.r3 + self.h)**2 - xR**2))
        yRtop = math.sqrt(max(0.0, (self.r3 + self.h + 2.0*self.w3 + 2.0*self.w4)**2 - xR**2))
        block1 = pya.Region(pya.Box(int(xR/dbu), int(yRbot/dbu), int((xR + self.w4)/dbu), int(yRtop/dbu)))
        trench.insert(block1)
        temp_b1 = block1.dup().transform(pya.Trans(pya.Trans.R180, 0, 0))
        trench.insert(temp_b1)
        
        xL = self.r2 - self.w2 - self.b - self.w4
        yLbot = math.sqrt(max(0.0, (self.r3 + self.h + self.w4)**2 - (self.r2 - self.w2 - self.b)**2))
        yLtop = math.sqrt(max(0.0, (self.r3 + self.h + 2.0*self.w3 + 3.0*self.w4)**2 - (self.r2 - self.w2 - self.b)**2))
        block2 = pya.Region(pya.Box(int(xL/dbu), int(yLbot/dbu), int((xL + self.w4)/dbu), int(yLtop/dbu)))
        trench.insert(block2)
        temp_b2 = block2.dup().transform(pya.Trans(pya.Trans.R180, 0, 0))
        trench.insert(temp_b2)
        
        trench.merge()
        self.cell.shapes(lyr_e).insert(trench)
        
        # 5. Spiral Delay Line (layer Lb)
        rCrit = self.r2 - self.w2 / 2.0
        nTurns = int(rCrit / (4.0 * self.w1))
        if nTurns < 1:
            nTurns = 1
        extraSpace = rCrit - nTurns * 4.0 * self.w1
        extraSpace /= float(nTurns)
        
        spiral = ex.draw_spiral_delay_line(dbu, self.w1, nTurns, 3.0 * self.w1 + extraSpace, self.a, self.num_sides)
        self.cell.shapes(lyr_b).insert(spiral)
        
        # 6. Connecting waveguide and bondPad (layer Lb)
        temp_wg = pya.Region(ex.draw_torus_arc(dbu, self.r2 - self.w2 / 2.0 + self.r, self.a, self.r, self.w1, 90.0, 180.0, self.num_sides))
        temp_wg.insert(pya.Box(int((self.r2 - self.w2 / 2.0 - self.w1 / 2.0)/dbu), 0, int((self.r2 - self.w2 / 2.0 + self.w1 / 2.0)/dbu), int(self.a/dbu)))
        
        startX = self.r2 - self.w2 / 2.0 + self.r
        startY = self.a + self.r - self.w1 / 2.0
        temp_wg.insert(pya.Box(int(startX/dbu), int(startY/dbu), int((startX + self.c)/dbu), int((startY + self.w1)/dbu)))
        
        pts_bp = [
            pya.DPoint(startX + self.c, startY + self.w1),
            pya.DPoint(startX + self.c + self.d, startY + self.w1/2.0 + self.e/2.0),
            pya.DPoint(startX + self.c + self.d + self.g, startY + self.w1/2.0 + self.e/2.0),
            pya.DPoint(startX + self.c + self.d + self.g, startY + self.w1/2.0 - self.e/2.0),
            pya.DPoint(startX + self.c + self.d, startY + self.w1/2.0 - self.e/2.0),
            pya.DPoint(startX + self.c, startY)
        ]
        bondPad = pya.Region(pya.Polygon([pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in pts_bp]))
        temp_wg.insert(bondPad)
        
        temp_wg_mirr = temp_wg.dup().transform(pya.Trans(pya.Trans.R180, 0, 0))
        temp_wg.insert(temp_wg_mirr)
        temp_wg.merge()
        self.cell.shapes(lyr_b).insert(temp_wg)
        
        # 7. Smaller bondPad (layer Lf)
        smallerBondPad = bondPad.sized(int(-self.f/dbu))
        smallerBondPad.insert(pya.Box(int((startX + self.c + self.d + self.g - self.f)/dbu), int((startY + self.w1/2.0 - self.e/2.0 + self.f)/dbu), int((startX + self.c + self.d + self.g)/dbu), int((startY + self.w1/2.0 + self.e/2.0 - self.f)/dbu)))
        
        temp_sbp = smallerBondPad.dup().transform(pya.Trans(pya.Trans.R180, 0, 0))
        smallerBondPad.insert(temp_sbp)
        smallerBondPad.merge()
        self.cell.shapes(lyr_f).insert(smallerBondPad)


# =====================================================================
# EXTRA PCells Exposing CNST / MEMS Native Names
# =====================================================================

# 1. Resolution Pattern Subclasses
class ResoPatternPCell(ResolutionTestPatternPCell):
    def __init__(self):
        super(ResoPatternPCell, self).__init__(default_style="Star")

class ResoPatternPiPCell(ResolutionTestPatternPCell):
    def __init__(self):
        super(ResoPatternPiPCell, self).__init__(default_style="PiStar")

class ResoPatternLSAPCell(ResolutionTestPatternPCell):
    def __init__(self):
        super(ResoPatternLSAPCell, self).__init__(default_style="LSA")


# 2. Spirals (Archimedean, Fermat, Logarithmic)
class SpiralArchPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralArchPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("width", self.TypeDouble, "Line Width (um)", default = 1.0)
        self.param("turns", self.TypeInt, "Number of Turns", default = 5)
        self.param("separation", self.TypeDouble, "Separation (um)", default = 2.0)
        self.param("inc", self.TypeDouble, "Angle Increment (rad)", default = 0.1)

    def display_text_impl(self):
        return f"spiralArch(Turns={self.turns}, W={self.width:.1f})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.1
        if self.turns < 1: self.turns = 1
        if self.separation < 0: self.separation = 0.0
        if self.inc <= 0: self.inc = 0.01

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_spiral_arch(self.layout, self.width, self.turns, self.separation, self.inc)
        self.cell.shapes(layer_idx).insert(region)


class SpiralFermatPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralFermatPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("width", self.TypeDouble, "Line Width (um)", default = 1.0)
        self.param("turns", self.TypeInt, "Number of Turns", default = 5)
        self.param("a", self.TypeDouble, "Coefficient A", default = 2.0)
        self.param("inc", self.TypeDouble, "Angle Increment (rad)", default = 0.1)

    def display_text_impl(self):
        return f"spiralFermat(Turns={self.turns}, a={self.a:.1f})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.1
        if self.turns < 1: self.turns = 1
        if self.a <= 0: self.a = 0.1
        if self.inc <= 0: self.inc = 0.01

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_spiral_fermat(self.layout, self.width, self.turns, self.a, self.inc)
        self.cell.shapes(layer_idx).insert(region)


class SpiralLogPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralLogPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("width", self.TypeDouble, "Line Width (um)", default = 1.0)
        self.param("turns", self.TypeInt, "Number of Turns", default = 5)
        self.param("a", self.TypeDouble, "Coefficient A", default = 1.0)
        self.param("b", self.TypeDouble, "Coefficient B", default = 0.1)
        self.param("inc", self.TypeDouble, "Angle Increment (rad)", default = 0.1)

    def display_text_impl(self):
        return f"spiralLog(Turns={self.turns}, a={self.a:.1f}, b={self.b:.2f})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.1
        if self.turns < 1: self.turns = 1
        if self.a <= 0: self.a = 0.1
        if self.inc <= 0: self.inc = 0.01

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_spiral_log(self.layout, self.width, self.turns, self.a, self.b, self.inc)
        self.cell.shapes(layer_idx).insert(region)


# 3. Spiral Delay Lines
class SpiralDelayLineArchPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralDelayLineArchPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("turns", self.TypeInt, "Number of turns", default = 5)
        self.param("width", self.TypeDouble, "Width (um)", default = 1.0)
        self.param("separation", self.TypeDouble, "Separation (um)", default = 2.0)
        self.param("resolution", self.TypeInt, "Resolution", default = 64)
        self.param("length", self.TypeDouble, "Length (um)", default = 20.0)

    def display_text_impl(self):
        return f"spiralDelayLineArch(Turns={self.turns})"

    def coerce_parameters_impl(self):
        if self.turns < 1: self.turns = 1
        if self.width <= 0: self.width = 0.1
        if self.separation < 0: self.separation = 0.0
        if self.resolution < 8: self.resolution = 8

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_spiral_delay_line_generic(self.layout, "Archimedean", self.turns, self.width, self.separation, 0.0, self.resolution, self.length, False, 0.0, 0)
        self.cell.shapes(layer_idx).insert(region)


class SpiralDelayLineFermatPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralDelayLineFermatPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("turns", self.TypeInt, "Number of turns", default = 5)
        self.param("width", self.TypeDouble, "Width (um)", default = 1.0)
        self.param("a", self.TypeDouble, "Coefficient a", default = 2.0)
        self.param("resolution", self.TypeInt, "Resolution", default = 64)
        self.param("length", self.TypeDouble, "Length (um)", default = 20.0)

    def display_text_impl(self):
        return f"spiralDelayLineFermat(Turns={self.turns}, a={self.a:.1f})"

    def coerce_parameters_impl(self):
        if self.turns < 1: self.turns = 1
        if self.width <= 0: self.width = 0.1
        if self.a <= 0: self.a = 0.1
        if self.resolution < 8: self.resolution = 8

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_spiral_delay_line_generic(self.layout, "Fermat", self.turns, self.width, 0.0, self.a, self.resolution, self.length, False, 0.0, 0)
        self.cell.shapes(layer_idx).insert(region)


class SpiralDelayLineArchV2PCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralDelayLineArchV2PCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("turns", self.TypeInt, "Number of turns", default = 5)
        self.param("width", self.TypeDouble, "Width (um)", default = 1.0)
        self.param("separation", self.TypeDouble, "Separation (um)", default = 2.0)
        self.param("resolution", self.TypeInt, "Resolution", default = 64)
        self.param("skipped_turns", self.TypeInt, "Skipped Turns", default = 1)
        self.param("length", self.TypeDouble, "Length (um)", default = 20.0)

    def display_text_impl(self):
        return f"spiralDelayLineArchV2(Turns={self.turns}, Skipped={self.skipped_turns})"

    def coerce_parameters_impl(self):
        if self.turns < 1: self.turns = 1
        if self.width <= 0: self.width = 0.1
        if self.separation < 0: self.separation = 0.0
        if self.resolution < 8: self.resolution = 8
        if self.skipped_turns < 0: self.skipped_turns = 0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_spiral_delay_line_generic(self.layout, "Archimedean", self.turns, self.width, self.separation, 0.0, self.resolution, self.length, False, 0.0, self.skipped_turns)
        self.cell.shapes(layer_idx).insert(region)


class SpiralDelayLineArchInvPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralDelayLineArchInvPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("turns", self.TypeInt, "Number of turns", default = 5)
        self.param("width", self.TypeDouble, "Width (um)", default = 1.0)
        self.param("separation", self.TypeDouble, "Separation (um)", default = 2.0)
        self.param("resolution", self.TypeInt, "Resolution", default = 64)
        self.param("length", self.TypeDouble, "Length (um)", default = 20.0)
        self.param("sleeveWidth", self.TypeDouble, "Sleeve Width (um)", default = 3.0)

    def display_text_impl(self):
        return f"spiralDelayLineArchInv(Turns={self.turns})"

    def coerce_parameters_impl(self):
        if self.turns < 1: self.turns = 1
        if self.width <= 0: self.width = 0.1
        if self.separation < 0: self.separation = 0.0
        if self.resolution < 8: self.resolution = 8
        if self.sleeveWidth <= 0: self.sleeveWidth = 0.1

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_spiral_delay_line_generic(self.layout, "Archimedean", self.turns, self.width, self.separation, 0.0, self.resolution, self.length, True, self.sleeveWidth, 0)
        self.cell.shapes(layer_idx).insert(region)


class SpiralDelayLineFermatInvPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralDelayLineFermatInvPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("turns", self.TypeInt, "Number of turns", default = 5)
        self.param("width", self.TypeDouble, "Width (um)", default = 1.0)
        self.param("a", self.TypeDouble, "Coefficient a", default = 2.0)
        self.param("resolution", self.TypeInt, "Resolution", default = 64)
        self.param("length", self.TypeDouble, "Length (um)", default = 20.0)
        self.param("sleeveWidth", self.TypeDouble, "Sleeve Width (um)", default = 3.0)

    def display_text_impl(self):
        return f"spiralDelayLineFermatInv(Turns={self.turns})"

    def coerce_parameters_impl(self):
        if self.turns < 1: self.turns = 1
        if self.width <= 0: self.width = 0.1
        if self.a <= 0: self.a = 0.1
        if self.resolution < 8: self.resolution = 8
        if self.sleeveWidth <= 0: self.sleeveWidth = 0.1

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_spiral_delay_line_generic(self.layout, "Fermat", self.turns, self.width, 0.0, self.a, self.resolution, self.length, True, self.sleeveWidth, 0)
        self.cell.shapes(layer_idx).insert(region)


class SpiralDelayLineArchV2InvPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(SpiralDelayLineArchV2InvPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("turns", self.TypeInt, "Number of turns", default = 5)
        self.param("width", self.TypeDouble, "Width (um)", default = 1.0)
        self.param("separation", self.TypeDouble, "Separation (um)", default = 2.0)
        self.param("resolution", self.TypeInt, "Resolution", default = 64)
        self.param("skipped_turns", self.TypeInt, "Skipped Turns", default = 1)
        self.param("length", self.TypeDouble, "Length (um)", default = 20.0)
        self.param("sleeveWidth", self.TypeDouble, "Sleeve Width (um)", default = 3.0)

    def display_text_impl(self):
        return f"spiralDelayLineArchV2Inv(Turns={self.turns}, Skipped={self.skipped_turns})"

    def coerce_parameters_impl(self):
        if self.turns < 1: self.turns = 1
        if self.width <= 0: self.width = 0.1
        if self.separation < 0: self.separation = 0.0
        if self.resolution < 8: self.resolution = 8
        if self.skipped_turns < 0: self.skipped_turns = 0
        if self.sleeveWidth <= 0: self.sleeveWidth = 0.1

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_spiral_delay_line_generic(self.layout, "Archimedean", self.turns, self.width, self.separation, 0.0, self.resolution, self.length, True, self.sleeveWidth, self.skipped_turns)
        self.cell.shapes(layer_idx).insert(region)


# 4. MEMS Actuators & Drives
class BentBeamActuatorPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(BentBeamActuatorPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width", self.TypeDouble, "Beam Width (um)", default = 2.0)
        self.param("length1", self.TypeDouble, "Total Width (Span) (um)", default = 200.0)
        self.param("length2", self.TypeDouble, "Half Span Offset (um)", default = 100.0)
        self.param("length3", self.TypeDouble, "Apex Height (um)", default = 10.0)
        self.param("baseHeight", self.TypeDouble, "Anchor Pad Height (um)", default = 20.0)
        self.param("baseWidth", self.TypeDouble, "Anchor Pad Width (um)", default = 30.0)
        self.param("anchorDistance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"bentBeam(L1={self.length1:.1f}, H={self.length3:.1f})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.5
        if self.length1 <= 0: self.length1 = 10.0
        if self.baseHeight <= 0: self.baseHeight = 1.0
        if self.baseWidth <= 0: self.baseWidth = 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        r_struct, r_anc = ex.draw_bent_beam(
            self.layout, self.width, self.length1, self.length2, self.length3,
            self.baseHeight, self.baseWidth, self.anchorDistance
        )
        self.cell.shapes(layer_idx).insert(r_struct)
        self.cell.shapes(anchor_idx).insert(r_anc)


class BentBeamArrayPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(BentBeamArrayPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("dimple_layer", self.TypeLayer, "Dimple Layer", default = pya.LayerInfo(3, 0))
        self.param("width", self.TypeDouble, "Beam Width (um)", default = 2.0)
        self.param("length1", self.TypeDouble, "Beam Length 1 (um)", default = 200.0)
        self.param("length2", self.TypeDouble, "Beam Length 2 (um)", default = 100.0)
        self.param("length3", self.TypeDouble, "Beam Length 3 (um)", default = 10.0)
        self.param("length4", self.TypeDouble, "Beam Length 4 (um)", default = 5.0)
        self.param("hOffset", self.TypeDouble, "Offset H (um)", default = 10.0)
        self.param("pitch", self.TypeDouble, "Pitch (um)", default = 15.0)
        self.param("numElements", self.TypeInt, "Number of Elements", default = 5)
        self.param("centralBeamWidth", self.TypeDouble, "Central Beam Width (um)", default = 6.0)
        self.param("dimpleHeight", self.TypeDouble, "Dimple Height (um)", default = 2.0)
        self.param("dimpleWidth", self.TypeDouble, "Dimple Width (um)", default = 4.0)
        self.param("baseWidth", self.TypeDouble, "Anchor Pad Width (um)", default = 30.0)
        self.param("anchorDistance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"bentBeamArray(N={self.numElements})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.5
        if self.numElements < 1: self.numElements = 1
        if self.pitch <= 0: self.pitch = 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        dimple_idx = self.layout.layer(self.dimple_layer)
        r_struct, r_anc, r_dimp = ex.draw_bent_beam_array(
            self.layout, self.width, self.length1, self.length2, self.length3, self.length4,
            self.hOffset, self.pitch, self.numElements, self.centralBeamWidth,
            self.dimpleHeight, self.dimpleWidth, self.baseWidth, self.anchorDistance
        )
        self.cell.shapes(layer_idx).insert(r_struct)
        self.cell.shapes(anchor_idx).insert(r_anc)
        self.cell.shapes(dimple_idx).insert(r_dimp)


class CombDriveV1PCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CombDriveV1PCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer 1", default = pya.LayerInfo(1, 0))
        self.param("layer2", self.TypeLayer, "Structural Layer 2", default = pya.LayerInfo(2, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(3, 0))
        self.param("width1", self.TypeDouble, "Electrode Width (um)", default = 2.0)
        self.param("width2", self.TypeDouble, "Base Width 2 (um)", default = 4.0)
        self.param("length1", self.TypeDouble, "Electrode Length (um)", default = 40.0)
        self.param("length2", self.TypeDouble, "Overlap/Displacement (um)", default = 20.0)
        self.param("numElectrodes", self.TypeInt, "Number of Electrodes", default = 10)
        self.param("pitch", self.TypeDouble, "Pitch (um)", default = 10.0)
        self.param("baseHeight", self.TypeDouble, "Base Height (um)", default = 10.0)
        self.param("anchorDistance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"combDriveV1(N={self.numElectrodes})"

    def coerce_parameters_impl(self):
        if self.width1 <= 0: self.width1 = 0.5
        if self.width2 <= 0: self.width2 = 0.5
        if self.length1 <= 0: self.length1 = 5.0
        if self.length2 <= 0: self.length2 = 5.0
        if self.numElectrodes < 2: self.numElectrodes = 2
        if self.pitch <= self.width1: self.pitch = self.width1 + 1.0
        if self.baseHeight <= 0: self.baseHeight = 2.0
        if self.anchorDistance < 0: self.anchorDistance = 0.0

    def produce_impl(self):
        lyr1 = self.layout.layer(self.layer)
        lyr2 = self.layout.layer(self.layer2)
        lyr_anc = self.layout.layer(self.anchor_layer)
        r_top, r_bottom, r_anchor = ex.draw_comb_drive_v1(self.layout, self.width1, self.width2, self.length1, self.length2, self.numElectrodes, self.pitch, self.baseHeight, 0, self.anchorDistance, 0)
        self.cell.shapes(lyr1).insert(r_top)
        self.cell.shapes(lyr2).insert(r_bottom)
        self.cell.shapes(lyr_anc).insert(r_anchor)


class LinearDriveV1PCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(LinearDriveV1PCell, self).__init__()
        self.param("layer", self.TypeLayer, "Electrodes Layer", default = pya.LayerInfo(1, 0))
        self.param("rotor_layer", self.TypeLayer, "Rotor/Middle Layer", default = pya.LayerInfo(2, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(3, 0))
        self.param("width1", self.TypeDouble, "Rotor Finger Width (um)", default = 2.0)
        self.param("length1", self.TypeDouble, "Finger Length (um)", default = 40.0)
        self.param("length2", self.TypeDouble, "Rotor Base Height (um)", default = 20.0)
        self.param("length3", self.TypeDouble, "Rotor Extent (um)", default = 20.0)
        self.param("gap", self.TypeDouble, "Gap (um)", default = 2.0)
        self.param("numElectrodes", self.TypeInt, "Number of Stator Electrodes", default = 10)
        self.param("pitch", self.TypeDouble, "Stator Pitch (um)", default = 20.0)
        self.param("baseHeight", self.TypeDouble, "Stator Pad Height (um)", default = 40.0)
        self.param("baseWidth", self.TypeDouble, "Stator Pad Width (um)", default = 15.0)
        self.param("rotorPitch", self.TypeDouble, "Rotor Pitch (um)", default = 10.0)
        self.param("anchorDistance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"linearDriveV1(N={self.numElectrodes})"

    def coerce_parameters_impl(self):
        if self.width1 <= 0: self.width1 = 0.5
        if self.length1 <= 0: self.length1 = 5.0
        if self.length2 <= 0: self.length2 = 5.0
        if self.length3 < 0: self.length3 = 0.0
        if self.gap <= 0: self.gap = 0.1
        if self.numElectrodes < 2: self.numElectrodes = 2
        if self.pitch <= self.baseWidth: self.pitch = self.baseWidth + 1.0
        if self.baseHeight <= 0: self.baseHeight = 5.0
        if self.baseWidth <= 0: self.baseWidth = 5.0
        if self.rotorPitch <= 0: self.rotorPitch = 1.0
        if self.anchorDistance < 0: self.anchorDistance = 0.0

    def produce_impl(self):
        lyr_elec = self.layout.layer(self.layer)
        lyr_rotor = self.layout.layer(self.rotor_layer)
        lyr_anc = self.layout.layer(self.anchor_layer)
        r_elec, r_anc, r_rotor = ex.draw_linear_drive_v1(
            self.layout, self.width1, self.length1, self.length2, self.length3, self.gap,
            self.numElectrodes, self.pitch, self.baseHeight, self.baseWidth, self.rotorPitch, self.anchorDistance
        )
        self.cell.shapes(lyr_elec).insert(r_elec)
        self.cell.shapes(lyr_rotor).insert(r_rotor)
        self.cell.shapes(lyr_anc).insert(r_anc)


# 5. MEMS Springs
class StraightSpringPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(StraightSpringPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(4, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(7, 0))
        self.param("w", self.TypeDouble, "Spoke/Beam Width (um)", default = 1.0)
        self.param("r_hub", self.TypeDouble, "Inner Hub Radius (um)", default = 4.0)
        self.param("w_ring", self.TypeDouble, "Outer Ring Width (um)", default = 3.4)
        self.param("r_ring", self.TypeDouble, "Outer Ring Radius (um)", default = 40.0)
        self.param("n_sides", self.TypeInt, "Rendering Resolution", default = 128)
        self.param("n_spokes", self.TypeInt, "Number of Spokes", default = 18)
        self.param("anchor_dist", self.TypeDouble, "Anchor Inset (um)", default = 0.2)

    def display_text_impl(self):
        return f"straightSpring(R={self.r_ring:.1f}um, Spokes={self.n_spokes})"

    def coerce_parameters_impl(self):
        if self.w < 0.1: self.w = 0.1
        if self.r_hub < 1.0: self.r_hub = 1.0
        if self.w_ring < 0.1: self.w_ring = 0.1
        if self.r_ring <= self.r_hub + self.w_ring: self.r_ring = self.r_hub + self.w_ring + 5.0
        if self.n_sides < 8: self.n_sides = 8
        if self.n_spokes < 2: self.n_spokes = 2

    def produce_impl(self):
        lyr = self.layout.layer(self.layer)
        lyr_anc = self.layout.layer(self.anchor_layer)
        r_struct, r_anc = ex.draw_straight_spring(self.layout, lyr, lyr_anc, self.w, self.r_hub, self.w_ring, self.r_ring, self.n_sides, self.n_spokes, self.anchor_dist)
        self.cell.shapes(lyr).insert(r_struct)
        self.cell.shapes(lyr_anc).insert(r_anc)


class StraightSpringEPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(StraightSpringEPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(4, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(7, 0))
        self.param("w", self.TypeDouble, "Spoke/Beam Width (um)", default = 1.0)
        self.param("r_hub", self.TypeDouble, "Inner Hub Radius (um)", default = 4.0)
        self.param("w_ring", self.TypeDouble, "Outer Ring Width (um)", default = 3.4)
        self.param("r_ring", self.TypeDouble, "Outer Ring Radius (um)", default = 40.0)
        self.param("n_sides", self.TypeInt, "Rendering Resolution", default = 128)
        self.param("n_spokes", self.TypeInt, "Number of Spokes", default = 18)
        self.param("gap", self.TypeDouble, "Electrode Gap (um)", default = 2.0)
        self.param("electrodeWidth", self.TypeDouble, "Electrode Width (um)", default = 2.0)
        self.param("numElectrodes", self.TypeInt, "Number of Electrodes", default = 4)
        self.param("gapFraction", self.TypeDouble, "Gap Fraction", default = 0.5)
        self.param("anchorElectrodeDistance", self.TypeDouble, "Electrode Anchor Distance (um)", default = 2.0)
        self.param("anchor_dist", self.TypeDouble, "Anchor Inset (um)", default = 0.2)

    def display_text_impl(self):
        return f"straightSpringE(R={self.r_ring:.1f}um)"

    def coerce_parameters_impl(self):
        if self.w < 0.1: self.w = 0.1
        if self.r_hub < 1.0: self.r_hub = 1.0
        if self.w_ring < 0.1: self.w_ring = 0.1
        if self.r_ring <= self.r_hub + self.w_ring: self.r_ring = self.r_hub + self.w_ring + 5.0
        if self.n_sides < 8: self.n_sides = 8
        if self.numElectrodes < 1: self.numElectrodes = 1

    def produce_impl(self):
        lyr = self.layout.layer(self.layer)
        lyr_anc = self.layout.layer(self.anchor_layer)
        r_struct, r_anc = ex.draw_straight_spring_electrodes(
            self.layout, lyr, lyr_anc, self.w, self.r_hub, self.w_ring, self.r_ring, self.n_sides, self.n_spokes,
            self.gap, self.electrodeWidth, self.numElectrodes, self.gapFraction, self.anchorElectrodeDistance, self.anchor_dist
        )
        self.cell.shapes(lyr).insert(r_struct)
        self.cell.shapes(lyr_anc).insert(r_anc)


class CircularSpringEPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CircularSpringEPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(4, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(7, 0))
        self.param("w", self.TypeDouble, "Spoke/Beam Width (um)", default = 1.0)
        self.param("r_hub", self.TypeDouble, "Inner Hub Radius (um)", default = 4.0)
        self.param("w_ring", self.TypeDouble, "Outer Ring Width (um)", default = 3.4)
        self.param("r_ring", self.TypeDouble, "Outer Ring Radius (um)", default = 40.0)
        self.param("n_sides", self.TypeInt, "Rendering Resolution", default = 128)
        self.param("n_spokes", self.TypeInt, "Number of Spokes", default = 18)
        self.param("gap", self.TypeDouble, "Electrode Gap (um)", default = 2.0)
        self.param("electrodeWidth", self.TypeDouble, "Electrode Width (um)", default = 2.0)
        self.param("numElectrodes", self.TypeInt, "Number of Electrodes", default = 4)
        self.param("gapFraction", self.TypeDouble, "Gap Fraction", default = 0.5)
        self.param("anchorElectrodeDistance", self.TypeDouble, "Electrode Anchor Distance (um)", default = 2.0)
        self.param("anchor_dist", self.TypeDouble, "Anchor Inset (um)", default = 0.2)

    def display_text_impl(self):
        return f"circularSpringE(R={self.r_ring:.1f}um)"

    def coerce_parameters_impl(self):
        if self.w < 0.1: self.w = 0.1
        if self.r_hub < 1.0: self.r_hub = 1.0
        if self.w_ring < 0.1: self.w_ring = 0.1
        if self.r_ring <= self.r_hub + self.w_ring: self.r_ring = self.r_hub + self.w_ring + 5.0
        if self.n_sides < 8: self.n_sides = 8
        if self.numElectrodes < 1: self.numElectrodes = 1

    def produce_impl(self):
        lyr = self.layout.layer(self.layer)
        lyr_anc = self.layout.layer(self.anchor_layer)
        r_struct, r_anc = ex.draw_circular_spring_electrode(
            self.layout, lyr, lyr_anc, self.w, self.r_hub, self.w_ring, self.r_ring, self.n_sides, self.n_spokes,
            self.gap, self.electrodeWidth, self.numElectrodes, self.gapFraction, self.anchorElectrodeDistance, self.anchor_dist
        )
        self.cell.shapes(lyr).insert(r_struct)
        self.cell.shapes(lyr_anc).insert(r_anc)


# 6. Radial Comb Drives
class CombRadialV1PCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CombRadialV1PCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("w1", self.TypeDouble, "Stator Finger Width (um)", default = 1.5)
        self.param("r1", self.TypeDouble, "Stator Center Radius (um)", default = 100.0)
        self.param("w2", self.TypeDouble, "Rotor Finger Width (um)", default = 1.5)
        self.param("r2", self.TypeDouble, "Rotor Center Radius (um)", default = 101.5)
        self.param("wc", self.TypeDouble, "Base/Spine Width (um)", default = 4.0)
        self.param("gap", self.TypeDouble, "Gap (um)", default = 2.0)
        self.param("numElements", self.TypeInt, "Number of Fingers", default = 10)
        self.param("numSides", self.TypeInt, "Fingers Resolution", default = 64)
        self.param("thetaALL", self.TypeDouble, "Total Angular Span (deg)", default = 20.0)
        self.param("thetaOverlap", self.TypeDouble, "Angular Overlap (deg)", default = 10.0)
        self.param("anchorDistance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"combRadialV1(N={self.numElements})"

    def coerce_parameters_impl(self):
        if self.w1 <= 0: self.w1 = 0.1
        if self.w2 <= 0: self.w2 = 0.1
        if self.numElements < 1: self.numElements = 1

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        r_base, r_fingers, r_anc = ex.draw_comb_radial(
            self.layout, self.w1, self.r1, self.w2, self.r2, self.wc, self.gap,
            self.numElements, self.numSides, self.thetaALL, self.thetaOverlap, self.anchorDistance, False
        )
        self.cell.shapes(layer_idx).insert(r_base)
        self.cell.shapes(layer_idx).insert(r_fingers)
        self.cell.shapes(anchor_idx).insert(r_anc)


class CombRadialV2PCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(CombRadialV2PCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("w1", self.TypeDouble, "Stator Finger Width (um)", default = 1.5)
        self.param("r1", self.TypeDouble, "Stator Center Radius (um)", default = 100.0)
        self.param("w2", self.TypeDouble, "Rotor Finger Width (um)", default = 1.5)
        self.param("r2", self.TypeDouble, "Rotor Center Radius (um)", default = 101.5)
        self.param("wc", self.TypeDouble, "Base/Spine Width (um)", default = 4.0)
        self.param("gap", self.TypeDouble, "Gap (um)", default = 2.0)
        self.param("numElements", self.TypeInt, "Number of Fingers", default = 10)
        self.param("numSides", self.TypeInt, "Fingers Resolution", default = 64)
        self.param("thetaALL", self.TypeDouble, "Total Angular Span (deg)", default = 20.0)
        self.param("thetaOverlap", self.TypeDouble, "Angular Overlap (deg)", default = 10.0)
        self.param("anchorDistance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"combRadialV2(N={self.numElements})"

    def coerce_parameters_impl(self):
        if self.w1 <= 0: self.w1 = 0.1
        if self.w2 <= 0: self.w2 = 0.1
        if self.numElements < 1: self.numElements = 1

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        r_base, r_fingers, r_anc = ex.draw_comb_radial(
            self.layout, self.w1, self.r1, self.w2, self.r2, self.wc, self.gap,
            self.numElements, self.numSides, self.thetaALL, self.thetaOverlap, self.anchorDistance, True
        )
        self.cell.shapes(layer_idx).insert(r_base)
        self.cell.shapes(layer_idx).insert(r_fingers)
        self.cell.shapes(anchor_idx).insert(r_anc)


# 7. Folded Springs Subclasses
class FoldedSpringBasePCell(pya.PCellDeclarationHelper):
    def __init__(self, style_str="1A"):
        super(FoldedSpringBasePCell, self).__init__()
        self.style_str = style_str
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width", self.TypeDouble, "Beam Width (um)", default = 1.5)
        self.param("length1", self.TypeDouble, "Beam Length 1 (um)", default = 80.0)
        self.param("length2", self.TypeDouble, "Beam Length 2 (um)", default = 80.0)
        self.param("pitch", self.TypeDouble, "Pitch (um)", default = 10.0)
        self.param("amplitude", self.TypeDouble, "Amplitude (um)", default = 15.0)
        self.param("num_periods", self.TypeInt, "Number of Periods", default = 5)
        self.param("baseHeight", self.TypeDouble, "Base Height (um)", default = 20.0)
        self.param("baseWidth", self.TypeDouble, "Base Width (um)", default = 30.0)
        self.param("anchorDistance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)
        self.param("num_sides", self.TypeInt, "Number of Sides (circular styles)", default = 32)
        self.param("diameter", self.TypeDouble, "Diameter (um)", default = 10.0)

    def display_text_impl(self):
        return f"FoldedSpring{self.style_str}(W={self.width:.1f})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.5
        if self.length1 < 0: self.length1 = 0.0
        if self.length2 < 0: self.length2 = 0.0
        if self.pitch <= 0: self.pitch = 1.0
        if self.num_periods < 1: self.num_periods = 1
        if self.baseHeight <= 0: self.baseHeight = 1.0
        if self.baseWidth <= 0: self.baseWidth = 1.0
        if self.anchorDistance < 0: self.anchorDistance = 0.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        r_struct, r_anc = ex.draw_folded_spring(
            self.layout, self.style_str, self.width, self.length1, self.length2, self.pitch,
            self.amplitude, self.num_periods, self.baseHeight, self.baseWidth, self.anchorDistance,
            self.num_sides, self.diameter
        )
        self.cell.shapes(layer_idx).insert(r_struct)
        self.cell.shapes(anchor_idx).insert(r_anc)

class FoldedSpring1APCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring1APCell, self).__init__("1A")
class FoldedSpring1BPCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring1BPCell, self).__init__("1B")
class FoldedSpring2APCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring2APCell, self).__init__("2A")
class FoldedSpring2BPCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring2BPCell, self).__init__("2B")
class FoldedSpring2CPCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring2CPCell, self).__init__("2C")
class FoldedSpring2DPCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring2DPCell, self).__init__("2D")
class FoldedSpring2EPCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring2EPCell, self).__init__("2E")
class FoldedSpring2FPCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring2FPCell, self).__init__("2F")
class FoldedSpring2GPCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring2GPCell, self).__init__("2G")
class FoldedSpring2HPCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring2HPCell, self).__init__("2H")
class FoldedSpring2IPCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring2IPCell, self).__init__("2I")
class FoldedSpring2JPCell(FoldedSpringBasePCell):
    def __init__(self): super(FoldedSpring2JPCell, self).__init__("2J")


# 8. Flexures Subclasses
class Flexure2APCell(AnchoredFlexuresPCell):
    def __init__(self): super(Flexure2APCell, self).__init__("V2A")
class Flexure2BPCell(AnchoredFlexuresPCell):
    def __init__(self): super(Flexure2BPCell, self).__init__("V2B")
class Flexure2CPCell(AnchoredFlexuresPCell):
    def __init__(self): super(Flexure2CPCell, self).__init__("V2C")
class Flexure2DPCell(AnchoredFlexuresPCell):
    def __init__(self): super(Flexure2DPCell, self).__init__("V2D")
class Flexure2EPCell(AnchoredFlexuresPCell):
    def __init__(self): super(Flexure2EPCell, self).__init__("V2E")
class Flexure4APCell(AnchoredFlexuresPCell):
    def __init__(self): super(Flexure4APCell, self).__init__("V4A")
class Flexure4BPCell(AnchoredFlexuresPCell):
    def __init__(self): super(Flexure4BPCell, self).__init__("V4B")
class Flexure4CPCell(AnchoredFlexuresPCell):
    def __init__(self): super(Flexure4CPCell, self).__init__("V4C")
class Flexure4DPCell(AnchoredFlexuresPCell):
    def __init__(self): super(Flexure4DPCell, self).__init__("V4D")
class Flexure4EPCell(AnchoredFlexuresPCell):
    def __init__(self): super(Flexure4EPCell, self).__init__("V4E")


# 9. Cantilever Arrays Subclasses
class CantileverArrayBasePCell(pya.PCellDeclarationHelper):
    def __init__(self, style_str="Linear"):
        super(CantileverArrayBasePCell, self).__init__()
        self.style_str = style_str
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("width", self.TypeDouble, "Beam Width (um)", default = 5.0)
        self.param("startL", self.TypeDouble, "Start Length (um)", default = 50.0)
        self.param("endL", self.TypeDouble, "End Length (um)", default = 150.0)
        self.param("pitch", self.TypeDouble, "Pitch (um)", default = 15.0)
        self.param("numElements", self.TypeInt, "Number of Elements", default = 10)
        self.param("baseHeight", self.TypeDouble, "Anchor Base Height (um)", default = 20.0)
        self.param("baseExtent", self.TypeDouble, "Anchor Base Extent (um)", default = 15.0)
        self.param("variance", self.TypeDouble, "Variance / Step", default = 10.0)

    def display_text_impl(self):
        return f"CantileverArray_{self.style_str}(N={self.numElements})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.5
        if self.startL <= 0: self.startL = 1.0
        if self.endL <= 0: self.endL = 1.0
        if self.pitch <= 0: self.pitch = 1.0
        if self.numElements < 1: self.numElements = 1
        if self.baseHeight <= 0: self.baseHeight = 1.0
        if self.baseExtent < 0: self.baseExtent = 0.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        r_struct = ex.draw_cantilever_array_generic(
            self.layout, self.style_str, self.width, self.startL, self.endL, self.pitch,
            self.numElements, self.baseHeight, self.baseExtent, self.variance
        )
        self.cell.shapes(layer_idx).insert(r_struct)

class CantileverLPCell(CantileverArrayBasePCell):
    def __init__(self): super(CantileverLPCell, self).__init__("Linear")
class CantileverPPCell(CantileverArrayBasePCell):
    def __init__(self): super(CantileverPPCell, self).__init__("Percentage")
class CantileverSinePCell(CantileverArrayBasePCell):
    def __init__(self): super(CantileverSinePCell, self).__init__("Sinusoid")
class CantileverLSEPCell(CantileverArrayBasePCell):
    def __init__(self): super(CantileverLSEPCell, self).__init__("LinearSE")
class CantileverNLSEPCell(CantileverArrayBasePCell):
    def __init__(self): super(CantileverNLSEPCell, self).__init__("NonLinearSE")
class CantileverCustomPCell(CantileverArrayBasePCell):
    def __init__(self): super(CantileverCustomPCell, self).__init__("Custom")


# 10. Cantilever Singles Subclasses
class CantileverSingleBasePCell(pya.PCellDeclarationHelper):
    def __init__(self, style_str="SRect"):
        super(CantileverSingleBasePCell, self).__init__()
        self.style_str = style_str
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width", self.TypeDouble, "Width (um)", default = 5.0)
        self.param("length", self.TypeDouble, "Length (um)", default = 100.0)
        self.param("widthTop", self.TypeDouble, "Top Width (um)", default = 3.0)
        self.param("lengthTop", self.TypeDouble, "Top Length (um)", default = 20.0)
        self.param("length2", self.TypeDouble, "Length 2 (um)", default = 20.0)
        self.param("length3", self.TypeDouble, "Length 3 (um)", default = 20.0)
        self.param("hollowW", self.TypeDouble, "Hollow Width/Inset (um)", default = 1.0)
        self.param("triangleHeight", self.TypeDouble, "Triangle/Tip Height (um)", default = 5.0)
        self.param("radius", self.TypeDouble, "Curvature Radius (um)", default = 10.0)
        self.param("gap", self.TypeDouble, "Gap (um)", default = 2.0)
        self.param("rX1", self.TypeDouble, "Fillet Radius X1 (um)", default = 5.0)
        self.param("rY1", self.TypeDouble, "Fillet Radius Y1 (um)", default = 5.0)
        self.param("rX2", self.TypeDouble, "Fillet Radius X2 (um)", default = 5.0)
        self.param("rY2", self.TypeDouble, "Fillet Radius Y2 (um)", default = 5.0)
        self.param("paddleW", self.TypeDouble, "Paddle Width (um)", default = 10.0)
        self.param("paddleL", self.TypeDouble, "Paddle Length (um)", default = 30.0)
        self.param("baseHeight", self.TypeDouble, "Base Pad Height (um)", default = 20.0)
        self.param("baseExtent", self.TypeDouble, "Base Pad Extent (um)", default = 15.0)
        self.param("anchorDistance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"Cantilever_{self.style_str}(W={self.width:.1f})"

    def coerce_parameters_impl(self):
        if self.width <= 0: self.width = 0.5
        if self.length <= 0: self.length = 1.0
        if self.baseHeight <= 0: self.baseHeight = 1.0
        if self.baseExtent < 0: self.baseExtent = 0.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        r_struct, r_anchor = ex.draw_cantilever_single_generic(
            self.layout, self.style_str, self.width, self.length, self.widthTop, self.lengthTop,
            self.length2, self.length3, self.hollowW, self.triangleHeight, self.radius, self.gap,
            self.rX1, self.rY1, self.rX2, self.rY2, self.paddleW, self.paddleL, self.baseHeight,
            self.baseExtent, self.anchorDistance
        )
        self.cell.shapes(layer_idx).insert(r_struct)
        self.cell.shapes(anchor_idx).insert(r_anchor)

class CantileverSRPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverSRPCell, self).__init__("SRect")
class CantileverSTriPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverSTriPCell, self).__init__("STriangle")
class CantileverSTrapPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverSTrapPCell, self).__init__("STrapezoid")
class CantileverSPaddlePCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverSPaddlePCell, self).__init__("SPaddle")
class CantileverSCHPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverSCHPCell, self).__init__("SCurvedHalf")
class CantileverSCFPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverSCFPCell, self).__init__("SCurvedFull")
class CantileverHRPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverHRPCell, self).__init__("HRect")
class CantileverHTriPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverHTriPCell, self).__init__("HTriangle")
class CantileverHTrapPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverHTrapPCell, self).__init__("HTrapezoid")
class CantileverHPaddlePCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverHPaddlePCell, self).__init__("HPaddle")
class CantileverHCHPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverHCHPCell, self).__init__("HCurvedHalf")
class CantileverHCFPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverHCFPCell, self).__init__("HCurvedFull")
class CantileverPB2PCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverPB2PCell, self).__init__("PBase2")
class CantileverPB3PCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverPB3PCell, self).__init__("PBase3")
class CantileverURPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverURPCell, self).__init__("URect")
class CantileverUCFPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverUCFPCell, self).__init__("UCurvedFull")
class CantileverUCPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverUCPCell, self).__init__("UCurved")
class CantileverUCCPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverUCCPCell, self).__init__("UCurvedCenter")
class CantileverUCPPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverUCPPCell, self).__init__("UCurvedPaddle")
class CantileverCEPCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverCEPCell, self).__init__("CE")
class CantileverCEPaddlePCell(CantileverSingleBasePCell):
    def __init__(self): super(CantileverCEPaddlePCell, self).__init__("CEPaddle")


# 11. Gear T PCell
class GearTPCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(GearTPCell, self).__init__()
        self.param("layer", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
        self.param("rad", self.TypeDouble, "Hub Radius (um)", default = 20.0)
        self.param("width", self.TypeDouble, "Gear Tooth Base Width (um)", default = 4.0)
        self.param("height", self.TypeDouble, "Gear Tooth Height (um)", default = 6.0)
        self.param("numGears", self.TypeInt, "Number of Teeth", default = 20)
        self.param("triangleL", self.TypeDouble, "Triangle Length (um)", default = 2.0)
        self.param("numSides", self.TypeInt, "Number of Sides for circles", default = 64)

    def display_text_impl(self):
        return f"gearT(Rad={self.rad:.1f}, N={self.numGears})"

    def coerce_parameters_impl(self):
        if self.rad <= 0: self.rad = 1.0
        if self.width <= 0: self.width = 0.5
        if self.height <= 0: self.height = 0.5
        if self.numGears < 3: self.numGears = 3
        if self.numSides < 8: self.numSides = 8

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        region = ex.draw_gear_t(self.layout, self.rad, self.width, self.height, self.numGears, self.triangleL, self.numSides)
        self.cell.shapes(layer_idx).insert(region)


# 12. Doubly Clamped Torsional V2 Beam
class dcBeamT2PCell(pya.PCellDeclarationHelper):
    def __init__(self):
        super(dcBeamT2PCell, self).__init__()
        self.param("layer", self.TypeLayer, "Structural Layer", default = pya.LayerInfo(1, 0))
        self.param("anchor_layer", self.TypeLayer, "Anchor Layer", default = pya.LayerInfo(2, 0))
        self.param("width1", self.TypeDouble, "Beam Width 1 (um)", default = 2.0)
        self.param("width2", self.TypeDouble, "Beam Width 2 (um)", default = 2.0)
        self.param("width3", self.TypeDouble, "Connector Width (um)", default = 4.0)
        self.param("width4", self.TypeDouble, "Outer Frame Width (um)", default = 5.0)
        self.param("length1", self.TypeDouble, "Beam Length 1 (um)", default = 50.0)
        self.param("length2", self.TypeDouble, "Length 2 (um)", default = 20.0)
        self.param("length3", self.TypeDouble, "Connector Length (um)", default = 30.0)
        self.param("gap", self.TypeDouble, "Gap (um)", default = 5.0)
        self.param("base_height", self.TypeDouble, "Base Height (um)", default = 20.0)
        self.param("base_width", self.TypeDouble, "Base Width (um)", default = 30.0)
        self.param("anchor_distance", self.TypeDouble, "Anchor Offset (um)", default = 2.0)

    def display_text_impl(self):
        return f"dcBeamT2(L1={self.length1:.1f})"

    def coerce_parameters_impl(self):
        if self.width1 <= 0: self.width1 = 0.5
        if self.width2 <= 0: self.width2 = 0.5
        if self.length1 <= 0: self.length1 = 1.0
        if self.base_height <= 0: self.base_height = 1.0
        if self.base_width <= 0: self.base_width = 1.0

    def produce_impl(self):
        layer_idx = self.layout.layer(self.layer)
        anchor_idx = self.layout.layer(self.anchor_layer)
        r_struct, r_anc = ex.draw_dc_beam_torsional2(
            self.layout, self.width1, self.width2, self.width3, self.width4,
            self.length1, self.length2, self.length3, self.gap, self.base_height, self.base_width, self.anchor_distance
        )
        self.cell.shapes(layer_idx).insert(r_struct)
        self.cell.shapes(anchor_idx).insert(r_anc)


# 13. Coupled Arrays Base PCell
class CoupledArrayBasePCell(pya.PCellDeclarationHelper):
    def __init__(self, style_str="Rect", is_electrode=False, force_const_w=False):
        super(CoupledArrayBasePCell, self).__init__()
        self.style_str = style_str
        self.is_electrode = is_electrode
        self.force_const_w = force_const_w
        
        self.param("layerFront", self.TypeLayer, "Front Layer", default = pya.LayerInfo(1, 0))
        self.param("layerBack", self.TypeLayer, "Back Layer", default = pya.LayerInfo(2, 0))
        self.param("layerMetal", self.TypeLayer, "Metal Layer", default = pya.LayerInfo(3, 0))
        self.param("numElements", self.TypeInt, "Number of Elements", default = 5)
        self.param("L1", self.TypeDouble, "Length 1 (um)", default = 50.0)
        self.param("W1a", self.TypeDouble, "Width 1a (um)", default = 5.0)
        self.param("W1b", self.TypeDouble, "Width 1b (um)", default = 5.0)
        self.param("L2", self.TypeDouble, "Length 2 (um)", default = 50.0)
        self.param("W2a", self.TypeDouble, "Width 2a (um)", default = 5.0)
        self.param("W2b", self.TypeDouble, "Width 2b (um)", default = 5.0)
        self.param("space", self.TypeDouble, "Space (um)", default = 5.0)
        self.param("lowerSpace", self.TypeDouble, "Lower Space (um)", default = 5.0)
        self.param("hOverlap", self.TypeDouble, "Overlap Height (um)", default = 5.0)
        self.param("hElectrode", self.TypeDouble, "Electrode Height (um)", default = 10.0)
        self.param("lengthSide", self.TypeDouble, "Side Length (um)", default = 20.0)
        self.param("LB", self.TypeDouble, "LB (um)", default = 50.0)
        self.param("HB", self.TypeDouble, "HB (um)", default = 20.0)
        self.param("diameter", self.TypeDouble, "Dot Diameter (um)", default = 2.0)
        self.param("numSides", self.TypeInt, "Num Sides", default = 32)

    def display_text_impl(self):
        return f"CoupledArray_{self.style_str}(N={self.numElements})"

    def coerce_parameters_impl(self):
        if self.numElements < 1: self.numElements = 1
        if self.L1 <= 0: self.L1 = 1.0
        if self.L2 <= 0: self.L2 = 1.0
        if self.W1a <= 0: self.W1a = 0.1
        if self.W2a <= 0: self.W2a = 0.1
        if self.numSides < 8: self.numSides = 8
        if self.force_const_w:
            self.W1b = self.W1a
            self.W2b = self.W2a

    def produce_impl(self):
        dbu = self.layout.dbu
        lyrFront = self.layout.layer(self.layerFront)
        lyrBack = self.layout.layer(self.layerBack)
        lyrMetal = self.layout.layer(self.layerMetal)
        
        front, metal, back = ex.draw_coupled_array(
            self.style_str, dbu, self.numElements, self.L1, self.W1a, self.W1b,
            self.L2, self.W2a, self.W2b, self.space, self.lowerSpace, self.hOverlap,
            self.hElectrode, self.lengthSide, self.LB, self.HB, self.diameter, self.numSides,
            lyrFront, lyrBack, lyrMetal, self.is_electrode
        )
        self.cell.shapes(lyrFront).insert(front)
        self.cell.shapes(lyrMetal).insert(metal)
        self.cell.shapes(lyrBack).insert(back)

class MARAPCell(CoupledArrayBasePCell):
    def __init__(self): super(MARAPCell, self).__init__(style_str="Rect", force_const_w=True)
class MATALWPCell(CoupledArrayBasePCell):
    def __init__(self): super(MATALWPCell, self).__init__(style_str="TrapCONST")
class MATAPCell(CoupledArrayBasePCell):
    def __init__(self): super(MATAPCell, self).__init__(style_str="TrapVLW")
class MAR2PCell(CoupledArrayBasePCell):
    def __init__(self): super(MAR2PCell, self).__init__(style_str="RT2", force_const_w=True)
class MAT2PCell(CoupledArrayBasePCell):
    def __init__(self): super(MAT2PCell, self).__init__(style_str="RT2", force_const_w=False)
class MAR3PCell(CoupledArrayBasePCell):
    def __init__(self): super(MAR3PCell, self).__init__(style_str="RT3", force_const_w=True, is_electrode=False)
class MAT3PCell(CoupledArrayBasePCell):
    def __init__(self): super(MAT3PCell, self).__init__(style_str="RT3", force_const_w=False, is_electrode=False)
class MARCPCell(CoupledArrayBasePCell):
    def __init__(self): super(MARCPCell, self).__init__(style_str="RT3", force_const_w=True, is_electrode=True)

