# 3DPrint Tapered Bearing Housing Maker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Amateur Radio](https://img.shields.io/badge/Amateur%20Radio-KB1U-red.svg)]([https://www.qrz.com/](https://www.qrz.com/db/KB1U))

A parametric 3D CAD designer and instant **direct-to-STL exporter** for trailer and automotive tapered roller bearing housings.

Trailer axle bearings are inexpensive, heavy-duty, and carry massive combined radial and thrust loads. However, the outer cup race features a precision conical taper that is difficult to machine on hobby tools without complex lathe setups. 

This tool designs and directly outputs **100% watertight, manifold 3D-printable flanged bearing blocks** tailored for antenna rotators, azimuth/elevation gimbals, wind turbine pivots, and heavy mechanical shafts. Print them solid in PETG/ASA for direct use, or print a prototype test fit and upload the STL to CNC machine from Aluminum.

---

## Features

- **Direct 3D Printable STL Export**: Vectorized Continuous Signed Distance Fields (SDF) and VTK Flying Edges generate sub-millimeter, watertight manifold STLs with **0 open edges** in seconds.
- **Precision Tapered Cup Race Seat**: Automatically models the conical seat matching your bearing's major OD, minor OD, and cup depth.
- **Central Through-Bore**: Clean through-hole along the center axis for the rotating shaft or axle spindle.
- **Flange Outline Shapes (Round vs. Oval / 2-Bolt Oblong)**:
  - **Circular / Round (Standard N-Bolt)**: Symmetrical circular flange with circular bolt circle pattern ($N = 2$ to $16$).
  - **Oval / 2-Bolt Oblong (Narrow Mount)**: Capsule/stadium-shaped flange with 2 inline mounting bolt holes along the major axis and compact narrow width across the hub. Tailored for mounting onto narrow channels, box tubing, and tight gimbal brackets!
- **Flange On Either Side (Positive Bearing Retention)**:
  - **Bottom / Base (Standard Flange)**: Traditional flanged bearing block with the mounting flange at the base and the bearing cup mouth pointing upward.
  - **Top / Bearing Retaining Face**: Places the flange flush with the wide mouth of the bearing cup. When bolted against a flat plate, gimbal frame, or bulkhead, **the mounting surface directly captures and retains the bearing within the housing**, enabling secure operation on smooth unthreaded axles or pivots without requiring a castle nut or retaining clip!
- **Optional Grease / Oil Seal Counterbore**:
  - Toggle the bottom seal pocket on or off with a single click.
  - When disabled, creates an unobstructed continuous through-bore and automatically optimizes/compacts housing height.
- **Dual Cup Seat Geometry Provisions**:
  - **Cylindrical Press-Fit with Retaining Shoulder**: The standard way trailer hubs are built. The outer cup presses into a cylindrical bore and rests against an internal backing shoulder.
  - **Direct Conical Tapered Raceway**: Direct conical beveled seat for custom cone/roller seating or direct beveled cup support.
  - **Drift Punch Knock-Out Notches**: Dual opposing notches at the shoulder allowing a punch to be inserted from the seal side to remove the bearing cup for maintenance without damaging the housing.
- **Tapered Contact Angle ($\alpha$) Engineering**:
  - Direct entry and automatic bidirectional synchronization between Contact Angle ($\alpha$) and Cup Minor OD / Shoulder ID:
    $$\text{Cup Minor OD} = \text{Cup Major OD} - 2 \cdot \text{Cup Depth} \cdot \tan(\alpha)$$
  - Instant presets for **Standard Trailer Hubs** ($\alpha \approx 14^\circ$, $F_a / F_r \approx 0.25$) and **Steep-Angle High-Thrust** ($\alpha \approx 28^\circ$, $F_a / F_r \approx 0.53$).
  - Dynamic display of the dynamic thrust-to-radial capacity ratio $F_a / F_r = \tan(\alpha)$.
- **N-Hole Flange Bolt Pattern & Directional Countersinks**:
  - Configurable number of bolts ($N = 2$ to $16$) on a circular pitch diameter (B.C.D.).
  - Automatic hole clocking so bolts never intersect the lubrication port or knock-out notches.
  - **Straight Through-Bores**: Retains full flange material thickness under hex bolt heads and heavy washers.
  - **Directional Countersinking**: Choose whether screw heads sit on the **Accessible Hub Shoulder** (driven into the mounting surface) or the **Mounting Face** (sub-flush screws).
- **Additive Manufacturing Hole-Shrinkage Compensation**:
  - Direct parameter for **Bearing Seat Fit / Shrink Offset** ($0.00\text{ mm}$ for CNC Aluminum up to $+0.20\text{ mm}$ for loose fit).
  - Compensates for thermoplastic shrinkage and polygon chordal segmentation during cooling so hardened steel cups press in cleanly without binding.
- **Grease Zerk Fitting Port**: Radial threaded tap hole entering the cavity below the bearing cup race for standard $1/4\text{"-28}$ or $1/8\text{" NPT}$ grease zerks.
- **Interactive 3D Preview**:
  - Studio 3-point lighting and shadow mapping.
  - Gimbal-lock-free turntable orbit (Left-Click Drag), pan (Middle/Shift Drag), and zoom (Right-Click Drag or Scroll).
  - Tapered rollers rendered tilted inward at the exact contact angle $\alpha$.
  - 3 Display Modes: **Housing + Bearing Assembly**, **Housing Only (STL)**, and **Cross-Section View** (clips the housing in half to inspect internal tapers, shoulder stops, and channels).
- **Multi-CAD Compatibility**: Exports production **STL**, **OpenSCAD (`.scad`)**, and **SolidWorks VBA Macro (`.bas`)**.

---

## Standard Bearing Presets Included (From 8 mm to 2.50" / 63.5 mm)

| Spindle / Axle Size | Bearing Cone | Cup Race | Cup Major OD | Contact Angle ($\alpha$) | Seal OD | Application / Rating |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$8\text{ mm}$ ($5/16\text{"}$)** | **608 / 608-2RS** | **Deep-Groove** | $22.00\text{ mm}$ ($0.866\text{"}$) | $0.0^\circ$ | $22.00\text{ mm}$ | **Skateboard, rollerblade, 3D printer & robot pivots** |
| **$8\text{ mm}$ Dual Hub** | **Dual 608-2RS** | **Pair** | $22.00\text{ mm}$ ($0.866\text{"}$) | $0.0^\circ$ | $22.00\text{ mm}$ | **Skateboard dual-bearing hub arrangement ($14\text{ mm}$ depth)** |
| **$0.750\text{"}$ ($3/4\text{"}$)** | **LM11949** | **LM11910** | $45.24\text{ mm}$ ($1.781\text{"}$) | $14.0^\circ$ | $45.24\text{ mm}$ | 1000–1500 lb light trailers, carts, light rotators |
| **$1.000\text{"}$ ($1\text{"}$)** | **L44643** | **L44610** | $50.29\text{ mm}$ ($1.980\text{"}$) | $14.0^\circ$ | $50.29\text{ mm}$ | 2000 lb straight BT8 trailer spindle |
| **$1.063\text{"}$ ($1\text{-}1/16\text{"}$)** | **L44649** | **L44610** | $50.29\text{ mm}$ ($1.980\text{"}$) | $14.0^\circ$ | $50.29\text{ mm}$ | Common 2000–2200 lb trailer axle outer/inner |
| **$1.250\text{"}$ ($1\text{-}1/4\text{"}$)** | **LM67048** | **LM67010** | $59.13\text{ mm}$ ($2.328\text{"}$) | $13.6^\circ$ | $59.13\text{ mm}$ | Common 3500–4400 lb axle outer bearing |
| **$1.375\text{"}$ ($1\text{-}3/8\text{"}$)** | **L68149** | **L68111** | $59.97\text{ mm}$ ($2.361\text{"}$) | $14.2^\circ$ | $65.00\text{ mm}$ | Standard 3500 lb Dexter #84 inner (10-19 seal) |
| **$1.500\text{"}$ ($1\text{-}1/2\text{"}$)** | **LM29749** | **LM29710** | $65.09\text{ mm}$ ($2.563\text{"}$) | $14.0^\circ$ | $65.09\text{ mm}$ | 4400–5200 lb trailer axle outer bearing |
| **$1.500\text{"}$ ($1\text{-}1/2\text{"}$)** | **15123** | **15245** | $62.00\text{ mm}$ ($2.441\text{"}$) | $13.5^\circ$ | $65.00\text{ mm}$ | Popular 5200 lb trailer axle outer bearing |
| **$1.625\text{"}$ ($1\text{-}5/8\text{"}$)** | **14125A** | **14276** | $69.01\text{ mm}$ ($2.717\text{"}$) | $14.0^\circ$ | $69.01\text{ mm}$ | 6000–7000 lb trailer axle outer bearing |
| **$1.750\text{"}$ ($1\text{-}3/4\text{"}$)** | **25580** | **25520** | $83.06\text{ mm}$ ($3.270\text{"}$) | $14.4^\circ$ | $85.75\text{ mm}$ | Standard 5200–7000 lb Dexter #42 inner (10-36 seal) |
| **$1.875\text{"}$ ($1\text{-}7/8\text{"}$)** | **25877** | **25821** | $73.03\text{ mm}$ ($2.875\text{"}$) | $13.4^\circ$ | $85.75\text{ mm}$ | Heavy utility, farm & industrial spindle |
| **$2.000\text{"}$ ($2\text{"}$)** | **28580** | **28521** | $92.08\text{ mm}$ ($3.625\text{"}$) | $14.3^\circ$ | $98.55\text{ mm}$ | **8,000–10,000 lb heavy trailer axle (Dexter/Lippert 8K)** |
| **$2.125\text{"}$ ($2\text{-}1/8\text{"}$)** | **387AS** | **382A** | $96.85\text{ mm}$ ($3.813\text{"}$) | $14.3^\circ$ | $98.55\text{ mm}$ | Heavy commercial 8K–10K trailer axle |
| **$2.250\text{"}$ ($2\text{-}1/4\text{"}$)** | **387A** | **382A** | $96.85\text{ mm}$ ($3.813\text{"}$) | $14.3^\circ$ | $104.78\text{ mm}$ | Standard 9,000–10,000 lb general duty axle |
| **$2.500\text{"}$ ($2\text{-}1/2\text{"}$)** | **3984** | **3920** | $112.71\text{ mm}$ ($4.438\text{"}$) | $14.2^\circ$ | $114.30\text{ mm}$ | Extra heavy-duty 10,000–12,000 lb dual-wheel axle |
| **$1.375\text{"}$ Steep Thrust** | Custom | Custom | $65.00\text{ mm}$ | **$28.0^\circ$** | $65.00\text{ mm}$ | High-thrust antenna rotators & vertical mast pivots |
| **$2.000\text{"}$ Steep Thrust** | Custom | Custom | $95.00\text{ mm}$ | **$28.0^\circ$** | $98.55\text{ mm}$ | Heavy-duty antenna arrays & satellite dishes |
| **$20\text{ mm}$ to $50\text{ mm}$ Metric** | **30204–30210** | ISO Metric | $47\text{ mm}$ to $90\text{ mm}$ | $13.8^\circ–14.2^\circ$ | $47\text{ mm}$ to $90\text{ mm}$ | Standard ISO metric tapered roller series |
| **Custom** | User-defined | User-defined | Any | Any | Any | Fully custom dimensions & angles |

---

## Installation & Running

### 1. Requirements
Python 3.10+ with standard scientific packages:
```bash
pip install -r requirements.txt
```

### 2. Launch
```bash
python 3DPrint_Bearing_Housing.py
```

---

## 3D Printing Recommendations

| Parameter | Recommended Setting |
| :--- | :--- |
| **Material** | **PETG**, **ASA**, or **ABS** (High grease resistance, toughness, and thermal stability). |
| **Orientation** | **Flange base or flat bearing face flat on build plate**. Zero support required! |
| **Perimeters / Walls** | **6 to 8 walls** (ensures 100% solid plastic behind the bearing seat). |
| **Infill** | **50% – 100% Gyroid or Rectilinear**. |
| **Bearing Seat Offset** | Set **`+0.10 mm` to `+0.15 mm`** in the app to compensate for hole shrinkage so your steel bearing cup presses in snug without binding. Use **`0.00 mm`** for CNC machining. |

---

## ⚠️ Safety Advisory: "Don't Shoot Your Eye Out" / Force & Load Limitations

A 3D-printed bearing holder is **wildly useful in the right application**. It is ideal for test fitting, alignment verification, prototyping, amateur radio antenna rotators, satellite tracking gimbals, manual pivots, solar trackers, robot arms, and low-speed turntables. It is also an invaluable, inexpensive test case before sending exported CAD files to a machine shop to mill out of 6061-T6 Aluminum.

**HOWEVER, HEED THIS CRUCIAL WARNING:**
Bearings are frequently used in mechanical systems with **tons of torque, high RPMs, enormous rotational inertia, and massive dynamic thrust forces** that could easily overwhelm, shear, or crack a 3D-printed plastic bearing retainer.

> **THIS TOOL DOES NOT JUDGE SAFETY — IT JUST MAKES BEARING HOLDERS.**

### Key Physical Limitations of Thermoplastic 3D Prints:
1. **Inter-Layer Delamination**: 3D prints are anisotropic. Tensile or bending loads trying to pull the bearing or flange apart place layer lines under tension, which are inherently weaker than solid molded or machined metal.
2. **Viscoelastic Creep**: Thermoplastics (especially PLA and PETG) slowly deform under sustained mechanical preload. A bearing preloaded tightly today will loosen or lose axial alignment over weeks of constant tension.
3. **Frictional Heating & Thermal Softening**: Rolling elements generate heat. While steel bearings easily run at $80^\circ\text{C}$–$120^\circ\text{C}$, PLA softens at $55^\circ\text{C}$, PETG at $75^\circ\text{C}$, and ABS at $95^\circ\text{C}$. High-RPM friction conducting into plastic can cause rapid bore softening and failure.
4. **Dynamic Shock & Gyroscopic Forces**: Rotating masses, wind gusts on tall masts, or road shocks generate peak forces $5\times$ to $10\times$ higher than static weight, risking sudden brittle catastrophic failure.

### Prudent Engineering Guidelines:
- **DO** use 3D prints for slow rotators, gimbals, test fixtures, prototyping, and low-risk pivots.
- **DO** use captive flange orientation (flange on bearing side) where the mounting bulkhead provides a solid metal barrier trapping the bearing inside.
- **NEVER** use 3D-printed bearing holders for highway trailers, passenger vehicles, overhead suspension, high-RPM shafts, human-carrying equipment, or any setup where structural failure could cause personal injury, falling hazards, or property damage.
- **When in doubt**, prototype in PETG/ASA first, then use the exported SolidWorks VBA macro (`.bas`) or STL to have the housing CNC machined from 6061-T6 Aluminum.

---

## Author & License

- **Author**: Andrew Freeston / **KB1U** / DC-LIGHT LLC
- **License**: [MIT License](LICENSE)
