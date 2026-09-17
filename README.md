# Head Animation OpenGL

A procedural 3D head animation built with Python and OpenGL for a Computer Graphics assignment at Escola Politécnica da PUCRS. The project loads a Wavefront `.obj` head model, animates a sequence of rotations and a fall, and then transforms the model into particles that bounce, rise in a spiral, regroup, compress, and explode with random colors.

## Features

- Wavefront OBJ loading for the included `Human_Head.obj` model.
- Real-time OpenGL rendering with lighting, depth testing, and face culling.
- Procedural head rotation using interpolated keyframes.
- Vertical movement followed by a gravity-based fall.
- Vertex-based particle simulation with:
  - Falling and bouncing particles.
  - Spiral formation.
  - Smooth regrouping into the original head shape.
  - Compression toward a central point.
  - Randomized colored explosion.
- Interactive camera movement and animation pause/play controls.

## Project structure

```text
T2 (2)/
├── Human_Head.obj  # 3D head model
├── Linha.py        # Line-related helpers
├── Objeto3D.py     # OBJ loading and OpenGL object rendering
├── Particle.py     # Particle behavior and animation phases
├── Ponto.py        # 3D point and rotation utilities
└── main.py         # Application entry point and animation loop
```

## Requirements

- Python 3
- An OpenGL-capable graphics environment
- PyOpenGL
- A GLUT implementation, such as FreeGLUT

Install the Python dependencies with:

```bash
python -m pip install PyOpenGL PyOpenGL_accelerate
```

You may also need to install FreeGLUT through your operating system's package manager. For example, on Debian or Ubuntu:

```bash
sudo apt-get install freeglut3-dev
```

## Running the animation

The model path is relative to the directory containing `main.py`, so run the application from `T2 (2)`:

```bash
cd "T2 (2)"
python main.py
```

A window opens with the head model rendered over a tiled floor. Press `p` to start the animation sequence.

## Controls

| Key | Action |
| --- | --- |
| `p` | Start the head rotation animation |
| `Space` | Pause or resume the animation |
| `w` / `s` | Move the camera forward / backward |
| `a` / `d` | Move the camera right / left |
| `q` / `e` | Move the camera up / down |

## Animation sequence

1. The head interpolates through a predefined set of rotations.
2. It rises and then falls under simulated gravity.
3. After impact, the model's vertices become independent particles.
4. The particles bounce and form a rising spiral.
5. The particles regroup into the original head shape.
6. The head compresses toward the center and ends in a colored particle explosion.

## Notes

- The project uses the fixed-function OpenGL API through `OpenGL.GL`, `OpenGL.GLU`, and `OpenGL.GLUT`.
- The included model is loaded at runtime from `Human_Head.obj`; keep the model and Python files together.
- Particle motion includes randomized values, so some details of the animation vary between runs.

## Authors

- Breno Spohr
- Thomaz Abrantes

Created for the Computer Graphics course at Escola Politécnica da PUCRS (2025/1).
