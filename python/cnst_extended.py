import pya
import math

# =====================================================================
# EXTENDED NIST NANOLITHOGRAPHY & MEMS/NEMS PCells
# =====================================================================

# 1. Torus Wave Boundary
def draw_torus_wave(layout, rad_in, rad_out, n, amp, num_sides, phase_out_of_phase):
    dbu = layout.dbu
    pts = []
    c = 2.0 * math.pi / num_sides
    # inner boundary
    for i in range(num_sides + 1):
        angle = i * c
        r_in = rad_in + amp * math.sin(angle * n)
        pts.append(pya.Point(int(r_in * math.cos(angle) / dbu), int(r_in * math.sin(angle) / dbu)))
    # outer boundary
    for j in range(num_sides, -1, -1):
        angle = j * c
        if phase_out_of_phase:
            r_out = rad_out + amp * math.cos(angle * n)
        else:
            r_out = rad_out + amp * math.sin(angle * n)
        pts.append(pya.Point(int(r_out * math.cos(angle) / dbu), int(r_out * math.sin(angle) / dbu)))
    
    return pya.Polygon(pts)

# 2. Fractals Recursive Draw Helpers
def draw_sierpinski_carpet(dbu, x, y, size, iterations, region):
    if iterations == 0:
        region.insert(pya.Box(int((x - size/2)/dbu), int((y - size/2)/dbu), int((x + size/2)/dbu), int((y + size/2)/dbu)))
    else:
        new_size = size / 3.0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                draw_sierpinski_carpet(dbu, x + dx * size/3.0, y + dy * size/3.0, new_size, iterations - 1, region)

def draw_sierpinski_triangle(dbu, x, y, L, iterations, region):
    if iterations == 0:
        pts = [
            pya.Point(int(x/dbu), int(y/dbu)),
            pya.Point(int((x + L/2)/dbu), int((y + L)/dbu)),
            pya.Point(int((x + L)/dbu), int(y/dbu))
        ]
        region.insert(pya.Polygon(pts))
    else:
        draw_sierpinski_triangle(dbu, x, y, L/2, iterations - 1, region)
        draw_sierpinski_triangle(dbu, x + L/4, y + L/2, L/2, iterations - 1, region)
        draw_sierpinski_triangle(dbu, x + L/2, y, L/2, iterations - 1, region)

def draw_vicsek_saltire(dbu, x, y, L, iterations, region):
    if iterations == 0:
        hl = L / 2.0
        offsets = [(0.0, 0.0), (-L, -L), (L, -L), (L, L), (-L, L)]
        for dx, dy in offsets:
            cx, cy = x + dx, y + dy
            region.insert(pya.Box(int((cx - hl)/dbu), int((cy - hl)/dbu), int((cx + hl)/dbu), int((cy + hl)/dbu)))
    else:
        offsets = [(0.0, 0.0), (-L, -L), (L, -L), (L, L), (-L, L)]
        for dx, dy in offsets:
            draw_vicsek_saltire(dbu, x + dx, y + dy, L/3.0, iterations - 1, region)

def draw_vicsek_cross(dbu, x, y, L, iterations, region):
    if iterations == 0:
        hl = L / 2.0
        offsets = [(0.0, 0.0), (-L, 0.0), (0.0, -L), (L, 0.0), (0.0, L)]
        for dx, dy in offsets:
            cx, cy = x + dx, y + dy
            region.insert(pya.Box(int((cx - hl)/dbu), int((cy - hl)/dbu), int((cx + hl)/dbu), int((cy + hl)/dbu)))
    else:
        offsets = [(0.0, 0.0), (-L, 0.0), (0.0, -L), (L, 0.0), (0.0, L)]
        for dx, dy in offsets:
            draw_vicsek_cross(dbu, x + dx, y + dy, L/3.0, iterations - 1, region)

# 3. Interdigitated Electrodes Draw Helper
def draw_interdigitated_electrodes(layout, type_val, w1, w2, length1, length2, overlap, num_elec, pitch, base_h, base_w):
    dbu = layout.dbu
    region = pya.Region()
    
    if type_val in [1, 2]:
        offset_y = 0.0
        if type_val == 2:
            offset_y = -base_h + w2
        # Base pad
        region.insert(pya.Box(0, int(offset_y/dbu), int(base_w/dbu), int((offset_y + base_h)/dbu)))
        # Spine
        spine_r = pya.Box(int(base_w/dbu), 0, int((base_w + length2 + (num_elec - 1)*pitch + w1)/dbu), int(w2/dbu))
        region.insert(spine_r)
        
        # Fingers
        start_x = base_w + length2
        for i in range(num_elec):
            fx = start_x + i * pitch
            region.insert(pya.Box(int(fx/dbu), int(w2/dbu), int((fx + w1)/dbu), int((w2 + length1)/dbu)))
            
        # Rotate 180 and union
        if overlap <= length1:
            temp = region.dup()
            offset_x = (num_elec - 1) * pitch + 2.0 * start_x + w1 - pitch / 2.0
            offset_y_shift = 2.0 * length1 + 2.0 * w2 - overlap
            
            trans = pya.Trans(pya.Trans.R180, int(offset_x/dbu), int(offset_y_shift/dbu))
            temp.transform(trans)
            region.insert(temp)
            
        if type_val == 2:
            region.transform(pya.Trans(0, int(-offset_y/dbu)))
            
    elif type_val in [3, 4]:
        offset_y_base = 0.0
        if type_val == 4:
            offset_y_base = -base_h + w2
            
        bond_pad = pya.Region(pya.Box(0, int(offset_y_base/dbu), int(base_w/dbu), int((offset_y_base + base_h)/dbu)))
        region.insert(bond_pad.dup())
        
        # Bottom spine
        region.insert(pya.Box(int(base_w/dbu), 0, int((base_w + length2 + (num_elec - 1)*pitch + w1)/dbu), int(w2/dbu)))
        
        # Second bond pad shifted in Y
        offset_y = 2.0 * length1 + 2.0 * w2 - base_h - overlap
        temp_pad = bond_pad.dup()
        if type_val == 4:
            temp_pad.transform(pya.Trans(0, int((offset_y - 2.0 * offset_y_base)/dbu)))
        else:
            temp_pad.transform(pya.Trans(0, int(offset_y/dbu)))
        region.insert(temp_pad)
        
        # Top spine
        region.insert(pya.Box(int(base_w/dbu), int((offset_y + base_h - w2)/dbu), int((base_w + length2 + (num_elec - 1)*pitch + w1 + pitch/2.0)/dbu), int((offset_y + base_h)/dbu)))
        
        # Fingers
        start_x = base_w + length2
        for i in range(num_elec + 1):
            if i < num_elec:
                region.insert(pya.Box(int((i*pitch + start_x)/dbu), int(w2/dbu), int((i*pitch + start_x + w1)/dbu), int((w2 + length1)/dbu)))
            
            fy_start = w2 + length1 - overlap
            fy_end = offset_y + base_h - w2
            region.insert(pya.Box(int((i*pitch + start_x - pitch/2.0)/dbu), int(fy_start/dbu), int((i*pitch + start_x + w1 - pitch/2.0)/dbu), int(fy_end/dbu)))
            
        if type_val == 4:
            region.transform(pya.Trans(0, int(-offset_y_base/dbu)))
            
    elif type_val == 5:
        region.insert(pya.Box(0, 0, int(base_w/dbu), int(base_h/dbu)))
        region.insert(pya.Box(int(base_w/dbu), int((base_h/2.0 - w2/2.0)/dbu), int((base_w + length2 + w2)/dbu), int((base_h/2.0 + w2/2.0)/dbu)))
        
        center_offset_y = (2.0 * length1 + 2.0 * w2 - overlap) / 2.0
        start_x = base_w + length2 + w2
        start_y = base_h / 2.0 + w2 / 2.0
        
        region.insert(pya.Box(int(start_x/dbu), int((base_h/2.0 - center_offset_y)/dbu), int((start_x + w2)/dbu), int(start_y/dbu)))
        region.insert(pya.Box(int((start_x + w2)/dbu), int((base_h/2.0 - center_offset_y)/dbu), int((start_x + w2 + (num_elec - 1)*pitch + pitch)/dbu), int((base_h/2.0 - center_offset_y + w2)/dbu)))
        
        start_x_f = start_x + w2 + pitch - w1
        for i in range(num_elec):
            fx = start_x_f + i * pitch
            region.insert(pya.Box(int(fx/dbu), int((base_h/2.0 - center_offset_y)/dbu), int((fx + w1)/dbu), int((base_h/2.0 - center_offset_y + length1 + w2)/dbu)))
            
        if overlap <= length1:
            temp = region.dup()
            offset_x = (num_elec - 1) * pitch + 2.0 * start_x_f + w1 - pitch / 2.0
            trans = pya.Trans(pya.Trans.R180, int(offset_x/dbu), int(base_h/dbu))
            temp.transform(trans)
            region.insert(temp)
            
    return region

# 4. Custom Barcode Draw Helper
def draw_barcode_39(layout, text, x_start, y_start, height, bar_width):
    dbu = layout.dbu
    region = pya.Region()
    
    # Simple Code 39 character mapping (9 bits: 1 = thick, 0 = thin; 5 bars, 4 spaces)
    # W = thick bar, w = thin bar, S = thick space, s = thin space
    # For simplicity, we just use a small set of characters or a standard pattern:
    code39_map = {
        '0': "101001101", '1': "110100101", '2': "101100101", '3': "110110010",
        '4': "101011001", '5': "110101100", '6': "101101100", '7': "101001101",
        '8': "110100110", '9': "101100110", 'A': "110100001", 'B': "101100001",
        'C': "110110000", 'D': "101011000", 'E': "110101100", 'F': "101101100",
        '-': "100101101", '*': "100110110"
    }
    
    # Start/stop symbol
    full_text = "*" + text.upper() + "*"
    curr_x = x_start
    
    for char in full_text:
        pattern = code39_map.get(char, "101001101")
        # Pattern has 9 elements: 5 bars, 4 spaces
        # Let's alternate drawing bars
        for idx, bit in enumerate(pattern):
            is_bar = (idx % 2 == 0)
            is_thick = (bit == '1')
            w = bar_width * 3.0 if is_thick else bar_width
            
            if is_bar:
                region.insert(pya.Box(int(curr_x/dbu), int(y_start/dbu), int((curr_x + w)/dbu), int((y_start + height)/dbu)))
            curr_x += w
        # Add character spacing
        curr_x += bar_width * 2.0
        
    return region

# 5. Bezier Curve Utilities
def compute_bezier_pts(x1, y1, cx1, cy1, cx2, cy2, x2, y2, n_pts):
    pts = []
    for i in range(n_pts + 1):
        t = i / float(n_pts)
        u = 1.0 - t
        # P(t) = u^3 * P0 + 3 * u^2 * t * P1 + 3 * u * t^2 * P2 + t^3 * P3
        bx = u**3 * x1 + 3.0 * u**2 * t * cx1 + 3.0 * u * t**2 * cx2 + t**3 * x2
        by = u**3 * y1 + 3.0 * u**2 * t * cy1 + 3.0 * u * t**2 * cy2 + t**3 * y2
        pts.append((bx, by))
    return pts

# 6. Smooth transitions (Fillets)
def create_fillet_points(x_center, y_center, r_x, r_y, start_deg, end_deg, n_pts):
    pts = []
    start_rad = math.radians(start_deg)
    end_rad = math.radians(end_deg)
    step = (end_rad - start_rad) / n_pts
    for i in range(n_pts + 1):
        ang = start_rad + i * step
        pts.append((x_center + r_x * math.cos(ang), y_center + r_y * math.sin(ang)))
    return pts

# 7. Anchors helper
def create_dc_anchors(dbu, width, base_h, base_ext, anchor_dist, anchor_layer):
    # Left anchor
    ax1 = anchor_dist
    ay1 = anchor_dist
    ax2 = base_ext - anchor_dist
    ay2 = base_h - anchor_dist
    r_anc = pya.Region()
    if ax1 < ax2 and ay1 < ay2:
        r_anc.insert(pya.Box(int(ax1/dbu), int(ay1/dbu), int(ax2/dbu), int(ay2/dbu)))
        
    # Right anchor (mirrored)
    bx1 = base_ext + width + anchor_dist
    bx2 = 2.0 * base_ext + width - anchor_dist
    if bx1 < bx2:
        r_anc.insert(pya.Box(int(bx1/dbu), int(ay1/dbu), int(bx2/dbu), int(ay2/dbu)))
        
    return r_anc

# 8. Grating Coupler Hyperbolic Teeth Helper
def draw_grating_teeth(layout, Q1, lambda0, nEff, nCladding, theta, thetaC, gratingPeriod, ratio, numElements, numSides, endcaps):
    dbu = layout.dbu
    region = pya.Region()
    angle_start = -abs(thetaC) / 2.0
    c = abs(thetaC) * (math.pi / 180.0) / numSides
    
    for k in range(Q1 - numElements, Q1):
        pts_forward = []
        pts_backward = []
        for i in range(numSides + 1):
            phi = math.radians(angle_start) + i * c
            r = (k * lambda0) / (nEff - nCladding * math.cos(phi) * math.cos(theta))
            if endcaps:
                r -= gratingPeriod * ratio / 2.0
            x = r * math.cos(phi)
            y = r * math.sin(phi)
            pts_forward.append(pya.Point(int(x/dbu), int(y/dbu)))
            
        if endcaps:
            # Strokepath with width = gratingPeriod * ratio
            w_dbu = int((gratingPeriod * ratio)/dbu)
            path = pya.Path(pts_forward, w_dbu)
            region.insert(path.simple_polygon())
        else:
            # Draw closed polygon by sweeping back on inner boundary
            for j in range(numSides, -1, -1):
                phi = math.radians(angle_start) + j * c
                r = (k * lambda0) / (nEff - nCladding * math.cos(phi) * math.cos(theta)) - gratingPeriod * ratio
                x = r * math.cos(phi)
                y = r * math.sin(phi)
                pts_backward.append(pya.Point(int(x/dbu), int(y/dbu)))
            poly_pts = pts_forward + pts_backward
            region.insert(pya.Polygon(poly_pts))
            
    return region

# 9. Ellipse Helper
def draw_ellipse(dbu, x, y, rx, ry, num_sides):
    pts = []
    da = 2.0 * math.pi / num_sides
    for i in range(num_sides):
        angle = i * da
        pts.append(pya.Point(int((x + rx * math.cos(angle))/dbu), int((y + ry * math.sin(angle))/dbu)))
    return pya.Polygon(pts)

# 10. Torus Arc Helper (draws a hollow circular sector/arc)
def draw_torus_arc(dbu, x, y, r, w, angle_start, angle_stop, num_sides):
    rin = r - w / 2.0
    r_out = r + w / 2.0
    rad_start = math.radians(angle_start)
    rad_stop = math.radians(angle_stop)
    angle_diff = angle_stop - angle_start
    if angle_diff < 0:
        angle_diff += 360.0
    
    pts = []
    da = math.radians(angle_diff) / num_sides
    # inner boundary sweep
    for i in range(num_sides + 1):
        a = rad_start + i * da
        pts.append(pya.Point(int((x + rin * math.cos(a))/dbu), int((y + rin * math.sin(a))/dbu)))
    # outer boundary sweep reversed
    for i in range(num_sides, -1, -1):
        a = rad_start + i * da
        pts.append(pya.Point(int((x + r_out * math.cos(a))/dbu), int((y + r_out * math.sin(a))/dbu)))
    return pya.Polygon(pts)

# 11. S-bend Funnel Helper (symmetric taper/transition via Bezier curves)
def draw_sbend_funnel(dbu, L, H, w1, n_points):
    # control points are (L/2, w1/2) and (L/2, H - w1/2), start at (0, w1/2), end at (L, H)
    pts = []
    for step in range(n_points + 1):
        t = step / float(n_points)
        omt = 1.0 - t
        x = 3.0 * omt * omt * t * (L/2.0) + 3.0 * omt * t * t * (L/2.0) + t * t * t * L
        y = omt * omt * omt * (w1/2.0) + 3.0 * omt * omt * t * (w1/2.0) + 3.0 * omt * t * t * (H - w1/2.0) + t * t * t * H
        pts.append((x, y))
    
    poly_pts = []
    for x, y in pts:
        poly_pts.append(pya.Point(int(x/dbu), int(y/dbu)))
    # mirror upper curve along the central axis (y=0) to form the closed funnel shape
    for x, y in reversed(pts):
        poly_pts.append(pya.Point(int(x/dbu), int(-y/dbu)))
    return pya.Polygon(poly_pts)

# 12. Double Spiral Delay Line (Archimedean)
def draw_spiral_delay_line(dbu, w1, n_turns, separation, length, num_sides):
    a_param = (separation + w1) / (2.0 * math.pi)
    upper_lim = 2.0 * n_turns * math.pi
    inc = 2.0 * math.pi / num_sides
    steps = int(upper_lim / inc)
    
    # Spiral 1 (theta: 0 to upper_lim)
    spiral1 = []
    for step in range(steps + 1):
        theta = step * inc
        r = a_param * theta
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        spiral1.append(pya.DPoint(x, y))
    # append straight extension y + length
    last = spiral1[-1]
    spiral1.append(pya.DPoint(last.x, last.y + length))
    
    # Spiral 2 (theta: 0 to upper_lim, r = -a * theta)
    spiral2 = []
    for step in range(steps + 1):
        theta = step * inc
        r = -a_param * theta
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        spiral2.append(pya.DPoint(x, y))
    # append straight extension y - length
    last = spiral2[-1]
    spiral2.append(pya.DPoint(last.x, last.y - length))
    
    spiral2.reverse()
    combined = spiral2 + spiral1
    
    pts = [pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in combined]
    path = pya.Path(pts, int(w1/dbu))
    return pya.Region(path.simple_polygon())

# 13. Stress-Relief Beam with Curved Ends (Anchor Fillets)
def draw_beam_curved_ends(dbu, L, W, r, num_sides, centered):
    beam = pya.Region(pya.Box(0, int(-W/(2.0*dbu)), int(L/dbu), int(W/(2.0*dbu))))
    
    # endBox at (0,0) going in +Y: rect from -r - W/2 to r + W/2, y from 0 to r
    end_box = pya.Region(pya.Box(int((-r - W/2.0)/dbu), 0, int((r + W/2.0)/dbu), int(r/dbu)))
    circ1 = pya.Region(draw_ellipse(dbu, r + W/2.0, r, r, r, num_sides))
    circ2 = pya.Region(draw_ellipse(dbu, -r - W/2.0, r, r, r, num_sides))
    end_box.subtract(circ1).subtract(circ2)
    
    # left end: end_box rotated -90 deg
    left_end = end_box.dup()
    left_end.transform(pya.Trans(pya.Trans.R270, 0, 0))
    
    # right end: end_box rotated 90 deg and translated to L
    right_end = end_box.dup()
    right_end.transform(pya.Trans(pya.Trans.R90, int(L/dbu), 0))
    
    beam.insert(left_end)
    beam.insert(right_end)
    
    if centered:
        beam.transform(pya.Trans(int(-L/(2.0*dbu)), 0))
        
    return beam
