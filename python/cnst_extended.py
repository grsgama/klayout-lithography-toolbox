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

# 14. Draw Text PCell helper
def draw_text(layout, cell, layer_info, text_str, x, y, size):
    dbu = layout.dbu
    try:
        text_cell = layout.create_cell("TEXT", "Basic", {"text": text_str, "layer": layer_info, "mag": size})
        if text_cell:
            cell.insert(pya.CellInstArray(text_cell.cell_index(), pya.Trans(int(x/dbu), int(y/dbu))))
    except:
        pass

# 15. Siemens Star
def draw_siemens_star(layout, rad, width, is_pi, n_pi, num_sides):
    dbu = layout.dbu
    region = pya.Region()
    w = (n_pi * math.pi) if is_pi else width
    num_elements = int((math.pi * 2.0 * rad) / (2.0 * w))
    if num_elements < 2:
        num_elements = 2
    d_theta = math.pi * 2.0 / num_elements
    for i in range(num_elements):
        theta = i * d_theta
        pts = [
            pya.Point(0, 0),
            pya.Point(int((rad * math.cos(theta) - (-w/2.0) * math.sin(theta))/dbu),
                      int((rad * math.sin(theta) + (-w/2.0) * math.cos(theta))/dbu)),
            pya.Point(int((rad * math.cos(theta) - (w/2.0) * math.sin(theta))/dbu),
                      int((rad * math.sin(theta) + (w/2.0) * math.cos(theta))/dbu))
        ]
        region.insert(pya.Polygon(pts))
    return region

# 16. LSA Pattern
def draw_lsa_pattern(layout, height, num_lines, start_w, end_w, delta_w, space):
    dbu = layout.dbu
    region = pya.Region()
    curr_x = 0.0
    w = start_w
    while w <= end_w + 1e-9:
        h = height
        for i in range(num_lines):
            if w < h:
                v_box = pya.Box(0, 0, int(w/dbu), int(h/dbu))
                h_box = pya.Box(0, 0, int(h/dbu), int(w/dbu))
                l_shape = pya.Region(v_box).join(pya.Region(h_box))
                l_shape.transform(pya.Trans(int((curr_x + 2 * i * w)/dbu), int((2 * i * w)/dbu)))
                region.insert(l_shape)
                h -= 2.0 * w
            else:
                break
        curr_x += height + space
        w += delta_w
    return region

# 17. General Spiral Delay Line
def draw_spiral_delay_line_generic(layout, style, turns, width, separation, a_coeff, resolution, length, is_inverse, sleeveWidth, skipped_turns):
    dbu = layout.dbu
    pts = []
    
    if skipped_turns > 0:
        pitch = separation + width if style == "Archimedean" else 2.0 * math.pi * width
        pitch_fact = pitch / (2.0 * math.pi)
        start_theta = skipped_turns * 2.0 * math.pi
        end_theta = (skipped_turns + turns) * 2.0 * math.pi
        inc = 2.0 * math.pi / resolution
        
        # Spiral 1 (theta: start_theta to end_theta)
        spiral1 = []
        theta = start_theta
        while theta <= end_theta + 1e-9:
            if style == "Archimedean":
                r = pitch_fact * theta
            else:
                r = a_coeff * math.sqrt(theta)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            spiral1.append(pya.DPoint(x, y))
            theta += inc
        last = spiral1[-1]
        spiral1.append(pya.DPoint(last.x, last.y + length))
        
        # Spiral 2
        spiral2 = []
        theta = start_theta
        while theta <= end_theta + 1e-9:
            if style == "Archimedean":
                r = -pitch_fact * theta
            else:
                r = -a_coeff * math.sqrt(theta)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            spiral2.append(pya.DPoint(x, y))
            theta += inc
        last = spiral2[-1]
        spiral2.append(pya.DPoint(last.x, last.y - length))
        
        spiral2.reverse()
        combined = spiral2 + [pya.DPoint(0,0)] + spiral1
        pts = [pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in combined]
    else:
        inc = 2.0 * math.pi / resolution
        upper_lim = 2.0 * turns * math.pi
        
        spiral1 = []
        theta = 0.0
        while theta <= upper_lim + 1e-9:
            if style == "Archimedean":
                r = ((separation + width) / (2.0 * math.pi)) * theta
            else:
                r = a_coeff * math.sqrt(theta)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            spiral1.append(pya.DPoint(x, y))
            theta += inc
        last = spiral1[-1]
        spiral1.append(pya.DPoint(last.x, last.y + length))
        
        spiral2 = []
        theta = 0.0
        while theta <= upper_lim + 1e-9:
            if style == "Archimedean":
                r = -((separation + width) / (2.0 * math.pi)) * theta
            else:
                r = -a_coeff * math.sqrt(theta)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            spiral2.append(pya.DPoint(x, y))
            theta += inc
        last = spiral2[-1]
        spiral2.append(pya.DPoint(last.x, last.y - length))
        
        spiral2.reverse()
        combined = spiral2 + spiral1
        pts = [pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in combined]
        
    if is_inverse:
        s_w = width + 2.0 * sleeveWidth
        path_sleeve = pya.Path(pts, int(s_w/dbu)).simple_polygon()
        path_core = pya.Path(pts, int(width/dbu)).simple_polygon()
        return pya.Region(path_sleeve) - pya.Region(path_core)
    else:
        path = pya.Path(pts, int(width/dbu))
        return pya.Region(path.simple_polygon())

# 18. Bent Beams
def draw_bent_beam(layout, width, length1, length2, length3, baseHeight, baseWidth, anchorDistance):
    dbu = layout.dbu
    r_struct = pya.Region()
    r_anchors = pya.Region()
    
    r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
    r_struct.insert(pya.Box(int((baseWidth + length1)/dbu), 0, int((2.0 * baseWidth + length1)/dbu), int(baseHeight/dbu)))
    
    pts = [
        pya.Point(int((baseWidth - width/2.0)/dbu), int(baseHeight/2.0/dbu)),
        pya.Point(int((baseWidth + length2)/dbu), int((baseHeight/2.0 + length3)/dbu)),
        pya.Point(int((baseWidth + length1 + width/2.0)/dbu), int(baseHeight/2.0/dbu))
    ]
    path = pya.Path(pts, int(width/dbu))
    r_struct.insert(path.simple_polygon())
    
    if anchorDistance < baseWidth / 2.0 and anchorDistance < baseHeight / 2.0:
        anc_box = pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((baseWidth - anchorDistance)/dbu), int((baseHeight - anchorDistance)/dbu))
        r_anchors.insert(anc_box)
        r_anchors.insert(anc_box.transformed(pya.Trans(int((baseWidth + length1)/dbu), 0)))
        
    return r_struct, r_anchors

def draw_bent_beam_array(layout, width, length1, length2, length3, length4, hOffset, pitch, numElements, centralBeamWidth, dimpleHeight, dimpleWidth, baseWidth, anchorDistance):
    dbu = layout.dbu
    r_struct = pya.Region()
    r_anchors = pya.Region()
    r_dimples = pya.Region()
    
    baseHeight = 2.0 * hOffset + pitch * (numElements - 1)
    r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
    r_struct.insert(pya.Box(int((baseWidth + length1)/dbu), 0, int((2.0 * baseWidth + length1)/dbu), int(baseHeight/dbu)))
    
    for i in range(numElements):
        pts = [
            pya.Point(int((baseWidth - width/2.0)/dbu), int((hOffset + i * pitch)/dbu)),
            pya.Point(int((baseWidth + length2)/dbu), int((hOffset + length3 + i * pitch)/dbu)),
            pya.Point(int((baseWidth + length1 + width/2.0)/dbu), int((hOffset + i * pitch)/dbu))
        ]
        path = pya.Path(pts, int(width/dbu))
        r_struct.insert(path.simple_polygon())
        
    centralBeamHeight = 2.0 * length4 + pitch * (numElements - 1)
    central = pya.Region(pya.Box(0, 0, int(centralBeamWidth/dbu), int(centralBeamHeight/dbu)))
    central.transform(pya.Trans(int((baseWidth + length2 - centralBeamWidth/2.0)/dbu), int((hOffset + length3 - length4)/dbu)))
    r_struct.insert(central)
    
    for i in range(1, numElements - 1):
        cy = pitch * i + hOffset + length3
        r_dimples.insert(pya.Box(int((baseWidth + length2 - dimpleWidth/2.0)/dbu), int((cy - dimpleHeight/2.0)/dbu),
                                 int((baseWidth + length2 + dimpleWidth/2.0)/dbu), int((cy + dimpleHeight/2.0)/dbu)))
        
    if anchorDistance < baseWidth / 2.0 and anchorDistance < baseHeight / 2.0:
        anc_box = pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((baseWidth - anchorDistance)/dbu), int((baseHeight - anchorDistance)/dbu))
        r_anchors.insert(anc_box)
        r_anchors.insert(anc_box.transformed(pya.Trans(int((baseWidth + length1)/dbu), 0)))
        
    return r_struct, r_anchors, r_dimples

# 19. Bi-Morph Actuator
def draw_bimorph_thermal(layout, width1, width2, width3, width4, length1, length2, length3, pitch, dimpleHeight, dimpleWidth, baseHeight, baseWidth, anchorDistance):
    dbu = layout.dbu
    r_struct = pya.Region()
    r_anchors = pya.Region()
    r_dimples = pya.Region()
    
    r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
    r_struct.insert(pya.Box(int(baseWidth/dbu), int((baseHeight - width1)/dbu), int((baseWidth + length1)/dbu), int(baseHeight/dbu)))
    r_struct.insert(pya.Box(int((baseWidth + length1)/dbu), int((baseHeight - width4)/dbu), int((baseWidth + length2)/dbu), int(baseHeight/dbu)))
    r_struct.insert(pya.Box(int((baseWidth + length2 - length3)/dbu), int(baseHeight/dbu), int((baseWidth + length2)/dbu), int((baseHeight + width3)/dbu)))
    r_struct.insert(pya.Box(0, int((baseHeight + width3)/dbu), int(baseWidth/dbu), int((2.0 * baseHeight + width3)/dbu)))
    r_struct.insert(pya.Box(int(baseWidth/dbu), int((baseHeight + width3)/dbu), int((baseWidth + length2)/dbu), int((baseHeight + width3 + width2)/dbu)))
    
    distance = length2 - length1
    if pitch > dimpleWidth and width4 > dimpleHeight and distance > dimpleWidth:
        numPeriods = int(distance / pitch)
        unoccupiedSpace = pitch - dimpleWidth
        edgeOffset = (distance - numPeriods * pitch + unoccupiedSpace) / 2.0
        xOffset = baseWidth + length1 + edgeOffset
        yOffset = baseHeight - (width4 - dimpleHeight) / 2.0 - dimpleHeight
        for i in range(numPeriods):
            r_dimples.insert(pya.Box(int((xOffset + i * pitch)/dbu), int(yOffset/dbu), int((xOffset + i * pitch + dimpleWidth)/dbu), int((yOffset + dimpleHeight)/dbu)))
            
    if anchorDistance < baseWidth / 2.0 and anchorDistance < baseHeight / 2.0:
        anc_box = pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((baseWidth - anchorDistance)/dbu), int((baseHeight - anchorDistance)/dbu))
        r_anchors.insert(anc_box)
        r_anchors.insert(anc_box.dup().transform(pya.Trans(0, int((baseHeight + width3)/dbu))))
        
    return r_struct, r_anchors, r_dimples

# 20. Comb Drive V1
def draw_comb_drive_v1(layout, width1, width2, length1, length2, numElectrodes, pitch, baseHeight, anchorDistance):
    dbu = layout.dbu
    r_top = pya.Region()
    r_bot = pya.Region()
    r_anchors = pya.Region()
    
    total_w = (numElectrodes - 1) * pitch + width1
    r_top.insert(pya.Box(0, int(-baseHeight/dbu), int(total_w/dbu), 0))
    
    for i in range(numElectrodes):
        r_top.insert(pya.Box(int((i * pitch)/dbu), int((-baseHeight - length1)/dbu), int((i * pitch + width1)/dbu), int(-baseHeight/dbu)))
        
    startX = pitch / 2.0
    startY = -baseHeight - 2.0 * length1 + length2
    r_bot.insert(pya.Box(int(startX/dbu), int((startY - width2)/dbu), int((startX + (numElectrodes - 2) * pitch + width1)/dbu), int(startY/dbu)))
    for i in range(numElectrodes - 1):
        r_bot.insert(pya.Box(int((i * pitch + startX)/dbu), int(startY/dbu), int((i * pitch + startX + width1)/dbu), int((startY + length1)/dbu)))
        
    if anchorDistance < total_w / 2.0 and anchorDistance < baseHeight / 2.0:
        r_anchors.insert(pya.Box(int(anchorDistance/dbu), int((-baseHeight + anchorDistance)/dbu), int((total_w - anchorDistance)/dbu), int(-anchorDistance/dbu)))
        
    return r_top, r_bot, r_anchors

# 21. Linear Drive L1
def draw_linear_drive_l1(layout, width1, length1, length2, length3, gap, numElectrodes, pitch, baseHeight, baseWidth, rotorPitch, anchorDistance):
    dbu = layout.dbu
    r_stators = pya.Region()
    r_anchors = pya.Region()
    r_rotor = pya.Region()
    
    lengthTopElectrodes = (numElectrodes - 1) * pitch + baseWidth
    startX = -lengthTopElectrodes / 2.0 - length3
    r_rotor.insert(pya.Box(int(startX/dbu), int(-length2/2.0/dbu), int(-startX/dbu), int(length2/2.0/dbu)))
    
    startX = -lengthTopElectrodes / 2.0
    startY = length2 + length1 + gap
    
    stator_single = pya.Box(int(startX/dbu), int(startY/dbu), int((startX + baseWidth)/dbu), int((startY + baseHeight)/dbu))
    anchor_single = pya.Box(int((startX + anchorDistance)/dbu), int((startY + anchorDistance)/dbu), int((startX + baseWidth - anchorDistance)/dbu), int((startY + baseHeight - anchorDistance)/dbu))
    
    for i in range(numElectrodes):
        shift = int((i * pitch)/dbu)
        r_stators.insert(stator_single.dup().transform(pya.Trans(shift, 0)))
        r_anchors.insert(anchor_single.dup().transform(pya.Trans(shift, 0)))
        
        trans_mirr = pya.Trans(shift, int((-2.0 * startY - baseHeight)/dbu))
        r_stators.insert(stator_single.dup().transform(trans_mirr))
        r_anchors.insert(anchor_single.dup().transform(trans_mirr))
        
    numMidFingers = int(lengthTopElectrodes / rotorPitch)
    for i in range(numMidFingers + 1):
        fx = i * rotorPitch - lengthTopElectrodes / 2.0
        r_rotor.insert(pya.Box(int(fx/dbu), int(length2/2.0/dbu), int((fx + width1)/dbu), int((length2/2.0 + length1)/dbu)))
        r_rotor.insert(pya.Box(int(fx/dbu), int((-length2/2.0 - length1)/dbu), int((fx + width1)/dbu), int(-length2/2.0/dbu)))
        
    return r_stators, r_anchors, r_rotor

# 22. Radial Comb Drive
def draw_comb_radial(layout, w1, r1, w2, r2, wc, gap, numElements, numSides, thetaALL, thetaOverlap, anchorDistance, mirror_mode=False):
    dbu = layout.dbu
    thetaPrime = abs((thetaALL - thetaOverlap) / 2.0)
    totalLengthUpper = (2 * numElements - 1) * wc + 2 * (numElements - 1) * gap
    totalLengthLower = 2 * (numElements - 1) * wc + 2 * (numElements - 1) * gap
    
    r_base = pya.Region(pya.Box(int(r2/dbu), int(-w2/2.0/dbu), int((r2 + (r1 - r2) + totalLengthLower - gap)/dbu), int(w2/2.0/dbu)))
    
    pts = [
        pya.Point(int((r1 * math.cos(math.radians(thetaALL)))/dbu), int((r1 * math.sin(math.radians(thetaALL)))/dbu)),
        pya.Point(int(((r1 + totalLengthUpper) * math.cos(math.radians(thetaALL)))/dbu), int(((r1 + totalLengthUpper) * math.sin(math.radians(thetaALL)))/dbu))
    ]
    path = pya.Path(pts, int(w1/dbu))
    r_base.insert(path.simple_polygon())
    
    r_fingers = pya.Region()
    for i in range(numElements):
        rad_finger = i * (2.0 * wc + 2.0 * gap) + r1 + wc / 2.0
        r_fingers.insert(draw_torus_arc(dbu, 0.0, 0.0, rad_finger, wc, thetaALL - thetaPrime - thetaOverlap, thetaALL, numSides))
        if i < numElements - 1:
            rad_rotor_finger = i * (2.0 * wc + 2.0 * gap) + r1 + wc / 2.0 + gap + wc
            r_base.insert(draw_torus_arc(dbu, 0.0, 0.0, rad_rotor_finger, wc, 0.0, thetaPrime + thetaOverlap, numSides))
            
    pts_anc = [
        pya.Point(int(((r1 + anchorDistance) * math.cos(math.radians(thetaALL)))/dbu), int(((r1 + anchorDistance) * math.sin(math.radians(thetaALL)))/dbu)),
        pya.Point(int(((r1 + totalLengthUpper - anchorDistance) * math.cos(math.radians(thetaALL)))/dbu), int(((r1 + totalLengthUpper - anchorDistance) * math.sin(math.radians(thetaALL)))/dbu))
    ]
    path_anc = pya.Path(pts_anc, int((w1 - 2.0 * anchorDistance)/dbu))
    r_anchor = pya.Region(path_anc.simple_polygon())
    
    if mirror_mode:
        trans_mirr = pya.Trans(pya.Trans.M0, 0, 0)
        r_base_m = r_base.dup().transform(trans_mirr)
        r_fingers_m = r_fingers.dup().transform(trans_mirr)
        r_anchor_m = r_anchor.dup().transform(trans_mirr)
        r_base.insert(r_base_m)
        r_fingers.insert(r_fingers_m)
        r_anchor.insert(r_anchor_m)
        
    return r_base, r_fingers, r_anchor

# 23. Folded Springs
def draw_folded_spring(layout, style, width, length1, length2, pitch, amplitude, num_periods, baseHeight, baseWidth, anchorDistance, num_sides, diameter):
    dbu = layout.dbu
    r_struct = pya.Region()
    r_anchors = pya.Region()
    
    def add_anc(bx, by, w, h):
        if anchorDistance < w/2.0 and anchorDistance < h/2.0:
            r_anchors.insert(pya.Box(int((bx + anchorDistance)/dbu), int((by + anchorDistance)/dbu),
                                     int((bx + w - anchorDistance)/dbu), int((by + h - anchorDistance)/dbu)))
                                     
    if style in ["1A", "2A"]:
        pts = [pya.Point(int(baseWidth/dbu), int(baseHeight/2.0/dbu))]
        startX = baseWidth + length1 + width / 2.0
        pts.append(pya.Point(int(startX/dbu), int(baseHeight/2.0/dbu)))
        for i in range(num_periods):
            x = i * 2.0 * pitch + startX
            pts.append(pya.Point(int(x/dbu), int((baseHeight / 2.0 + amplitude)/dbu)))
            pts.append(pya.Point(int((x + pitch)/dbu), int((baseHeight / 2.0 + amplitude)/dbu)))
            pts.append(pya.Point(int((x + pitch)/dbu), int((baseHeight / 2.0 - amplitude)/dbu)))
            pts.append(pya.Point(int((x + 2.0 * pitch)/dbu), int((baseHeight / 2.0 - amplitude)/dbu)))
            pts.append(pya.Point(int((x + 2.0 * pitch)/dbu), int(baseHeight/2.0/dbu)))
        endX = (num_periods - 1) * 2.0 * pitch + startX + 2.0 * pitch + length2 + width / 2.0
        pts.append(pya.Point(int(endX/dbu), int(baseHeight/2.0/dbu)))
        
        path = pya.Path(pts, int(width/dbu))
        r_struct.insert(path.simple_polygon())
        r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
        add_anc(0, 0, baseWidth, baseHeight)
        
        if style == "2A":
            r_struct.insert(pya.Box(int(endX/dbu), 0, int((endX + baseWidth)/dbu), int(baseHeight/dbu)))
            add_anc(endX, 0, baseWidth, baseHeight)
            
    elif style in ["1B", "2B"]:
        pts = [pya.Point(int(baseWidth/dbu), int(width/2.0/dbu))]
        startX = baseWidth + length1 + width / 2.0
        pts.append(pya.Point(int(startX/dbu), int(width/2.0/dbu)))
        for i in range(num_periods):
            x = i * 2.0 * pitch + startX
            pts.append(pya.Point(int(x/dbu), int((width / 2.0 + 2.0 * amplitude)/dbu)))
            pts.append(pya.Point(int((x + pitch)/dbu), int((width / 2.0 + 2.0 * amplitude)/dbu)))
            pts.append(pya.Point(int((x + pitch)/dbu), int(width/2.0/dbu)))
            pts.append(pya.Point(int((x + 2.0 * pitch)/dbu), int(width/2.0/dbu)))
        endX = (num_periods - 1) * 2.0 * pitch + startX + 2.0 * pitch + length2 + width / 2.0 - pitch
        pts.append(pya.Point(int(endX/dbu), int(width/2.0/dbu)))
        
        path = pya.Path(pts, int(width/dbu))
        r_struct.insert(path.simple_polygon())
        r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
        add_anc(0, 0, baseWidth, baseHeight)
        
        if style == "2B":
            r_struct.insert(pya.Box(int(endX/dbu), 0, int((endX + baseWidth)/dbu), int(baseHeight/dbu)))
            add_anc(endX, 0, baseWidth, baseHeight)
            
    elif style == "2C":
        pts = [pya.Point(int((baseWidth/2.0)/dbu), int(baseHeight/dbu))]
        startX = baseWidth / 2.0
        startY = baseHeight + length1 + width / 2.0
        pts.append(pya.Point(int(startX/dbu), int(startY/dbu)))
        for i in range(num_periods):
            x = i * 2.0 * pitch + startX
            pts.append(pya.Point(int(x/dbu), int((startY + amplitude)/dbu)))
            pts.append(pya.Point(int((x + pitch)/dbu), int((startY + amplitude)/dbu)))
            pts.append(pya.Point(int((x + pitch)/dbu), int(startY/dbu)))
            pts.append(pya.Point(int((x + 2.0 * pitch)/dbu), int(startY/dbu)))
            pts.append(pya.Point(int((x + 2.0 * pitch)/dbu), int((startY + amplitude)/dbu)))
        endX = (num_periods - 1) * 2.0 * pitch + startX + 2.0 * pitch
        endY = startY + amplitude + length2
        pts.append(pya.Point(int(endX/dbu), int(endY/dbu)))
        
        path = pya.Path(pts, int(width/dbu))
        r_struct.insert(path.simple_polygon())
        r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
        add_anc(0, 0, baseWidth, baseHeight)
        
        r_struct.insert(pya.Box(int((endX - baseWidth/2.0)/dbu), int(endY/dbu), int((endX + baseWidth/2.0)/dbu), int((endY + baseHeight)/dbu)))
        add_anc(endX - baseWidth/2.0, endY, baseWidth, baseHeight)
        
    elif style == "2D":
        pts = [pya.Point(int((baseWidth/2.0)/dbu), int(baseHeight/dbu))]
        startX = baseWidth / 2.0
        startY = baseHeight + length1 + width / 2.0
        pts.append(pya.Point(int(startX/dbu), int(startY/dbu)))
        for i in range(num_periods):
            x = i * 2.0 * pitch + startX
            pts.append(pya.Point(int(x/dbu), int((startY + amplitude)/dbu)))
            pts.append(pya.Point(int((x + pitch)/dbu), int((startY + amplitude)/dbu)))
            pts.append(pya.Point(int((x + pitch)/dbu), int(startY/dbu)))
            if i != num_periods - 1:
                pts.append(pya.Point(int((x + 2.0 * pitch)/dbu), int(startY/dbu)))
            else:
                pts.append(pya.Point(int((x + pitch)/dbu), int((startY - length2)/dbu)))
        endX = (num_periods - 1) * 2.0 * pitch + startX + pitch - baseWidth / 2.0
        
        path = pya.Path(pts, int(width/dbu))
        r_struct.insert(path.simple_polygon())
        r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
        add_anc(0, 0, baseWidth, baseHeight)
        
        r_struct.insert(pya.Box(int(endX/dbu), 0, int((endX + baseWidth)/dbu), int(baseHeight/dbu)))
        add_anc(endX, 0, baseWidth, baseHeight)
        
    elif style in ["2E", "2F", "2G", "2H", "2I", "2J"]:
        halfwayPoint = (pitch + width) / 2.0
        if style == "2E":
            r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
            add_anc(0, 0, baseWidth, baseHeight)
            startX = baseWidth + length1
            startY = baseHeight / 2.0 - width / 2.0
            r_struct.insert(pya.Box(int(baseWidth/dbu), int(startY/dbu), int((baseWidth + length1)/dbu), int((startY + width)/dbu)))
            
            meander = pya.Region(pya.Box(int(startX/dbu), int(startY/dbu), int((startX + width)/dbu), int((startY + amplitude + width)/dbu)))
            meander.insert(draw_torus_arc(dbu, startX + halfwayPoint, startY + amplitude + width, pitch/2.0, width, 0.0, 180.0, num_sides))
            meander.insert(pya.Box(int((startX + pitch)/dbu), int((startY - amplitude - width)/dbu), int((startX + pitch + width)/dbu), int((startY + amplitude + width)/dbu)))
            meander.insert(draw_torus_arc(dbu, startX + pitch + halfwayPoint, startY - amplitude - width, pitch/2.0, width, 180.0, 360.0, num_sides))
            meander.insert(pya.Box(int((startX + pitch * 2.0)/dbu), int((startY - amplitude - width)/dbu), int((startX + pitch * 2.0 + width)/dbu), int((startY + width)/dbu)))
            
            for i in range(num_periods):
                temp = meander.dup().transform(pya.Trans(int((i * 2.0 * pitch)/dbu), 0))
                r_struct.insert(temp)
                
            lastElement = num_periods * 2.0 * pitch + startX
            r_struct.insert(pya.Box(int(lastElement/dbu), int(startY/dbu), int((lastElement + length2 + width)/dbu), int((startY + width)/dbu)))
            r_struct.insert(pya.Box(int((lastElement + length2 + width)/dbu), int((startY - baseHeight/2.0 + width/2.0)/dbu), int((lastElement + length2 + width + baseWidth)/dbu), int((startY + baseHeight/2.0 + width/2.0)/dbu)))
            add_anc(lastElement + width + length2, startY - baseHeight/2.0 + width/2.0, baseWidth, baseHeight)
            
        elif style == "2F":
            r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
            add_anc(0, 0, baseWidth, baseHeight)
            r_struct.insert(pya.Box(int(baseWidth/dbu), 0, int((baseWidth + length1)/dbu), int(width/dbu)))
            startX = baseWidth + length1
            
            meander = pya.Region(pya.Box(int(startX/dbu), 0, int((startX + width)/dbu), int((amplitude + width)/dbu)))
            meander.insert(draw_torus_arc(dbu, startX + halfwayPoint, amplitude + width, pitch/2.0, width, 0.0, 180.0, num_sides))
            meander.insert(pya.Box(int((startX + pitch)/dbu), 0, int((startX + pitch + width)/dbu), int((amplitude + width)/dbu)))
            
            for i in range(num_periods):
                if i != num_periods - 1:
                    r_struct.insert(draw_torus_arc(dbu, i * 2.0 * pitch + startX + pitch + halfwayPoint, 0.0, pitch/2.0, width, 180.0, 360.0, num_sides))
                temp = meander.dup().transform(pya.Trans(int((i * 2.0 * pitch)/dbu), 0))
                r_struct.insert(temp)
                
            startX_end = startX + num_periods * 2.0 * pitch - pitch
            r_struct.insert(pya.Box(int(startX_end/dbu), 0, int((startX_end + length2 + width)/dbu), int(width/dbu)))
            r_struct.insert(pya.Box(int((startX_end + length2 + width)/dbu), 0, int((startX_end + length2 + width + baseWidth)/dbu), int(baseHeight/dbu)))
            add_anc(startX_end + length2 + width, 0, baseWidth, baseHeight)
            
        elif style == "2G":
            r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
            add_anc(0, 0, baseWidth, baseHeight)
            startX = baseWidth / 2.0 - width / 2.0
            startY = baseHeight + length1
            r_struct.insert(pya.Box(int(startX/dbu), int(baseHeight/dbu), int((startX + width)/dbu), int(startY/dbu)))
            
            meander = pya.Region(pya.Box(int(startX/dbu), int(startY/dbu), int((startX + width)/dbu), int((startY + amplitude + width)/dbu)))
            meander.insert(draw_torus_arc(dbu, startX + halfwayPoint, startY + amplitude + width, pitch/2.0, width, 0.0, 180.0, num_sides))
            meander.insert(pya.Box(int((startX + pitch)/dbu), int(startY/dbu), int((startX + pitch + width)/dbu), int((startY + amplitude + width)/dbu)))
            
            for i in range(num_periods):
                r_struct.insert(draw_torus_arc(dbu, i * 2.0 * pitch + startX + pitch + halfwayPoint, startY, pitch/2.0, width, 180.0, 360.0, num_sides))
                temp = meander.dup().transform(pya.Trans(int((i * 2.0 * pitch)/dbu), 0))
                r_struct.insert(temp)
                
            lastX = startX + num_periods * 2.0 * pitch
            r_struct.insert(pya.Box(int(lastX/dbu), int(startY/dbu), int((lastX + width)/dbu), int((startY + amplitude + width)/dbu)))
            r_struct.insert(pya.Box(int(lastX/dbu), int((startY + amplitude)/dbu), int((lastX + width)/dbu), int((startY + amplitude + length2 + width)/dbu)))
            r_struct.insert(pya.Box(int((lastX - baseWidth/2.0 + width/2.0)/dbu), int((startY + amplitude + length2)/dbu), int((lastX + baseWidth/2.0 + width/2.0)/dbu), int((startY + amplitude + length2 + baseHeight)/dbu)))
            add_anc(lastX - baseWidth/2.0 + width/2.0, startY + amplitude + length2, baseWidth, baseHeight)
            
        elif style == "2H":
            r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
            add_anc(0, 0, baseWidth, baseHeight)
            startX = baseWidth / 2.0 - width / 2.0
            startY = baseHeight + length1
            r_struct.insert(pya.Box(int(startX/dbu), int(baseHeight/dbu), int((startX + width)/dbu), int(startY/dbu)))
            
            meander = pya.Region(pya.Box(int(startX/dbu), int(startY/dbu), int((startX + width)/dbu), int((startY + amplitude + width)/dbu)))
            meander.insert(draw_torus_arc(dbu, startX + halfwayPoint, startY + amplitude + width, pitch/2.0, width, 0.0, 180.0, num_sides))
            meander.insert(pya.Box(int((startX + pitch)/dbu), int(startY/dbu), int((startX + pitch + width)/dbu), int((startY + amplitude + width)/dbu)))
            
            for i in range(num_periods):
                if i != num_periods - 1:
                    r_struct.insert(draw_torus_arc(dbu, i * 2.0 * pitch + startX + pitch + halfwayPoint, startY, pitch/2.0, width, 180.0, 360.0, num_sides))
                temp = meander.dup().transform(pya.Trans(int((i * 2.0 * pitch)/dbu), 0))
                r_struct.insert(temp)
                
            startX_end = startX + num_periods * 2.0 * pitch - pitch
            r_struct.insert(pya.Box(int(startX_end/dbu), int(baseHeight/dbu), int((startX_end + width)/dbu), int((baseHeight + length2 + width)/dbu)))
            r_struct.insert(pya.Box(int((startX_end - baseWidth/2.0 + width/2.0)/dbu), 0, int((startX_end + baseWidth/2.0 + width/2.0)/dbu), int(baseHeight/dbu)))
            add_anc(startX_end - baseWidth/2.0 + width/2.0, 0, baseWidth, baseHeight)
            
        elif style in ["2I", "2J"]:
            radius = diameter # as in java
            diam_total = 2.0 * radius
            r_struct.insert(draw_ellipse(dbu, radius, radius, radius, radius, num_sides))
            r_struct.insert(pya.Box(int((radius - width/2.0)/dbu), int((diam_total - width)/dbu), int((radius + width/2.0)/dbu), int((diam_total + width + length1)/dbu)))
            
            startX = radius - width/2.0
            startY = diam_total + length1 + width
            
            meander = pya.Region(pya.Box(int(startX/dbu), int(startY/dbu), int((startX + width)/dbu), int((startY + amplitude + width)/dbu)))
            meander.insert(draw_torus_arc(dbu, startX + halfwayPoint, startY + amplitude + width, pitch/2.0, width, 0.0, 180.0, num_sides))
            meander.insert(pya.Box(int((startX + pitch)/dbu), int(startY/dbu), int((startX + pitch + width)/dbu), int((startY + amplitude + width)/dbu)))
            
            for i in range(num_periods):
                if style == "2I" or i != num_periods - 1:
                    r_struct.insert(draw_torus_arc(dbu, i * 2.0 * pitch + startX + pitch + halfwayPoint, startY, pitch/2.0, width, 180.0, 360.0, num_sides))
                temp = meander.dup().transform(pya.Trans(int((i * 2.0 * pitch)/dbu), 0))
                r_struct.insert(temp)
                
            if style == "2I":
                lastX = startX + num_periods * 2.0 * pitch
                r_struct.insert(pya.Box(int(lastX/dbu), int(startY/dbu), int((lastX + width)/dbu), int((startY + amplitude + width)/dbu)))
                r_struct.insert(pya.Box(int(lastX/dbu), int((startY + amplitude)/dbu), int((lastX + width)/dbu), int((startY + amplitude + length2 + width)/dbu)))
                r_struct.insert(draw_ellipse(dbu, lastX + width/2.0, startY + amplitude + length2 + radius, radius, radius, num_sides))
                
                # Align to center (0,0) as in java translation
                r_struct.transform(pya.Trans(int(-radius/dbu), int(-radius/dbu)))
                
                # Anchors
                anchors_ellipse = pya.Region(draw_ellipse(dbu, radius, radius, radius - anchorDistance, radius - anchorDistance, num_sides))
                temp_anc = anchors_ellipse.dup().transform(pya.Trans(int((lastX + width/2.0 - radius)/dbu), int((startY + amplitude + length2)/dbu)))
                anchors_ellipse.insert(temp_anc)
                anchors_ellipse.transform(pya.Trans(int(-radius/dbu), int(-radius/dbu)))
                r_anchors = anchors_ellipse
            else: # 2J
                startX_end = startX + num_periods * 2.0 * pitch - pitch
                r_struct.insert(pya.Box(int(startX_end/dbu), int((diam_total - width)/dbu), int((startX_end + width)/dbu), int((diam_total + length2 + width)/dbu)))
                r_struct.insert(draw_ellipse(dbu, startX_end + width/2.0, radius, radius, radius, num_sides))
                
                r_struct.transform(pya.Trans(int(-radius/dbu), int(-radius/dbu)))
                
                anchors_ellipse = pya.Region(draw_ellipse(dbu, radius, radius, radius - anchorDistance, radius - anchorDistance, num_sides))
                temp_anc = anchors_ellipse.dup().transform(pya.Trans(int((startX_end + width/2.0 - radius)/dbu), 0))
                anchors_ellipse.insert(temp_anc)
                anchors_ellipse.transform(pya.Trans(int(-radius/dbu), int(-radius/dbu)))
                r_anchors = anchors_ellipse
                
    r_struct.merge()
    r_anchors.merge()
    return r_struct, r_anchors

# 24. Coupled Arrays
def draw_coupled_array(style, dbu, numElements, L1, W1a, W1b, L2, W2a, W2b, space, lowerSpace, hOverlap, hElectrode, lengthSide, LB, HB, diameter, numSides, layerFront, layerBack, layerMetal, ISELECTRODE=False):
    front = pya.Region()
    metal = pya.Region()
    back = pya.Region()
    
    def get_circle(cx, cy, r):
        return draw_ellipse(dbu, cx, cy, r, r, numSides)
        
    def get_trap_beam(Wa, Wb, L, top):
        pts = []
        if not top:
            pts = [
                pya.Point(int(-Wa/2.0/dbu), 0),
                pya.Point(int(Wa/2.0/dbu), 0),
                pya.Point(int(Wb/2.0/dbu), int(L/dbu)),
                pya.Point(int(-Wb/2.0/dbu), int(L/dbu))
            ]
        else:
            pts = [
                pya.Point(int(-Wa/2.0/dbu), int(L/dbu)),
                pya.Point(int(Wa/2.0/dbu), int(L/dbu)),
                pya.Point(int(Wb/2.0/dbu), 0),
                pya.Point(int(-Wb/2.0/dbu), 0)
            ]
        return pya.Region(pya.Polygon(pts))
        
    def get_side_electrodes(L, Wa, Wb, hOver, lenSide, top):
        pts = []
        d = (L - hOver) * (Wa - Wb) / (2.0 * L)
        w_bot = Wa - 2.0 * d
        w_top = Wb
        if not top:
            pts = [
                pya.Point(int(-w_bot/2.0/dbu), 0),
                pya.Point(int(w_bot/2.0/dbu), 0),
                pya.Point(int((w_bot/2.0 + lenSide)/dbu), 0),
                pya.Point(int((w_top/2.0 + lenSide)/dbu), int(hOver/dbu)),
                pya.Point(int(w_top/2.0/dbu), int(hOver/dbu)),
                pya.Point(int(-w_top/2.0/dbu), int(hOver/dbu)),
                pya.Point(int((-w_top/2.0 - lenSide)/dbu), int(hOver/dbu)),
                pya.Point(int((-w_bot/2.0 - lenSide)/dbu), 0)
            ]
        else:
            pts = [
                pya.Point(int(-w_bot/2.0/dbu), int(hOver/dbu)),
                pya.Point(int(w_bot/2.0/dbu), int(hOver/dbu)),
                pya.Point(int((w_bot/2.0 + lenSide)/dbu), int(hOver/dbu)),
                pya.Point(int((w_top/2.0 + lenSide)/dbu), 0),
                pya.Point(int(w_top/2.0/dbu), 0),
                pya.Point(int(-w_top/2.0/dbu), 0),
                pya.Point(int((-w_top/2.0 - lenSide)/dbu), 0),
                pya.Point(int((-w_bot/2.0 - lenSide)/dbu), int(hOver/dbu))
            ]
        return pya.Region(pya.Polygon(pts))

    if style == "Rect":
        leverBottom = pya.Region(pya.Box(0, 0, int(W1a/dbu), int(L1/dbu)))
        leverTop = pya.Region(pya.Box(0, 0, int(W2a/dbu), int(L2/dbu)))
        sideElectrode = pya.Region(pya.Box(0, 0, int(lengthSide/dbu), int(hOverlap/dbu)))
        
        electrodeLength = numElements * (2.0 * space + W1a + W2a) + space
        front.insert(pya.Box(0, 0, int(electrodeLength/dbu), int(hElectrode/dbu)))
        front.insert(pya.Box(0, int((hElectrode + L1 + L2 - hOverlap)/dbu), int(electrodeLength/dbu), int((hElectrode + L1 + L2 - hOverlap + hElectrode)/dbu)))
        
        for i in range(numElements):
            pitch_shift = i * (2.0 * space + W1a + W2a)
            temp = leverBottom.dup().transform(pya.Trans(int((pitch_shift + 2.0 * space + W2a)/dbu), int(hElectrode/dbu)))
            front.insert(temp)
            metal.insert(get_circle(pitch_shift + 2.0 * space + W2a + W1a / 2.0, hElectrode + L1 - hOverlap / 2.0, diameter / 2.0))
            
            temp = leverTop.dup().transform(pya.Trans(int((pitch_shift + space)/dbu), int((L1 - hOverlap + hElectrode)/dbu)))
            front.insert(temp)
            metal.insert(get_circle(pitch_shift + space + W2a / 2.0, L1 - hOverlap / 2.0 + hElectrode, diameter / 2.0))
            
        front.insert(sideElectrode.dup().transform(pya.Trans(int(electrodeLength/dbu), int((L1 - hOverlap + hElectrode)/dbu))))
        front.insert(sideElectrode.dup().transform(pya.Trans(int(-lengthSide/dbu), int((L1 - hOverlap + hElectrode)/dbu))))
        
        back = pya.Region(create_back_side_path(dbu, L1, L2, hOverlap, electrodeLength, hElectrode, LB, HB))
        
    elif style == "RT2":
        topElectrode = pya.Region(pya.Box(0, 0, int((2.0 * lengthSide + W2a)/dbu), int(hElectrode/dbu)))
        botElectrode = pya.Region(pya.Box(0, 0, int((2.0 * lengthSide + W1a)/dbu), int(hElectrode/dbu)))
        
        botElectrode.insert(get_trap_beam(W1a, W1b, L1, False).transform(pya.Trans(int(lengthSide/dbu), int(hElectrode/dbu))))
        topElectrode.insert(get_trap_beam(W2a, W2b, L2, True).transform(pya.Trans(int(lengthSide/dbu), int(-L2/dbu))))
        
        d1 = (W1a - W1b) / 2.0
        d2 = (W2a - W2b) / 2.0
        x1 = d1 * hOverlap / L1
        x2 = d2 * hOverlap / L2
        xOffset = x1 if x1 >= x2 else x2
        centerOffset = (W2a - W1a) / 2.0
        pitch = 2.0 * lengthSide + W1a + lowerSpace
        botOffset = W2b / 2.0 + W1b / 2.0 + space + centerOffset + xOffset
        
        FRONT_all = pya.Region()
        METAL_all = pya.Region()
        
        front_single = botElectrode.dup().transform(pya.Trans(int(botOffset/dbu), 0))
        front_single.insert(topElectrode.dup().transform(pya.Trans(0, int((L1 + L2 - hOverlap + hElectrode)/dbu))))
        
        metal_single = pya.Region()
        metal_single.insert(get_circle(W1a / 2.0 + lengthSide + botOffset, hElectrode + L1 - hOverlap / 2.0, diameter / 2.0))
        metal_single.insert(get_circle(W2a / 2.0 + lengthSide, hOverlap / 2.0 - L2 + L1 + L2 - hOverlap + hElectrode, diameter / 2.0))
        
        for i in range(numElements):
            shift = int((i * pitch)/dbu)
            FRONT_all.insert(front_single.dup().transform(pya.Trans(shift, 0)))
            METAL_all.insert(metal_single.dup().transform(pya.Trans(shift, 0)))
            
        front = FRONT_all
        metal = METAL_all
        
        shiftPitch = 0.0 if ISELECTRODE else lowerSpace
        total_len = numElements * pitch - shiftPitch
        back_raw = create_back_side_path(dbu, L1, L2, hOverlap, total_len, hElectrode, LB, HB)
        back = pya.Region(back_raw)
        
        trans_offset = pya.Trans(int(-botOffset/dbu), 0)
        front.transform(trans_offset)
        metal.transform(trans_offset)
        back.transform(trans_offset)
        
    elif style == "RT3":
        d1 = (W1a - W1b) / 2.0
        e1 = (1.0 - hOverlap / L1) * d1
        d2 = (W2a - W2b) / 2.0
        e2 = (1.0 - hOverlap / L2) * d2
        LeBot = 4.0 * space + 4.0 * d2 + 2.0 * W2b + W1b - 2.0 * e2
        LeTop = LeBot + lowerSpace if ISELECTRODE else LeBot
        pitch = LeBot + lowerSpace
        pxLower = 2.0 * space + d2 + W2b - e1
        qxTop = LeBot - space - W2a
        
        leverBottom = get_trap_beam(W1a, W1b, L1, False)
        leverTop = get_trap_beam(W2a, W2b, L2, True)
        
        topElectrode = pya.Region(pya.Box(0, 0, int(LeTop/dbu), int(hElectrode/dbu)))
        botElectrode = pya.Region(pya.Box(0, 0, int(LeBot/dbu), int(hElectrode/dbu)))
        
        botElectrode.insert(leverBottom.dup().transform(pya.Trans(int(pxLower/dbu), int(hElectrode/dbu))))
        topElectrode.insert(leverTop.dup().transform(pya.Trans(int(space/dbu), int(-L2/dbu))))
        topElectrode.insert(leverTop.dup().transform(pya.Trans(int(qxTop/dbu), int(-L2/dbu))))
        
        front_single = botElectrode.dup()
        front_single.insert(topElectrode.dup().transform(pya.Trans(0, int((L1 + L2 - hOverlap + hElectrode)/dbu))))
        
        metal_single = pya.Region()
        metal_single.insert(get_circle(W1a / 2.0 + pxLower, L1 - hOverlap / 2.0 + hElectrode, diameter / 2.0))
        metal_single.insert(get_circle(W2a / 2.0 + space, hOverlap / 2.0 - L2 + L1 + L2 - hOverlap + hElectrode, diameter / 2.0))
        metal_single.insert(get_circle(W2a / 2.0 + qxTop, hOverlap / 2.0 - L2 + L1 + L2 - hOverlap + hElectrode, diameter / 2.0))
        
        FRONT_all = pya.Region()
        METAL_all = pya.Region()
        for i in range(numElements):
            shift = int((i * pitch)/dbu)
            FRONT_all.insert(front_single.dup().transform(pya.Trans(shift, 0)))
            METAL_all.insert(metal_single.dup().transform(pya.Trans(shift, 0)))
            
        front = FRONT_all
        metal = METAL_all
        
        shiftPitch = 0.0 if ISELECTRODE else lowerSpace
        total_len = numElements * pitch - shiftPitch
        back = pya.Region(create_back_side_path(dbu, L1, L2, hOverlap, total_len, hElectrode, LB, HB))
        
    elif style == "TrapVLW":
        leverBottom = get_trap_beam(W1a, W1b, L1, False)
        leverTop = get_trap_beam(W2a, W2b, L2, True)
        d = (L1 - hOverlap) * (W1a - W1b) / (2.0 * L1)
        pitch = W1a + W2b + 2.0 * space - 2.0 * d
        electrodeLength = space + (numElements - 1) * pitch + W1a - d + space + W2b + (W2a - W2b) / 2.0 + space
        
        front.insert(pya.Box(0, 0, int(electrodeLength/dbu), int(hElectrode/dbu)))
        front.insert(pya.Box(0, int((L1 + L2 - hOverlap + hElectrode)/dbu), int(electrodeLength/dbu), int((L1 + L2 - hOverlap + 2.0*hElectrode)/dbu)))
        
        metal.insert(get_circle(space + W1a/2.0, hElectrode + L1 - hOverlap/2.0, diameter/2.0))
        
        e = electrodeLength - W2a - space - (numElements - 1) * pitch
        for i in range(numElements):
            shift = i * pitch
            front.insert(leverBottom.dup().transform(pya.Trans(int((shift + space)/dbu), int(hElectrode/dbu))))
            metal.insert(get_circle(shift + space + W1a/2.0, hElectrode + L1 - hOverlap/2.0, diameter/2.0))
            
            front.insert(leverTop.dup().transform(pya.Trans(int((shift + e)/dbu), int((L1 - hOverlap + hElectrode)/dbu))))
            metal.insert(get_circle(shift + e + W2a/2.0, L1 - hOverlap/2.0 + hElectrode, diameter/2.0))
            
        sideElectrodeBottom = get_side_electrodes(L1, W1a, W1b, hOverlap, lengthSide, False)
        sideElectrodeTop = get_side_electrodes(L2, W2a, W2b, hOverlap, lengthSide, True)
        
        dPrime = (W2a - W2b) / 2.0
        front.insert(sideElectrodeBottom.dup().transform(pya.Trans(int(d/dbu), int((L1 - hOverlap + hElectrode)/dbu))))
        front.insert(sideElectrodeTop.dup().transform(pya.Trans(int((electrodeLength - dPrime)/dbu), int((L1 - hOverlap + hElectrode)/dbu))))
        
        back = pya.Region(create_back_side_path(dbu, L1, L2, hOverlap, electrodeLength, hElectrode, LB, HB))
        
    elif style == "TrapCONST":
        leverBottom = get_trap_beam(W1a, W1b, L1, False)
        leverTop = get_trap_beam(W1a, W1b, L1, True)
        d = (L1 - hOverlap) * (W1a - W1b) / (2.0 * L1)
        pitch = W1a + W1b + 2.0 * space - 2.0 * d
        electrodeLength = space + (numElements - 1) * pitch + W1a - d + space + W1b + (W1a - W1b) / 2.0 + space
        
        front.insert(pya.Box(0, 0, int(electrodeLength/dbu), int(hElectrode/dbu)))
        front.insert(pya.Box(0, int((L1 + L1 - hOverlap + hElectrode)/dbu), int(electrodeLength/dbu), int((L1 + L1 - hOverlap + 2.0*hElectrode)/dbu)))
        
        metal.insert(get_circle(space + W1a/2.0, hElectrode + L1 - hOverlap/2.0, diameter/2.0))
        
        e = electrodeLength - W1a - space - (numElements - 1) * pitch
        for i in range(numElements):
            shift = i * pitch
            front.insert(leverBottom.dup().transform(pya.Trans(int((shift + space)/dbu), int(hElectrode/dbu))))
            metal.insert(get_circle(shift + space + W1a/2.0, hElectrode + L1 - hOverlap/2.0, diameter/2.0))
            
            front.insert(leverTop.dup().transform(pya.Trans(int((shift + e)/dbu), int((L1 - hOverlap + hElectrode)/dbu))))
            metal.insert(get_circle(shift + e + W1a/2.0, L1 - hOverlap/2.0 + hElectrode, diameter/2.0))
            
        sideElectrodeBottom = get_side_electrodes(L1, W1a, W1b, hOverlap, lengthSide, False)
        sideElectrodeTop = get_side_electrodes(L1, W1a, W1b, hOverlap, lengthSide, True)
        
        dPrime = (W1a - W1b) / 2.0
        front.insert(sideElectrodeBottom.dup().transform(pya.Trans(int(d/dbu), int((L1 - hOverlap + hElectrode)/dbu))))
        front.insert(sideElectrodeTop.dup().transform(pya.Trans(int((electrodeLength - dPrime)/dbu), int((L1 - hOverlap + hElectrode)/dbu))))
        
        back = pya.Region(create_back_side_path(dbu, L1, L1, hOverlap, electrodeLength, hElectrode, LB, HB))
        
    front.merge()
    metal.merge()
    back.merge()
    return front, metal, back

# helper: backside path with bezier curves
def create_back_side_path(dbu, L1, L2, hOverlap, electrodeLength, hElectrode, LB, HB):
    top = L1 + L2 - hOverlap
    pts = []
    
    pts.append(pya.DPoint(0.0, 0.0))
    pts.append(pya.DPoint(electrodeLength, 0.0))
    
    bez = compute_bezier_pts(electrodeLength, 0.0, electrodeLength + LB / 2.0, 0.0, electrodeLength + LB, HB / 2.0, electrodeLength + LB, HB, 16)
    pts += [pya.DPoint(p[0], p[1]) for p in bez[1:]]
    
    pts.append(pya.DPoint(electrodeLength + LB, top + HB))
    
    bez = compute_bezier_pts(electrodeLength + LB, top + HB, electrodeLength + LB, top + 1.5 * HB, electrodeLength + LB / 2.0, top + 2.0 * HB, electrodeLength, top + 2.0 * HB, 16)
    pts += [pya.DPoint(p[0], p[1]) for p in bez[1:]]
    
    pts.append(pya.DPoint(0.0, top + 2.0 * HB))
    
    bez = compute_bezier_pts(0.0, top + 2.0 * HB, -LB / 2.0, top + 2.0 * HB, -LB, top + 1.5 * HB, -LB, top + HB, 16)
    pts += [pya.DPoint(p[0], p[1]) for p in bez[1:]]
    
    pts.append(pya.DPoint(-LB, HB))
    
    bez = compute_bezier_pts(-LB, HB, -LB, HB / 2.0, -LB / 2.0, 0.0, 0.0, 0.0, 16)
    pts += [pya.DPoint(p[0], p[1]) for p in bez[1:]]
    
    pts_trans = [pya.Point(int(p.x/dbu), int((p.y + hElectrode - HB)/dbu)) for p in pts]
    return pya.Polygon(pts_trans)


def draw_gear_t(layout, rad, width, height, numGears, triangleL, numSides):
    dbu = layout.dbu
    region = pya.Region()
    
    # Inner circle
    inner_pts = []
    for i in range(numSides):
        angle = i * 2.0 * math.pi / numSides
        inner_pts.append(pya.Point(int(rad * math.cos(angle)/dbu), int(rad * math.sin(angle)/dbu)))
    region.insert(pya.Polygon(inner_pts))
    
    # Teeth
    pts_tooth = [
        pya.Point(0, int(-height / 2.0 / dbu)),
        pya.Point(int((rad + width)/dbu), int(-height / 2.0 / dbu)),
        pya.Point(int((rad + width + triangleL)/dbu), 0),
        pya.Point(int((rad + width)/dbu), int(height / 2.0 / dbu)),
        pya.Point(0, int(height / 2.0 / dbu))
    ]
    tooth_poly = pya.Polygon(pts_tooth)
    tooth_region = pya.Region(tooth_poly)
    
    dTheta = 2.0 * math.pi / numGears
    for i in range(numGears):
        temp = tooth_region.dup()
        temp.transform(pya.ICplxTrans(1.0, math.degrees(i * dTheta), False, 0, 0))
        region.insert(temp)
        
    region.merge()
    return region


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


def draw_straight_spring(layout, layer_idx, anchor_layer_idx, width, radiusCenterHub, widthRing, radiusRing, numSides, numElements, anchorDistance):
    dbu = layout.dbu
    region = pya.Region()
    
    # Hub circle
    hub_poly = draw_ellipse(dbu, 0.0, 0.0, radiusCenterHub, radiusCenterHub, numSides)
    region.insert(hub_poly)
    
    # Outer ring torus
    ring_poly = draw_ellipse(dbu, 0.0, 0.0, radiusRing + widthRing/2.0, radiusRing + widthRing/2.0, numSides)
    ring_hole = draw_ellipse(dbu, 0.0, 0.0, radiusRing - widthRing/2.0, radiusRing - widthRing/2.0, numSides)
    region.insert(pya.Region(ring_poly) - pya.Region(ring_hole))
    
    # Spokes (straight beams)
    beam_box = pya.Box(0, int(-width/2.0/dbu), int(radiusRing/dbu), int(width/2.0/dbu))
    beam_reg = pya.Region(beam_box)
    
    dTheta = 2.0 * math.pi / numElements
    for i in range(numElements):
        temp = beam_reg.dup()
        temp.transform(pya.ICplxTrans(1.0, math.degrees(i * dTheta), False, 0, 0))
        region.insert(temp)
        
    # Anchor circle
    r_anchor = radiusCenterHub - anchorDistance
    anchor_region = pya.Region(draw_ellipse(dbu, 0.0, 0.0, r_anchor, r_anchor, numSides))
    
    region.merge()
    anchor_region.merge()
    return region, anchor_region


def draw_straight_spring_electrodes(layout, layer_idx, anchor_layer_idx, width, radiusCenterHub, widthRing, radiusRing, numSides, numElements, gap, electrodeWidth, numElectrodes, gapFraction, anchorElectrodeDistance, anchorDistance):
    dbu = layout.dbu
    # Base straight spring
    region, anchor_region = draw_straight_spring(layout, layer_idx, anchor_layer_idx, width, radiusCenterHub, widthRing, radiusRing, numSides, numElements, anchorDistance)
    
    # Electrodes
    radiusElectrodeINNER = radiusRing + widthRing / 2.0 + gap
    radiusElectrodeMID = radiusElectrodeINNER + electrodeWidth / 2.0
    
    electrodes_poly = draw_ellipse(dbu, 0.0, 0.0, radiusElectrodeMID + electrodeWidth/2.0, radiusElectrodeMID + electrodeWidth/2.0, numSides)
    electrodes_hole = draw_ellipse(dbu, 0.0, 0.0, radiusElectrodeMID - electrodeWidth/2.0, radiusElectrodeMID - electrodeWidth/2.0, numSides)
    electrodes = pya.Region(electrodes_poly) - pya.Region(electrodes_hole)
    
    circumference = math.pi * 2.0 * radiusElectrodeINNER
    electrodeSegment = circumference / float(numElectrodes)
    theta_deg = (electrodeSegment * gapFraction) / radiusElectrodeINNER * (180.0 / math.pi)
    
    # Subtraction arc
    r_arc_out = radiusElectrodeINNER + electrodeWidth * 1.5
    arc = pya.Region(draw_torus_arc(dbu, 0.0, 0.0, r_arc_out, r_arc_out, -theta_deg / 2.0, theta_deg / 2.0, numSides))
    
    if gapFraction > 0.0 and gapFraction < 1.0:
        dTheta = 2.0 * math.pi / numElectrodes
        for i in range(numElectrodes):
            temp = arc.dup()
            temp.transform(pya.ICplxTrans(1.0, math.degrees(i * dTheta), False, 0, 0))
            electrodes -= temp
            
    region.insert(electrodes)
    
    # Anchor torus
    anchorTorus_poly = draw_ellipse(dbu, 0.0, 0.0, radiusElectrodeMID + (electrodeWidth/2.0 - anchorElectrodeDistance), radiusElectrodeMID + (electrodeWidth/2.0 - anchorElectrodeDistance), numSides)
    anchorTorus_hole = draw_ellipse(dbu, 0.0, 0.0, radiusElectrodeMID - (electrodeWidth/2.0 - anchorElectrodeDistance), radiusElectrodeMID - (electrodeWidth/2.0 - anchorElectrodeDistance), numSides)
    anchorTorus = pya.Region(anchorTorus_poly) - pya.Region(anchorTorus_hole)
    
    theta_anc_deg = (electrodeSegment * gapFraction + 2.0 * anchorElectrodeDistance) / radiusElectrodeINNER * (180.0 / math.pi)
    arc_anc = pya.Region(draw_torus_arc(dbu, 0.0, 0.0, r_arc_out, r_arc_out, -theta_anc_deg / 2.0, theta_anc_deg / 2.0, numSides))
    
    if gapFraction > 0.0 and gapFraction < 1.0:
        dTheta = 2.0 * math.pi / numElectrodes
        for i in range(numElectrodes):
            temp = arc_anc.dup()
            temp.transform(pya.ICplxTrans(1.0, math.degrees(i * dTheta), False, 0, 0))
            anchorTorus -= temp
            
    anchor_region.insert(anchorTorus)
    
    region.merge()
    anchor_region.merge()
    return region, anchor_region


def draw_circular_spring_electrode(layout, layer_idx, anchor_layer_idx, width, radiusCenterHub, widthRing, radiusRing, numSides, numElements, gap, electrodeWidth, numElectrodes, gapFraction, anchorElectrodeDistance, anchorDistance):
    dbu = layout.dbu
    # Base circular spring
    region, anchor_region = draw_circular_spring(layout, layer_idx, anchor_layer_idx, width, radiusCenterHub, widthRing, radiusRing, numSides, numElements, anchorDistance)
    
    # Electrodes
    radiusElectrodeINNER = radiusRing + widthRing / 2.0 + gap
    radiusElectrodeMID = radiusElectrodeINNER + electrodeWidth / 2.0
    
    electrodes_poly = draw_ellipse(dbu, 0.0, 0.0, radiusElectrodeMID + electrodeWidth/2.0, radiusElectrodeMID + electrodeWidth/2.0, numSides)
    electrodes_hole = draw_ellipse(dbu, 0.0, 0.0, radiusElectrodeMID - electrodeWidth/2.0, radiusElectrodeMID - electrodeWidth/2.0, numSides)
    electrodes = pya.Region(electrodes_poly) - pya.Region(electrodes_hole)
    
    circumference = math.pi * 2.0 * radiusElectrodeINNER
    electrodeSegment = circumference / float(numElectrodes)
    theta_deg = (electrodeSegment * gapFraction) / radiusElectrodeINNER * (180.0 / math.pi)
    
    r_arc_out = radiusElectrodeINNER + electrodeWidth * 1.5
    arc = pya.Region(draw_torus_arc(dbu, 0.0, 0.0, r_arc_out, r_arc_out, -theta_deg / 2.0, theta_deg / 2.0, numSides))
    
    if gapFraction > 0.0 and gapFraction < 1.0:
        dTheta = 2.0 * math.pi / numElectrodes
        for i in range(numElectrodes):
            temp = arc.dup()
            temp.transform(pya.ICplxTrans(1.0, math.degrees(i * dTheta), False, 0, 0))
            electrodes -= temp
            
    region.insert(electrodes)
    
    # Anchor torus
    anchorTorus_poly = draw_ellipse(dbu, 0.0, 0.0, radiusElectrodeMID + (electrodeWidth/2.0 - anchorElectrodeDistance), radiusElectrodeMID + (electrodeWidth/2.0 - anchorElectrodeDistance), numSides)
    anchorTorus_hole = draw_ellipse(dbu, 0.0, 0.0, radiusElectrodeMID - (electrodeWidth/2.0 - anchorElectrodeDistance), radiusElectrodeMID - (electrodeWidth/2.0 - anchorElectrodeDistance), numSides)
    anchorTorus = pya.Region(anchorTorus_poly) - pya.Region(anchorTorus_hole)
    
    theta_anc_deg = (electrodeSegment * gapFraction + 2.0 * anchorElectrodeDistance) / radiusElectrodeINNER * (180.0 / math.pi)
    arc_anc = pya.Region(draw_torus_arc(dbu, 0.0, 0.0, r_arc_out, r_arc_out, -theta_anc_deg / 2.0, theta_anc_deg / 2.0, numSides))
    
    if gapFraction > 0.0 and gapFraction < 1.0:
        dTheta = 2.0 * math.pi / numElectrodes
        for i in range(numElectrodes):
            temp = arc_anc.dup()
            temp.transform(pya.ICplxTrans(1.0, math.degrees(i * dTheta), False, 0, 0))
            anchorTorus -= temp
            
    anchor_region.insert(anchorTorus)
    
    region.merge()
    anchor_region.merge()
    return region, anchor_region


def draw_comb_drive_v1(layout, width1, width2, length1, length2, numElectrodes, pitch, baseHeight, baseLayer, anchorDistance, anchorLayer):
    dbu = layout.dbu
    r_top = pya.Region(pya.Box(0, int(-baseHeight/dbu), int(((numElectrodes - 1) * pitch + width1)/dbu), 0))
    r_anchor = pya.Region(pya.Box(int(anchorDistance/dbu), int((-baseHeight + anchorDistance)/dbu), int(((numElectrodes - 1) * pitch + width1 - anchorDistance)/dbu), int(-anchorDistance/dbu)))
    
    startX = 0.0
    startY = -baseHeight - length1
    for i in range(numElectrodes):
        r_top.insert(pya.Box(int((i * pitch + startX)/dbu), int(startY/dbu), int((i * pitch + startX + width1)/dbu), int((startY + length1)/dbu)))
        
    startX = pitch / 2.0
    startY = -baseHeight - 2.0 * length1 + length2
    r_bottom = pya.Region(pya.Box(int(startX/dbu), int((startY - width2)/dbu), int((startX + (numElectrodes - 2) * pitch + width1)/dbu), int(startY/dbu)))
    for i in range(numElectrodes - 1):
        r_bottom.insert(pya.Box(int((i * pitch + startX)/dbu), int(startY/dbu), int((i * pitch + startX + width1)/dbu), int((startY + length1)/dbu)))
        
    r_top.merge()
    r_bottom.merge()
    r_anchor.merge()
    return r_top, r_bottom, r_anchor


def draw_linear_drive_v1(layout, width1, length1, length2, length3, gap, numElectrodes, pitch, baseHeight, baseWidth, rotorPitch, anchorDistance):
    dbu = layout.dbu
    lengthTopElectrodes = (numElectrodes - 1) * pitch + baseWidth
    startX = -lengthTopElectrodes / 2.0 - length3
    
    r_middle = pya.Region(pya.Box(int(startX/dbu), int(-length2/2.0/dbu), int(-startX/dbu), int(length2/2.0/dbu)))
    
    startX = -lengthTopElectrodes / 2.0
    startY = length2 + length1 + gap
    
    electrode = pya.Box(int(startX/dbu), int(startY/dbu), int((startX + baseWidth)/dbu), int((startY + baseHeight)/dbu))
    anchor = pya.Box(int((startX + anchorDistance)/dbu), int((startY + anchorDistance)/dbu), int((startX + baseWidth - anchorDistance)/dbu), int((startY + baseHeight - anchorDistance)/dbu))
    
    r_electrodes = pya.Region()
    r_anchors = pya.Region()
    
    for i in range(numElectrodes):
        shift_x = int((i * pitch)/dbu)
        
        # Top pads
        r_electrodes.insert(electrode.moved(shift_x, 0))
        r_anchors.insert(anchor.moved(shift_x, 0))
        
        # Bottom pads
        shift_y = int((-2.0 * startY - baseHeight)/dbu)
        r_electrodes.insert(electrode.moved(shift_x, shift_y))
        r_anchors.insert(anchor.moved(shift_x, shift_y))
        
    numMidFingers = int(lengthTopElectrodes / rotorPitch)
    for i in range(numMidFingers + 1):
        fx_start = i * rotorPitch - lengthTopElectrodes / 2.0
        # Upper fingers
        r_middle.insert(pya.Box(int(fx_start/dbu), int(length2/2.0/dbu), int((fx_start + width1)/dbu), int((length2/2.0 + length1)/dbu)))
        # Lower fingers
        r_middle.insert(pya.Box(int(fx_start/dbu), int((-length2/2.0 - length1)/dbu), int((fx_start + width1)/dbu), int(-length2/2.0/dbu)))
        
    r_electrodes.merge()
    r_anchors.merge()
    r_middle.merge()
    
    return r_electrodes, r_anchors, r_middle


def draw_dc_beam_torsional2(layout, width1, width2, width3, width4, length1, length2, length3, gap, baseHeight, baseWidth, anchorDistance):
    dbu = layout.dbu
    r_struct = pya.Region()
    r_anchor = pya.Region()
    
    r_struct.insert(pya.Box(0, 0, int(baseWidth/dbu), int(baseHeight/dbu)))
    r_anchor.insert(pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((baseWidth - anchorDistance)/dbu), int((baseHeight - anchorDistance)/dbu)))
    
    startX = baseWidth
    startY = baseHeight / 2.0 - width3 / 2.0
    r_struct.insert(pya.Box(int(startX/dbu), int(startY/dbu), int((startX + length3)/dbu), int((startY + width3)/dbu)))
    
    frame_y_min = baseHeight / 2.0 - length1 / 2.0 - length2 - width4
    frame_y_max = baseHeight / 2.0 + length1 / 2.0 + length2 + width4
    startX += length3
    r_struct.insert(pya.Box(int(startX/dbu), int(frame_y_min/dbu), int((startX + 2.0 * gap + 2.0 * width4 + width1)/dbu), int(frame_y_max/dbu)))
    r_struct -= pya.Region(pya.Box(int((startX + width4)/dbu), int((frame_y_min + width4)/dbu), int((startX + 2.0 * gap + width4 + width1)/dbu), int((frame_y_max - width4)/dbu)))
    
    center_spring_x = startX + width4 + gap + width1 / 2.0 - width2 / 2.0
    r_struct.insert(pya.Box(int(center_spring_x/dbu), int(frame_y_min/dbu), int((center_spring_x + width2)/dbu), int(frame_y_max/dbu)))
    
    beam_x = center_spring_x + width2 / 2.0 - width1 / 2.0
    beam_y = frame_y_min + width4 + length2
    r_struct.insert(pya.Box(int(beam_x/dbu), int(beam_y/dbu), int((beam_x + width1)/dbu), int((beam_y + length1)/dbu)))
    
    right_conn_x = startX + width1 + gap + width4
    right_conn_y = beam_y + length1 / 2.0 - width3 / 2.0
    r_struct.insert(pya.Box(int(right_conn_x/dbu), int(right_conn_y/dbu), int((right_conn_x + length3)/dbu), int((right_conn_y + width3)/dbu)))
    
    right_base_x = right_conn_x + length3
    right_base_y = right_conn_y + width3 / 2.0 - baseHeight / 2.0
    r_struct.insert(pya.Box(int(right_base_x/dbu), int(right_base_y/dbu), int((right_base_x + baseWidth)/dbu), int((right_base_y + baseHeight)/dbu)))
    r_anchor.insert(pya.Box(int((right_base_x + anchorDistance)/dbu), int((right_base_y + anchorDistance)/dbu), int((right_base_x + baseWidth - anchorDistance)/dbu), int((right_base_y + baseHeight - anchorDistance)/dbu)))
    
    r_struct.merge()
    r_anchor.merge()
    return r_struct, r_anchor


def draw_cantilever_single_generic(layout, style, width, length, widthTop, lengthTop, length2, length3, hollowW, triangleHeight, radius, gap, rX1, rY1, rX2, rY2, paddleW, paddleL, baseHeight, baseExtent, anchorDistance):
    dbu = layout.dbu
    r_struct = pya.Region()
    r_anchor = pya.Region()
    
    def add_s_anchor(w, bh, be):
        if anchorDistance < be + w / 2.0:
            r_anchor.insert(pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((2.0 * be + w - anchorDistance)/dbu), int((bh - anchorDistance)/dbu)))

    def add_pb_anchor(bh, bl):
        if anchorDistance < bl / 2.0:
            r_anchor.insert(pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((bl - anchorDistance)/dbu), int((bh - anchorDistance)/dbu)))

    if style == "SRect":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "STriangle":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        pts_tri = [
            pya.Point(int(baseExtent/dbu), int((baseHeight + length)/dbu)),
            pya.Point(int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)),
            pya.Point(int((baseExtent + width / 2.0)/dbu), int((baseHeight + length + triangleHeight)/dbu))
        ]
        r_struct.insert(pya.Polygon(pts_tri))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "STrapezoid":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        pts_trap = [
            pya.Point(int(baseExtent/dbu), int(baseHeight/dbu)),
            pya.Point(int((baseExtent + width)/dbu), int(baseHeight/dbu)),
            pya.Point(int((baseExtent + width / 2.0 + widthTop / 2.0)/dbu), int((baseHeight + length)/dbu)),
            pya.Point(int((baseExtent + width / 2.0 - widthTop / 2.0)/dbu), int((baseHeight + length)/dbu))
        ]
        r_struct.insert(pya.Polygon(pts_trap))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "SPaddle":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        r_struct.insert(pya.Box(int((baseExtent + width/2.0 - widthTop/2.0)/dbu), int((baseHeight + length)/dbu), int((baseExtent + width/2.0 + widthTop/2.0)/dbu), int((baseHeight + length + lengthTop)/dbu)))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "SCurvedHalf":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        torus = draw_torus_arc(dbu, baseExtent + width / 2.0 + radius, baseHeight, radius, width, 90.0, 180.0, 64)
        r_struct.insert(torus)
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "SCurvedFull":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        torus = draw_torus_arc(dbu, baseExtent + width / 2.0 + radius, baseHeight, radius, width, 0.0, 180.0, 64)
        r_struct.insert(torus)
        r_struct.insert(pya.Box(int((baseExtent + 2.0 * radius)/dbu), int((baseHeight - length)/dbu), int((baseExtent + 2.0 * radius + width)/dbu), int(baseHeight/dbu)))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "HRect":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        if hollowW < width / 2.0:
            r_struct -= pya.Region(pya.Box(int((baseExtent + hollowW)/dbu), int(baseHeight/dbu), int((baseExtent + width - hollowW)/dbu), int((baseHeight + length - hollowW)/dbu)))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "HTriangle":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        pts_tri = [
            pya.Point(int(baseExtent/dbu), int((baseHeight + length)/dbu)),
            pya.Point(int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)),
            pya.Point(int((baseExtent + width / 2.0)/dbu), int((baseHeight + length + triangleHeight)/dbu))
        ]
        r_struct.insert(pya.Polygon(pts_tri))
        if hollowW < width / 2.0:
            triHollow = 2.0 * triangleHeight * hollowW / width
            pts_hollow = [
                pya.Point(int((baseExtent + hollowW)/dbu), int(baseHeight/dbu)),
                pya.Point(int((baseExtent + width - hollowW)/dbu), int(baseHeight/dbu)),
                pya.Point(int((baseExtent + width - hollowW)/dbu), int((baseHeight + length)/dbu)),
                pya.Point(int((baseExtent + width / 2.0)/dbu), int((baseHeight + length + triangleHeight - triHollow)/dbu)),
                pya.Point(int((baseExtent + hollowW)/dbu), int((baseHeight + length)/dbu))
            ]
            r_struct -= pya.Region(pya.Polygon(pts_hollow))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "HTrapezoid":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        pts_trap = [
            pya.Point(int((baseExtent + hollowW / 2.0)/dbu), int(baseHeight/dbu)),
            pya.Point(int((baseExtent + width / 2.0 - widthTop / 2.0)/dbu), int((baseHeight + length - hollowW / 2.0)/dbu)),
            pya.Point(int((baseExtent + width / 2.0 + widthTop / 2.0)/dbu), int((baseHeight + length - hollowW / 2.0)/dbu)),
            pya.Point(int((baseExtent + width - hollowW / 2.0)/dbu), int(baseHeight/dbu))
        ]
        path = pya.Path(pts_trap, int(hollowW/dbu))
        r_struct.insert(path.simple_polygon())
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "HPaddle":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        r_struct.insert(pya.Box(int((baseExtent + width/2.0 - widthTop/2.0)/dbu), int((baseHeight + length)/dbu), int((baseExtent + width/2.0 + widthTop/2.0)/dbu), int((baseHeight + length + lengthTop)/dbu)))
        if hollowW < width / 2.0 and hollowW < widthTop:
            hollow1 = pya.Box(int((baseExtent + hollowW)/dbu), int(baseHeight/dbu), int((baseExtent + width - hollowW)/dbu), int((baseHeight + length + hollowW)/dbu))
            hollow2 = pya.Box(int((baseExtent + width/2.0 - widthTop/2.0 + hollowW)/dbu), int((baseHeight + length + hollowW)/dbu), int((baseExtent + width/2.0 + widthTop/2.0 - hollowW)/dbu), int((baseHeight + length + lengthTop - hollowW)/dbu))
            r_struct -= pya.Region(hollow1).join(pya.Region(hollow2))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "HCurvedHalf":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        torus = draw_torus_arc(dbu, baseExtent + width / 2.0 + radius, baseHeight, radius, width, 90.0, 180.0, 64)
        r_struct.insert(torus)
        if hollowW < width / 2.0:
            hollow_torus = draw_torus_arc(dbu, baseExtent + width / 2.0 + radius, baseHeight, radius, width - 2.0 * hollowW, (1.5707963267948966 + hollowW / radius) * 57.29577951308232, 180.0, 64)
            r_struct -= pya.Region(hollow_torus)
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "HCurvedFull":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        torus = draw_torus_arc(dbu, baseExtent + width / 2.0 + radius, baseHeight, radius, width, 0.0, 180.0, 64)
        r_struct.insert(torus)
        r_struct.insert(pya.Box(int((baseExtent + 2.0 * radius)/dbu), int((baseHeight - length)/dbu), int((baseExtent + 2.0 * radius + width)/dbu), int(baseHeight/dbu)))
        if hollowW < width / 2.0:
            hollow_torus = draw_torus_arc(dbu, baseExtent + width / 2.0 + radius, baseHeight, radius, width - 2.0 * hollowW, 0.0, 180.0, 64)
            hollow_rect = pya.Box(int((baseExtent + 2.0 * radius + hollowW)/dbu), int((baseHeight - length + hollowW)/dbu), int((baseExtent + 2.0 * radius + width - hollowW)/dbu), int(baseHeight/dbu))
            r_struct -= pya.Region(hollow_torus).join(pya.Region(hollow_rect))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "PB2":
        bx = lengthTop / 2.0 - gap / 2.0
        r_struct.insert(pya.Box(0, 0, int((baseExtent + bx)/dbu), int(baseHeight/dbu)))
        if gap <= lengthTop - 2.0 * width:
            r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
            r_struct.insert(pya.Box(int(baseExtent/dbu), int((baseHeight + length - width)/dbu), int((baseExtent + lengthTop)/dbu), int((baseHeight + length)/dbu)))
            add_pb_anchor(baseHeight, baseExtent + bx)
            
            temp_arm = pya.Region(pya.Box(0, 0, int((baseExtent + bx)/dbu), int(baseHeight/dbu)))
            temp_arm.insert(pya.Box(int((bx - width)/dbu), int(baseHeight/dbu), int(bx/dbu), int((baseHeight + length2)/dbu)))
            temp_arm.transform(pya.Trans(int((baseExtent + lengthTop / 2.0 + gap / 2.0)/dbu), int((length - length2)/dbu)))
            r_struct.insert(temp_arm)
            
            temp_anc = pya.Region()
            if anchorDistance < (baseExtent + bx) / 2.0:
                temp_anc.insert(pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((baseExtent + bx - anchorDistance)/dbu), int((baseHeight - anchorDistance)/dbu)))
            temp_anc.transform(pya.Trans(int((baseExtent + lengthTop / 2.0 + gap / 2.0)/dbu), int((length - length2)/dbu)))
            r_anchor.insert(temp_anc)
            
    elif style == "PB3":
        bx = (lengthTop - 2.0 * gap) / 2.0
        r_struct.insert(pya.Box(0, 0, int((baseExtent + bx / 2.0)/dbu), int(baseHeight/dbu)))
        if gap <= (lengthTop - 4.0 * width) / 2.0:
            r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
            r_struct.insert(pya.Box(int(baseExtent/dbu), int((baseHeight + length - width)/dbu), int((baseExtent + lengthTop)/dbu), int((baseHeight + length)/dbu)))
            add_pb_anchor(baseHeight, baseExtent + bx / 2.0)
            
            temp_mid = pya.Region(pya.Box(0, 0, int(bx/dbu), int(baseHeight/dbu)))
            temp_mid.insert(pya.Box(int((bx - width)/2.0/dbu), int(baseHeight/dbu), int((bx + width)/2.0/dbu), int((baseHeight + length2)/dbu)))
            temp_mid.transform(pya.Trans(int((baseExtent + bx / 2.0 + gap)/dbu), int((length - length2)/dbu)))
            r_struct.insert(temp_mid)
            
            temp_mid_anc = pya.Region()
            if anchorDistance < bx / 2.0:
                temp_mid_anc.insert(pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((bx - anchorDistance)/dbu), int((baseHeight - anchorDistance)/dbu)))
            temp_mid_anc.transform(pya.Trans(int((baseExtent + bx / 2.0 + gap)/dbu), int((length - length2)/dbu)))
            r_anchor.insert(temp_mid_anc)
            
            temp_right = pya.Region(pya.Box(0, 0, int((baseExtent + bx / 2.0)/dbu), int(baseHeight/dbu)))
            temp_right.insert(pya.Box(int((bx / 2.0 - width)/dbu), int(baseHeight/dbu), int((bx / 2.0)/dbu), int((baseHeight + length3)/dbu)))
            temp_right.transform(pya.Trans(int((baseExtent + 2.0 * gap + 1.5 * bx)/dbu), int((length - length3)/dbu)))
            r_struct.insert(temp_right)
            
            temp_right_anc = pya.Region()
            if anchorDistance < (baseExtent + bx / 2.0) / 2.0:
                temp_right_anc.insert(pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((baseExtent + bx / 2.0 - anchorDistance)/dbu), int((baseHeight - anchorDistance)/dbu)))
            temp_right_anc.transform(pya.Trans(int((baseExtent + 2.0 * gap + 1.5 * bx)/dbu), int((length - length3)/dbu)))
            r_anchor.insert(temp_right_anc)
            
    elif style == "UR":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int((baseHeight + length - width)/dbu), int((baseExtent + lengthTop)/dbu), int((baseHeight + length)/dbu)))
        r_struct.insert(pya.Box(int((baseExtent + lengthTop - width)/dbu), int((baseHeight + length - length2)/dbu), int((baseExtent + lengthTop)/dbu), int((baseHeight + length)/dbu)))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "UCF":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        torus1 = draw_torus_arc(dbu, baseExtent + width / 2.0 + radius, baseHeight + length, radius, width, 90.0, 180.0, 64)
        r_struct.insert(torus1)
        r_struct.insert(pya.Box(int((baseExtent + width / 2.0 + radius)/dbu), int((baseHeight + length + radius - width / 2.0)/dbu), int((baseExtent + width / 2.0 + radius + lengthTop)/dbu), int((baseHeight + length + radius + width / 2.0)/dbu)))
        torus2 = draw_torus_arc(dbu, baseExtent + width / 2.0 + radius + lengthTop, baseHeight + length, radius, width, 0.0, 90.0, 64)
        r_struct.insert(torus2)
        r_struct.insert(pya.Box(int((baseExtent + 2.0 * radius + lengthTop)/dbu), int((baseHeight + length - length2)/dbu), int((baseExtent + 2.0 * radius + lengthTop + width)/dbu), int((baseHeight + length)/dbu)))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "UC":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        torus = draw_torus_arc(dbu, baseExtent + width / 2.0 + radius, baseHeight + length, radius, width, 0.0, 180.0, 64)
        r_struct.insert(torus)
        r_struct.insert(pya.Box(int((baseExtent + 2.0 * radius)/dbu), int((baseHeight + length - length2)/dbu), int((baseExtent + 2.0 * radius + width)/dbu), int((baseHeight + length)/dbu)))
        add_s_anchor(width, baseHeight, baseExtent)
        
    elif style == "UCC":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        add_s_anchor(width, baseHeight, baseExtent)
        r_struct.insert(pya.Box(int(baseExtent/dbu), int((baseHeight + length - width)/dbu), int((baseExtent + lengthTop)/dbu), int((baseHeight + length)/dbu)))
        
        LBOT = length2 if length2 > 0.0 else 0.0
        LTOP = length if length2 > 0.0 else length - length2
        r_struct.insert(pya.Box(int((baseExtent + lengthTop / 2.0 - widthTop / 2.0)/dbu), int((baseHeight + LBOT)/dbu), int((baseExtent + lengthTop / 2.0 + widthTop / 2.0)/dbu), int((baseHeight + LTOP)/dbu)))
        
        temp_mid = pya.Region(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        temp_mid.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length3)/dbu)))
        temp_mid.transform(pya.Trans(int((lengthTop - width)/dbu), int((length - length3)/dbu)))
        r_struct.insert(temp_mid)
        
        temp_mid_anc = pya.Region()
        if anchorDistance < baseExtent + width / 2.0:
            temp_mid_anc.insert(pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((2.0 * baseExtent + width - anchorDistance)/dbu), int((baseHeight - anchorDistance)/dbu)))
        temp_mid_anc.transform(pya.Trans(int((lengthTop - width)/dbu), int((length - length3)/dbu)))
        r_anchor.insert(temp_mid_anc)
        
    elif style == "UCP":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        r_struct.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length)/dbu)))
        add_s_anchor(width, baseHeight, baseExtent)
        r_struct.insert(pya.Box(int(baseExtent/dbu), int((baseHeight + length - width)/dbu), int((baseExtent + lengthTop)/dbu), int((baseHeight + length)/dbu)))
        
        r_struct.insert(pya.Box(int((baseExtent + lengthTop / 2.0 - widthTop / 2.0)/dbu), int((baseHeight + length - width / 2.0 - length2)/dbu), int((baseExtent + lengthTop / 2.0 + widthTop / 2.0)/dbu), int((baseHeight + length - width / 2.0 + length2)/dbu)))
        
        temp_mid = pya.Region(pya.Box(0, 0, int((2.0 * baseExtent + width)/dbu), int(baseHeight/dbu)))
        temp_mid.insert(pya.Box(int(baseExtent/dbu), int(baseHeight/dbu), int((baseExtent + width)/dbu), int((baseHeight + length3)/dbu)))
        temp_mid.transform(pya.Trans(int((lengthTop - width)/dbu), int((length - length3)/dbu)))
        r_struct.insert(temp_mid)
        
        temp_mid_anc = pya.Region()
        if anchorDistance < baseExtent + width / 2.0:
            temp_mid_anc.insert(pya.Box(int(anchorDistance/dbu), int(anchorDistance/dbu), int((2.0 * baseExtent + width - anchorDistance)/dbu), int((baseHeight - anchorDistance)/dbu)))
        temp_mid_anc.transform(pya.Trans(int((lengthTop - width)/dbu), int((length - length3)/dbu)))
        r_anchor.insert(temp_mid_anc)
        
    elif style == "CE":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width + 2.0 * rX1)/dbu), int((baseHeight + rY1)/dbu)))
        ellipse1 = draw_ellipse(dbu, baseExtent, baseHeight + rY1, rX1, rY1, 64)
        r_struct -= pya.Region(ellipse1)
        r_struct -= pya.Box(0, int(baseHeight/dbu), int(baseExtent/dbu), int((baseHeight + rY1)/dbu))
        
        ellipse2 = draw_ellipse(dbu, baseExtent + width + 2.0 * rX1, baseHeight + rY1, rX1, rY1, 64)
        r_struct -= pya.Region(ellipse2)
        r_struct -= pya.Box(int((baseExtent + width + 2.0 * rX1)/dbu), int(baseHeight/dbu), int((2.0 * baseExtent + width + 2.0 * rX1)/dbu), int((baseHeight + rY1)/dbu))
        
        r_struct.insert(pya.Box(int((baseExtent + rX1)/dbu), int((baseHeight + rY1)/dbu), int((baseExtent + rX1 + width)/dbu), int((baseHeight + rY1 + length)/dbu)))
        add_s_anchor(width + 2.0 * rX1, baseHeight, baseExtent)
        
    elif style == "CEPaddle":
        r_struct.insert(pya.Box(0, 0, int((2.0 * baseExtent + width + 2.0 * rX1)/dbu), int((baseHeight + rY1)/dbu)))
        ellipse1 = draw_ellipse(dbu, baseExtent, baseHeight + rY1, rX1, rY1, 64)
        r_struct -= pya.Region(ellipse1)
        r_struct -= pya.Box(0, int(baseHeight/dbu), int(baseExtent/dbu), int((baseHeight + rY1)/dbu))
        
        ellipse2 = draw_ellipse(dbu, baseExtent + width + 2.0 * rX1, baseHeight + rY1, rX1, rY1, 64)
        r_struct -= pya.Region(ellipse2)
        r_struct -= pya.Box(int((baseExtent + width + 2.0 * rX1)/dbu), int(baseHeight/dbu), int((2.0 * baseExtent + width + 2.0 * rX1)/dbu), int((baseHeight + rY1)/dbu))
        
        r_struct.insert(pya.Box(int((baseExtent + rX1)/dbu), int((baseHeight + rY1)/dbu), int((baseExtent + rX1 + width)/dbu), int((baseHeight + rY1 + length)/dbu)))
        r_struct.insert(pya.Box(int((baseExtent + rX1 - rX2)/dbu), int((baseHeight + rY1 + length)/dbu), int((baseExtent + rX1 + width + rX2)/dbu), int((baseHeight + rY1 + length + rY2)/dbu)))
        
        ellipse3 = draw_ellipse(dbu, baseExtent + rX1 - rX2, baseHeight + rY1 + length, rX2, rY2, 64)
        r_struct -= pya.Region(ellipse3)
        ellipse4 = draw_ellipse(dbu, baseExtent + rX1 + width + rX2, baseHeight + rY1 + length, rX2, rY2, 64)
        r_struct -= pya.Region(ellipse4)
        
        r_struct.insert(pya.Box(int((baseExtent + rX1 - rX2 - paddleW)/dbu), int((baseHeight + rY1 + length + rY2)/dbu), int((baseExtent + rX1 + width + rX2 + paddleW)/dbu), int((baseHeight + rY1 + length + rY2 + paddleL)/dbu)))
        add_s_anchor(width + 2.0 * rX1, baseHeight, baseExtent)
        
    r_struct.merge()
    r_anchor.merge()
    return r_struct, r_anchor


def draw_cantilever_array_generic(layout, style, width, startL, endL, pitch, numElements, baseHeight, baseExtent, variance):
    dbu = layout.dbu
    r_struct = pya.Region()
    
    baseLength = 2.0 * baseExtent + (numElements - 1) * pitch + width
    r_struct.insert(pya.Box(0, 0, int(baseLength/dbu), int(baseHeight/dbu)))
    
    curr_l = startL
    if style == "Linear":
        for i in range(numElements):
            x = baseExtent + i * pitch
            r_struct.insert(pya.Box(int(x/dbu), int(baseHeight/dbu), int((x + width)/dbu), int((baseHeight + curr_l)/dbu)))
            curr_l += variance
    elif style == "Percentage":
        for i in range(numElements):
            x = baseExtent + i * pitch
            r_struct.insert(pya.Box(int(x/dbu), int(baseHeight/dbu), int((x + width)/dbu), int((baseHeight + curr_l)/dbu)))
            curr_l *= (1.0 + variance / 100.0)
    elif style == "Sinusoid":
        sinInc = 2.0 * math.pi / numElements
        for i in range(numElements):
            x = baseExtent + i * pitch
            sineLength = startL + variance * math.sin(i * sinInc)
            r_struct.insert(pya.Box(int(x/dbu), int(baseHeight/dbu), int((x + width)/dbu), int((baseHeight + sineLength)/dbu)))
    elif style == "LinearSE":
        deltaL = (endL - startL) / float(numElements - 1) if numElements > 1 else 0.0
        for i in range(numElements):
            x = baseExtent + i * pitch
            r_struct.insert(pya.Box(int(x/dbu), int(baseHeight/dbu), int((x + width)/dbu), int((baseHeight + curr_l)/dbu)))
            curr_l += deltaL
    elif style == "NonLinearSE":
        ratio = abs(endL / startL) if startL != 0.0 else endL
        root = 1.0 / float(numElements - 1) if numElements > 1 else 1.0
        for i in range(numElements):
            x = baseExtent + i * pitch
            r_struct.insert(pya.Box(int(x/dbu), int(baseHeight/dbu), int((x + width)/dbu), int((baseHeight + curr_l)/dbu)))
            if startL != 0.0:
                curr_l *= ratio ** root
            else:
                curr_l = 1.0 * (ratio ** root)
                
    r_struct.merge()
    return r_struct


# 31. Draw Archimedean Spiral
def draw_spiral_arch(layout, width, turns, separation, inc):
    dbu = layout.dbu
    upper_lim = math.pi * 2.0 * turns
    a = (separation + width) / (math.pi * 2.0)
    
    pts = []
    theta = 0.0
    while theta <= upper_lim + 1e-9:
        r = a * theta
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        pts.append(pya.DPoint(x, y))
        theta += inc
        
    theta = upper_lim
    while theta >= -1e-9:
        r = a * theta
        x = (r + width) * math.cos(theta)
        y = (r + width) * math.sin(theta)
        pts.append(pya.DPoint(x, y))
        theta -= inc
        
    pts_dbu = [pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in pts]
    region = pya.Region()
    region.insert(pya.Polygon(pts_dbu))
    region.merge()
    return region


# 32. Draw Fermat Spiral
def draw_spiral_fermat(layout, width, turns, a, inc):
    dbu = layout.dbu
    upper_lim = math.pi * 2.0 * turns
    
    pts = []
    theta = 0.0
    while theta <= upper_lim + 1e-9:
        r = math.sqrt(a * a * theta)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        pts.append(pya.DPoint(x, y))
        theta += inc
        
    theta = upper_lim
    while theta >= -1e-9:
        r = math.sqrt(a * a * theta)
        x = (r + width) * math.cos(theta)
        y = (r + width) * math.sin(theta)
        pts.append(pya.DPoint(x, y))
        theta -= inc
        
    pts_dbu = [pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in pts]
    region = pya.Region()
    region.insert(pya.Polygon(pts_dbu))
    region.merge()
    return region


# 33. Draw Logarithmic Spiral
def draw_spiral_log(layout, width, turns, a, b, inc):
    dbu = layout.dbu
    upper_lim = math.pi * 2.0 * turns
    
    pts = []
    theta = 0.0
    while theta <= upper_lim + 1e-9:
        r = a * math.exp(b * theta)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        pts.append(pya.DPoint(x, y))
        theta += inc
        
    theta = upper_lim
    while theta >= -1e-9:
        r = a * math.exp(b * theta)
        x = (r + width) * math.cos(theta)
        y = (r + width) * math.sin(theta)
        pts.append(pya.DPoint(x, y))
        theta -= inc
        
    pts_dbu = [pya.Point(int(p.x/dbu), int(p.y/dbu)) for p in pts]
    region = pya.Region()
    region.insert(pya.Polygon(pts_dbu))
    region.merge()
    return region



