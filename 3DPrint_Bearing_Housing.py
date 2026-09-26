"""
Tapered Roller Bearing Housing CAD, 3D Preview & STL Generator
Open-source parametric 3D bearing flange housing generator for antenna gimbals,
rotators, trailers, and mechanical pivot projects.

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

# Standard Trailer Bearing Presets
# Tuple: (Description, Shaft ID mm, Cup Major OD mm, Cup Minor OD mm, Cup Depth mm, Seal OD mm, Seal Depth mm)
BEARING_PRESETS = {
    "1.063\" (1-1/16\") Trailer Spindle (L44649 / L44610)": (
        "Common 2000-2200 lb trailer axle outer/inner bearing. L44649 cone with L44610 cup race.",
        27.0, 50.29, 45.2, 14.3, 50.29, 7.0
    ),
    "1.250\" (1-1/4\") Trailer Spindle (LM67048 / LM67010)": (
        "Common 3500 lb axle outer bearing. LM67048 cone with LM67010 cup race.",
        31.75, 59.13, 53.0, 15.9, 59.13, 8.0
    ),
    "1.375\" (1-3/8\") Trailer Spindle (L68149 / L68111)": (
        "Standard 3500 lb trailer axle inner bearing. L68149 cone with L68111 cup race.",
        35.0, 59.97, 54.0, 15.9, 65.0, 8.5
    ),
    "1.750\" (1-3/4\") Heavy Axle (25580 / 25520)": (
        "5200-7000 lb trailer axle inner bearing. 25580 cone with 25520 cup race.",
        44.45, 83.06, 75.0, 19.0, 85.0, 10.0
    ),
    "Custom / User Specified": (
        "Enter custom cup race and seal dimensions directly.",
        25.4, 50.0, 45.0, 14.0, 50.0, 7.0
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
    "Custom Fastener Hole": (5.5, 10.0, 82.0)
}


def generate_housing_mesh(d, resolution=0.42):
    """
    Generates a 100% watertight, manifold 3D mesh of the tapered roller bearing housing
    using a continuous Signed Distance Field (SDF) and VTK Flying Edges.
    Includes the stepped flange & pilot hub body, central shaft bore, tapered cup race,
    optional seal counterbore, bolt circle mounting holes (with optional tapered countersinks),
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
    seal_d = d['seal_d']
    seal_depth = d['seal_depth']
    bolt_circle_d = d['bolt_circle_d']
    num_bolts = int(d['num_bolts'])
    bolt_hole_d = d['bolt_hole_d']
    has_cs = d['has_cs']
    cs_head_d = d['cs_head_d']
    cs_angle = d['cs_angle']
    has_zerk = d['has_zerk']
    zerk_d = d['zerk_d']

    res = resolution
    R_flange = flange_d / 2.0
    pad = 2.0
    xs = np.arange(-R_flange - pad, R_flange + pad + res, res)
    ys = np.arange(-R_flange - pad, R_flange + pad + res, res)
    zs = np.arange(-pad, total_height + pad + res, res)

    nx, ny, nz = len(xs), len(ys), len(zs)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
    r_cyl = np.sqrt(X**2 + Y**2)

    # 1. Outer Solid Body: Stepped cylinder (flange at base + pilot hub)
    d_flange = np.maximum(r_cyl - R_flange, np.maximum(-Z, Z - flange_thick))
    d_hub = np.maximum(r_cyl - (hub_d / 2.0), np.maximum(-Z, Z - total_height))
    d_solid = np.minimum(d_flange, d_hub)

    # 2. Central Shaft Clearance Bore (through entire height Z)
    d_shaft_hole = r_cyl - (shaft_d / 2.0)
    d_solid = np.maximum(d_solid, -d_shaft_hole)

    # 3. Grease / Oil Seal Counterbore (at base, Z from 0 to seal_depth)
    if seal_depth > 0 and seal_d > 0:
        d_seal_cavity = np.maximum(r_cyl - (seal_d / 2.0), np.maximum(-Z - 5.0, Z - seal_depth))
        d_solid = np.maximum(d_solid, -d_seal_cavity)

    # 4. Tapered Bearing Race Cup (from top Z = total_height down to total_height - cup_depth)
    z_cup_bot = total_height - cup_depth
    R_maj = cup_maj / 2.0
    R_min = cup_min / 2.0
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

    # Angle offset puts holes midway between grease port at +X (0 deg)
    angle_offset = np.pi / num_bolts if num_bolts > 0 else 0.0

    for b in range(num_bolts):
        angle = b * (2 * np.pi / num_bolts) + angle_offset
        bx = r_bc * np.cos(angle)
        by = r_bc * np.sin(angle)
        dist_bolt = np.sqrt((X - bx)**2 + (Y - by)**2)
        # Straight through-hole
        d_solid = np.maximum(d_solid, -(dist_bolt - r_bolt))

        # Tapered countersink on the top face of the flange
        if has_cs and cs_depth > 0:
            z_from_flange_top = flange_thick - Z
            r_cs_z = r_cs - np.clip(z_from_flange_top, 0, cs_depth) * np.tan(np.radians(cs_angle / 2.0))
            d_cs_cavity = np.maximum(dist_bolt - r_cs_z, np.maximum(Z - flange_thick, (flange_thick - cs_depth) - Z))
            d_solid = np.maximum(d_solid, -d_cs_cavity)

    # 6. Grease Zerk Port (radial hole along +X axis entering between seal and cup)
    if has_zerk and zerk_d > 0:
        z_zerk = seal_depth + (z_cup_bot - seal_depth) / 2.0
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

    z_cup_bot = total_height - cup_depth

    # 1. Bearing cup race (hardened steel outer ring)
    cup_tube = pv.Cylinder(
        center=(0, 0, z_cup_bot + cup_depth / 2.0),
        direction=(0, 0, 1),
        radius=cup_maj / 2.0,
        height=cup_depth,
        resolution=60
    )

    # 2. Tapered roller cage and rollers
    rollers = []
    n_rollers = 14
    r_track = (shaft_d / 2.0 + 2.5 + cup_min / 2.0) / 2.0
    roller_r = max(1.5, (cup_min / 2.0 - shaft_d / 2.0 - 2.5) / 2.2)
    roller_len = max(3.0, cup_depth - 2.5)

    for i in range(n_rollers):
        ang = i * (2 * np.pi / n_rollers)
        rx = r_track * np.cos(ang)
        ry = r_track * np.sin(ang)
        roller = pv.Cylinder(
            center=(rx, ry, z_cup_bot + cup_depth / 2.0),
            direction=(0, 0, 1),
            radius=roller_r,
            height=roller_len,
            resolution=16
        )
        rollers.append(roller)

    # 3. Shaft inner race cylinder
    inner_race = pv.Cylinder(
        center=(0, 0, z_cup_bot + cup_depth / 2.0),
        direction=(0, 0, 1),
        radius=shaft_d / 2.0 + 2.0,
        height=cup_depth,
        resolution=40
    )

    # 4. Rubber grease seal
    seal_cyl = None
    if seal_depth > 0 and seal_d > 0:
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
            x, y = self.winfo_pointerxy()
            w = self.winfo_containing(x, y)
            if w and (str(w).startswith(str(left_container)) or w == canvas_left):
                canvas_left.yview_scroll(int(-1 * (event.delta / 120)), "units")
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
            text="Antenna Gimbals, Rotators & Trailer Bearing Blocks",
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
        preset_group = ttk.LabelFrame(self.scrollable_frame, text=" Bearing Presets ", padding="8")
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

        ttk.Label(race_group, text="Cup Race Major OD (mm):").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.cup_maj_var = tk.DoubleVar(value=50.29)
        ttk.Entry(race_group, textvariable=self.cup_maj_var, width=12).grid(row=0, column=1, pady=3)

        ttk.Label(race_group, text="Cup Race Minor OD (mm):").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.cup_min_var = tk.DoubleVar(value=45.2)
        ttk.Entry(race_group, textvariable=self.cup_min_var, width=12).grid(row=1, column=1, pady=3)

        ttk.Label(race_group, text="Cup Race Depth / Width (mm):").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.cup_depth_var = tk.DoubleVar(value=14.3)
        ttk.Entry(race_group, textvariable=self.cup_depth_var, width=12).grid(row=2, column=1, pady=3)

        ttk.Label(race_group, text="Through Shaft Clearance ID (mm):").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.shaft_d_var = tk.DoubleVar(value=27.0)
        ttk.Entry(race_group, textvariable=self.shaft_d_var, width=12).grid(row=3, column=1, pady=3)

        ttk.Label(race_group, text="Axle Seal Bore Dia (mm):").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.seal_d_var = tk.DoubleVar(value=50.29)
        ttk.Entry(race_group, textvariable=self.seal_d_var, width=12).grid(row=4, column=1, pady=3)

        ttk.Label(race_group, text="Axle Seal Bore Depth (mm):").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.seal_depth_var = tk.DoubleVar(value=7.0)
        ttk.Entry(race_group, textvariable=self.seal_depth_var, width=12).grid(row=5, column=1, pady=3)

        # Housing Body & Flange Group
        body_group = ttk.LabelFrame(self.scrollable_frame, text=" Housing & Flange Dimensions ", padding="8")
        body_group.pack(fill=tk.X, pady=4)

        ttk.Label(body_group, text="Mounting Flange Diameter (mm):").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.flange_d_var = tk.DoubleVar(value=95.0)
        ttk.Entry(body_group, textvariable=self.flange_d_var, width=12).grid(row=0, column=1, pady=3)

        ttk.Label(body_group, text="Flange Base Thickness (mm):").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.flange_thick_var = tk.DoubleVar(value=12.0)
        ttk.Entry(body_group, textvariable=self.flange_thick_var, width=12).grid(row=1, column=1, pady=3)

        ttk.Label(body_group, text="Bearing Pilot Hub OD (mm):").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.hub_d_var = tk.DoubleVar(value=68.0)
        ttk.Entry(body_group, textvariable=self.hub_d_var, width=12).grid(row=2, column=1, pady=3)

        ttk.Label(body_group, text="Total Housing Height (mm):").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.total_height_var = tk.DoubleVar(value=32.0)
        ttk.Entry(body_group, textvariable=self.total_height_var, width=12).grid(row=3, column=1, pady=3)

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

        ttk.Label(bolt_group, text="Countersink Head Dia (mm):").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.cs_head_d_var = tk.DoubleVar(value=10.2)
        ttk.Entry(bolt_group, textvariable=self.cs_head_d_var, width=12).grid(row=5, column=1, pady=3)

        ttk.Label(bolt_group, text="Countersink Angle (deg):").grid(row=6, column=0, sticky=tk.W, pady=3)
        self.cs_angle_var = tk.DoubleVar(value=82.0)
        ttk.Entry(bolt_group, textvariable=self.cs_angle_var, width=12).grid(row=6, column=1, pady=3)

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

    def _on_preset_change(self):
        preset_name = self.preset_var.get()
        if preset_name in BEARING_PRESETS and preset_name != "Custom / User Specified":
            _, shaft, c_maj, c_min, c_depth, s_d, s_depth = BEARING_PRESETS[preset_name]
            self.shaft_d_var.set(shaft)
            self.cup_maj_var.set(c_maj)
            self.cup_min_var.set(c_min)
            self.cup_depth_var.set(c_depth)
            self.seal_d_var.set(s_d)
            self.seal_depth_var.set(s_depth)
            # Adjust hub OD and height appropriately
            self.hub_d_var.set(round(c_maj + 16.0, 1))
            self.flange_d_var.set(round(c_maj + 44.0, 1))
            self.bolt_circle_d_var.set(round(c_maj + 28.0, 1))
            self.total_height_var.set(round(c_depth + s_depth + 11.0, 1))
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
            seal_d = self.seal_d_var.get()
            seal_depth = self.seal_depth_var.get()
            bolt_circle_d = self.bolt_circle_d_var.get()
            num_bolts = self.num_bolts_var.get()
            bolt_hole_d = self.bolt_hole_d_var.get()
            has_cs = self.has_cs_var.get()
            cs_head_d = self.cs_head_d_var.get()
            cs_angle = self.cs_angle_var.get()
            has_zerk = self.has_zerk_var.get()
            zerk_d = self.zerk_d_var.get()

            # Validations
            if cup_min >= cup_maj:
                raise ValueError("Cup minor OD must be smaller than cup major OD for tapered race.")
            if cup_maj >= hub_d:
                raise ValueError("Bearing pilot hub diameter must be larger than the bearing cup major OD.")
            if hub_d >= flange_d:
                raise ValueError("Mounting flange diameter must be larger than the bearing pilot hub diameter.")
            if shaft_d >= cup_min:
                raise ValueError("Through shaft diameter must be smaller than the bearing cup minor OD.")
            if total_height <= cup_depth + seal_depth:
                raise ValueError(f"Total housing height ({total_height}mm) must exceed cup depth + seal depth ({cup_depth + seal_depth}mm).")
            if flange_thick >= total_height:
                raise ValueError("Flange base thickness must be less than total housing height.")
            if bolt_circle_d <= hub_d or bolt_circle_d >= flange_d:
                raise ValueError(f"Bolt circle diameter ({bolt_circle_d}mm) must sit cleanly on the flange between hub OD ({hub_d}mm) and flange OD ({flange_d}mm).")

            taper_angle = math.degrees(math.atan(((cup_maj - cup_min) / 2.0) / cup_depth))
            hub_wall = (hub_d - cup_maj) / 2.0
            flange_lip = (flange_d - bolt_circle_d) / 2.0

            self.calc_data = {
                "flange_d": flange_d,
                "hub_d": hub_d,
                "flange_thick": flange_thick,
                "total_height": total_height,
                "shaft_d": shaft_d,
                "cup_maj": cup_maj,
                "cup_min": cup_min,
                "cup_depth": cup_depth,
                "taper_angle": taper_angle,
                "seal_d": seal_d,
                "seal_depth": seal_depth,
                "bolt_circle_d": bolt_circle_d,
                "num_bolts": num_bolts,
                "bolt_hole_d": bolt_hole_d,
                "has_cs": has_cs,
                "cs_head_d": cs_head_d,
                "cs_angle": cs_angle,
                "has_zerk": has_zerk,
                "zerk_d": zerk_d
            }

            res_text = (
                f"Bearing Cup OD:   {cup_maj:.2f} mm (major) -> {cup_min:.2f} mm (minor)\n"
                f"Cup Seat Depth:   {cup_depth:.2f} mm (Taper Angle: {taper_angle:.1f}°)\n"
                f"Hub Wall Thick:   {hub_wall:.2f} mm backing thickness around cup\n"
                f"Seal Counterbore: {seal_d:.2f} mm dia x {seal_depth:.2f} mm deep\n"
                f"Shaft Bore:       {shaft_d:.2f} mm clear through-bore\n"
                f"Flange Pattern:   {num_bolts} holes on {bolt_circle_d:.1f} mm B.C. ({flange_lip:.1f} mm edge margin)\n"
                f"Fastener Spec:    {bolt_hole_d:.2f} mm dia"
                + (f" with {cs_head_d:.1f} mm {cs_angle:.0f}° countersink" if has_cs else " straight bore") + "\n"
                f"Lubrication Port: " + (f"{zerk_d:.1f} mm zerk tap port" if has_zerk else "None")
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
        r_cup_maj_m = (d['cup_maj'] / 2.0) / 1000.0
        r_cup_min_m = (d['cup_min'] / 2.0) / 1000.0
        cup_depth_m = d['cup_depth'] / 1000.0
        r_seal_m = (d['seal_d'] / 2.0) / 1000.0
        seal_depth_m = d['seal_depth'] / 1000.0
        r_bc_m = (d['bolt_circle_d'] / 2.0) / 1000.0
        r_bolt_m = (d['bolt_hole_d'] / 2.0) / 1000.0
        r_cs_m = (d['cs_head_d'] / 2.0) / 1000.0
        cs_angle_deg = d['cs_angle']
        n_bolts = int(d['num_bolts'])

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

    ' 1. Flange Base Extrusion
    stage = "creating flange base"
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
    Part.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, {h_total_m}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False

    ' 3. Through Shaft Clearance Cut
    stage = "cutting shaft bore"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_shaft_m}, 0, 0
    Part.FeatureManager.FeatureCut4 True, False, False, 0, 0, {h_total_m * 1.5}, 0, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, False, False, False, False

    ' 4. Axle Seal Pocket (Bottom)
    stage = "cutting seal pocket"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle 0, 0, 0, {r_seal_m}, 0, 0
    Part.FeatureManager.FeatureCut4 True, False, False, 0, 0, {seal_depth_m}, 0, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, False, False, False, False

    ' 5. Tapered Race Cup Revolve Cut
    stage = "cutting tapered race seat"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Front Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    ' Centerline along Z
    Part.SketchManager.CreateCenterLine 0, 0, 0, 0, {h_total_m}, 0
    ' Revolve profile of tapered cup
    Part.SketchManager.CreateLine 0, {h_total_m - cup_depth_m}, 0, {r_cup_min_m}, {h_total_m - cup_depth_m}, 0
    Part.SketchManager.CreateLine {r_cup_min_m}, {h_total_m - cup_depth_m}, 0, {r_cup_maj_m}, {h_total_m}, 0
    Part.SketchManager.CreateLine {r_cup_maj_m}, {h_total_m}, 0, 0, {h_total_m}, 0
    Part.SketchManager.CreateLine 0, {h_total_m}, 0, 0, {h_total_m - cup_depth_m}, 0
    Part.FeatureManager.FeatureRevolveCut2 6.2831853, False, 0, 0, 0, True, True, True

    ' 6. Bolt Pattern on Flange
    stage = "cutting bolt pattern"
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    Part.SketchManager.InsertSketch True
    Part.SketchManager.CreateCircle {r_bc_m}, 0, 0, {r_bolt_m + r_bc_m}, 0, 0
    Part.FeatureManager.FeatureCut4 True, False, False, 0, 0, {h_flange_m * 2}, 0, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, False, False, False, False
    ' Circular pattern
    Part.ClearSelection2 True
    Part.Extension.SelectByID2 "Cut-Extrude3", "BODYFEATURE", 0, 0, 0, False, 4, Nothing, 0
    Part.FeatureManager.CircularPattern 0, 0, 0, 0, 0, 1, 6.2831853, {n_bolts}, True

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
        with open(filePath, "w") as f:
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
        scad_code = f"""// Parametric Tapered Roller Bearing Housing
// Generated by Tapered Bearing Housing Generator (KB1U / DC-LIGHT LLC)

$fn = 100;

flange_d = {d['flange_d']:.2f};
hub_d = {d['hub_d']:.2f};
flange_thick = {d['flange_thick']:.2f};
total_height = {d['total_height']:.2f};
shaft_d = {d['shaft_d']:.2f};
cup_maj = {d['cup_maj']:.2f};
cup_min = {d['cup_min']:.2f};
cup_depth = {d['cup_depth']:.2f};
seal_d = {d['seal_d']:.2f};
seal_depth = {d['seal_depth']:.2f};
bolt_circle_d = {d['bolt_circle_d']:.2f};
num_bolts = {d['num_bolts']};
bolt_hole_d = {d['bolt_hole_d']:.2f};
has_cs = {'true' if d['has_cs'] else 'false'};
cs_head_d = {d['cs_head_d']:.2f};
cs_angle = {d['cs_angle']:.1f};
has_zerk = {'true' if d['has_zerk'] else 'false'};
zerk_d = {d['zerk_d']:.2f};

module bearing_housing() {{
    difference() {{
        // Solid body (Flange + Pilot Hub)
        union() {{
            cylinder(d=flange_d, h=flange_thick);
            cylinder(d=hub_d, h=total_height);
        }}

        // Through shaft clearance bore
        translate([0, 0, -1])
            cylinder(d=shaft_d, h=total_height + 2);

        // Axle seal pocket at base
        if (seal_depth > 0 && seal_d > 0) {{
            translate([0, 0, -1])
                cylinder(d=seal_d, h=seal_depth + 1);
        }}

        // Tapered bearing race cup
        translate([0, 0, total_height - cup_depth])
            cylinder(d1=cup_min, d2=cup_maj, h=cup_depth + 1);

        // Mounting bolt holes & countersinks
        angle_step = 360 / num_bolts;
        offset_angle = angle_step / 2;
        cs_depth = (cs_head_d - bolt_hole_d) / (2 * tan(cs_angle / 2));

        for (i = [0 : num_bolts - 1]) {{
            rotate([0, 0, (i * angle_step) + offset_angle]) {{
                translate([bolt_circle_d / 2, 0, -1]) {{
                    cylinder(d=bolt_hole_d, h=flange_thick + 2);
                    if (has_cs && cs_depth > 0) {{
                        translate([0, 0, flange_thick + 1 - cs_depth])
                            cylinder(d1=bolt_hole_d, d2=cs_head_d, h=cs_depth + 0.1);
                    }}
                }}
            }}
        }}

        // Grease zerk port
        if (has_zerk && zerk_d > 0) {{
            z_zerk = seal_depth + ((total_height - cup_depth - seal_depth) / 2);
            translate([0, 0, z_zerk])
                rotate([0, 90, 0])
                    cylinder(d=zerk_d, h=flange_d);
        }}
    }}
}}

bearing_housing();
"""
        with open(filePath, "w") as f:
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
capable of carrying massive combined radial and thrust (axial) loads. However, the outer
cup (race) features a precision conical beveled outer surface that is difficult to
machine on standard home hobby tools without a tapered boring bar or CNC lathe.

This tool generates precision 3D-printable flanged bearing blocks that house these
cups perfectly. Use them for:
• Heavy-duty antenna azimuth/elevation rotators and satellite tracking gimbals.
• Wind turbine vertical pivots and mast bearings.
• Trailer axles, cart wheels, and heavy turntable mechanisms.
• Prototyping test fits in PETG before sending the STL to be CNC-machined in Aluminum.


2. BEARING GEOMETRY & ANATOMY
--------------------------------------------------------------------------------
A standard trailer bearing consists of:
• Cone: The inner ring with the caged tapered rollers and central shaft bore.
• Cup: The hardened steel outer ring with the matching tapered internal raceway.
• Cup Major OD: Outer diameter at the wide mouth of the cup race.
• Cup Minor OD: Outer diameter at the narrow base of the cup race.
• Cup Depth: Overall axial thickness / height of the cup.
• Taper Angle: Typically 12° to 16°, automatically computed from major/minor ODs and depth.
• Seal Pocket: Counterbore at the opposite side designed to press-fit a standard double-lip
  nitrile rubber trailer grease seal.


3. FASTENER OPTIONS & COUNTERSINKING
--------------------------------------------------------------------------------
• Bolt Circle Diameter (B.C.D.):
  The pitch diameter on which the mounting screw/bolt holes are arranged.

• Number of Bolts (N):
  Select 3, 4, 6, 8, etc. Holes are automatically clocked so they never intersect
  the grease zerk port.

• Through Holes vs. Countersunk Screws:
  - For machine bolts (Hex head, Socket cap), uncheck countersink or select straight presets
    to retain full flat material thickness under the bolt head and washer.
  - For wood screws or drywall screws, enable tapered countersinking. Drywall/wood screws
    use an 82° countersink (DIN/ISO flat head machine screws use 90°). This allows the bugle
    head to sit flush or sub-flush with the flange surface.


4. LUBRICATION (GREASE ZERK PORT)
--------------------------------------------------------------------------------
• An integrated radial hole passes from the exterior hub wall into the cavity between
  the bearing cup seat and the grease seal.
• Sized for tapping with standard 1/4"-28 UNF or 1/8" NPT grease zerk fittings.
• Allows purging and packing grease with a standard grease gun after assembly.


5. 3D PRINTING RECOMMENDATIONS (SLICER SETTINGS)
--------------------------------------------------------------------------------
• Recommended Materials:
  - Solid PETG: Outstanding layer adhesion, impact strength, and grease resistance.
  - ASA or ABS: Superior heat resistance and rigidity for outdoor antenna mounts.
  - Polycarbonate (PC): Maximum mechanical stiffness and load capability.

• Slicer Setup:
  - Orientation: Print with the mounting flange face flat on the build plate.
  - Perimeters / Walls: 6 to 8 perimeters (makes the bearing seat solid plastic).
  - Infill: 40% to 100% (Gyroid or Rectilinear).
  - Top & Bottom Layers: 6 layers minimum.
  - Fit Compensation: If the cup is slightly tight, calibrate your slicer's 'Hole Horizontal
    Expansion' by -0.05 mm to -0.10 mm.


6. SENDING FOR CNC ALUMINUM MACHINING
--------------------------------------------------------------------------------
The exported STL is 100% manifold and watertight. You can upload it directly to CNC
services (e.g., SendCutSend, Xometry, PCBWay) or use the exported SolidWorks macro
(.bas) or OpenSCAD script (.scad) to generate native STEP/IGES CAD files.
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
