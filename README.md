🌌 🎮 Key Features for the Project
Your project could go beyond basic starfields and evolve into a fully interactive 3D-style Pygame scene. Some core elements might be:

-	✅ 3D starfield with movement & depth
-	✅ 3D planet and moon rotation (simulate spheres)
-	✅ Camera movement (move forward, backward, look around)
-	✅ User controls for exploration (WASD to navigate, mouse to look)
-	✅ Dynamic lighting (basic shading effects)
-	✅ Comet trails & particle effects
-	✅ Asteroid belt with rotating rocks
-	✅ Scalable “hyperspace jump” effect
-	✅ Smooth frame rates with delta time


------

# Project Starflight: Hyperspace Initiative

## Overview
This project is a progressive series of Python programs that simulate 3D space scenes using Pygame. The project evolves from simple 3D starfields and rotating cubes to a sophisticated interactive space simulation with sound, particle effects, and multiple 3D objects. Each file represents a stage in the development, adding new features and complexity.

## Project Structure

- **square.py**: The starting point. Renders a 3D starfield and a single rotating cube using Pygame. Demonstrates basic 3D projection and animation.
![image](https://github.com/user-attachments/assets/084b0e1c-103b-497c-90b4-874fc792bdec)
![image](https://github.com/user-attachments/assets/e6d4247a-ce64-4371-910d-aa2613c94098)

---

- **square2.py**: Adds a rotating 3D square alongside the cube, with improved projection and visual separation. Both shapes rotate independently, and the starfield remains as a background.
![image](https://github.com/user-attachments/assets/aa4e7c1a-a880-4ff5-9a46-bbd3e2ff26fa)
![image](https://github.com/user-attachments/assets/3f161362-7860-4f6b-8c13-34a246273932)

---

- **square3.py**: Introduces user interaction. The cube and square can be rotated and scaled using keyboard controls. The code is refactored for better color management and usability.
![image](https://github.com/user-attachments/assets/744f4da8-d347-4e9a-a95f-a9c233a5d558)
![image](https://github.com/user-attachments/assets/681ae006-aded-47fb-8fd7-59b7359f8f2d)
![image](https://github.com/user-attachments/assets/f3a98c3f-9f65-4530-81a7-bc6caab4e7f2)

---

- **square4.py**: Enhances the scene with a denser starfield, a fog effect, and a 3D ground plane grid. The cube and square now have lighting and perspective improvements. The code structure is more modular, and visual effects are richer.
![image](https://github.com/user-attachments/assets/f39956f6-4ae1-4ee9-969a-5f126b339ed6)
![image](https://github.com/user-attachments/assets/b3c81d34-2a6c-4b36-8dc0-ff89bbb8373d)

---

- **square5.py**: Major expansion. Adds a class-based architecture for 3D objects, including cubes, pyramids, and a spaceship model. Introduces a particle system for effects like engine trails. The starfield and ground plane are more immersive, and the camera system is more advanced.
![image](https://github.com/user-attachments/assets/64a74f2e-8b03-45d0-8e69-8c000dd8a470)
![image](https://github.com/user-attachments/assets/76debebe-8d03-4f9c-8948-87854cdbc378)

---

- **square6.py**: Further expands the simulation with asteroids and nebula clouds. The world is larger, the starfield is denser, and the particle and object systems are more robust. The code supports more complex 3D scenes and interactions.
![image](https://github.com/user-attachments/assets/07f8b565-6081-476e-887f-5f32aedf7ed6)
![image](https://github.com/user-attachments/assets/62b7466a-fe35-4f33-bee5-592c582f9608)
![image](https://github.com/user-attachments/assets/3eb65ca6-c969-4840-9653-14bcdaa147f9)

---

- **square7.py**: The most advanced version. Adds sound effects (engine hum, warp activation, impacts) and a targeting system. The simulation includes all previous features: stars, ground plane, 3D objects, asteroids, nebulae, and particles. The code is highly modular and demonstrates advanced Pygame and 3D programming techniques.
![image](https://github.com/user-attachments/assets/6464fe76-6667-40b2-ae42-3967687978f9)
![image](https://github.com/user-attachments/assets/2f556cab-c546-4dc1-aa47-3ca4fc885656)
![image](https://github.com/user-attachments/assets/ba081112-1b96-4f10-acb7-713d04549689)
![image](https://github.com/user-attachments/assets/acf9f2ad-3acd-4f58-bab8-0aa612618602)
![image](https://github.com/user-attachments/assets/159077cb-399c-4d8c-8420-fc16bcf310f6)
![image](https://github.com/user-attachments/assets/849d8de3-e5ae-4853-9dbd-66695b1d3236)
![image](https://github.com/user-attachments/assets/d733ee82-05fe-4a02-bf54-5abaf5818186)
![image](https://github.com/user-attachments/assets/44140f50-fd70-4ff4-bb20-d3863941040d)
![image](https://github.com/user-attachments/assets/ebbc6cb1-9da6-4f42-8822-71e29b93c4a3)
![image](https://github.com/user-attachments/assets/ad962b3f-673d-4876-8448-876ab053f31e)

- **sounds/**: Contains sound assets used in the latest version:
  - `engine_hum.ogg`: Background engine hum sound.
  - `warp_activate.ogg`: Sound effect for warp activation.
  - `impact.ogg`: Sound effect for impacts or collisions.

- **python project.docx**: (Not directly readable here) Presumably contains project documentation, planning, or a report.

- **200**: Empty or placeholder file.

## How to Run
1. Install Python 3.x and Pygame:
   ```bash
   pip install pygame
   ```
2. Run any of the Python files (e.g., `python square7.py`) to see the corresponding version of the simulation.
3. For full experience (in `square7.py`), ensure the `sounds/` directory is present with the required `.ogg` files.

## Controls (in advanced versions)
- Arrow keys: Rotate objects
- W/S: Scale objects
- ESC: Quit
- Additional controls may be present in later versions (see code comments).

## Evolution
This project demonstrates the step-by-step evolution of a 3D space simulation in Python, starting from basic graphics to a feature-rich, interactive, and audiovisual experience. Each file builds upon the previous, showcasing new programming concepts and techniques.

---

*Created as a learning and demonstration project for 3D graphics, Pygame, and Python programming.* 
