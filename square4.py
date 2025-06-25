import pygame
import random
import math
import time

# Screen setup
WIDTH, HEIGHT = 800, 600
NUM_STARS = 200  # Increased number of stars for a denser field
FOG_COLOR = (10, 10, 30) # A dark blue/purple for a space-like fog

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced 3D Scene") # Set window title
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
LIGHT_GREY = (180, 180, 180)
DARK_GREY = (50, 50, 50)
BLUE = (0, 150, 255)
GREEN = (0, 255, 100)
RED = (255, 50, 50)
YELLOW = (255, 200, 0)

class Star:
    def __init__(self):
        # Initial positions adjusted for a more spread-out starfield
        self.x = random.uniform(-WIDTH, WIDTH)
        self.y = random.uniform(-HEIGHT, HEIGHT)
        self.z = random.uniform(1, 1500) # Deeper Z-range for more depth
        self.initial_size = random.uniform(1, 3)
        self.color = random.choice([WHITE, LIGHT_GREY]) # Varied star colors

    def update(self, speed_multiplier=1.0):
        self.z -= 5 * speed_multiplier # Make stars move faster
        if self.z < 1:
            self.z = 1500 # Reset Z to the far end
            self.x = random.uniform(-WIDTH, WIDTH)
            self.y = random.uniform(-HEIGHT, HEIGHT)
            self.initial_size = random.uniform(1, 3) # Reset size for new star

    def project(self, win):
        # Perspective factor for projection. Increased 'focal length' for more dramatic perspective
        projection_strength = 300
        factor = projection_strength / (projection_strength - self.z + 0.001)

        x = self.x * factor + WIDTH // 2
        y = self.y * factor + HEIGHT // 2
        size = self.initial_size * factor

        # Draw stars only if they are within the screen bounds and have a visible size
        if 0 < x < WIDTH and 0 < y < HEIGHT and size > 0.5:
            # Add a slight fade effect based on distance
            alpha = max(0, min(255, int(255 * (self.z / projection_strength) * 2)))
            star_color = (self.color[0], self.color[1], self.color[2], 255 - alpha) # Apply alpha

            # Draw a circle for a softer star look
            pygame.draw.circle(win, star_color, (int(x), int(y)), int(size / 2))


def draw_ground_plane(win, camera_y_offset):
    # draw a grid that looks like a ground plane
    num_lines = 30 # More lines for a denser grid
    spacing = 40
    perspective_offset = 200 # Adjust this to control the perspective distortion
    horizon_y = HEIGHT // 2 + camera_y_offset

    for i in range(-num_lines, num_lines + 1):
        # Vertical lines (extend further back, fade with distance)
        # Calculate color based on distance from camera (further lines are darker)
        # The 'abs(i)' in the original gave a symmetric color, here we want a linear fade
        color_val = max(30, 80 - int(abs(i) * 1.5)) # Darken lines further from center
        line_color = (color_val, color_val, color_val + 20) # Slight blue tint

        # Vertical lines
        x1_vert = WIDTH // 2 + i * spacing
        y1_vert = horizon_y
        y2_vert = HEIGHT

        # Horizontal lines (fade with distance as they go up towards the horizon)
        # We need to project these lines based on Z-depth for correct perspective
        for j in range(0, num_lines + 1):
            z_depth = j * spacing * 2 # Represents distance into the plane
            factor = perspective_offset / (perspective_offset + z_depth + 0.001)
            y_proj = horizon_y + (j * spacing * 0.5) * factor # Vertical compression

            if y_proj < HEIGHT:
                line_color_h_val = max(20, 100 - int(j * 4)) # Fade horizontal lines
                line_color_h = (line_color_h_val, line_color_h_val + 10, line_color_h_val + 30)

                pygame.draw.line(win, line_color_h, (0, int(y_proj)), (WIDTH, int(y_proj)), 1)

        # Draw vertical lines over the horizontal ones to ensure they're always visible
        pygame.draw.line(win, line_color, (x1_vert, int(y1_vert)), (x1_vert, y2_vert), 1)


def rotate_point_3d(point, angle_x, angle_y, angle_z):
    x, y, z = point
    # Rotate around X-axis
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
    # Rotate around Y-axis
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x, z = x * cos_y - z * sin_y, x * sin_y + z * cos_y
    # Rotate around Z-axis
    cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
    x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
    return x, y, z

def project_point(point, projection_center_x, projection_center_y, camera_z=200):
    x, y, z = point
    factor = camera_z / (camera_z - z + 0.001)
    return (x * factor + projection_center_x, y * factor + projection_center_y)

def draw_3d_square(win, angle_x, angle_y, angle_z, scale, offset_x, offset_y, offset_z, camera_z):
    size = 60 * scale
    points = [
        [-size, -size, 0], [size, -size, 0], [size, size, 0], [-size, size, 0]
    ]
    
    # Apply offset to points
    points = [(p[0] + offset_x, p[1] + offset_y, p[2] + offset_z) for p in points]

    projected = []
    for p in points:
        rotated_p = rotate_point_3d(p, angle_x, angle_y, angle_z)
        projected.append(project_point(rotated_p, WIDTH // 2 - 200, HEIGHT // 2, camera_z))

    # Add a simple lighting effect based on orientation
    # For a square, we can approximate a 'normal' by looking at the average Z of points
    avg_z = sum(p[2] for p in points) / len(points)
    light_intensity = max(0.2, min(1.0, (camera_z - avg_z) / camera_z)) # Brighter closer
    square_color = (int(200 * light_intensity), int(200 * light_intensity), int(0 * light_intensity)) # Yellow base

    if len(projected) == 4:
        pygame.draw.polygon(win, square_color, projected, 0)  # filled yellow
        pygame.draw.lines(win, (0, 0, 0), True, projected, 2)  # border

def draw_3d_cube(win, angle_x, angle_y, angle_z, scale, offset_x, offset_y, offset_z, camera_z):
    size = 100 * scale
    vertices = [
        [-size, -size, -size], [ size, -size, -size], [ size, size, -size], [-size, size, -size],
        [-size, -size, size], [ size, -size, size], [ size, size, size], [-size, size, size]
    ]

    # Apply offset to vertices
    vertices = [(v[0] + offset_x, v[1] + offset_y, v[2] + offset_z) for v in vertices]

    projected = []
    for v in vertices:
        rotated_v = rotate_point_3d(v, angle_x, angle_y, angle_z)
        projected.append(project_point(rotated_v, WIDTH // 2 + 200, HEIGHT // 2, camera_z))

    faces = [
        (0,1,2,3), # Front
        (4,5,6,7), # Back
        (0,1,5,4), # Bottom
        (2,3,7,6), # Top
        (1,2,6,5), # Right
        (0,3,7,4), # Left
    ]
    
    # Define colors for each face for better visual distinction
    colors = [
        (0, 200, 255), # Cyan
        (0, 180, 220), # Darker Cyan
        (0, 160, 200), # Even darker Cyan
        (0, 140, 180), # Blue-ish
        (0, 120, 160), # Even more blue
        (0, 100, 140)  # Darkest blue
    ]

    # Sort faces by average Z-depth to ensure correct drawing order (painter's algorithm)
    # This is a basic form of back-face culling/sorting and can have issues with complex shapes.
    face_z_values = []
    for i, face in enumerate(faces):
        avg_z = sum(vertices[v_idx][2] for v_idx in face) / len(face)
        face_z_values.append((avg_z, i))
    
    face_z_values.sort(key=lambda x: x[0], reverse=True) # Sort from furthest to closest

    for avg_z, face_idx in face_z_values:
        face = faces[face_idx]
        color = colors[face_idx]
        
        # Calculate lighting based on the face's normal (approximate)
        # This is very simplified, a proper normal calculation would be better
        # For a cube, we can use the average z of the face's vertices
        
        # Determine a color modifier based on light source (e.g., from top-left)
        # This is a highly simplified diffuse lighting model
        light_source = (1, 1, 1) # Example light direction
        
        # Calculate a rough face normal (only works for axis-aligned faces)
        # For a more robust solution, you'd need cross products of edge vectors
        normal_x, normal_y, normal_z = 0, 0, 0
        if face_idx == 0: normal_z = -1 # Front face
        elif face_idx == 1: normal_z = 1 # Back face
        elif face_idx == 2: normal_y = -1 # Bottom face
        elif face_idx == 3: normal_y = 1 # Top face
        elif face_idx == 4: normal_x = 1 # Right face
        elif face_idx == 5: normal_x = -1 # Left face

        dot_product = normal_x * light_source[0] + normal_y * light_source[1] + normal_z * light_source[2]
        
        # Clamp to 0-1 range and ensure minimum brightness
        light_factor = max(0.3, dot_product) 
        
        # Apply lighting to color
        lit_color = (int(color[0] * light_factor), int(color[1] * light_factor), int(color[2] * light_factor))

        if all(0 <= p[0] < WIDTH and 0 <= p[1] < HEIGHT for p in [projected[i] for i in face]): # Only draw if visible
            pygame.draw.polygon(win, lit_color, [projected[i] for i in face])
            pygame.draw.lines(win, (0, 0, 0), True, [projected[i] for i in face], 1) # Thin black border

def main():
    stars = [Star() for _ in range(NUM_STARS)]
    running = True
    t = 0
    
    # Camera variables for movement
    camera_z = 200 # Initial camera Z for projection
    camera_y_offset = 0 # For vertical camera movement

    # Object positions (can be static or animated)
    square_pos_z = 100
    cube_pos_z = 100

    # User input for movement
    move_speed = 5
    rotation_speed = 0.05
    
    # Store key states
    keys = {
        'up': False, 'down': False, 'left': False, 'right': False,
        'w': False, 's': False, 'a': False, 'd': False
    }

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: keys['up'] = True
                if event.key == pygame.K_DOWN: keys['down'] = True
                if event.key == pygame.K_LEFT: keys['left'] = True
                if event.key == pygame.K_RIGHT: keys['right'] = True
                if event.key == pygame.K_w: keys['w'] = True
                if event.key == pygame.K_s: keys['s'] = True
                if event.key == pygame.K_a: keys['a'] = True
                if event.key == pygame.K_d: keys['d'] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP: keys['up'] = False
                if event.key == pygame.K_DOWN: keys['down'] = False
                if event.key == pygame.K_LEFT: keys['left'] = False
                if event.key == pygame.K_RIGHT: keys['right'] = False
                if event.key == pygame.K_w: keys['w'] = False
                if event.key == pygame.K_s: keys['s'] = False
                if event.key == pygame.K_a: keys['a'] = False
                if event.key == pygame.K_d: keys['d'] = False

        # Apply movement based on key states
        if keys['up']: camera_y_offset -= move_speed
        if keys['down']: camera_y_offset += move_speed
        if keys['w']:
            for star in stars:
                star.z = max(1, star.z - move_speed * 2) # Move forward through stars
            square_pos_z = max(1, square_pos_z - move_speed)
            cube_pos_z = max(1, cube_pos_z - move_speed)
        if keys['s']:
            for star in stars:
                star.z += move_speed * 2 # Move backward through stars
            square_pos_z += move_speed
            cube_pos_z += move_speed

        win.fill(FOG_COLOR) # Fill with fog color for atmospheric effect

        # Update and draw stars
        star_speed_multiplier = 1.0
        if keys['w']: star_speed_multiplier = 3.0 # Faster star movement when moving forward
        if keys['s']: star_speed_multiplier = 0.5 # Slower star movement when moving backward

        for star in stars:
            star.update(star_speed_multiplier)
            star.project(win)

        draw_ground_plane(win, camera_y_offset)

        # Smooth auto scale for objects
        scale = 1 + 0.3 * math.sin(t * 2)

        # Drawing 3D square and cube with offsets and camera_z
        draw_3d_square(win, t * 0.5, t * 0.7, t * 0.3, scale, -200, 0, square_pos_z, camera_z)
        draw_3d_cube(win, t * 0.3, t * 0.4, t * 0.2, scale, 200, 0, cube_pos_z, camera_z)

        pygame.display.flip()
        clock.tick(60)
        t += 0.01

    pygame.quit()

if __name__ == "__main__":
    main()