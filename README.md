# Random Projects

A collection of small standalone Python scripts — each file is a self-contained 
experiment or utility.

---

## Projects

### `BarcodeReading.py`
Reads barcodes directly from a USB barcode scanner by interfacing with the 
device at the USB level using `pyusb`, bypassing the need for camera input.

**Deps:** pyusb

---

### `ProjectorTopCompression.py`
Corrects projector distortion using OpenGL. Applies vertical keystone 
correction and compresses the top of the image via per-corner scale factors, 
adjustable in real time with keyboard input. Runs fullscreen.

**Deps:** pygame, PyOpenGL, numpy, opencv-python

---

### `PumpDesignMath.py`
Calculates pump specifications needed to compress nitrogen to liquid state. 
Sweeps across pipe radius (1–100mm), power (0.1–20kW), and RPM (500–5000) 
to find viable configurations given target pressure and chamber geometry.

**Deps:** math (stdlib)

---

### `rasterizer.py`
A software rasterizer built from scratch. Implements a vec3 type, camera with 
pitch/yaw, and triangle rendering pipeline using OpenGL as a display backend.

**Deps:** pygame, PyOpenGL, ctypes (stdlib)

---

### `raycaster.py`
A Wolfenstein-style raycasting engine with a 16×16 tile map, multiprocessing 
for ray batch rendering, and a Pygame display loop.

**Deps:** pygame, multiprocessing (stdlib)

---

## Running

Each script is standalone. Install dependencies as needed:

```bash
pip install pygame PyOpenGL numpy opencv-python pyusb
```
