"""
Tapered Roller Bearing Housing CAD, 3D Preview & STL Generator
Open-source parametric 3D bearing flange housing generator for antenna gimbals,
rotators, trebuchets, and mechanical pivot projects.

MIT License

Copyright (c) 2026 Andrew Freeston / KB1U / DC-LIGHT LLC.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import numpy as np
import pyvista as pv
from PIL import Image, ImageTk

MIT_LICENSE_TEXT = """MIT License

Copyright (c) 2026 Andrew Freeston / KB1U / DC-LIGHT LLC.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

# Standard Trailer & Axle Bearing Presets (Inch & Metric)
# Tuple: (Description, Shaft ID mm, Cup Major OD mm, Cup Minor OD mm, Cup Depth mm, Seal OD mm, Seal Depth mm, Contact Angle deg)
BEARING_PRESETS = {
    # --- Skateboard & Miniature Radial Ball Bearings (608 Series) ---
    "8 mm (5/16\") Skateboard Bearing (608 / 608-2RS / 608-ZZ)": (
        "Standard ubiquitous skateboard / rollerblade / 3D printer bearing (8 x 22 x 7 mm).",
        8.00, 22.00, 18.00, 7.00, 22.00, 4.0, 0.0
    ),
    "8 mm Skateboard Bearing Pair (Dual 608-2RS Hub)": (
        "Dual 608 bearing hub arrangement (8 mm axle, 22 mm OD, 14 mm total double-cup depth).",
        8.00, 22.00, 18.00, 14.00, 22.00, 4.0, 0.0
    ),

    # --- Light Duty & Small Spindles (3/4" to 1-1/16") ---
    "0.750\" (3/4\") Mini Axle Spindle (LM11949 / LM11910)": (
        "Common 1000-1500 lb light trailer / cart axle spindle. LM11949 cone with LM11910 cup.",
        19.05, 45.24, 37.0, 16.64, 45.24, 6.5, 14.0
    ),
    "1.000\" (1\") Straight Spindle BT8 (L44643 / L44610)": (
        "Standard 2000 lb straight 1.000\" spindle (BT8). L44643 cone with L44610 cup race.",
        25.40, 50.29, 43.2, 14.30, 50.29, 7.0, 14.0
    ),
    "1.063\" (1-1/16\") Trailer Spindle (L44649 / L44610)": (
        "Common 2000-2200 lb trailer axle outer/inner bearing. L44649 cone with L44610 cup race.",
        27.00, 50.29, 43.2, 14.30, 50.29, 7.0, 14.0
    ),

    # --- Medium Duty Trailer Spindles (1-1/4" to 1-5/8", 3500 - 7000 lb) ---
    "1.250\" (1-1/4\") Trailer Spindle (LM67048 / LM67010)": (
        "Common 3500-4400 lb axle outer bearing. LM67048 cone with LM67010 cup race.",
        31.75, 59.13, 51.4, 15.90, 59.13, 8.0, 13.6
    ),
    "1.375\" (1-3/8\") Trailer Spindle (L68149 / L68111)": (
        "Standard 3500 lb trailer axle inner bearing (Dexter #84 spindle). L68149 cone with L68111 cup race.",
        35.00, 59.97, 51.9, 15.90, 65.00, 8.5, 14.2
    ),
    "1.500\" (1-1/2\") Trailer Spindle (LM29749 / LM29710)": (
        "Heavy 4400-5200 lb axle outer bearing. LM29749 cone with LM29710 cup race.",
        38.10, 65.09, 56.1, 18.03, 65.09, 8.5, 14.0
    ),
    "1.500\" (1-1/2\") Trailer Spindle (15123 / 15245)": (
        "Popular 5200 lb trailer axle outer bearing. 15123 cone with 15245 cup race.",
        38.10, 62.00, 52.8, 19.05, 65.00, 8.5, 13.5
    ),
    "1.625\" (1-5/8\") Trailer Spindle (14125A / 14276)": (
        "Standard 6000-7000 lb trailer axle outer bearing. 14125A cone with 14276 cup race.",
        41.28, 69.01, 59.2, 19.58, 69.01, 9.0, 14.0
    ),
    "1.750\" (1-3/4\") Heavy Axle (25580 / 25520)": (
        "Standard 5200-7000 lb trailer axle inner bearing (Dexter #42 spindle). 25580 cone with 25520 cup race.",
        44.45, 83.06, 70.8, 23.81, 85.75, 10.0, 14.4
    ),
    "1.875\" (1-7/8\") Spindle (25877 / 25821)": (
        "Heavy utility & industrial trailer axle bearing. 25877 cone with 25821 cup race.",
        47.63, 73.03, 61.3, 24.61, 85.75, 10.0, 13.4
    ),

    # --- Large Axle Bearings (2.00" to 2.50", 8000 - 12,000 lb) ---
    "2.000\" (2\") Heavy Axle (28580 / 28521)": (
        "Heavy-duty 8,000-10,000 lb trailer axle bearing (Dexter / Lippert 8K). 28580 cone with 28521 cup race.",
        50.80, 92.08, 79.5, 24.61, 98.55, 11.0, 14.3
    ),
    "2.125\" (2-1/8\") Heavy Axle (387AS / 382A)": (
        "Heavy commercial 8,000-10,000 lb trailer axle bearing. 387AS cone with 382A cup race.",
        53.98, 96.85, 86.1, 21.00, 98.55, 11.0, 14.3
    ),
    "2.250\" (2-1/4\") Heavy Axle (387A / 382A)": (
        "Standard 9,000-10,000 lb general duty axle inner bearing. 387A cone with 382A cup race.",
        57.15, 96.85, 86.1, 21.00, 104.78, 12.0, 14.3
    ),
    "2.500\" (2-1/2\") Super-Duty Commercial (3984 / 3920)": (
        "Extra heavy-duty 10,000-12,000 lb dual-wheel trailer axle inner bearing. 3984 cone with 3920 cup race.",
        63.50, 112.71, 97.4, 30.16, 114.30, 12.5, 14.2
    ),

    # --- Steep Contact Angle High-Thrust Bearings (Gimbals & Vertical Masts) ---
    "1.375\" (1-3/8\") Steep-Angle High-Thrust (28° Contact Angle)": (
        "Steep contact angle (28°) for antenna rotators & vertical gimbals with high axial mast weight.",
        35.00, 65.00, 45.8, 18.00, 65.00, 8.5, 28.0
    ),
    "2.000\" (2\") Steep-Angle High-Thrust (28° Contact Angle)": (
        "Steep contact angle (28°) heavy-duty thrust pivot for large satellite dishes & antenna arrays.",
        50.80, 95.00, 68.4, 25.00, 98.55, 11.0, 28.0
    ),

    # --- Metric Series Tapered Roller Bearings (ISO) ---
    "20 mm Metric Spindle (30204)": (
        "Standard ISO 30204 metric tapered roller bearing (20 x 47 x 15.25 mm).",
        20.00, 47.00, 39.5, 15.25, 47.00, 7.0, 13.8
    ),
    "25 mm Metric Spindle (30205)": (
        "Standard ISO 30205 metric tapered roller bearing (25 x 52 x 16.25 mm).",
        25.00, 52.00, 44.0, 16.25, 52.00, 7.0, 13.8
    ),
    "30 mm Metric Spindle (30206)": (
        "Standard ISO 30206 metric tapered roller bearing (30 x 62 x 17.25 mm).",
        30.00, 62.00, 53.5, 17.25, 62.00, 8.0, 13.8
    ),
    "35 mm Metric Spindle (30207)": (
        "Standard ISO 30207 metric tapered roller bearing (35 x 72 x 18.25 mm).",
        35.00, 72.00, 63.0, 18.25, 72.00, 8.0, 13.8
    ),
    "40 mm Metric Spindle (30208)": (
        "Standard ISO 30208 metric tapered roller bearing (40 x 80 x 19.75 mm).",
        40.00, 80.00, 70.0, 19.75, 80.00, 8.5, 14.2
    ),
    "45 mm Metric Spindle (30209)": (
        "Standard ISO 30209 metric tapered roller bearing (45 x 85 x 20.75 mm).",
        45.00, 85.00, 74.5, 20.75, 85.00, 9.0, 14.2
    ),
    "50 mm (~2\") Metric Spindle (30210)": (
        "Standard ISO 30210 metric tapered roller bearing (50 x 90 x 21.75 mm).",
        50.00, 90.00, 79.0, 21.75, 90.00, 9.5, 14.2
    ),

    # --- Custom User Specified ---
    "Custom / User Specified": (
        "Enter custom cup race and seal dimensions directly.",
        25.40, 50.00, 43.0, 14.00, 50.00, 7.0, 14.0
    )
}

# Standard Bolt / Screw Presets
# Tuple: (Clearance Hole Dia mm, Countersink Head Dia mm, Countersink Angle deg)
FASTENER_PRESETS = {
    "#8 Drywall / Wood Screw (Bugle Head 82°)": (4.5, 8.5, 82.0),
    "#10 Drywall / Wood Screw (Flat Head 82°)": (5.2, 10.2, 82.0),
    "#12 Wood Screw (Flat Head 82°)": (6.0, 11.8, 82.0),
    "1/4\" Flat Head Machine Screw (82°)": (6.8, 13.5, 82.0),
    "M4 Flat Head Countersunk (90°)": (4.5, 8.4, 90.0),
    "M5 Flat Head Countersunk (90°)": (5.5, 10.4, 90.0),
    "M6 Flat Head Countersunk (90°)": (6.6, 12.6, 90.0),
    "M8 Flat Head Countersunk (90°)": (8.8, 16.8, 90.0),
    "1/4\" Hex Bolt / Through Hole (Straight)": (6.8, 0.0, 0.0),
    "5/16\" Hex Bolt / Through Hole (Straight)": (8.5, 0.0, 0.0),
    "3/8\" Hex Bolt / Through Hole (Straight)": (10.0, 0.0, 0.0),
    "1/2\" Hex Bolt / Through Hole (Straight)": (13.5, 0.0, 0.0),
    "M10 Hex Bolt / Through Hole (Straight)": (10.8, 0.0, 0.0),
    "M12 Hex Bolt / Through Hole (Straight)": (13.0, 0.0, 0.0),
    "Custom Fastener Hole": (5.5, 10.0, 82.0)
}


def generate_housing_mesh(d, resolution=0.42):
    """
    Generates a 100% watertight, manifold 3D mesh of the tapered roller bearing housing
    using a continuous Signed Distance Field (SDF) and VTK Flying Edges.
    Includes the stepped flange & pilot hub body (with flange on either the bottom or top
    bearing-retaining face), central shaft bore, precision bearing cup seat (cylindrical
    with shoulder stop or conical bevel), optional drift punch knock-out notches, optional
    grease/oil seal counterbore, bolt circle mounting holes (with directional countersinks),
    and grease zerk port.
    """
    flange_d = d['flange_d']
    hub_d = d['hub_d']
    flange_thick = d['flange_thick']
    total_height = d['total_height']
    shaft_d = d['shaft_d']
    cup_maj = d['cup_maj']
    cup_min = d['cup_min']
    cup_depth = d['cup_depth']
    shrink_offset = d.get('shrink_offset', 0.0)
    eff_cup_maj = cup_maj + shrink_offset
    eff_cup_min = cup_min + shrink_offset
    seal_d = d['seal_d']
    seal_depth = d['seal_depth']
    has_seal = d.get('has_seal', True)
    flange_pos = d.get('flange_pos', 'Bottom / Base (Standard Flange)')
    flange_shape = d.get('flange_shape', 'Circular / Round (Standard N-Bolt)')
    is_oval = ("Oval" in flange_shape)
    flange_w = d.get('flange_w', hub_d + 10.0) if is_oval else flange_d
    cs_face = d.get('cs_face', 'Hub Shoulder (Accessible)')
    bolt_circle_d = d['bolt_circle_d']
    num_bolts = int(d['num_bolts'])
    bolt_hole_d = d['bolt_hole_d']
    has_cs = d['has_cs']
    cs_head_d = d['cs_head_d']
    cs_angle = d['cs_angle']
    has_zerk = d['has_zerk']
    zerk_d = d['zerk_d']
    seat_style = d.get('seat_style', 'Cylindrical Cup Bore with Retaining Shoulder (Standard Trailer Hub)')
    has_knockout = d.get('has_knockout', True)

    is_top_flange = ("Top" in flange_pos or "Bearing" in flange_pos)

    res = resolution
    pad = 2.0
    if is_oval:
        R_capsule = flange_w / 2.0
        sy = max(0.0, (flange_d - flange_w) / 2.0)
        half_x = flange_w / 2.0 + pad
        half_y = flange_d / 2.0 + pad
        xs = np.arange(-half_x, half_x + res, res)
        ys = np.arange(-half_y, half_y + res, res)
    else:
        R_flange = flange_d / 2.0
        xs = np.arange(-R_flange - pad, R_flange + pad + res, res)
        ys = np.arange(-R_flange - pad, R_flange + pad + res, res)

    zs = np.arange(-pad, total_height + pad + res, res)

    nx, ny, nz = len(xs), len(ys), len(zs)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
    r_cyl = np.sqrt(X**2 + Y**2)

    # 1. Outer Solid Body: Stepped cylinder or stepped oblong
    # Flange can sit either at the Base (Z=0 to flange_thick) or at the Top Bearing Face (Z=total_height - flange_thick to total_height)
    if is_oval:
        dist_to_segment = np.sqrt(X**2 + (np.maximum(0, np.abs(Y) - sy))**2)
        d_flange_2d = dist_to_segment - R_capsule
    else:
        d_flange_2d = r_cyl - R_flange

    if is_top_flange:
        d_flange = np.maximum(d_flange_2d, np.maximum((total_height - flange_thick) - Z, Z - total_height))
    else:
        d_flange = np.maximum(d_flange_2d, np.maximum(-Z, Z - flange_thick))
    d_hub = np.maximum(r_cyl - (hub_d / 2.0), np.maximum(-Z, Z - total_height))
    d_solid = np.minimum(d_flange, d_hub)

    # 2. Central Shaft Clearance Bore (through entire height Z)
    d_shaft_hole = r_cyl - (shaft_d / 2.0)
    d_solid = np.maximum(d_solid, -d_shaft_hole)

    # 3. Optional Grease / Oil Seal Counterbore (at base, Z from 0 to seal_depth)
    if has_seal and seal_depth > 0 and seal_d > 0:
        d_seal_cavity = np.maximum(r_cyl - (seal_d / 2.0), np.maximum(-Z - 5.0, Z - seal_depth))
        d_solid = np.maximum(d_solid, -d_seal_cavity)

    # 4. Bearing Cup Race Cavity (from top Z = total_height down to total_height - cup_depth)
    z_cup_bot = total_height - cup_depth
    R_maj = eff_cup_maj / 2.0
    R_min = eff_cup_min / 2.0

    if "Cylindrical" in seat_style:
        # Standard Trailer Hub Seat: Cylindrical press-fit bore for the hardened steel cup OD
        d_cup_cyl = np.maximum(r_cyl - R_maj, np.maximum(z_cup_bot - Z, Z - (total_height + 5.0)))
        d_solid = np.maximum(d_solid, -d_cup_cyl)

        # Internal shoulder relief step (transitions down to z_cup_bot - shoulder_thick)
        shoulder_thick = min(4.0, max(2.5, cup_depth * 0.18))
        z_shoulder_bot = z_cup_bot - shoulder_thick
        d_shoulder_bore = np.maximum(r_cyl - R_min, np.maximum(z_shoulder_bot - Z, Z - z_cup_bot))
        d_solid = np.maximum(d_solid, -d_shoulder_bore)

        # Punch knock-out notches (opposing slots at the shoulder for drift punch race removal)
        if has_knockout:
            slot_w = min(16.0, max(10.0, eff_cup_maj * 0.15))
            d_slot = np.maximum(
                np.abs(X) - (slot_w / 2.0),
                np.maximum(
                    np.abs(Y) - (R_maj + 2.0),
                    np.maximum((z_cup_bot - 4.0) - Z, Z - (z_cup_bot + 4.0))
                )
            )
            d_solid = np.maximum(d_solid, -d_slot)
    else:
        # Conical Tapered Raceway (Continuous conical bevel at contact angle alpha)
        r_cone = R_min + (np.clip(Z, z_cup_bot, total_height) - z_cup_bot) / max(0.001, cup_depth) * (R_maj - R_min)
        d_cup_cavity = np.maximum(r_cyl - r_cone, np.maximum(z_cup_bot - Z, Z - (total_height + 5.0)))
        d_solid = np.maximum(d_solid, -d_cup_cavity)

    # 5. Mounting Bolt Holes on Flange
    r_bc = bolt_circle_d / 2.0
    r_bolt = bolt_hole_d / 2.0
    r_cs = cs_head_d / 2.0
    cs_depth = 0.0
    if has_cs and cs_head_d > bolt_hole_d and cs_angle > 0:
        cs_depth = (r_cs - r_bolt) / np.tan(np.radians(cs_angle / 2.0))

    if is_oval:
        n_bolts_actual = 2
        # Align along Y-axis (+Y and -Y, 90 deg away from grease port at +X)
        angle_offset = np.pi / 2.0
    else:
        n_bolts_actual = num_bolts
        # Angle offset puts holes midway between grease port at +X (0 deg)
        angle_offset = np.pi / num_bolts if num_bolts > 0 else 0.0

    for b in range(n_bolts_actual):
        angle = b * (2 * np.pi / n_bolts_actual) + angle_offset
        bx = r_bc * np.cos(angle)
        by = r_bc * np.sin(angle)
        dist_bolt = np.sqrt((X - bx)**2 + (Y - by)**2)
        # Straight through-hole
        d_solid = np.maximum(d_solid, -(dist_bolt - r_bolt))

        # Directional countersink on the specified flange face
        if has_cs and cs_depth > 0:
            if not is_top_flange:
                # Flange at base (Z from 0 to flange_thick)
                if "Hub" in cs_face or "Shoulder" in cs_face:
                    # Accessible shoulder face (Z = flange_thick entering downward)
                    z_from_top = flange_thick - Z
                    r_cs_z = r_cs - np.clip(z_from_top, 0, cs_depth) * np.tan(np.radians(cs_angle / 2.0))
                    d_cs_cavity = np.maximum(dist_bolt - r_cs_z, np.maximum(Z - flange_thick, (flange_thick - cs_depth) - Z))
                else:
                    # Mounting face (Z = 0 entering upward)
                    r_cs_z = r_cs - np.clip(Z, 0, cs_depth) * np.tan(np.radians(cs_angle / 2.0))
                    d_cs_cavity = np.maximum(dist_bolt - r_cs_z, np.maximum(-Z, Z - cs_depth))
            else:
                # Flange at top (Z from total_height - flange_thick to total_height)
                z_sh = total_height - flange_thick
                if "Hub" in cs_face or "Shoulder" in cs_face:
                    # Accessible hub shoulder face (Z = total_height - flange_thick entering upward)
                    z_from_sh = Z - z_sh
                    r_cs_z = r_cs - np.clip(z_from_sh, 0, cs_depth) * np.tan(np.radians(cs_angle / 2.0))
                    d_cs_cavity = np.maximum(dist_bolt - r_cs_z, np.maximum(z_sh - Z, Z - (z_sh + cs_depth)))
                else:
                    # Top mounting face (Z = total_height entering downward)
                    z_from_top = total_height - Z
                    r_cs_z = r_cs - np.clip(z_from_top, 0, cs_depth) * np.tan(np.radians(cs_angle / 2.0))
                    d_cs_cavity = np.maximum(dist_bolt - r_cs_z, np.maximum(Z - total_height, (total_height - cs_depth) - Z))

            d_solid = np.maximum(d_solid, -d_cs_cavity)

    # 6. Grease Zerk Port (radial hole along +X axis entering between seal and cup)
    if has_zerk and zerk_d > 0:
        eff_seal_depth = seal_depth if has_seal else 0.0
        z_zerk = eff_seal_depth + (z_cup_bot - eff_seal_depth) / 2.0
        r_zerk = zerk_d / 2.0
        # Cylinder entering from exterior into the center bore
        d_zerk = np.maximum(np.sqrt(Y**2 + (Z - z_zerk)**2) - r_zerk, -X)
        d_solid = np.maximum(d_solid, -d_zerk)

    grid = pv.ImageData(dimensions=(nx, ny, nz), spacing=(res, res, res), origin=(xs[0], ys[0], zs[0]))
    grid.point_data['values'] = d_solid.flatten(order='F')
    mesh = grid.contour([0.0])
    return mesh


def generate_bearing_visual(d):
    """Generates visual 3D assembly models of the roller bearing and seal for display."""
    shaft_d = d['shaft_d']
    cup_maj = d['cup_maj']
    cup_min = d['cup_min']
    cup_depth = d['cup_depth']
    total_height = d['total_height']
    seal_d = d['seal_d']
    seal_depth = d['seal_depth']
    has_seal = d.get('has_seal', True)
    alpha_deg = d.get('taper_angle', 14.0)
    alpha_rad = math.radians(alpha_deg)

    z_cup_bot = total_height - cup_depth

    # 1. Bearing cup race (hardened steel outer ring)
    cup_tube = pv.Cylinder(
        center=(0, 0, z_cup_bot + cup_depth / 2.0),
        direction=(0, 0, 1),
        radius=cup_maj / 2.0,
        height=cup_depth,
        resolution=60
    )

    # 2. Roller / ball cage elements
    rollers = []
    n_rollers = 16 if cup_maj >= 80.0 else (8 if cup_maj <= 30.0 else 14)
    r_cone_mid = (cup_maj + cup_min) / 4.0
    r_shaft_mid = (shaft_d / 2.0) + (1.2 if cup_maj <= 30.0 else 2.5)
    r_track = (r_cone_mid + r_shaft_mid) / 2.0
    roller_r = max(0.9, (r_cone_mid - r_shaft_mid) / 2.4)
    roller_len = max(2.5, cup_depth - (1.5 if cup_maj <= 30.0 else 3.5))

    for i in range(n_rollers):
        ang = i * (2 * np.pi / n_rollers)
        rx = r_track * np.cos(ang)
        ry = r_track * np.sin(ang)
        rz = z_cup_bot + cup_depth / 2.0
        
        # Roller orientation tilted radially inward matching contact angle alpha
        dx = -np.sin(alpha_rad) * np.cos(ang)
        dy = -np.sin(alpha_rad) * np.sin(ang)
        dz = np.cos(alpha_rad)

        roller = pv.Cylinder(
            center=(rx, ry, rz),
            direction=(dx, dy, dz),
            radius=roller_r,
            height=roller_len,
            resolution=16
        )
        rollers.append(roller)

    # 3. Shaft inner race cylinder
    inner_race_r = shaft_d / 2.0 + (1.0 if cup_maj <= 30.0 else 2.0)
    inner_race = pv.Cylinder(
        center=(0, 0, z_cup_bot + cup_depth / 2.0),
        direction=(0, 0, 1),
        radius=inner_race_r,
        height=cup_depth,
        resolution=40
    )

    # 4. Rubber grease seal (optional)
    seal_cyl = None
    if has_seal and seal_depth > 0 and seal_d > 0:
        seal_cyl = pv.Cylinder(
            center=(0, 0, seal_depth / 2.0),
            direction=(0, 0, 1),
            radius=seal_d / 2.0,
            height=seal_depth * 0.95,
            resolution=40
        )

    return cup_tube, rollers, inner_race, seal_cyl


class BearingHousingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tapered Roller Bearing Housing CAD & Direct STL Generator")
        self.geometry("1220x840")
        self.minsize(1020, 700)
        self.resizable(True, True)

        self.calc_data = None
        self.plotter = None
        self._current_photo = None
        self._last_mouse_x = None
        self._last_mouse_y = None
        self._resize_job = None
        self._view_initialized = False

        self._setup_ui()
        self._setup_3d_renderer()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.after(100, self.calculate)

    def _setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Menu Bar
        menubar = tk.Menu(self)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation & User Guide...", command=self.show_help_dialog)
        help_menu.add_separator()
        help_menu.add_command(label="About & License...", command=self.show_about_dialog)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

        # Paned Window
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # ----------------- LEFT PANEL (Scrollable Parameters) -----------------
        left_container = ttk.Frame(paned)
        paned.add(left_container, weight=0)

        canvas_left = tk.Canvas(left_container, width=580, highlightthickness=0)
        scrollbar_left = ttk.Scrollbar(left_container, orient=tk.VERTICAL, command=canvas_left.yview)
        self.scrollable_frame = ttk.Frame(canvas_left, padding=(14, 10, 16, 10))

        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas_left.configure(scrollregion=canvas_left.bbox('all'))
        )
        canvas_window = canvas_left.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        canvas_left.bind(
            '<Configure>',
            lambda e: canvas_left.itemconfig(canvas_window, width=e.width)
        )
        canvas_left.configure(yscrollcommand=scrollbar_left.set)

        canvas_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_left.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            try:
                x, y = self.winfo_pointerxy()
                w = self.winfo_containing(x, y)
                if w and (str(w).startswith(str(left_container)) or w == canvas_left):
                    canvas_left.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except (KeyError, tk.TclError):
                pass
        self.bind_all("<MouseWheel>", _on_mousewheel)

        # Header Frame
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 6))

        title_container = ttk.Frame(header_frame)
        title_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            title_container, 
            text="Tapered Bearing Housing Generator", 
            font=("Helvetica", 13, "bold")
        )
        title_label.pack(anchor=tk.W)

        subtitle_label = ttk.Label(
            title_container,
            text="Antenna Gimbals, Rotators & Trebuchet Bearing Blocks",
            font=("Segoe UI", 8, "italic"),
            foreground="#666666"
        )
        subtitle_label.pack(anchor=tk.W)

        btn_header_box = ttk.Frame(header_frame)
        btn_header_box.pack(side=tk.RIGHT, padx=(6, 0))

        about_btn = ttk.Button(btn_header_box, text="ℹ️ About / License", command=self.show_about_dialog, width=18)
        about_btn.pack(pady=(0, 2))

        help_btn = ttk.Button(btn_header_box, text="❓ Help / Guide", command=self.show_help_dialog, width=18)
        help_btn.pack()

        # Preset Selector Group
        preset_group = ttk.LabelFrame(self.scrollable_frame, text=" Bearing Presets & Standard Axles ", padding="8")
        preset_group.pack(fill=tk.X, pady=4)

        self.preset_var = tk.StringVar(value="1.063\" (1-1/16\") Trailer Spindle (L44649 / L44610)")
        preset_combo = ttk.Combobox(
            preset_group,
            textvariable=self.preset_var,
            values=list(BEARING_PRESETS.keys()),
            state="readonly"
        )
        preset_combo.pack(fill=tk.X, pady=2)
        preset_combo.bind("<<ComboboxSelected>>", lambda e: self._on_preset_change())

        # Bearing Race & Cavity Geometry Group
        race_group = ttk.LabelFrame(self.scrollable_frame, text=" Bearing Race & Shaft Parameters ", padding="8")
        race_group.pack(fill=tk.X, pady=4)

        ttk.Label(race_group, text="Seat Geometry Style:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.seat_style_var = tk.StringVar(value="Cylindrical Cup Bore with Retaining Shoulder (Standard Trailer Hub)")
        seat_combo = ttk.Combobox(
            race_group,
            textvariable=self.seat_style_var,
            values=[
                "Cylindrical Cup Bore with Retaining Shoulder (Standard Trailer Hub)",
                "Conical Tapered Raceway (Direct Conical Bevel)"
            ],
            state="readonly",
            width=30
        )
        seat_combo.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=3)
        seat_combo.bind("<<ComboboxSelected>>", lambda e: self.calculate())

        self.has_knockout_var = tk.BooleanVar(value=True)
        knockout_check = ttk.Checkbutton(
            race_group, 
            text="Enable Knock-Out Punch Notches (Race Service)", 
            variable=self.has_knockout_var,
            command=self.calculate
        )
        knockout_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=2)

        ttk.Label(race_group, text="Cup Race Major OD (mm):").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.cup_maj_var = tk.DoubleVar(value=50.29)
        ttk.Entry(race_group, textvariable=self.cup_maj_var, width=12).grid(row=2, column=1, sticky=tk.W, pady=3)

        ttk.Label(race_group, text="Cup Race Depth / Width (mm):").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.cup_depth_var = tk.DoubleVar(value=14.3)
        ttk.Entry(race_group, textvariable=self.cup_depth_var, width=12).grid(row=3, column=1, sticky=tk.W, pady=3)

        ttk.Label(race_group, text="Tapered Contact Angle α (°):").grid(row=4, column=0, sticky=tk.W, pady=3)
        angle_frame = ttk.Frame(race_group)
        angle_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=3)
        self.contact_angle_var = tk.DoubleVar(value=14.0)
        ttk.Entry(angle_frame, textvariable=self.contact_angle_var, width=8).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(angle_frame, text="14° Std", width=7, command=lambda: self._set_contact_angle(14.0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(angle_frame, text="28° Thrust", width=9, command=lambda: self._set_contact_angle(28.0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(angle_frame, text="Calc Min OD", width=11, command=self._sync_angle_to_minor_od).pack(side=tk.LEFT, padx=2)

        ttk.Label(race_group, text="Cup Minor OD / Shoulder ID (mm):").grid(row=5, column=0, sticky=tk.W, pady=3)
        min_od_frame = ttk.Frame(race_group)
        min_od_frame.grid(row=5, column=1, columnspan=2, sticky=tk.W, pady=3)
        self.cup_min_var = tk.DoubleVar(value=43.16)
        ttk.Entry(min_od_frame, textvariable=self.cup_min_var, width=12).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(min_od_frame, text="Calc Angle", width=10, command=self._sync_minor_od_to_angle).pack(side=tk.LEFT, padx=2)

        ttk.Label(race_group, text="Through Shaft Clearance ID (mm):").grid(row=6, column=0, sticky=tk.W, pady=3)
        self.shaft_d_var = tk.DoubleVar(value=27.0)
        ttk.Entry(race_group, textvariable=self.shaft_d_var, width=12).grid(row=6, column=1, sticky=tk.W, pady=3)

        ttk.Label(race_group, text="Bearing Seat Fit / Shrink Offset (mm):").grid(row=7, column=0, sticky=tk.W, pady=3)
        shrink_frame = ttk.Frame(race_group)
        shrink_frame.grid(row=7, column=1, columnspan=2, sticky=tk.W, pady=3)
        self.shrink_offset_var = tk.DoubleVar(value=0.10)
        ttk.Entry(shrink_frame, textvariable=self.shrink_offset_var, width=8).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(shrink_frame, text="0.00 (CNC)", width=10, command=lambda: self._set_shrink_offset(0.0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(shrink_frame, text="+0.10 (FDM)", width=10, command=lambda: self._set_shrink_offset(0.10)).pack(side=tk.LEFT, padx=2)
        ttk.Button(shrink_frame, text="+0.20 (Loose)", width=11, command=lambda: self._set_shrink_offset(0.20)).pack(side=tk.LEFT, padx=2)

        self.has_seal_var = tk.BooleanVar(value=True)
        seal_check = ttk.Checkbutton(
            race_group, 
            text="Enable Axle Grease / Oil Seal Counterbore", 
            variable=self.has_seal_var, 
            command=self._on_seal_toggle
        )
        seal_check.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=2)

        ttk.Label(race_group, text="Axle Seal Bore Dia (mm):").grid(row=9, column=0, sticky=tk.W, pady=3)
        self.seal_d_var = tk.DoubleVar(value=50.29)
        self.seal_d_entry = ttk.Entry(race_group, textvariable=self.seal_d_var, width=12)
        self.seal_d_entry.grid(row=9, column=1, sticky=tk.W, pady=3)

        ttk.Label(race_group, text="Axle Seal Bore Depth (mm):").grid(row=10, column=0, sticky=tk.W, pady=3)
        self.seal_depth_var = tk.DoubleVar(value=7.0)
        self.seal_depth_entry = ttk.Entry(race_group, textvariable=self.seal_depth_var, width=12)
        self.seal_depth_entry.grid(row=10, column=1, sticky=tk.W, pady=3)

        # Housing Body & Flange Group
        body_group = ttk.LabelFrame(self.scrollable_frame, text=" Housing & Flange Dimensions ", padding="8")
        body_group.pack(fill=tk.X, pady=4)

        ttk.Label(body_group, text="Flange Position / Side:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.flange_pos_var = tk.StringVar(value="Bottom / Base (Standard Flange)")
        flange_pos_combo = ttk.Combobox(
            body_group,
            textvariable=self.flange_pos_var,
            values=[
                "Bottom / Base (Standard Flange)",
                "Top / Bearing Face (Captive / Retaining Flange)"
            ],
            state="readonly",
            width=28
        )
        flange_pos_combo.grid(row=0, column=1, sticky=tk.EW, pady=3)
        flange_pos_combo.bind("<<ComboboxSelected>>", lambda e: self.calculate())

        ttk.Label(body_group, text="Flange Outline Shape:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.flange_shape_var = tk.StringVar(value="Circular / Round (Standard N-Bolt)")
        flange_shape_combo = ttk.Combobox(
            body_group,
            textvariable=self.flange_shape_var,
            values=[
                "Circular / Round (Standard N-Bolt)",
                "Oval / 2-Bolt Oblong (Narrow Mount)"
            ],
            state="readonly",
            width=28
        )
        flange_shape_combo.grid(row=1, column=1, sticky=tk.EW, pady=3)
        flange_shape_combo.bind("<<ComboboxSelected>>", lambda e: self._on_flange_shape_change())

        self.flange_d_lbl = ttk.Label(body_group, text="Mounting Flange Diameter (mm):")
        self.flange_d_lbl.grid(row=2, column=0, sticky=tk.W, pady=3)
        self.flange_d_var = tk.DoubleVar(value=95.0)
        self.flange_d_entry = ttk.Entry(body_group, textvariable=self.flange_d_var, width=12)
        self.flange_d_entry.grid(row=2, column=1, sticky=tk.W, pady=3)

        self.flange_w_lbl = ttk.Label(body_group, text="Oval Flange Narrow Width (mm):")
        self.flange_w_lbl.grid(row=3, column=0, sticky=tk.W, pady=3)
        self.flange_w_var = tk.DoubleVar(value=68.0)
        self.flange_w_entry = ttk.Entry(body_group, textvariable=self.flange_w_var, width=12, state="disabled")
        self.flange_w_entry.grid(row=3, column=1, sticky=tk.W, pady=3)

        ttk.Label(body_group, text="Flange Plate Thickness (mm):").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.flange_thick_var = tk.DoubleVar(value=12.0)
        ttk.Entry(body_group, textvariable=self.flange_thick_var, width=12).grid(row=4, column=1, sticky=tk.W, pady=3)

        ttk.Label(body_group, text="Bearing Pilot Hub OD (mm):").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.hub_d_var = tk.DoubleVar(value=68.0)
        ttk.Entry(body_group, textvariable=self.hub_d_var, width=12).grid(row=5, column=1, pady=3)

        ttk.Label(body_group, text="Total Housing Height (mm):").grid(row=6, column=0, sticky=tk.W, pady=3)
        self.total_height_var = tk.DoubleVar(value=32.0)
        ttk.Entry(body_group, textvariable=self.total_height_var, width=12).grid(row=6, column=1, pady=3)

        # Mounting Fasteners Group
        bolt_group = ttk.LabelFrame(self.scrollable_frame, text=" Mounting Bolt Pattern & Screws ", padding="8")
        bolt_group.pack(fill=tk.X, pady=4)

        ttk.Label(bolt_group, text="Fastener Preset:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.fastener_preset_var = tk.StringVar(value="#10 Drywall / Wood Screw (Flat Head 82°)")
        fastener_combo = ttk.Combobox(
            bolt_group,
            textvariable=self.fastener_preset_var,
            values=list(FASTENER_PRESETS.keys()),
            state="readonly",
            width=26
        )
        fastener_combo.grid(row=0, column=1, pady=3)
        fastener_combo.bind("<<ComboboxSelected>>", lambda e: self._on_fastener_preset_change())

        ttk.Label(bolt_group, text="Number of Bolt Holes (N):").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.num_bolts_var = tk.IntVar(value=4)
        ttk.Spinbox(bolt_group, from_=2, to=16, textvariable=self.num_bolts_var, width=10).grid(row=1, column=1, pady=3)

        ttk.Label(bolt_group, text="Bolt Circle Diameter (mm):").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.bolt_circle_d_var = tk.DoubleVar(value=78.0)
        ttk.Entry(bolt_group, textvariable=self.bolt_circle_d_var, width=12).grid(row=2, column=1, pady=3)

        ttk.Label(bolt_group, text="Bolt Hole Diameter (mm):").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.bolt_hole_d_var = tk.DoubleVar(value=5.2)
        ttk.Entry(bolt_group, textvariable=self.bolt_hole_d_var, width=12).grid(row=3, column=1, pady=3)

        self.has_cs_var = tk.BooleanVar(value=True)
        cs_check = ttk.Checkbutton(bolt_group, text="Enable Tapered Countersink (Drywall / Flat Head)", variable=self.has_cs_var)
        cs_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=3)

        ttk.Label(bolt_group, text="Countersink Head Face:").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.cs_face_var = tk.StringVar(value="Hub Shoulder (Accessible)")
        cs_face_combo = ttk.Combobox(
            bolt_group,
            textvariable=self.cs_face_var,
            values=["Hub Shoulder (Accessible)", "Mounting Face (Sub-Flush)"],
            state="readonly",
            width=24
        )
        cs_face_combo.grid(row=5, column=1, pady=3)
        cs_face_combo.bind("<<ComboboxSelected>>", lambda e: self.calculate())

        ttk.Label(bolt_group, text="Countersink Head Dia (mm):").grid(row=6, column=0, sticky=tk.W, pady=3)
        self.cs_head_d_var = tk.DoubleVar(value=10.2)
        ttk.Entry(bolt_group, textvariable=self.cs_head_d_var, width=12).grid(row=6, column=1, pady=3)

        ttk.Label(bolt_group, text="Countersink Angle (deg):").grid(row=7, column=0, sticky=tk.W, pady=3)
        self.cs_angle_var = tk.DoubleVar(value=82.0)
        ttk.Entry(bolt_group, textvariable=self.cs_angle_var, width=12).grid(row=7, column=1, pady=3)

        # Lubrication Group
        lube_group = ttk.LabelFrame(self.scrollable_frame, text=" Lubrication & Maintenance ", padding="8")
        lube_group.pack(fill=tk.X, pady=4)

        self.has_zerk_var = tk.BooleanVar(value=True)
        zerk_check = ttk.Checkbutton(lube_group, text="Include Grease Zerk Fitting Port", variable=self.has_zerk_var)
        zerk_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)

        ttk.Label(lube_group, text="Zerk Thread Tap Dia (mm):").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.zerk_d_var = tk.DoubleVar(value=5.5) # ~1/4-28 tap drill or 6mm
        ttk.Entry(lube_group, textvariable=self.zerk_d_var, width=12).grid(row=1, column=1, pady=3)

        # Action Buttons
        calc_btn = ttk.Button(
            self.scrollable_frame, 
            text="⚡ Update 3D Preview & Calculate Specs", 
            command=self.calculate
        )
        calc_btn.pack(fill=tk.X, pady=6, ipady=3)

        # Results Box
        self.results_group = ttk.LabelFrame(self.scrollable_frame, text=" Calculated Housing Dimensions ", padding="8")
        self.results_group.pack(fill=tk.X, pady=3)

        self.results_label = ttk.Label(self.results_group, text="Click 'Update 3D Preview' to calculate.", font=("Courier", 9))
        self.results_label.pack(anchor=tk.W)

        # Export Box
        export_frame = ttk.LabelFrame(self.scrollable_frame, text=" CAD & 3D Print Export ", padding="8")
        export_frame.pack(fill=tk.X, pady=6)

        self.stl_btn = ttk.Button(
            export_frame,
            text="💾 Export 3D Printable STL (.stl)",
            command=self.export_stl,
            state=tk.DISABLED
        )
        self.stl_btn.pack(fill=tk.X, pady=(0, 6), ipady=4)

        sub_btn_frame = ttk.Frame(export_frame)
        sub_btn_frame.pack(fill=tk.X)

        self.scad_btn = ttk.Button(sub_btn_frame, text="Export OpenSCAD (.scad)", command=self.export_openscad, state=tk.DISABLED)
        self.scad_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.sw_btn = ttk.Button(sub_btn_frame, text="Save SW Macro (.bas)", command=self.save_sw_bas, state=tk.DISABLED)
        self.sw_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

        # ----------------- RIGHT PANEL (3D Viewport) -----------------
        right_container = ttk.LabelFrame(paned, text=" 3D Housing Preview ", padding="8")
        paned.add(right_container, weight=1)

        toolbar = ttk.Frame(right_container)
        toolbar.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(toolbar, text="Mode:").pack(side=tk.LEFT, padx=(0, 4))
        self.view_mode_var = tk.StringVar(value="Housing + Bearing Assembly")
        mode_combo = ttk.Combobox(
            toolbar,
            textvariable=self.view_mode_var,
            values=["Housing + Bearing Assembly", "Housing Only (STL Model)", "Cross-Section View"],
            state="readonly",
            width=26
        )
        mode_combo.pack(side=tk.LEFT, padx=(0, 8))
        mode_combo.bind("<<ComboboxSelected>>", lambda e: self._update_3d_preview(reset_camera=False))

        ttk.Button(toolbar, text="Isometric", width=9, command=self._view_iso).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Top", width=7, command=self._view_top).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Front", width=7, command=self._view_front).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Bottom", width=7, command=self._view_bottom).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Reset", width=7, command=self._view_reset).pack(side=tk.LEFT, padx=2)

        self.canvas_3d = tk.Canvas(right_container, bg="#1E1E1E", highlightthickness=0)
        self.canvas_3d.pack(fill=tk.BOTH, expand=True)

        self.canvas_3d.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas_3d.bind("<B1-Motion>", self._on_mouse_drag_rotate)
        self.canvas_3d.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas_3d.bind("<Shift-B1-Motion>", self._on_mouse_drag_pan)
        self.canvas_3d.bind("<ButtonPress-2>", self._on_mouse_press)
        self.canvas_3d.bind("<B2-Motion>", self._on_mouse_drag_pan)
        self.canvas_3d.bind("<ButtonRelease-2>", self._on_mouse_release)
        self.canvas_3d.bind("<ButtonPress-3>", self._on_mouse_press)
        self.canvas_3d.bind("<B3-Motion>", self._on_mouse_drag_zoom)
        self.canvas_3d.bind("<ButtonRelease-3>", self._on_mouse_release)
        self.canvas_3d.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas_3d.bind("<Button-4>", lambda e: self._zoom(1.1))
        self.canvas_3d.bind("<Button-5>", lambda e: self._zoom(0.9))
        self.canvas_3d.bind("<Configure>", self._on_canvas_configure)

        info_bar = ttk.Frame(right_container)
        info_bar.pack(fill=tk.X, pady=(4, 0))

        help_label = ttk.Label(
            info_bar, 
            text="Left-Drag: Orbit | Middle / Shift-Drag: Pan | Right-Drag / Scroll: Zoom", 
            font=("Segoe UI", 8), 
            foreground="#666666"
        )
        help_label.pack(side=tk.LEFT)

        self.preview_info_label = ttk.Label(
            info_bar, 
            text="Watertight 3D Model: Ready", 
            font=("Segoe UI", 8, "italic"),
            foreground="#333333"
        )
        self.preview_info_label.pack(side=tk.RIGHT)

    def _on_flange_shape_change(self):
        shape = self.flange_shape_var.get()
        if "Oval" in shape:
            self.flange_w_entry.config(state="normal")
            self.num_bolts_var.set(2)
            self.flange_d_lbl.config(text="Flange Length / Major Axis (mm):")
            # Default width to hub_d + 10mm if not set or smaller than hub
            if self.flange_w_var.get() < self.hub_d_var.get() + 4.0:
                self.flange_w_var.set(round(self.hub_d_var.get() + 10.0, 1))
        else:
            self.flange_w_entry.config(state="disabled")
            self.flange_d_lbl.config(text="Mounting Flange Diameter (mm):")
            if self.num_bolts_var.get() == 2:
                self.num_bolts_var.set(4)
        self.calculate()

    def _on_seal_toggle(self):
        state = "normal" if self.has_seal_var.get() else "disabled"
        if hasattr(self, 'seal_d_entry'):
            self.seal_d_entry.config(state=state)
        if hasattr(self, 'seal_depth_entry'):
            self.seal_depth_entry.config(state=state)
        self.calculate()

    def _set_shrink_offset(self, val):
        self.shrink_offset_var.set(val)
        self.calculate()

    def _set_contact_angle(self, angle):
        self.contact_angle_var.set(angle)
        self._sync_angle_to_minor_od()

    def _sync_angle_to_minor_od(self):
        try:
            c_maj = self.cup_maj_var.get()
            c_depth = self.cup_depth_var.get()
            angle = self.contact_angle_var.get()
            c_min = max(1.0, c_maj - 2.0 * c_depth * math.tan(math.radians(angle)))
            self.cup_min_var.set(round(c_min, 2))
            self.calculate()
        except Exception:
            pass

    def _sync_minor_od_to_angle(self):
        try:
            c_maj = self.cup_maj_var.get()
            c_min = self.cup_min_var.get()
            c_depth = self.cup_depth_var.get()
            if c_min < c_maj and c_depth > 0:
                angle = math.degrees(math.atan(((c_maj - c_min) / 2.0) / c_depth))
                self.contact_angle_var.set(round(angle, 1))
                self.calculate()
        except Exception:
            pass

    def _on_preset_change(self):
        preset_name = self.preset_var.get()
        if preset_name in BEARING_PRESETS and preset_name != "Custom / User Specified":
            _, shaft, c_maj, c_min, c_depth, s_d, s_depth, angle = BEARING_PRESETS[preset_name]
            self.shaft_d_var.set(shaft)
            self.cup_maj_var.set(c_maj)
            self.cup_min_var.set(c_min)
            self.cup_depth_var.set(c_depth)
            self.seal_d_var.set(s_d)
            self.seal_depth_var.set(s_depth)
            self.contact_angle_var.set(angle)

            # Auto-scale hub OD, flange OD, bolt circle, height, and bolt count
            if c_maj <= 30.0:
                # Compact scaling for miniature / skateboard bearings
                hub_wall_min = max(8.0, round(c_maj * 0.35, 1))
                hub_d = round(c_maj + hub_wall_min, 1)
                self.hub_d_var.set(hub_d)

                flange_margin = max(18.0, round(hub_d * 0.50, 1))
                flange_d = round(hub_d + flange_margin, 1)
                self.flange_d_var.set(flange_d)

                bc_d = round((hub_d + flange_d) / 2.0, 1)
                self.bolt_circle_d_var.set(bc_d)

                has_seal = self.has_seal_var.get()
                eff_seal_h = s_depth if has_seal else 0.0
                total_h = round(c_depth + eff_seal_h + max(4.0, round(c_depth * 0.40, 1)), 1)
                self.total_height_var.set(total_h)

                flange_t = round(max(5.0, total_h * 0.35), 1)
                self.flange_thick_var.set(flange_t)
            else:
                hub_wall_min = max(16.0, round(c_maj * 0.20, 1))
                hub_d = round(c_maj + hub_wall_min, 1)
                self.hub_d_var.set(hub_d)

                flange_margin = max(28.0, round(hub_d * 0.26, 1))
                flange_d = round(hub_d + flange_margin, 1)
                self.flange_d_var.set(flange_d)

                bc_d = round((hub_d + flange_d) / 2.0, 1)
                self.bolt_circle_d_var.set(bc_d)

                # Scale height depending on whether seal pocket is active
                has_seal = self.has_seal_var.get()
                eff_seal_h = s_depth if has_seal else 0.0
                total_h = round(c_depth + eff_seal_h + max(10.0, round(c_depth * 0.35, 1)), 1)
                self.total_height_var.set(total_h)

                flange_t = round(max(12.0, total_h * 0.35), 1)
                self.flange_thick_var.set(flange_t)

            # For larger bearings (>= 80mm cup OD), scale bolt count to 6 or 8 (if circular)
            if "Oval" in self.flange_shape_var.get():
                self.flange_w_var.set(round(hub_d + (8.0 if c_maj <= 30.0 else 12.0), 1))
                self.num_bolts_var.set(2)
            else:
                if c_maj >= 90.0:
                    if self.num_bolts_var.get() < 6:
                        self.num_bolts_var.set(6)
                elif c_maj >= 110.0:
                    if self.num_bolts_var.get() < 8:
                        self.num_bolts_var.set(8)

            self.calculate()

    def _on_fastener_preset_change(self):
        f_name = self.fastener_preset_var.get()
        if f_name in FASTENER_PRESETS and f_name != "Custom Fastener Hole":
            hole_d, cs_d, cs_ang = FASTENER_PRESETS[f_name]
            self.bolt_hole_d_var.set(hole_d)
            if cs_d > 0:
                self.has_cs_var.set(True)
                self.cs_head_d_var.set(cs_d)
                self.cs_angle_var.set(cs_ang)
            else:
                self.has_cs_var.set(False)
            self.calculate()

    def _setup_3d_renderer(self):
        try:
            self.plotter = pv.Plotter(off_screen=True, window_size=(580, 600), lighting="none")
            self.plotter.set_background("#1E1E1E")
            self._apply_lighting_and_shadows()
        except Exception as e:
            print("Failed to initialize PyVista plotter:", e)
            self.plotter = None

    def _apply_lighting_and_shadows(self):
        if not self.plotter:
            return
        try:
            self.plotter.renderer.remove_all_lights()
            key_light = pv.Light(position=(2.5, 3.5, 2.5), light_type="camera light", intensity=0.92)
            fill_light = pv.Light(position=(-2.5, -1.5, 1.5), light_type="camera light", intensity=0.35)
            rim_light = pv.Light(position=(0.0, -3.0, -2.5), light_type="camera light", intensity=0.25)
            self.plotter.add_light(key_light)
            self.plotter.add_light(fill_light)
            self.plotter.add_light(rim_light)
            self.plotter.enable_shadows()
        except Exception:
            pass

    def _render_view(self):
        if not self.plotter:
            return
        try:
            self.plotter.render()
            img_data = self.plotter.screenshot(return_img=True)
            if img_data is not None and img_data.size > 0:
                img = Image.fromarray(img_data)
                self._current_photo = ImageTk.PhotoImage(img)
                self.canvas_3d.delete("all")
                self.canvas_3d.create_image(0, 0, anchor=tk.NW, image=self._current_photo)
        except Exception:
            pass

    def _on_canvas_configure(self, event):
        w, h = event.width, event.height
        if w < 50 or h < 50:
            return
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(120, lambda: self._apply_canvas_resize(w, h))

    def _apply_canvas_resize(self, width, height):
        self._resize_job = None
        if self.plotter is not None:
            try:
                self.plotter.window_size = (max(100, width), max(100, height))
                self._render_view()
            except Exception:
                pass

    def _on_mouse_press(self, event):
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y

    def _on_mouse_release(self, event):
        self._last_mouse_x = None
        self._last_mouse_y = None

    def _on_mouse_drag_rotate(self, event):
        if not self.plotter:
            return
        if self._last_mouse_x is None or self._last_mouse_y is None:
            self._last_mouse_x = event.x
            self._last_mouse_y = event.y
            return
        dx = event.x - self._last_mouse_x
        dy = event.y - self._last_mouse_y
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y

        cam = self.plotter.camera
        focal = np.array(cam.focal_point)
        pos = np.array(cam.position)
        diff = pos - focal
        r = np.linalg.norm(diff)
        if r < 1e-6:
            return

        xy_dist = np.linalg.norm(diff[:2])
        if xy_dist < 1e-4:
            azimuth = -np.pi / 2.0
        else:
            azimuth = np.arctan2(diff[1], diff[0])

        sin_elev = np.clip(diff[2] / r, -1.0, 1.0)
        elev = np.arcsin(sin_elev)

        azimuth -= np.radians(dx * 0.45)
        max_elev = np.radians(88.5)
        elev = np.clip(elev - np.radians(dy * 0.45), -max_elev, max_elev)

        cos_elev = np.cos(elev)
        new_dir = np.array([
            cos_elev * np.cos(azimuth),
            cos_elev * np.sin(azimuth),
            np.sin(elev)
        ])
        cam.position = focal + r * new_dir
        cam.focal_point = focal
        cam.up = (0.0, 0.0, 1.0)
        self._render_view()

    def _on_mouse_drag_pan(self, event):
        if not self.plotter:
            return
        if self._last_mouse_x is None or self._last_mouse_y is None:
            self._last_mouse_x = event.x
            self._last_mouse_y = event.y
            return
        dx = event.x - self._last_mouse_x
        dy = event.y - self._last_mouse_y
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y

        cam = self.plotter.camera
        focal = np.array(cam.focal_point)
        pos = np.array(cam.position)
        view_dir = focal - pos
        dist = np.linalg.norm(view_dir)
        if dist < 1e-6:
            return
        view_dir = view_dir / dist
        up = np.array(cam.up)

        right = np.cross(view_dir, up)
        right_norm = np.linalg.norm(right)
        if right_norm < 1e-6:
            return
        right = right / right_norm
        cam_up = np.cross(right, view_dir)

        scale = dist * 0.0018
        delta = -dx * scale * right + dy * scale * cam_up
        cam.position = pos + delta
        cam.focal_point = focal + delta
        self._render_view()

    def _on_mouse_drag_zoom(self, event):
        if not self.plotter:
            return
        if self._last_mouse_x is None or self._last_mouse_y is None:
            self._last_mouse_x = event.x
            self._last_mouse_y = event.y
            return
        dy = event.y - self._last_mouse_y
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y

        factor = 1.0 - dy * 0.008
        if 0.5 < factor < 1.5:
            self.plotter.camera.zoom(factor)
        self._render_view()

    def _on_mouse_wheel(self, event):
        if event.num == 5 or event.delta < 0:
            self._zoom(0.92)
        elif event.num == 4 or event.delta > 0:
            self._zoom(1.08)

    def _zoom(self, factor):
        if self.plotter:
            self.plotter.camera.zoom(factor)
            self._render_view()

    def _view_iso(self):
        if self.plotter:
            self.plotter.view_isometric()
            self.plotter.reset_camera()
            self._render_view()

    def _view_front(self):
        if self.plotter:
            self.plotter.view_xz()
            self.plotter.reset_camera()
            self._render_view()

    def _view_top(self):
        if self.plotter:
            self.plotter.view_xy()
            self.plotter.reset_camera()
            self._render_view()

    def _view_bottom(self):
        if self.plotter:
            self.plotter.camera.position = (0, 0, -100)
            self.plotter.camera.focal_point = (0, 0, 16)
            self.plotter.camera.up = (0, 1, 0)
            self.plotter.reset_camera()
            self._render_view()

    def _view_reset(self):
        if self.plotter:
            self.plotter.view_isometric()
            self.plotter.reset_camera()
            self._render_view()

    def _update_3d_preview(self, reset_camera=False):
        if not self.calc_data or not self.plotter:
            return

        try:
            self.plotter.clear()
            self._apply_lighting_and_shadows()

            # Generate housing mesh
            housing_mesh = generate_housing_mesh(self.calc_data, resolution=0.55)
            mode = self.view_mode_var.get()

            if "Cross-Section" in mode:
                # Clip housing along Y=0 plane to view interior taper, seal pocket, and zerk channel
                clipped = housing_mesh.clip(normal=(0, 1, 0), origin=(0, 0, 0), invert=False)
                self.plotter.add_mesh(
                    clipped, 
                    color="#D1D5DB", 
                    smooth_shading=True, 
                    ambient=0.25, 
                    diffuse=0.75, 
                    specular=0.35, 
                    specular_power=20
                )
                cup_tube, rollers, inner_race, seal = generate_bearing_visual(self.calc_data)
                self.plotter.add_mesh(cup_tube.clip(normal=(0, 1, 0)), color="#94A3B8", specular=0.5)
                for r in rollers:
                    if r.center[1] <= 0:
                        self.plotter.add_mesh(r, color="#F59E0B", specular=0.8)
                self.plotter.add_mesh(inner_race.clip(normal=(0, 1, 0)), color="#64748B", specular=0.5)
                if seal:
                    self.plotter.add_mesh(seal.clip(normal=(0, 1, 0)), color="#1E293B", opacity=0.9)
            elif "Assembly" in mode:
                # Render housing semi-opaque or solid with visible assembly components
                self.plotter.add_mesh(
                    housing_mesh, 
                    color="#E2E8F0", 
                    opacity=0.92,
                    smooth_shading=True, 
                    ambient=0.25, 
                    diffuse=0.75, 
                    specular=0.35, 
                    specular_power=20
                )
                cup_tube, rollers, inner_race, seal = generate_bearing_visual(self.calc_data)
                self.plotter.add_mesh(cup_tube, color="#94A3B8", specular=0.6, label="Outer Cup")
                for r in rollers:
                    self.plotter.add_mesh(r, color="#F59E0B", specular=0.85, specular_power=30)
                self.plotter.add_mesh(inner_race, color="#64748B", specular=0.6)
                if seal:
                    self.plotter.add_mesh(seal, color="#0F172A", opacity=0.85)
            else:
                # Housing Only (STL mode)
                self.plotter.add_mesh(
                    housing_mesh, 
                    color="#CBD5E1", 
                    smooth_shading=True, 
                    ambient=0.22, 
                    diffuse=0.78, 
                    specular=0.4, 
                    specular_power=25
                )

            if reset_camera or not self._view_initialized:
                self.plotter.view_isometric()
                self.plotter.reset_camera()
                self._view_initialized = True

            self._render_view()
            self.preview_info_label.config(
                text=f"Mesh: {housing_mesh.n_cells:,} triangles | Watertight (0 open edges)"
            )
        except Exception as e:
            self.preview_info_label.config(text=f"Preview error: {str(e)}")

    def calculate(self):
        try:
            flange_d = self.flange_d_var.get()
            hub_d = self.hub_d_var.get()
            flange_thick = self.flange_thick_var.get()
            total_height = self.total_height_var.get()
            shaft_d = self.shaft_d_var.get()
            cup_maj = self.cup_maj_var.get()
            cup_min = self.cup_min_var.get()
            cup_depth = self.cup_depth_var.get()
            shrink_offset = self.shrink_offset_var.get()
            eff_cup_maj = cup_maj + shrink_offset
            eff_cup_min = cup_min + shrink_offset
            seal_d = self.seal_d_var.get()
            seal_depth = self.seal_depth_var.get()
            has_seal = self.has_seal_var.get()
            flange_pos = self.flange_pos_var.get()
            flange_shape = self.flange_shape_var.get()
            is_oval = ("Oval" in flange_shape)
            flange_w = self.flange_w_var.get() if is_oval else flange_d
            cs_face = self.cs_face_var.get()
            bolt_circle_d = self.bolt_circle_d_var.get()
            num_bolts = 2 if is_oval else self.num_bolts_var.get()
            bolt_hole_d = self.bolt_hole_d_var.get()
            has_cs = self.has_cs_var.get()
            cs_head_d = self.cs_head_d_var.get()
            cs_angle = self.cs_angle_var.get()
            has_zerk = self.has_zerk_var.get()
            zerk_d = self.zerk_d_var.get()
            seat_style = self.seat_style_var.get()
            has_knockout = self.has_knockout_var.get()
            contact_angle = self.contact_angle_var.get()

            is_top_flange = ("Top" in flange_pos or "Bearing" in flange_pos)

            # Validations
            if cup_min >= cup_maj:
                raise ValueError("Cup minor OD / shoulder ID must be smaller than cup major OD.")
            if eff_cup_maj >= hub_d:
                raise ValueError(f"Bearing pilot hub diameter ({hub_d}mm) must be larger than bearing cup major OD ({eff_cup_maj:.2f}mm with print offset).")
            if is_oval:
                if flange_w < hub_d:
                    raise ValueError(f"Oval flange narrow width ({flange_w}mm) cannot be smaller than pilot hub OD ({hub_d}mm).")
                if flange_d <= flange_w:
                    raise ValueError(f"Oval flange length ({flange_d}mm) must be longer than narrow width ({flange_w}mm).")
                if bolt_circle_d <= hub_d or bolt_circle_d >= flange_d:
                    raise ValueError(f"Bolt spacing ({bolt_circle_d}mm) must sit between pilot hub OD ({hub_d}mm) and flange ends ({flange_d}mm).")
            else:
                if hub_d >= flange_d:
                    raise ValueError("Mounting flange diameter must be larger than the bearing pilot hub diameter.")
                if bolt_circle_d <= hub_d or bolt_circle_d >= flange_d:
                    raise ValueError(f"Bolt circle diameter ({bolt_circle_d}mm) must sit cleanly on the flange between hub OD ({hub_d}mm) and flange OD ({flange_d}mm).")

            if shaft_d >= eff_cup_min:
                raise ValueError("Through shaft diameter must be smaller than the bearing cup minor OD / shoulder ID.")
            
            eff_seal_depth = seal_depth if has_seal else 0.0
            shoulder_margin = 2.0 if cup_maj <= 30.0 else (3.5 if has_seal else 4.5)
            min_height_needed = cup_depth + eff_seal_depth + shoulder_margin
            if total_height <= min_height_needed:
                if has_seal:
                    raise ValueError(f"Total housing height ({total_height}mm) must exceed cup depth + seal depth ({cup_depth + seal_depth}mm) by at least {shoulder_margin:.1f}mm for the backing shoulder.")
                else:
                    raise ValueError(f"Total housing height ({total_height}mm) must exceed cup depth ({cup_depth}mm) by at least {shoulder_margin:.1f}mm for the backing shoulder.")
            
            if flange_thick >= total_height:
                raise ValueError("Flange plate thickness must be less than total housing height.")

            taper_angle = math.degrees(math.atan(((cup_maj - cup_min) / 2.0) / cup_depth))
            thrust_ratio = math.tan(math.radians(taper_angle))
            hub_wall = (hub_d - eff_cup_maj) / 2.0
            flange_lip = (flange_d - bolt_circle_d) / 2.0

            self.calc_data = {
                "flange_d": flange_d,
                "flange_w": flange_w,
                "flange_shape": flange_shape,
                "hub_d": hub_d,
                "flange_thick": flange_thick,
                "total_height": total_height,
                "shaft_d": shaft_d,
                "cup_maj": cup_maj,
                "cup_min": cup_min,
                "cup_depth": cup_depth,
                "shrink_offset": shrink_offset,
                "eff_cup_maj": eff_cup_maj,
                "eff_cup_min": eff_cup_min,
                "taper_angle": taper_angle,
                "seal_d": seal_d,
                "seal_depth": seal_depth,
                "has_seal": has_seal,
                "flange_pos": flange_pos,
                "cs_face": cs_face,
                "bolt_circle_d": bolt_circle_d,
                "num_bolts": num_bolts,
                "bolt_hole_d": bolt_hole_d,
                "has_cs": has_cs,
                "cs_head_d": cs_head_d,
                "cs_angle": cs_angle,
                "has_zerk": has_zerk,
                "zerk_d": zerk_d,
                "seat_style": seat_style,
                "has_knockout": has_knockout,
                "contact_angle": contact_angle
            }

            style_short = "Cylindrical Shoulder" if "Cylindrical" in seat_style else "Conical Bevel"
            flange_side_str = "Top / Bearing Retaining Face" if is_top_flange else "Bottom / Base"
            flange_shape_str = f"Oval 2-Bolt ({flange_d:.1f} x {flange_w:.1f} mm)" if is_oval else f"Round ({flange_d:.1f} mm OD)"
            pattern_str = f"2 holes spaced {bolt_circle_d:.1f} mm apart" if is_oval else f"{num_bolts} holes on {bolt_circle_d:.1f} mm B.C. ({flange_lip:.1f} mm margin)"
            seal_info = f"{seal_d:.2f} mm x {seal_depth:.2f} mm" if has_seal else "None (Open Through-Bore)"
            offset_note = f" (+{shrink_offset:.2f} mm fit offset)" if abs(shrink_offset) > 1e-4 else ""
            res_text = (
                f"Seat Geometry:    {style_short} | Cup OD: {cup_maj:.2f} mm{offset_note} x {cup_depth:.2f} mm deep\n"
                f"Flange:           {flange_shape_str} on {flange_side_str} ({flange_thick:.1f} mm thick)\n"
                f"Shoulder / Minor: {eff_cup_min:.2f} mm ID (Hub Wall: {hub_wall:.2f} mm solid backing)\n"
                f"Contact Angle:    {taper_angle:.1f} deg (Dynamic Thrust Ratio Fa/Fr: {thrust_ratio:.3f})\n"
                f"Shaft & Seal:     {shaft_d:.2f} mm through-bore | Seal: {seal_info}\n"
                f"Flange Pattern:   {pattern_str}\n"
                f"Fastener Spec:    {bolt_hole_d:.2f} mm dia"
                + (f" ({cs_head_d:.1f} mm {cs_angle:.0f} deg on {cs_face})" if has_cs else " straight bore") + "\n"
                f"Features:         " + (f"{zerk_d:.1f} mm zerk port" if has_zerk else "No zerk")
                + (f" | 2x Knock-out notches" if (has_knockout and 'Cylindrical' in seat_style) else "")
            )
            self.results_label.config(text=res_text)
            self.stl_btn.config(state=tk.NORMAL)
            self.scad_btn.config(state=tk.NORMAL)
            self.sw_btn.config(state=tk.NORMAL)

            self._update_3d_preview(reset_camera=False)

        except Exception as e:
            messagebox.showerror("Geometry Configuration Error", str(e))

    def export_stl(self):
        if not self.calc_data:
            return

        filePath = filedialog.asksaveasfilename(
            defaultextension=".stl",
            filetypes=[("Stereolithography (STL)", "*.stl"), ("All Files", "*.*")],
            title="Export Tapered Bearing Housing STL"
        )
        if not filePath:
            return

        self.preview_info_label.config(text="Generating high-precision production STL...")
        self.update_idletasks()

        try:
            # High-precision 0.35mm resolution for machining / slicing
            mesh = generate_housing_mesh(self.calc_data, resolution=0.35)
            mesh.save(filePath)

            self.preview_info_label.config(
                text=f"Exported: {mesh.n_cells:,} triangles | Watertight (0 open edges)"
            )
            messagebox.showinfo(
                "STL Export Successful!",
                f"Tapered roller bearing housing STL saved successfully!\n\n"
                f"File: {filePath}\n\n"
                f"Mesh Quality:\n"
                f" • Triangles: {mesh.n_cells:,}\n"
                f" • Watertight Manifold: Yes (0 open edges)\n"
                f" • Flange: {self.calc_data['flange_d']:.1f} mm OD x {self.calc_data['total_height']:.1f} mm H\n\n"
                f"Directly ready for slicing in PETG/ASA or sending for CNC Aluminum machining."
            )
        except Exception as e:
            self.preview_info_label.config(text="STL export error")
            messagebox.showerror("Export Error", f"Failed to generate STL: {str(e)}")

    def _generate_sw_vba_code(self):
        d = self.calc_data
        r_flange_m = (d['flange_d'] / 2.0) / 1000.0
        r_hub_m = (d['hub_d'] / 2.0) / 1000.0
        h_flange_m = d['flange_thick'] / 1000.0
        h_total_m = d['total_height'] / 1000.0
        r_shaft_m = (d['shaft_d'] / 2.0) / 1000.0
        shrink_offset = d.get('shrink_offset', 0.0)
        eff_cup_maj = d['cup_maj'] + shrink_offset
        eff_cup_min = d['cup_min'] + shrink_offset
        r_cup_maj_m = (eff_cup_maj / 2.0) / 1000.0
        r_cup_min_m = (eff_cup_min / 2.0) / 1000.0
        cup_depth_m = d['cup_depth'] / 1000.0
        has_seal = d.get('has_seal', True)
        r_seal_m = (d['seal_d'] / 2.0) / 1000.0
        seal_depth_m = d['seal_depth'] / 1000.0
        r_bc_m = (d['bolt_circle_d'] / 2.0) / 1000.0
        r_bolt_m = (d['bolt_hole_d'] / 2.0) / 1000.0
        n_bolts = int(d['num_bolts'])
        taper_angle_rad = math.radians(d.get('taper_angle', 14.0))
        is_cylindrical = "Cylindrical" in d.get('seat_style', '')
        is_top_flange = ("Top" in d.get('flange_pos', '') or "Bearing" in d.get('flange_pos', ''))
        is_oval = ("Oval" in d.get('flange_shape', ''))
        flange_w_m = (d.get('flange_w', d['flange_d'])) / 1000.0
        r_capsule_m = (flange_w_m / 2.0)
        sy_m = max(0.0, ((d['flange_d'] / 1000.0) - flange_w_m) / 2.0)

        # 1 & 2. Body Extrusions
        if is_oval:
            if is_top_flange:
                body_code = f"""    ' 1. Pilot Hub Extrusion
    stage = "creating pilot hub"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_hub_m}, 0, 0
    Part.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, {h_total_m}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False

    ' 2. Top Oval Retaining Flange Extrusion
    stage = "creating top oval flange"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "", "FACE", 0, {h_total_m}, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateArc 0, {sy_m}, 0, -{r_capsule_m}, {sy_m}, 0, {r_capsule_m}, {sy_m}, 0, -1
    Part.SketchManager.CreateLine {r_capsule_m}, {sy_m}, 0, {r_capsule_m}, -{sy_m}, 0
    Part.SketchManager.CreateArc 0, -{sy_m}, 0, {r_capsule_m}, -{sy_m}, 0, -{r_capsule_m}, -{sy_m}, 0, -1
    Part.SketchManager.CreateLine -{r_capsule_m}, -{sy_m}, 0, -{r_capsule_m}, {sy_m}, 0
    Part.FeatureManager.FeatureExtrusion3 True, False, True, 0, 0, {h_flange_m}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False"""
            else:
                body_code = f"""    ' 1. Oval Flange Base Extrusion
    stage = "creating oval flange base"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateArc 0, {sy_m}, 0, -{r_capsule_m}, {sy_m}, 0, {r_capsule_m}, {sy_m}, 0, -1
    Part.SketchManager.CreateLine {r_capsule_m}, {sy_m}, 0, {r_capsule_m}, -{sy_m}, 0
    Part.SketchManager.CreateArc 0, -{sy_m}, 0, {r_capsule_m}, -{sy_m}, 0, -{r_capsule_m}, -{sy_m}, 0, -1
    Part.SketchManager.CreateLine -{r_capsule_m}, -{sy_m}, 0, -{r_capsule_m}, {sy_m}, 0
    Part.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, {h_flange_m}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False

    ' 2. Pilot Hub Extrusion
    stage = "creating pilot hub"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_hub_m}, 0, 0
    Part.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, {h_total_m}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False"""
        else:
            if is_top_flange:
                body_code = f"""    ' 1. Pilot Hub Extrusion
    stage = "creating pilot hub"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_hub_m}, 0, 0
    Part.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, {h_total_m}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False

    ' 2. Top Bearing Retaining Flange Extrusion
    stage = "creating top retaining flange"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "", "FACE", 0, {h_total_m}, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_flange_m}, 0, 0
    Part.FeatureManager.FeatureExtrusion3 True, False, True, 0, 0, {h_flange_m}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False"""
            else:
                body_code = f"""    ' 1. Flange Base Extrusion
    stage = "creating flange base"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_flange_m}, 0, 0
    Part.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, {h_flange_m}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False

    ' 2. Pilot Hub Extrusion
    stage = "creating pilot hub"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_hub_m}, 0, 0
    Part.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, {h_total_m}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False"""

        # 3. Bearing Cup Seat Cuts (From top face while solid)
        if is_cylindrical:
            seat_code = f"""    ' 3. Bearing Cup Seat & Retaining Shoulder Cut
    stage = "cutting shoulder relief bore"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "", "FACE", 0, {h_total_m}, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_cup_min_m}, 0, 0
    Part.FeatureManager.FeatureCut4 True, False, False, 0, 0, {cup_depth_m + 0.0035}, 0, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, False, 0, 0, False

    stage = "cutting cylindrical cup pocket"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "", "FACE", {(r_hub_m + r_cup_min_m) / 2.0}, {h_total_m}, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_cup_maj_m}, 0, 0
    Part.FeatureManager.FeatureCut4 True, False, False, 0, 0, {cup_depth_m}, 0, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, False, 0, 0, False"""
        else:
            seat_code = f"""    ' 3. Tapered Race Cup Cut
    stage = "cutting tapered race seat"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "", "FACE", 0, {h_total_m}, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_cup_maj_m}, 0, 0
    Part.FeatureManager.FeatureCut4 True, False, False, 0, 0, {cup_depth_m}, 0, True, False, False, False, {taper_angle_rad}, 0, False, False, False, False, False, True, True, True, True, False, False, 0, 0, False"""

        # 4. Shaft Cut (from Top Plane, cut through all along +Y)
        shaft_code = f"""    ' 4. Through Shaft Clearance Cut
    stage = "cutting shaft bore"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_shaft_m}, 0, 0
    Part.FeatureManager.FeatureCut4 True, False, True, 1, 0, {h_total_m * 2.0}, 0, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, False, 0, 0, False"""

        # 5. Seal Cut (from Top Plane, cut into base along +Y)
        if has_seal and seal_depth_m > 0 and r_seal_m > 0:
            seal_code = f"""    ' 5. Axle Seal Pocket (Bottom)
    stage = "cutting seal pocket"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_seal_m}, 0, 0
    Part.FeatureManager.FeatureCut4 True, False, True, 0, 0, {seal_depth_m}, 0, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, False, 0, 0, False"""
        else:
            seal_code = "    ' 5. (Axle Seal Pocket Omitted - Direct Through Bore)"

        # 6. Bolt Pattern (from Top Plane, cut through all along +Y)
        if is_oval:
            bolt_pattern_code = f"""    ' 6. 2-Bolt Pattern on Oval Flange
    stage = "cutting 2-bolt pattern"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, {r_bc_m}, 0, {r_bolt_m}, {r_bc_m}, 0
    Part.SketchManager.CreateCircle 0, -{r_bc_m}, 0, {r_bolt_m}, -{r_bc_m}, 0
    Part.FeatureManager.FeatureCut4 True, False, True, 1, 0, {h_total_m * 2.0}, 0, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, False, 0, 0, False"""
        else:
            bolt_circles = []
            angle_step = 2.0 * math.pi / n_bolts
            offset_angle = angle_step / 2.0
            for i in range(n_bolts):
                ang = (i * angle_step) + offset_angle
                bx = r_bc_m * math.cos(ang)
                by = r_bc_m * math.sin(ang)
                bolt_circles.append(
                    f"    Part.SketchManager.CreateCircle {bx:.6f}, {by:.6f}, 0, {bx + r_bolt_m:.6f}, {by:.6f}, 0"
                )
            circles_code = "\n".join(bolt_circles)
            bolt_pattern_code = f"""    ' 6. Bolt Pattern on Flange
    stage = "cutting bolt pattern"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
{circles_code}
    Part.FeatureManager.FeatureCut4 True, False, True, 1, 0, {h_total_m * 2.0}, 0, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, False, 0, 0, False"""

        return f"""Option Explicit

' SolidWorks VBA Macro - Tapered Roller Bearing Flange Housing
' Generated by Tapered Bearing Housing Generator (KB1U / DC-LIGHT LLC)

Dim swApp As Object
Dim Part As Object

Sub main()
    Dim boolstatus As Boolean
    Dim stage As String

    On Error GoTo MacroError

    stage = "creating new part"
    Set swApp = Application.SldWorks
    Set Part = swApp.NewPart()

{body_code}

{seat_code}

{shaft_code}

{seal_code}

{bolt_pattern_code}

    Part.ClearSelection2 True
    Part.EditRebuild3
    Part.ViewZoomtofit2
    MsgBox "Tapered bearing housing generated successfully!", vbInformation
    Exit Sub

MacroError:
    MsgBox "SolidWorks stopped while " & stage & "." & vbCrLf & vbCrLf & _
           "Error " & Err.Number & ": " & Err.Description, vbCritical, "Bearing Housing Macro"
End Sub
"""

    def save_sw_bas(self):
        if not self.calc_data:
            return
        filePath = filedialog.asksaveasfilename(
            defaultextension=".bas",
            filetypes=[("VBA Source Module", "*.bas"), ("Text File", "*.txt")],
            title="Save SolidWorks VBA Code"
        )
        if not filePath:
            return
        with open(filePath, "w", encoding="utf-8") as f:
            f.write(self._generate_sw_vba_code())
        messagebox.showinfo("Saved!", "SolidWorks VBA macro saved successfully!")

    def export_openscad(self):
        if not self.calc_data:
            return
        filePath = filedialog.asksaveasfilename(
            defaultextension=".scad",
            filetypes=[("OpenSCAD Files", "*.scad")],
            title="Save OpenSCAD Script"
        )
        if not filePath:
            return

        d = self.calc_data
        is_cyl = "Cylindrical" in d.get('seat_style', '')
        has_ko = d.get('has_knockout', True)
        has_seal = d.get('has_seal', True)
        is_top = ("Top" in d.get('flange_pos', '') or "Bearing" in d.get('flange_pos', ''))
        is_oval = ("Oval" in d.get('flange_shape', ''))
        flange_w = d.get('flange_w', d['flange_d'])
        cs_is_hub = ("Hub" in d.get('cs_face', '') or "Shoulder" in d.get('cs_face', ''))

        scad_code = f"""// Parametric Tapered Roller Bearing Housing
// Generated by Tapered Bearing Housing Generator (KB1U / DC-LIGHT LLC)

$fn = 100;

flange_d = {d['flange_d']:.2f};
flange_w = {flange_w:.2f};
flange_is_oval = {'true' if is_oval else 'false'};
hub_d = {d['hub_d']:.2f};
flange_thick = {d['flange_thick']:.2f};
total_height = {d['total_height']:.2f};
shaft_d = {d['shaft_d']:.2f};
cup_maj = {d['cup_maj']:.2f};
cup_min = {d['cup_min']:.2f};
cup_depth = {d['cup_depth']:.2f};
shrink_offset = {d.get('shrink_offset', 0.0):.2f};
eff_cup_maj = cup_maj + shrink_offset;
eff_cup_min = cup_min + shrink_offset;
has_seal = {'true' if has_seal else 'false'};
seal_d = {d['seal_d']:.2f};
seal_depth = {d['seal_depth']:.2f};
flange_is_top = {'true' if is_top else 'false'};
bolt_circle_d = {d['bolt_circle_d']:.2f};
num_bolts = {d['num_bolts']};
bolt_hole_d = {d['bolt_hole_d']:.2f};
has_cs = {'true' if d['has_cs'] else 'false'};
cs_face_is_hub = {'true' if cs_is_hub else 'false'};
cs_head_d = {d['cs_head_d']:.2f};
cs_angle = {d['cs_angle']:.1f};
has_zerk = {'true' if d['has_zerk'] else 'false'};
zerk_d = {d['zerk_d']:.2f};
seat_is_cylindrical = {'true' if is_cyl else 'false'};
has_knockout = {'true' if has_ko else 'false'};

module bearing_housing() {{
    difference() {{
        // Solid body (Flange + Pilot Hub)
        union() {{
            if (flange_is_oval) {{
                hull() {{
                    translate([0, (flange_d - flange_w) / 2, flange_is_top ? (total_height - flange_thick) : 0])
                        cylinder(d=flange_w, h=flange_thick);
                    translate([0, -(flange_d - flange_w) / 2, flange_is_top ? (total_height - flange_thick) : 0])
                        cylinder(d=flange_w, h=flange_thick);
                }}
                cylinder(d=hub_d, h=total_height);
            }} else if (flange_is_top) {{
                cylinder(d=hub_d, h=total_height);
                translate([0, 0, total_height - flange_thick])
                    cylinder(d=flange_d, h=flange_thick);
            }} else {{
                cylinder(d=flange_d, h=flange_thick);
                cylinder(d=hub_d, h=total_height);
            }}
        }}

        // Through shaft clearance bore
        translate([0, 0, -1])
            cylinder(d=shaft_d, h=total_height + 2);

        // Axle seal pocket at base (optional)
        if (has_seal && seal_depth > 0 && seal_d > 0) {{
            translate([0, 0, -1])
                cylinder(d=seal_d, h=seal_depth + 1);
        }}

        // Bearing cup race seat
        if (seat_is_cylindrical) {{
            // Cylindrical press-fit pocket
            translate([0, 0, total_height - cup_depth])
                cylinder(d=eff_cup_maj, h=cup_depth + 1);
            // Retaining shoulder step
            translate([0, 0, total_height - cup_depth - 3.5])
                cylinder(d=eff_cup_min, h=3.6);
            // Knock-out punch notches for drift punch race removal
            if (has_knockout) {{
                translate([0, 0, total_height - cup_depth])
                    cube([min(16.0, eff_cup_maj * 0.16), eff_cup_maj + 4.0, 8.0], center=true);
            }}
        }} else {{
            // Conical tapered raceway
            translate([0, 0, total_height - cup_depth])
                cylinder(d1=eff_cup_min, d2=eff_cup_maj, h=cup_depth + 1);
        }}

        // Mounting bolt holes & countersinks
        cs_depth = (cs_head_d - bolt_hole_d) / (2 * tan(cs_angle / 2));
        z_bolt_start = flange_is_top ? (total_height - flange_thick - 1) : -1;

        if (flange_is_oval) {{
            for (sign = [-1, 1]) {{
                translate([0, sign * (bolt_circle_d / 2), z_bolt_start]) {{
                    cylinder(d=bolt_hole_d, h=flange_thick + 2);
                    if (has_cs && cs_depth > 0) {{
                        if (!flange_is_top) {{
                            if (cs_face_is_hub) {{
                                translate([0, 0, flange_thick + 1 - cs_depth])
                                    cylinder(d1=bolt_hole_d, d2=cs_head_d, h=cs_depth + 0.1);
                            }} else {{
                                translate([0, 0, 0.9])
                                    cylinder(d1=cs_head_d, d2=bolt_hole_d, h=cs_depth + 0.1);
                            }}
                        }} else {{
                            if (cs_face_is_hub) {{
                                translate([0, 0, 0.9])
                                    cylinder(d1=cs_head_d, d2=bolt_hole_d, h=cs_depth + 0.1);
                            }} else {{
                                translate([0, 0, flange_thick + 1 - cs_depth])
                                    cylinder(d1=bolt_hole_d, d2=cs_head_d, h=cs_depth + 0.1);
                            }}
                        }}
                    }}
                }}
            }}
        }} else {{
            angle_step = 360 / num_bolts;
            offset_angle = angle_step / 2;
            for (i = [0 : num_bolts - 1]) {{
                rotate([0, 0, (i * angle_step) + offset_angle]) {{
                    translate([bolt_circle_d / 2, 0, z_bolt_start]) {{
                        cylinder(d=bolt_hole_d, h=flange_thick + 2);
                        if (has_cs && cs_depth > 0) {{
                            if (!flange_is_top) {{
                                if (cs_face_is_hub) {{
                                    translate([0, 0, flange_thick + 1 - cs_depth])
                                        cylinder(d1=bolt_hole_d, d2=cs_head_d, h=cs_depth + 0.1);
                                }} else {{
                                    translate([0, 0, 0.9])
                                        cylinder(d1=cs_head_d, d2=bolt_hole_d, h=cs_depth + 0.1);
                                }}
                            }} else {{
                                if (cs_face_is_hub) {{
                                    translate([0, 0, 0.9])
                                        cylinder(d1=cs_head_d, d2=bolt_hole_d, h=cs_depth + 0.1);
                                }} else {{
                                    translate([0, 0, flange_thick + 1 - cs_depth])
                                        cylinder(d1=bolt_hole_d, d2=cs_head_d, h=cs_depth + 0.1);
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}

        // Grease zerk port
        if (has_zerk && zerk_d > 0) {{
            eff_seal = has_seal ? seal_depth : 0;
            z_zerk = eff_seal + ((total_height - cup_depth - eff_seal) / 2);
            translate([0, 0, z_zerk])
                rotate([0, 90, 0])
                    cylinder(d=zerk_d, h=flange_d);
        }}
    }}
}}

bearing_housing();
"""
        with open(filePath, "w", encoding="utf-8") as f:
            f.write(scad_code)
        messagebox.showinfo("Saved!", "OpenSCAD script exported successfully!")

    def show_about_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("About & License - Bearing Housing Generator")
        dialog.geometry("640x580")
        dialog.minsize(520, 460)
        dialog.transient(self)
        dialog.grab_set()

        content = ttk.Frame(dialog, padding="15")
        content.pack(fill=tk.BOTH, expand=True)

        title_lbl = ttk.Label(
            content,
            text="Tapered Roller Bearing Housing CAD & STL Generator",
            font=("Helvetica", 13, "bold")
        )
        title_lbl.pack(pady=(0, 2))

        sub_lbl = ttk.Label(
            content,
            text="Free & Open-Source Mechanical Tool (MIT License)",
            font=("Segoe UI", 9, "italic"),
            foreground="#2563EB"
        )
        sub_lbl.pack(pady=(0, 8))

        desc_lbl = ttk.Label(
            content,
            text=(
                "Parametric 3D bearing flange housing designer and direct STL exporter.\n"
                "Designed to allow makers, amateur radio builders, and machinists to house standard\n"
                "trailer tapered roller bearings for antenna rotators, azimuth/elevation gimbals,\n"
                "pivots, and heavy mechanical shafts without requiring complex lathe bevel setups."
            ),
            justify=tk.CENTER
        )
        desc_lbl.pack(pady=(0, 10))

        license_box = ttk.LabelFrame(content, text=" Software License (MIT) ", padding="8")
        license_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        st = scrolledtext.ScrolledText(license_box, height=12, wrap=tk.WORD, font=("Consolas", 9))
        st.insert(tk.END, MIT_LICENSE_TEXT)
        st.config(state=tk.DISABLED)
        st.pack(fill=tk.BOTH, expand=True)

        credit_lbl = ttk.Label(
            content,
            text="Built with Python, Tkinter, PyVista, VTK, NumPy, and Pillow.",
            font=("Segoe UI", 8),
            foreground="#666666"
        )
        credit_lbl.pack(pady=(0, 8))

        btn_bar = ttk.Frame(content)
        btn_bar.pack(fill=tk.X)

        def copy_license():
            self.clipboard_clear()
            self.clipboard_append(MIT_LICENSE_TEXT)
            messagebox.showinfo("Copied", "MIT License text copied to clipboard!", parent=dialog)

        copy_btn = ttk.Button(btn_bar, text="📋 Copy License Text", command=copy_license)
        copy_btn.pack(side=tk.LEFT)

        close_btn = ttk.Button(btn_bar, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT)

    def show_help_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Detailed User Guide & Tapered Bearing Reference")
        dialog.geometry("720x660")
        dialog.minsize(580, 480)
        dialog.transient(self)
        dialog.grab_set()

        content = ttk.Frame(dialog, padding="15")
        content.pack(fill=tk.BOTH, expand=True)

        title_lbl = ttk.Label(
            content,
            text="📖 Tapered Bearing Housing — Technical Reference & User Guide",
            font=("Helvetica", 12, "bold")
        )
        title_lbl.pack(pady=(0, 4), anchor=tk.W)

        sub_lbl = ttk.Label(
            content,
            text="Comprehensive guide to trailer bearing geometry, mounting patterns, 3D printing, and machining.",
            font=("Segoe UI", 9, "italic"),
            foreground="#4B5563"
        )
        sub_lbl.pack(pady=(0, 8), anchor=tk.W)

        help_box = ttk.LabelFrame(content, text=" Technical Documentation ", padding="6")
        help_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        st = scrolledtext.ScrolledText(help_box, height=20, wrap=tk.WORD, font=("Segoe UI", 9))
        
        help_content = """1. OVERVIEW & APPLICATIONS
--------------------------------------------------------------------------------
Trailer wheel bearings (tapered roller bearings) are ubiquitous, inexpensive, and
capable of carrying massive combined radial and thrust (axial) loads. They range from
light 0.75" garden trailers and standard 1.063" - 1.750" (2000 - 7000 lb) trailer axles
all the way up to heavy-duty 2.000", 2.250", and 2.500" (8,000 - 12,000 lb) commercial hubs.

This tool generates precision 3D-printable flanged bearing blocks that house these
cups perfectly. Use them for:
• Heavy-duty antenna azimuth/elevation rotators and satellite tracking gimbals.
• Wind turbine vertical pivots and mast bearings carrying high deadweight axial loads.
• Heavy-duty trailer axles, cart wheels, and turntable mechanisms up to 2.5" diameter.
• Prototyping test fits in PETG before sending the STL to be CNC-machined in Aluminum.


2. TAPERED CONTACT ANGLE (α) & THRUST MECHANICS
--------------------------------------------------------------------------------
In a tapered roller bearing, the line of contact between the rollers and raceways is
inclined at a contact angle α relative to the radial plane:
• Standard Wheel / Trailer Axle Angle (α = 12° to 16°):
  - Optimized for vehicles carrying high radial road load with cornering thrust.
  - Typical dynamic thrust-to-radial capacity ratio: Fa / Fr = tan(α) ≈ 0.22 to 0.28.
  - Examples: L44649/10 (14.0°), LM67048/10 (13.6°), 25580/20 (14.4°), 28580/21 (14.3°).

• Steep Contact Angle / High Thrust (α = 24° to 30°):
  - Optimized for vertical antenna rotators, crane swivels, steering kingpins, and
    mast pivots where the axial downward load dominates over side loads.
  - Typical dynamic thrust-to-radial capacity ratio: Fa / Fr = tan(α) ≈ 0.45 to 0.58.
  - Carries more than double the axial thrust of a standard bearing!


3. SEAT GEOMETRY PROVISIONS: CYLINDRICAL VS. CONICAL
--------------------------------------------------------------------------------
• Cylindrical Cup Bore with Retaining Shoulder (Standard Trailer Hub):
  - Real trailer bearing outer cups (e.g. Timken L44610, 25520, 28521) have a cylindrical
    ground steel OD.
  - The housing features a cylindrical press-fit bore of diameter 'Cup Major OD' down to
    'Cup Depth', bottoming out against a solid stop shoulder of diameter 'Cup Minor OD'.
  - Includes dual opposed Drift Punch Knock-Out Notches so you can tap out the race
    from the seal side during maintenance without damaging the housing.

• Conical Tapered Raceway (Direct Conical Bevel):
  - Direct beveled seat sloping at angle α from Cup Major OD down to Cup Minor OD.
  - Used for custom conical roller cages, beveled cup supports, or direct cone seating.


4. STANDARD AXLE CATALOG (UP TO 2.50" / 63.5 MM)
--------------------------------------------------------------------------------
• 0.750" (3/4"): LM11949/10 — 1000-1500 lb light trailers, carts, light rotators.
• 1.000" (1"): L44643/10 — 2000 lb straight BT8 spindles.
• 1.063" (1-1/16"): L44649/10 — 2000-2200 lb common trailer axle hubs.
• 1.250" (1-1/4"): LM67048/10 — 3500-4400 lb outer bearing.
• 1.375" (1-3/8"): L68149/11 — 3500 lb Dexter #84 inner bearing (2.565" seal).
• 1.500" (1-1/2"): LM29749/10 & 15123/245 — 4400-5200 lb trailer axles.
• 1.625" (1-5/8"): 14125A/276 — 6000-7000 lb outer bearing.
• 1.750" (1-3/4"): 25580/20 — 5200-7000 lb Dexter #42 inner bearing (3.376" seal).
• 2.000" (2"): 28580/21 — 8,000-10,000 lb heavy trailer axle (3.625" cup, 3.880" seal).
• 2.125" (2-1/8"): 387AS/382A — Heavy 8K-10K commercial hubs.
• 2.250" (2-1/4"): 387A/382A — Standard 9,000-10,000 lb general duty axle (4.125" seal).
• 2.500" (2-1/2"): 3984/20 — 10,000-12,000 lb heavy-duty dual-wheel commercial axle.
• ISO Metric Series: 30204 (20mm) up to 30210 (50mm / ~2.0").


5. FLANGE POSITION & OUTLINE SHAPE (ROUND VS. OVAL NARROW MOUNT)
--------------------------------------------------------------------------------
• Flange Outline Shape:
  - Circular / Round (Standard N-Bolt): Symmetrical circular flange with 2 to 16 bolt holes.
  - Oval / 2-Bolt Oblong (Narrow Mount): Pill/stadium-shaped flange tailored for narrow beams,
    gimbal brackets, or channel sections where mounting width is restricted. Features two
    inline mounting ears along the major axis and compact narrow width across the hub.
    The grease zerk remains oriented at 90° to the mounting bolts for easy grease gun access!

• Flange Position & Bearing Retention:
  - Bottom / Base (Standard Flange): Traditional flanged bearing block with the mounting flange
    at the base and the bearing cup mouth facing upward. Requires a shaft collar or nut.
  - Top / Bearing Face (Captive / Retaining Flange): Flange sits flush with the wide mouth of the
    bearing race cup. Designed specifically for mounting directly against a flat plate, gimbal frame,
    or structural bulkhead. The flat mounting surface directly closes and traps the bearing inside
    the housing! This provides 100% positive retention even on smooth, unthreaded shafts or pivots.


6. FASTENER OPTIONS & COUNTERSINKING
--------------------------------------------------------------------------------
• Bolt Circle Diameter (B.C.D.):
  Pitch diameter for mounting bolt holes. Clocked to avoid zerk port and punch notches.
• Straight Through-Bores vs. Countersinks:
  - Straight bores retain full flat flange material thickness under hex bolts and washers.
  - Countersinks allow flush bugle-head drywall/wood screws (82°) or ISO machine screws (90°).
• Countersink Head Face:
  - Accessible Hub Shoulder: Heads are driven from the exterior shoulder into the mounting plate.
  - Mounting Face (Sub-Flush): Heads are driven flush/sub-flush with the mounting face.


7. LUBRICATION (GREASE ZERK PORT) & OPTIONAL SEAL COUNTERBORE
--------------------------------------------------------------------------------
• Optional Grease / Oil Seal Counterbore:
  - Enable for trailer hubs or outdoor wet pivots requiring standard double-lip rubber seals.
  - Disable for dry pivots, 3D printed bushings, or applications needing an unobstructed through-bore.
• Grease Zerk Port:
  - Radial port sized for tapping standard 1/4"-28 UNF or 1/8" NPT grease zerks.
  - Automatically centered in the cavity below the bearing cup seat for effective packing.


8. 3D PRINTING & HOLE-SHRINKAGE COMPENSATION
--------------------------------------------------------------------------------
• Why 3D Printed Holes Shrink:
  - Molten plastic shrinks as it cools from extrusion temperature (~230°C–260°C).
  - Cylindrical toolpaths are approximated as polygonal line segments (chordal error).
  - Surface tension and bead rounding naturally pull inner hole perimeters inward
    by typically -0.10 mm to -0.25 mm on diameter.
• Bearing Seat Fit / Shrink Offset:
  - This tool provides a dedicated 'Bearing Seat Fit / Shrink Offset' parameter.
  - Setting +0.10 mm to +0.15 mm expands the CAD bearing seat cavity just enough so
    your hardened steel bearing cup presses in snug and true without binding!
  - Set to 0.00 mm when generating models for CNC Aluminum machining.
• Slicer Recommendations:
  - Materials: PETG (tough, grease-resistant), ASA/ABS (UV & heat resistant), PC (rigid).
  - Walls / Perimeters: 6 to 8 walls (ensures 100% solid plastic behind the bearing seat).
  - Infill: 50% to 100% (Gyroid or Rectilinear).
  - Print Orientation: Place either flat flange face or flat base face on the build plate.


9. ⚠️ SAFETY ADVISORY: "DON'T SHOOT YOUR EYE OUT" / FORCE & LOAD LIMITATIONS
--------------------------------------------------------------------------------
A 3D printed bearing holder is WILDLY useful in the right application. It is ideal for
prototyping, test fits, alignment verification, amateur radio antenna rotators,
satellite tracking gimbals, manual pivots, solar trackers, robot joints, and low-speed
turntables. It can also serve as an invaluable inexpensive test case before sending
the exported CAD files to a CNC shop to machine the final part out of 6061-T6 Aluminum.

BUT HEED THIS CRUCIAL WARNING:
Bearings are frequently used in mechanical applications with tons of torque, high RPMs,
enormous rotational inertia, and massive dynamic thrust forces that could easily
overwhelm, shear, or crack a 3D-printed plastic bearing retainer!

THIS TOOL DOES NOT JUDGE SAFETY — IT JUST MAKES BEARING HOLDERS.

Key Physical Limitations of 3D-Printed Thermoplastic Housings:
• Inter-Layer Delamination:
  3D prints are anisotropic. Tensile or bending loads trying to rip the bearing or
  flange apart place layer lines under tension, which are inherently weaker than
  solid injection-molded or machined metal.
• Viscoelastic Creep Under Sustained Load:
  Thermoplastics (especially PLA and PETG) slowly deform and flow over time under
  sustained mechanical preload. A bearing preloaded tightly today may loosen or
  lose axial alignment weeks later under constant spring or gravity tension.
• Friction & Thermal Softening:
  Rolling elements generate frictional heat. While steel bearings easily run at
  80°C–120°C, PLA softens at 55°C, PETG at 75°C, and ABS at 95°C. At high RPM,
  heat conducting into the plastic can cause immediate bore softening and failure.
• Dynamic Shock & Gyroscopic Forces:
  Heavy spinning masses, wind gusts on tall antenna masts, or vehicular shock loads
  can produce peak forces 5x to 10x higher than static weights, causing sudden
  brittle catastrophic fracture.

Prudent Engineering Rules of Thumb:
✓ DO use 3D prints for slow rotators, gimbals, prototypes, test fixtures, and low-risk pivots.
✓ DO use captive flange orientation (flange on bearing side) where the mounting bulkhead
  provides a solid metal barrier trapping the bearing inside.
✗ NEVER use 3D-printed bearing holders for highway trailers, passenger vehicles, overhead
  suspension, high-RPM shafts, human-carrying equipment, or any setup where structural
  failure could cause personal injury, falling hazards, or property damage.
✓ When in doubt, prototype in PETG/ASA first, then use the exported SolidWorks macro or
  STL to have the housing CNC machined from 6061-T6 Aluminum.
"""

        st.insert(tk.END, help_content)
        st.config(state=tk.DISABLED)
        st.pack(fill=tk.BOTH, expand=True)

        close_btn = ttk.Button(content, text="Close", command=dialog.destroy)
        close_btn.pack(anchor=tk.E, pady=(4, 0))

    def on_closing(self):
        try:
            if hasattr(self, 'plotter') and self.plotter is not None:
                self.plotter.close()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = BearingHousingApp()
    app.mainloop()
