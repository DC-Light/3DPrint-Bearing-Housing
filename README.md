# 3DPrint Tapered Bearing Housing Maker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Amateur Radio](https://img.shields.io/badge/Amateur%20Radio-KB1U-red.svg)](https://www.qrz.com/)

A parametric 3D CAD designer and instant **direct-to-STL exporter** for trailer and automotive tapered roller bearing housings.

Trailer axle bearings are inexpensive, heavy-duty, and carry massive combined radial and thrust loads. However, the outer cup race features a precision conical taper that is difficult to machine on hobby tools without complex lathe setups. 

This tool designs and directly outputs **100% watertight, manifold 3D-printable flanged bearing blocks** tailored for antenna rotators, azimuth/elevation gimbals, wind turbine pivots, and heavy mechanical shafts. Print them solid in PETG/ASA for direct use, or print a prototype test fit and upload the STL to CNC machine from Aluminum.

---

## Features

- **Direct 3D Printable STL Export**: Vectorized Continuous Signed Distance Fields (SDF) and VTK Flying Edges generate sub-millimeter, watertight manifold STLs with **0 open edges** in seconds.
- **Precision Tapered Cup Race Seat**: Automatically models the conical seat matching your bearing's major OD, minor OD, and cup depth.
- **Central Through-Bore**: Clean through-hole along the center axis for the rotating shaft or axle spindle.
- **Grease / Oil Seal Counterbore**: Sized for press-fitting standard double-lip trailer grease seals.
- **N-Hole Flange Bolt Pattern**:
  - Configurable number of bolts ($N = 2$ to $16$).
  - Circular bolt pitch diameter (B.C.D.).
  - Automatic hole clocking so bolts never intersect the lubrication port.
- **Through-Holes & Tapered Countersinks**:
  - **Straight Through-Bores**: Retains full flange material thickness under hex bolt heads and heavy washers.
  - **Tapered Countersinking**: Designed for bugle-head wood screws and drywall screws ($82^\circ$) or ISO machine screws ($90^\circ$).
- **Grease Zerk Fitting Port**: Radial threaded tap hole entering between the seal and cup race for standard $1/4\text{"-28}$ or $1/8\text{" NPT}$ grease zerks.
- **Interactive 3D Preview**:
  - Studio 3-point lighting and shadow mapping.
  - Gimbal-lock-free turntable orbit (Left-Click Drag), pan (Middle/Shift Drag), and zoom (Right-Click Drag or Scroll).
  - 3 Display Modes: **Housing + Bearing Assembly**, **Housing Only (STL)**, and **Cross-Section View** (clips the housing in half to inspect internal tapers and channels).
- **Multi-CAD Compatibility**: Exports production **STL**, **OpenSCAD (`.scad`)**, and **SolidWorks VBA Macro (`.bas`)**.

---

## Standard Bearing Presets Included

| Spindle / Axle Size | Bearing Cone | Cup Race | Cup Major OD | Cup Minor OD | Seal OD |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$1.063\text{"}$ ($1\text{-}1/16\text{"}$)** | **L44649** | **L44610** | $50.29\text{ mm}$ ($1.980\text{"}$) | $45.20\text{ mm}$ | $50.29\text{ mm}$ |
| **$1.250\text{"}$ ($1\text{-}1/4\text{"}$)** | **LM67048** | **LM67010** | $59.13\text{ mm}$ ($2.328\text{"}$) | $53.00\text{ mm}$ | $59.13\text{ mm}$ |
| **$1.375\text{"}$ ($1\text{-}3/8\text{"}$)** | **L68149** | **L68111** | $59.97\text{ mm}$ ($2.361\text{"}$) | $54.00\text{ mm}$ | $65.00\text{ mm}$ |
| **$1.750\text{"}$ ($1\text{-}3/4\text{"}$)** | **25580** | **25520** | $83.06\text{ mm}$ ($3.270\text{"}$) | $75.00\text{ mm}$ | $85.00\text{ mm}$ |
| **Custom** | User-defined | User-defined | Any | Any | Any |

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
| **Material** | **PETG**, **ASA**, or **ABS** (High grease resistance and mechanical toughness). |
| **Orientation** | **Flange base flat on the build plate**. No supports required! |
| **Perimeters / Walls** | **6 to 8 walls** (ensures solid plastic behind the tapered cup seat). |
| **Infill** | **40% – 100% Gyroid**. |
| **Fit Calibration** | If the cup fits slightly tight, set slicer **Hole Horizontal Expansion** to $-0.05\text{ mm}$ to $-0.10\text{ mm}$. |

---

## Author & License

- **Author**: Andrew Freeston / **KB1U** / DC-LIGHT LLC
- **License**: [MIT License](LICENSE)
