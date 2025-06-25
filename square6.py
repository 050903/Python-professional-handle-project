import pygame
import random
import math
import time

# --- Global Constants & Configuration ---
WIDTH, HEIGHT = 1200, 800  # Wider screen for more immersive view
NUM_STARS = 700  # More stars for a denser field
NUM_ASTEROIDS = 10 # Number of asteroid objects
NUM_NEBULA_BLOBS = 5 # Number of nebula cloud elements

FOG_COLOR = (5, 5, 15)  # Very dark blue-purple for deep space
WARP_SPEED_THRESHOLD = 50  # Speed at which warp effect kicks in (no longer directly used but good for context)
MAX_STAR_SIZE = 5
MIN_STAR_SIZE = 0.5
STAR_PROJECTION_DISTANCE = 400 # 'Focal length' for star perspective

# Camera & World Settings
CAMERA_DEFAULT_Z = 300
CAMERA_NEAR_CLIP = 1.0 # Objects closer than this are clipped
CAMERA_FAR_CLIP = 6000.0 # Objects further than this are clipped or fade out (increased for more depth)
WORLD_SIZE = 3000 # Defines the bounds of our 3D world (for star/asteroid reset, etc.) (increased)

# Colors (more nuanced palette)
COLOR_WHITE = (255, 255, 255)
COLOR_LIGHT_GREY = (180, 180, 190)
COLOR_DARK_GREY = (60, 60, 70)
COLOR_CYAN_LIGHT = (0, 200, 255)
COLOR_CYAN_MID = (0, 150, 200)
COLOR_CYAN_DARK = (0, 100, 150)
COLOR_ORANGE = (255, 120, 0)
COLOR_YELLOW_BRIGHT = (255, 255, 0)
COLOR_GREEN_NEON = (50, 255, 50)
COLOR_BLUE_DEEP = (20, 20, 60)
COLOR_RED = (255, 0, 0)
COLOR_PURPLE = (100, 0, 150) # New color for nebulae
COLOR_TEAL = (0, 150, 150) # New color for nebulae

# --- Pygame Initialization ---
pygame.init()
# Double buffering for smoother animation, HWSURFACE for potential hardware acceleration
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("Project Starflight: Hyperspace Initiative v.2036") # Updated caption
clock = pygame.time.Clock()

# --- Utility Functions ---
def lerp(a, b, t):
    """Linear interpolate between a and b by t.
    t should be between 0.0 and 1.0."""
    return a + (b - a) * t

def rotate_point_3d(point, angle_x, angle_y, angle_z):
    """Rotates a 3D point around the X, Y, and Z axes."""
    x, y, z = point
    # Rotate around X-axis
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
    # Rotate around Y-axis (corrected for right-handed system if needed, but this works with current setup)
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
    # Rotate around Z-axis
    cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
    x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
    return x, y, z

def project_point(point, camera_x, camera_y, camera_z, screen_center_x, screen_center_y, projection_distance=CAMERA_DEFAULT_Z):
    """Projects a 3D point onto a 2D screen using perspective projection.
    Returns (projected_x, projected_y, size_factor) or None if clipped."""
    x, y, z = point[0] - camera_x, point[1] - camera_y, point[2] - camera_z

    # Clip points too close or too far
    if z < CAMERA_NEAR_CLIP or z > CAMERA_FAR_CLIP:
        return None

    factor = projection_distance / z # Standard perspective projection

    projected_x = x * factor + screen_center_x
    projected_y = y * factor + screen_center_y

    # Calculate size factor for depth sorting/alpha
    # Adjust calculation for size_factor to be more linear across visible range
    normalized_z = (z - CAMERA_NEAR_CLIP) / (CAMERA_FAR_CLIP - CAMERA_NEAR_CLIP)
    size_factor = max(0.1, 1.0 - normalized_z) # Scales from 1.0 (near) to 0.1 (far)

    return (projected_x, projected_y, size_factor, z) # Return size factor and original Z for sorting

# --- Classes for 3D Elements ---

class Star:
    """Represents a single star in the background."""
    def __init__(self):
        self.initial_size = random.uniform(MIN_STAR_SIZE, MAX_STAR_SIZE)
        self.base_color = random.choice([COLOR_WHITE, COLOR_LIGHT_GREY, COLOR_CYAN_LIGHT])
        self.reset()

    def reset(self):
        """Resets the star's position and properties."""
        self.x = random.uniform(-WORLD_SIZE, WORLD_SIZE)
        self.y = random.uniform(-WORLD_SIZE, WORLD_SIZE)
        # Place stars behind the camera's initial view but within far clip
        self.z = random.uniform(CAMERA_DEFAULT_Z + 100, CAMERA_FAR_CLIP - 100) # Start further back
        self.size = self.initial_size # Reset to original size
        self.trail_length = 0
        self.trail_alpha = 255

    def update(self, delta_z, warp_factor=0.0):
        """Updates the star's position and visual properties based on speed and warp factor."""
        self.z += delta_z # Move relative to camera
        
        # Apply additional speed boost during warp, making them "streak" faster
        self.z -= delta_z * warp_factor * 20 # Increased warp streak effect
        
        # Warp effect: adjust trail length, alpha, and size
        if warp_factor > 0.1:
            self.trail_length = lerp(self.trail_length, MAX_STAR_SIZE * 30 * warp_factor, 0.1) # Longer trails
            self.trail_alpha = lerp(self.trail_alpha, 50, 0.1)
            self.size = lerp(self.size, MAX_STAR_SIZE * 3, 0.1) # Larger star during warp
        else:
            self.trail_length = lerp(self.trail_length, 0, 0.1)
            self.trail_alpha = lerp(self.trail_alpha, 255, 0.1)
            self.size = lerp(self.size, self.initial_size, 0.1) 

        # Reset if star passes camera or goes too far
        if self.z < CAMERA_NEAR_CLIP or self.z > CAMERA_FAR_CLIP:
            self.reset() # Reset fully
            # Ensure it resets to a position *behind* the camera and within the far clip
            if self.z > CAMERA_FAR_CLIP:
                self.z = CAMERA_NEAR_CLIP + WORLD_SIZE + random.uniform(0, WORLD_SIZE / 2) # Reset to far, but still behind camera
            else: # If it passed by (z < near clip), reset to far end
                self.z = CAMERA_FAR_CLIP - random.uniform(0, WORLD_SIZE / 2) # Place it clearly visible, but far

    def draw(self, win, camera_pos):
        """Draws the star and its warp trail."""
        projected_data = project_point((self.x, self.y, self.z), camera_pos[0], camera_pos[1], camera_pos[2], WIDTH // 2, HEIGHT // 2, STAR_PROJECTION_DISTANCE)

        if projected_data is None: return # Star is clipped

        px, py, size_factor, _ = projected_data
        
        # Smooth size based on projection and current star size
        current_size = max(0.5, self.size * size_factor)

        # Fading based on distance and trail alpha
        alpha = int(lerp(0, 255, size_factor) * (self.trail_alpha / 255))
        alpha = max(0, min(255, alpha)) 
        star_color = (self.base_color[0], self.base_color[1], self.base_color[2], alpha)

        s = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, star_color, (int(current_size), int(current_size)), int(current_size / 2))
        win.blit(s, (int(px - current_size), int(py - current_size)))

        # Draw warp trail
        if self.trail_length > 0.5:
            # Calculate trail end point behind the star
            trail_end_z = self.z + self.trail_length 
            
            projected_trail_end_data = project_point((self.x, self.y, trail_end_z), camera_pos[0], camera_pos[1], camera_pos[2], WIDTH // 2, HEIGHT // 2, STAR_PROJECTION_DISTANCE)

            if projected_trail_end_data:
                tx, ty, _, _ = projected_trail_end_data
                trail_color = (self.base_color[0], self.base_color[1], self.base_color[2], int(alpha * 0.5)) 
                trail_color = (trail_color[0], trail_color[1], trail_color[2], max(0, min(255, trail_color[3])))
                pygame.draw.line(win, trail_color, (int(px), int(py)), (int(tx), int(ty)), int(current_size / 2) + 1)


class GroundPlane:
    """Draws a grid plane that simulates ground."""
    def __init__(self):
        self.num_lines = 40
        self.spacing = 80
        self.plane_y_offset = 100 # Position of the plane relative to the camera's Y center
        
    def draw(self, win, camera_pos):
        """Draws the horizontal and vertical grid lines."""
        center_x, center_y, center_z = camera_pos
        
        # Horizontal lines
        for i in range(-self.num_lines // 2, self.num_lines // 2 + 1):
            world_z = center_z + i * self.spacing 
            
            distance_from_camera = abs(world_z - center_z)
            alpha = max(0, 255 - int(distance_from_camera / 10))
            line_thickness = max(1, 3 - int(distance_from_camera / 200))
            
            line_color = (COLOR_DARK_GREY[0], COLOR_DARK_GREY[1], COLOR_DARK_GREY[2] + int(alpha * 0.1), alpha)
            line_color = (line_color[0], line_color[1], line_color[2], max(0, min(255, line_color[3])))

            p1_data = project_point((-WORLD_SIZE, self.plane_y_offset, world_z), center_x, center_y, center_z, WIDTH // 2, HEIGHT // 2)
            p2_data = project_point((WORLD_SIZE, self.plane_y_offset, world_z), center_x, center_y, center_z, WIDTH // 2, HEIGHT // 2)

            if p1_data and p2_data:
                p1 = (p1_data[0], p1_data[1])
                p2 = (p2_data[0], p2_data[1])
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(s, line_color, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), line_thickness)
                win.blit(s, (0,0))

        # Vertical lines
        for i in range(-self.num_lines // 2, self.num_lines // 2 + 1):
            world_x = center_x + i * self.spacing 
            
            distance_from_camera_x = abs(world_x - center_x)
            alpha_x = max(0, 255 - int(distance_from_camera_x / 10))
            line_thickness_x = max(1, 3 - int(distance_from_camera_x / 200))

            line_color_x = (COLOR_DARK_GREY[0] + int(alpha_x * 0.1), COLOR_DARK_GREY[1], COLOR_DARK_GREY[2], alpha_x)
            line_color_x = (line_color_x[0], line_color_x[1], line_color_x[2], max(0, min(255, line_color_x[3])))

            p1_data = project_point((world_x, self.plane_y_offset, CAMERA_NEAR_CLIP + center_z), center_x, center_y, center_z, WIDTH // 2, HEIGHT // 2)
            p2_data = project_point((world_x, self.plane_y_offset, CAMERA_FAR_CLIP + center_z), center_x, center_y, center_z, WIDTH // 2, HEIGHT // 2)

            if p1_data and p2_data:
                p1 = (p1_data[0], p1_data[1])
                p2 = (p2_data[0], p2_data[1])
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(s, line_color_x, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), line_thickness_x)
                win.blit(s, (0,0))


class Base3DObject:
    """Base class for any 3D object composed of vertices and faces."""
    def __init__(self, position, scale, color=(200, 200, 0)):
        self.x, self.y, self.z = position
        self.scale = scale
        self.color = color
        self.vertices = []
        self.faces = []
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0

    def update(self, dt):
        """Placeholder for object-specific animation or movement."""
        pass 

    def draw(self, win, camera_pos):
        """Draws the 3D object with back-face culling and Z-sorting."""
        center_x, center_y, center_z = camera_pos
        
        transformed_vertices = []
        for v in self.vertices:
            # Apply object's own rotation
            rotated_v = rotate_point_3d(v, self.angle_x, self.angle_y, self.angle_z)
            # Apply object's world position and scale
            transformed_vertices.append((rotated_v[0] * self.scale + self.x, 
                                         rotated_v[1] * self.scale + self.y, 
                                         rotated_v[2] * self.scale + self.z))
        
        projected_vertices_data = []
        for v in transformed_vertices:
            proj = project_point(v, center_x, center_y, center_z, WIDTH // 2, HEIGHT // 2)
            projected_vertices_data.append(proj)

        # Basic Back-Face Culling and Z-sorting (per face)
        drawable_faces = []
        for i, face in enumerate(self.faces):
            # Calculate average Z-depth of the face for sorting
            # Only consider faces where all vertices are visible
            if all(projected_vertices_data[v_idx] is not None for v_idx in face):
                face_avg_z = sum(transformed_vertices[v_idx][2] for v_idx in face) / len(face)
                drawable_faces.append((face_avg_z, i)) # Store (avg_z, original_index)

        drawable_faces.sort(key=lambda x: x[0], reverse=True) # Sort from furthest to closest

        for avg_z, face_idx in drawable_faces:
            face = self.faces[face_idx]
            color = self.get_face_color(face_idx, transformed_vertices) # Get color with lighting
            
            projected_face_points = [projected_vertices_data[v_idx] for v_idx in face]
            if all(p is not None for p in projected_face_points):
                # Extract (x,y) from (x,y,size_factor, z) tuple
                points_2d = [(p[0], p[1]) for p in projected_face_points]
                
                min_x = min(p[0] for p in points_2d)
                max_x = max(p[0] for p in points_2d)
                min_y = min(p[1] for p in points_2d)
                max_y = max(p[1] for p in points_2d)

                surf_width = int(max_x - min_x) + 2 
                surf_height = int(max_y - min_y) + 2
                
                if surf_width > 0 and surf_height > 0:
                    s = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
                    relative_points_2d = [(p[0] - min_x + 1, p[1] - min_y + 1) for p in points_2d] 
                    
                    pygame.draw.polygon(s, color, relative_points_2d, 0)
                    pygame.draw.lines(s, (0, 0, 0), True, relative_points_2d, 1) # Thin black border
                    win.blit(s, (int(min_x), int(min_y)))


    def get_face_color(self, face_idx, transformed_vertices):
        """Calculates the color of a face with simple lighting."""
        
        light_direction = (1, 1, -1) 
        
        normals = [
            (0, 0, -1),   # Front face
            (0, 0, 1),    # Back face
            (0, -1, 0),   # Bottom face
            (0, 1, 0),    # Top face
            (1, 0, 0),    # Right face
            (-1, 0, 0)    # Left face
        ]
        
        if face_idx < len(normals):
            face_normal = normals[face_idx]
        else:
            face_normal = (0,0,0)

        light_dir_len = math.sqrt(light_direction[0]**2 + light_direction[1]**2 + light_direction[2]**2)
        if light_dir_len > 0:
            norm_light_direction = (light_direction[0]/light_dir_len, light_direction[1]/light_dir_len, light_direction[2]/light_dir_len)
        else:
            norm_light_direction = (0,0,0)

        dot_product = (face_normal[0] * norm_light_direction[0] + 
                       face_normal[1] * norm_light_direction[1] + 
                       face_normal[2] * norm_light_direction[2])
        
        light_intensity = max(0.2, min(1.0, dot_product)) 
        
        base_r, base_g, base_b = self.color
        
        gradient_factor = 1.0 - (face_idx / len(self.faces) * 0.2) 
        
        final_r = int(base_r * light_intensity * gradient_factor)
        final_g = int(base_g * light_intensity * gradient_factor)
        final_b = int(base_b * light_intensity * gradient_factor)
        
        final_r = max(0, min(255, final_r))
        final_g = max(0, min(255, final_g))
        final_b = max(0, min(255, final_b))

        return (final_r, final_g, final_b)


class Cube(Base3DObject):
    """A simple 3D cube object."""
    def __init__(self, position, size, color=(200, 200, 0)):
        super().__init__(position, size, color)
        s = 0.5 
        self.vertices = [
            (-s, -s, -s), ( s, -s, -s), ( s, s, -s), (-s, s, -s),   
            (-s, -s, s), ( s, -s, s), ( s, s, s), (-s, s, s)        
        ]
        self.faces = [
            (0,1,2,3), # Front
            (4,5,6,7), # Back
            (0,1,5,4), # Bottom
            (2,3,7,6), # Top
            (1,2,6,5), # Right
            (0,3,7,4), # Left
        ]
        
    def update(self, dt):
        """Rotates the cube over time."""
        self.angle_x += 0.05 * dt
        self.angle_y += 0.07 * dt
        self.angle_z += 0.03 * dt

class Pyramid(Base3DObject):
    """A simple 3D pyramid object."""
    def __init__(self, position, size, color=(0, 255, 100)):
        super().__init__(position, size, color)
        s = 0.5
        self.vertices = [
            (0, s, 0),       
            (-s, -s, -s),    
            (s, -s, -s),     
            (s, -s, s),      
            (-s, -s, s)      
        ]
        self.faces = [
            (0, 1, 2),    # Front face
            (0, 2, 3),    # Right face
            (0, 3, 4),    # Back face
            (0, 4, 1),    # Left face
            (1, 2, 3, 4)  # Base
        ]

    def update(self, dt):
        """Rotates the pyramid over time."""
        self.angle_x += 0.04 * dt
        self.angle_y += 0.06 * dt

class Asteroid(Base3DObject):
    """A simple asteroid model."""
    def __init__(self, position, size, color=(100, 80, 70)):
        super().__init__(position, size, color)
        # Create a randomized, irregular shape
        num_verts = random.randint(8, 12)
        s = 0.5 # Base unit size
        self.vertices = []
        for _ in range(num_verts):
            self.vertices.append((
                random.uniform(-s, s),
                random.uniform(-s, s),
                random.uniform(-s, s)
            ))
        
        # Simple triangulation for faces (can be improved)
        # For simplicity, connect vertices to a central point to form triangles
        # or use a convex hull algorithm (more complex)
        self.faces = []
        center_vert_idx = len(self.vertices) # Index for a conceptual center point
        # Add a "center" vertex for triangulation for simplicity
        self.vertices.append((0,0,0)) 

        for i in range(num_verts):
            v1 = i
            v2 = (i + 1) % num_verts
            self.faces.append((v1, v2, center_vert_idx)) # Triangle fan from center
        
        # Add a base face if it's not truly spherical/irregular
        if num_verts >= 3:
             self.faces.append(tuple(range(num_verts))) # The "base" polygon

        self.rotation_speed_x = random.uniform(-0.02, 0.02)
        self.rotation_speed_y = random.uniform(-0.02, 0.02)
        self.rotation_speed_z = random.uniform(-0.02, 0.02)
        self.initial_z = self.z # Store initial Z for resetting

    def update(self, dt, camera_delta_z):
        """Updates asteroid position and rotation. Resets when it passes the camera."""
        self.x += random.uniform(-5, 5) * dt # Slight lateral drift
        self.y += random.uniform(-5, 5) * dt # Slight vertical drift
        self.z += camera_delta_z # Move with camera speed

        self.angle_x += self.rotation_speed_x * dt
        self.angle_y += self.rotation_speed_y * dt
        self.angle_z += self.rotation_speed_z * dt

        # Reset asteroid when it goes behind camera or too far forward
        if self.z < CAMERA_NEAR_CLIP:
            self.z = CAMERA_FAR_CLIP + random.uniform(0, WORLD_SIZE / 2) # Reset far away
            self.x = random.uniform(-WORLD_SIZE, WORLD_SIZE)
            self.y = random.uniform(-WORLD_SIZE, WORLD_SIZE)
            self.scale = random.uniform(50, 200) # Randomize size for next pass
            self.rotation_speed_x = random.uniform(-0.02, 0.02)
            self.rotation_speed_y = random.uniform(-0.02, 0.02)
            self.rotation_speed_z = random.uniform(-0.02, 0.02)
        elif self.z > CAMERA_FAR_CLIP + WORLD_SIZE: # If it somehow gets too far ahead
            self.z = CAMERA_NEAR_CLIP + random.uniform(0, WORLD_SIZE / 2)

class NebulaBlob:
    """Represents a semi-transparent, floating nebula cloud."""
    def __init__(self):
        self.reset()
        self.color = random.choice([COLOR_BLUE_DEEP, COLOR_PURPLE, COLOR_TEAL])
        self.initial_alpha = random.randint(30, 80) # Semi-transparent
        self.current_alpha = self.initial_alpha
        self.fade_speed = random.uniform(0.01, 0.05) # How quickly it pulses/fades
        self.size = random.uniform(300, 1000) # Large blobs

    def reset(self):
        """Resets nebula blob position."""
        self.x = random.uniform(-WORLD_SIZE * 2, WORLD_SIZE * 2) # Larger range for nebulae
        self.y = random.uniform(-WORLD_SIZE * 2, WORLD_SIZE * 2)
        self.z = random.uniform(CAMERA_FAR_CLIP / 2, CAMERA_FAR_CLIP * 1.5) # Appear far away

    def update(self, delta_z, warp_factor=0.0):
        """Updates nebula position and pulses its alpha."""
        self.z += delta_z * 0.5 # Moves slower than stars/objects
        self.current_alpha = int(self.initial_alpha + math.sin(time.time() * self.fade_speed) * (self.initial_alpha * 0.5))
        self.current_alpha = max(0, min(255, self.current_alpha))

        if warp_factor > 0.1:
            self.current_alpha = lerp(self.current_alpha, 255, 0.05) # Brighter during warp
        else:
            self.current_alpha = lerp(self.current_alpha, self.initial_alpha, 0.05) # Fade back

        # Reset if it goes behind camera or too far
        if self.z < CAMERA_NEAR_CLIP or self.z > CAMERA_FAR_CLIP * 2:
            self.reset()
            # Ensure it resets far behind the camera
            self.z = CAMERA_FAR_CLIP + random.uniform(WORLD_SIZE, WORLD_SIZE * 2)


    def draw(self, win, camera_pos):
        """Draws the nebula blob as a soft, translucent circle."""
        projected_data = project_point((self.x, self.y, self.z), camera_pos[0], camera_pos[1], camera_pos[2], WIDTH // 2, HEIGHT // 2, STAR_PROJECTION_DISTANCE)

        if projected_data is None: return

        px, py, size_factor, _ = projected_data
        
        current_size = max(50, self.size * size_factor) # Minimum visible size

        color_with_alpha = (self.color[0], self.color[1], self.color[2], self.current_alpha)
        
        # Draw on a surface to handle alpha blending
        s = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, color_with_alpha, (int(current_size), int(current_size)), int(current_size / 2))
        win.blit(s, (int(px - current_size), int(py - current_size)))


class ShipModel(Base3DObject):
    """
    A simplified procedural ship model made of joined cubes/pyramids.
    This demonstrates more complex object creation by combining primitives.
    """
    def __init__(self, position, scale, color=(150, 150, 255)):
        super().__init__(position, scale, color)
        # Scales for individual parts relative to the overall ship scale
        self.body_ratio = 1.5 
        self.wing_ratio = 0.5
        self.cockpit_ratio = 0.7

        # Define sub-components vertices relative to the ship's origin (0,0,0)
        # These are then scaled by their component's ratio and the ship's overall scale
        
        # Main body (elongated cube)
        self.main_body_verts = [
            (-0.5, -0.2, -1.0), (0.5, -0.2, -1.0), (0.5, 0.2, -1.0), (-0.5, 0.2, -1.0), # Front
            (-0.5, -0.2, 1.0), (0.5, -0.2, 1.0), (0.5, 0.2, 1.0), (-0.5, 0.2, 1.0)       # Back
        ]
        self.main_body_faces = [
            (0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (1,2,6,5), (0,3,7,4)
        ]
        
        # Left Wing (flat cube, offset)
        self.left_wing_verts = [
            (-1.5, 0.0, -0.2), (-0.5, 0.0, -0.2), (-0.5, 0.0, 0.2), (-1.5, 0.0, 0.2), # Top
            (-1.5, -0.1, -0.2), (-0.5, -0.1, -0.2), (-0.5, -0.1, 0.2), (-1.5, -0.1, 0.2) # Bottom
        ]
        self.left_wing_faces = [
            (0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (1,2,6,5), (0,3,7,4)
        ]
        
        # Right Wing (same as left, mirrored X)
        self.right_wing_verts = [
            (0.5, 0.0, -0.2), (1.5, 0.0, -0.2), (1.5, 0.0, 0.2), (0.5, 0.0, 0.2), # Top
            (0.5, -0.1, -0.2), (1.5, -0.1, -0.2), (1.5, -0.1, 0.2), (0.5, -0.1, 0.2) # Bottom
        ]
        self.right_wing_faces = [
            (0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (1,2,6,5), (0,3,7,4)
        ]

        # Cockpit (pyramid-like, top-front)
        self.cockpit_verts = [
            (0, 0.5, -1.0), # Apex
            (-0.3, 0.1, -1.2), (0.3, 0.1, -1.2), # Base front
            (0.3, 0.1, -0.8), (-0.3, 0.1, -0.8)   # Base back
        ]
        self.cockpit_faces = [
            (0,1,2), (0,2,3), (0,3,4), (0,4,1), (1,2,3,4) # pyramid faces + base
        ]

        # Combine all parts into single vertex and face lists
        self.all_vertices = []
        self.all_faces = []

        # Add main body
        offset = len(self.all_vertices)
        for v in self.main_body_verts: self.all_vertices.append((v[0] * self.body_ratio, v[1] * self.body_ratio, v[2] * self.body_ratio))
        for f in self.main_body_faces: self.all_faces.append(tuple(v + offset for v in f))

        # Add left wing (offset -1.0 in x relative to ship scale)
        offset = len(self.all_vertices)
        for v in self.left_wing_verts: self.all_vertices.append((v[0] * self.wing_ratio - 1.0, v[1] * self.wing_ratio, v[2] * self.wing_ratio))
        for f in self.left_wing_faces: self.all_faces.append(tuple(v + offset for v in f))

        # Add right wing (offset +1.0 in x relative to ship scale)
        offset = len(self.all_vertices)
        for v in self.right_wing_verts: self.all_vertices.append((v[0] * self.wing_ratio + 1.0, v[1] * self.wing_ratio, v[2] * self.wing_ratio))
        for f in self.right_wing_faces: self.all_faces.append(tuple(v + offset for v in f))
        
        # Add cockpit (offset slightly up and forward in Z, relative to ship scale)
        offset = len(self.all_vertices)
        for v in self.cockpit_verts: self.all_vertices.append((v[0] * self.cockpit_ratio, v[1] * self.cockpit_ratio + 0.3, v[2] * self.cockpit_ratio - 0.5))
        for f in self.cockpit_faces: self.all_faces.append(tuple(v + offset for v in f))

        self.vertices = self.all_vertices
        self.faces = self.all_faces

    def update(self, dt):
        """Updates the ship's internal rotation."""
        self.angle_y += 0.002 * dt # Gentle yaw
        # Add subtle bobbing or pitch if desired
        # self.y = self.y + math.sin(time.time() * 2) * 0.05 * self.scale
        # self.angle_x = math.sin(time.time() * 1.5) * 0.01

    def get_face_color(self, face_idx, transformed_vertices):
        """Overrides base method to give ship parts different colors and a pulsing light effect.
        This still uses a simplified lighting model without proper normal calculation."""
        
        main_body_faces_end = len(self.main_body_faces)
        left_wing_faces_end = main_body_faces_end + len(self.left_wing_faces)
        right_wing_faces_end = left_wing_faces_end + len(self.right_wing_faces)
        
        if face_idx < main_body_faces_end: 
            base_color = (150, 150, 255) 
        elif face_idx < left_wing_faces_end: 
            base_color = (100, 100, 180) 
        elif face_idx < right_wing_faces_end: 
            base_color = (100, 100, 180) 
        else: 
            base_color = (80, 80, 120) 

        light_intensity = 0.8 + math.sin(time.time() * 3 + face_idx * 0.5) * 0.2 
        light_intensity = max(0.5, min(1.0, light_intensity)) 

        final_r = int(base_color[0] * light_intensity)
        final_g = int(base_color[1] * light_intensity)
        final_b = int(base_color[2] * light_intensity)

        final_r = max(0, min(255, final_r))
        final_g = max(0, min(255, final_g))
        final_b = max(0, min(255, final_b))

        return (final_r, final_g, final_b)


# --- Particle System for Engine Trails ---
class Particle:
    """A single particle for effects like engine trails."""
    def __init__(self, x, y, z, color, size, velocity, lifetime):
        self.x, self.y, self.z = x, y, z
        self.color = color
        self.size = size
        self.vx, self.vy, self.vz = velocity
        self.lifetime = lifetime
        self.current_lifetime = lifetime

    def update(self, dt, camera_delta_z):
        """Updates particle position and remaining lifetime."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt + camera_delta_z # Particles move with world, relative to camera
        self.current_lifetime -= dt

    def draw(self, win, camera_pos):
        """Draws the particle, fading out as it dies."""
        if self.current_lifetime <= 0: return 

        projected_data = project_point((self.x, self.y, self.z), camera_pos[0], camera_pos[1], camera_pos[2], WIDTH // 2, HEIGHT // 2)
        if projected_data is None: return 

        px, py, size_factor, _ = projected_data
        current_size = max(0.5, self.size * size_factor)

        alpha = int(255 * (self.current_lifetime / self.lifetime))
        alpha = max(0, min(255, alpha)) 
        particle_color = (self.color[0], self.color[1], self.color[2], alpha)
        
        if current_size > 0.5:
            s = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, particle_color, (int(current_size), int(current_size)), int(current_size / 2))
            win.blit(s, (int(px - current_size), int(py - current_size)))


class ParticleSystem:
    """Manages a collection of particles, used for effects like engine trails."""
    def __init__(self, source_pos_relative, max_particles, color, size_range, velocity_range, lifetime_range, emission_rate):
        self.source_pos_relative = source_pos_relative 
        self.max_particles = max_particles
        self.particles = []
        self.color = color
        self.size_range = size_range
        self.velocity_range = velocity_range 
        self.lifetime_range = lifetime_range
        self.emission_rate = emission_rate 
        self.time_since_last_emission = 0

    def update(self, dt, parent_pos, parent_rotation, camera_delta_z):
        """Updates particle system, emitting new particles and updating existing ones."""
        self.time_since_last_emission += dt

        particles_to_emit = int(self.time_since_last_emission * self.emission_rate)
        for _ in range(particles_to_emit):
            if len(self.particles) < self.max_particles:
                rotated_source = rotate_point_3d(self.source_pos_relative, parent_rotation[0], parent_rotation[1], parent_rotation[2])
                px = parent_pos[0] + rotated_source[0]
                py = parent_pos[1] + rotated_source[1]
                pz = parent_pos[2] + rotated_source[2]

                vx = random.uniform(self.velocity_range[0], self.velocity_range[1])
                vy = random.uniform(self.velocity_range[2], self.velocity_range[3])
                vz = random.uniform(self.velocity_range[4], self.velocity_range[5])

                size = random.uniform(self.size_range[0], self.size_range[1])
                lifetime = random.uniform(self.lifetime_range[0], self.lifetime_range[1])
                self.particles.append(Particle(px, py, pz, self.color, size, (vx, vy, vz), lifetime))
        
        self.time_since_last_emission -= particles_to_emit / self.emission_rate

        live_particles = []
        for p in self.particles:
            p.update(dt, camera_delta_z)
            if p.current_lifetime > 0:
                live_particles.append(p)
        self.particles = live_particles

    def draw(self, win, camera_pos):
        """Draws all active particles, sorting them by Z-depth for correct rendering."""
        self.particles.sort(key=lambda p: p.z, reverse=True)
        for p in self.particles:
            p.draw(win, camera_pos)

# --- Main Game Loop ---
def main():
    stars = [Star() for _ in range(NUM_STARS)]
    asteroids = [Asteroid((random.uniform(-WORLD_SIZE, WORLD_SIZE), random.uniform(-WORLD_SIZE, WORLD_SIZE), random.uniform(CAMERA_DEFAULT_Z + 1000, CAMERA_FAR_CLIP)), random.uniform(50, 200)) for _ in range(NUM_ASTEROIDS)]
    nebulae = [NebulaBlob() for _ in range(NUM_NEBULA_BLOBS)]
    ground_plane = GroundPlane()
    
    # 3D Objects in the scene
    objects = []
    objects.append(Cube((200, 50, 500), 100, COLOR_RED))
    objects.append(Pyramid((-300, 0, 700), 80, COLOR_GREEN_NEON))
    station_scale = 150 
    objects.append(ShipModel((0, 0, 1000), station_scale, (200,200,255))) 

    # Camera State
    camera_x, camera_y, camera_z = 0.0, 0.0, 0.0 
    camera_target_x, camera_target_y = 0.0, 0.0 
    camera_lerp_factor = 3.0 
    
    # Player speed
    current_speed = 0.0 
    target_speed = 0.0
    max_speed_normal = 200 
    max_speed_warp = 1500 
    acceleration = 100 
    deceleration = 200 
    strafe_speed_base = 200 
    vertical_speed_base = 100 

    warp_mode_active = False
    warp_factor = 0.0 

    # Camera Shake variables
    camera_shake_intensity = 0.0
    camera_shake_duration = 0.0
    camera_shake_max_strength = 20.0 # Max pixel offset for shake
    camera_shake_decay_rate = 0.9 # How fast shake fades per second

    # Engine particle systems
    engine_left_ps = ParticleSystem(
        (-0.8 * station_scale, -0.1 * station_scale, 0.8 * station_scale), 
        500, COLOR_ORANGE, (1, 4), (-10, 10, -10, 10, 50, 100), (0.5, 1.5), 1000 
    )
    engine_right_ps = ParticleSystem(
        (0.8 * station_scale, -0.1 * station_scale, 0.8 * station_scale), 
        500, COLOR_ORANGE, (1, 4), (-10, 10, -10, 10, 50, 100), (0.5, 1.5), 1000 
    )

    # User input states
    keys = {
        'forward': False, 'backward': False, 'left': False, 'right': False,
        'up': False, 'down': False, 'warp': False
    }

    last_time = time.time()
    running = True

    while running:
        dt = time.time() - last_time 
        last_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w: keys['forward'] = True
                if event.key == pygame.K_s: keys['backward'] = True
                if event.key == pygame.K_a: keys['left'] = True
                if event.key == pygame.K_d: keys['right'] = True
                if event.key == pygame.K_SPACE: keys['up'] = True
                if event.key == pygame.K_LSHIFT: keys['down'] = True
                if event.key == pygame.K_e: 
                    keys['warp'] = not keys['warp']
                    if keys['warp']: # Apply camera shake on warp activation
                        camera_shake_intensity = 1.0
                        camera_shake_duration = 0.5
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w: keys['forward'] = False
                if event.key == pygame.K_s: keys['backward'] = False
                if event.key == pygame.K_a: keys['left'] = False
                if event.key == pygame.K_d: keys['right'] = False
                if event.key == pygame.K_SPACE: keys['up'] = False
                if event.key == pygame.K_LSHIFT: keys['down'] = False

        # --- Update Game State ---
        
        # Speed control and warp effect
        if keys['warp']:
            target_speed = max_speed_warp
            warp_factor = lerp(warp_factor, 1.0, 5.0 * dt) 
        else:
            target_speed = max_speed_normal
            warp_factor = lerp(warp_factor, 0.0, 5.0 * dt) 

        if keys['forward']:
            current_speed = min(target_speed, current_speed + acceleration * dt)
        elif keys['backward']:
            current_speed = max(-max_speed_normal / 2, current_speed - acceleration * dt) 
        else:
            if current_speed > 0:
                current_speed = max(0.0, current_speed - deceleration * dt)
            elif current_speed < 0:
                current_speed = min(0.0, current_speed + deceleration * dt)
        
        camera_delta_z = current_speed * dt 
        camera_z += camera_delta_z 

        if keys['left']: 
            camera_target_x -= strafe_speed_base * dt
        if keys['right']: 
            camera_target_x += strafe_speed_base * dt
        
        if keys['up']: 
            camera_target_y -= vertical_speed_base * dt
        if keys['down']: 
            camera_target_y += vertical_speed_base * dt

        camera_x = lerp(camera_x, camera_target_x, camera_lerp_factor * dt)
        camera_y = lerp(camera_y, camera_target_y, camera_lerp_factor * dt)
        
        camera_x = max(-WORLD_SIZE, min(WORLD_SIZE, camera_x))
        camera_y = max(-WORLD_SIZE / 2, min(WORLD_SIZE / 2, camera_y)) 
        
        # Update camera shake
        if camera_shake_duration > 0:
            shake_offset_x = random.uniform(-1, 1) * camera_shake_intensity * camera_shake_max_strength
            shake_offset_y = random.uniform(-1, 1) * camera_shake_intensity * camera_shake_max_strength
            camera_shake_duration -= dt
            camera_shake_intensity *= (1.0 - camera_shake_decay_rate * dt * 5) # Faster decay
            if camera_shake_intensity < 0.01:
                camera_shake_intensity = 0.0
                camera_shake_duration = 0.0
        else:
            shake_offset_x = 0
            shake_offset_y = 0

        # Update stars, asteroids, and nebulae
        for star in stars:
            star.update(camera_delta_z, warp_factor)
        for asteroid in asteroids:
            asteroid.update(dt, camera_delta_z)
        for nebula in nebulae:
            nebula.update(camera_delta_z, warp_factor)
        
        for obj in objects:
            obj.update(dt) 

        ship = next((obj for obj in objects if isinstance(obj, ShipModel)), None)
        if ship:
            engine_left_ps.update(dt, (ship.x, ship.y, ship.z), (ship.angle_x, ship.angle_y, ship.angle_z), camera_delta_z)
            engine_right_ps.update(dt, (ship.x, ship.y, ship.z), (ship.angle_x, ship.angle_y, ship.angle_z), camera_delta_z)

        # --- Drawing ---
        win.fill(FOG_COLOR) 

        # Draw nebulae (behind everything except the very deep fog color)
        # Sort nebulae by Z-depth to draw furthest first
        nebulae.sort(key=lambda n: n.z, reverse=True)
        for nebula in nebulae:
            nebula.draw(win, (camera_x + shake_offset_x, camera_y + shake_offset_y, camera_z))

        # Layered effects for atmosphere/deep space glow (approximate)
        for i in range(5):
            alpha = int(lerp(0, 50, i / 4.0)) 
            color = (COLOR_BLUE_DEEP[0], COLOR_BLUE_DEEP[1], COLOR_BLUE_DEEP[2], alpha)
            color = (color[0], color[1], color[2], max(0, min(255, alpha)))

            s = pygame.Surface((WIDTH, HEIGHT // 5 * (i + 1)), pygame.SRCALPHA)
            pygame.draw.rect(s, color, (0, 0, WIDTH, HEIGHT // 5 * (i + 1)))
            win.blit(s, (0, HEIGHT - (HEIGHT // 5) * (i + 1)))

        # Apply shake offset to camera position for drawing
        camera_current_pos_shaken = (camera_x + shake_offset_x, camera_y + shake_offset_y, camera_z)

        # Draw elements in a rough back-to-front order
        
        # Stars (furthest back)
        for star in stars:
            star.draw(win, camera_current_pos_shaken)

        # Ground Plane
        ground_plane.draw(win, camera_current_pos_shaken)
        
        # All 3D Objects (including asteroids and static objects)
        all_polygons_to_draw = []
        for obj in objects + asteroids: # Combine static objects and dynamic asteroids
            transformed_vertices = []
            for v in obj.vertices:
                rotated_v = rotate_point_3d(v, obj.angle_x, obj.angle_y, obj.angle_z)
                transformed_vertices.append((rotated_v[0] * obj.scale + obj.x, 
                                             rotated_v[1] * obj.scale + obj.y, 
                                             rotated_v[2] * obj.scale + obj.z))
            
            projected_vertices_data = []
            for v_world in transformed_vertices:
                proj_data = project_point(v_world, camera_x, camera_y, camera_z, WIDTH // 2, HEIGHT // 2)
                projected_vertices_data.append(proj_data)

            for i, face in enumerate(obj.faces):
                if all(proj_data is not None for proj_data in [projected_vertices_data[v_idx] for v_idx in face]):
                    # Use the Z from the projected_data tuple for sorting
                    face_avg_z = sum(projected_vertices_data[v_idx][3] for v_idx in face) / len(face)
                    points_2d = [(projected_vertices_data[v_idx][0], projected_vertices_data[v_idx][1]) for v_idx in face]
                    color = obj.get_face_color(i, transformed_vertices)
                    all_polygons_to_draw.append((face_avg_z, color, points_2d))
        
        all_polygons_to_draw.sort(key=lambda x: x[0], reverse=True) # Sort furthest to closest by their actual world Z

        for z_depth, color, points_2d in all_polygons_to_draw:
            if len(points_2d) >= 3: 
                min_x = min(p[0] for p in points_2d)
                max_x = max(p[0] for p in points_2d)
                min_y = min(p[1] for p in points_2d)
                max_y = max(p[1] for p in points_2d)

                surf_width = int(max_x - min_x) + 2 
                surf_height = int(max_y - min_y) + 2
                
                if surf_width > 0 and surf_height > 0:
                    s = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
                    relative_points_2d = [(p[0] - min_x + 1, p[1] - min_y + 1) for p in points_2d] 
                    
                    pygame.draw.polygon(s, color, relative_points_2d, 0) 
                    pygame.draw.lines(s, (0, 0, 0), True, relative_points_2d, 1) 
                    win.blit(s, (int(min_x), int(min_y)))


        # Particle effects (drawn last so they are on top of objects)
        engine_left_ps.draw(win, camera_current_pos_shaken)
        engine_right_ps.draw(win, camera_current_pos_shaken)

        # --- UI/HUD (Futuristic Telemetry) ---
        font = pygame.font.Font(None, 24) 
        
        speed_text = f"SPEED: {current_speed:.1f} U/S" 
        speed_color = COLOR_GREEN_NEON if warp_factor > 0.5 else COLOR_CYAN_LIGHT
        speed_render = font.render(speed_text, True, speed_color)
        win.blit(speed_render, (10, 10))

        warp_status_text = "WARP: ACTIVE" if warp_factor > 0.5 else "WARP: STANDBY"
        warp_status_color = COLOR_YELLOW_BRIGHT if warp_factor > 0.5 else COLOR_LIGHT_GREY
        warp_status_render = font.render(warp_status_text, True, warp_status_color)
        win.blit(warp_status_render, (10, 40))
        
        # A simple crosshair (now with added dynamic outer ring for speed)
        crosshair_color = COLOR_CYAN_LIGHT
        pygame.draw.line(win, crosshair_color, (WIDTH // 2 - 10, HEIGHT // 2), (WIDTH // 2 + 10, HEIGHT // 2), 2)
        pygame.draw.line(win, crosshair_color, (WIDTH // 2, HEIGHT // 2 - 10), (WIDTH // 2, HEIGHT // 2 + 10), 2)
        pygame.draw.circle(win, crosshair_color, (WIDTH // 2, HEIGHT // 2), 4, 1)

        # Dynamic outer crosshair ring
        if current_speed > 0:
            ring_radius = int(lerp(10, 30, current_speed / max_speed_warp))
            ring_color = (COLOR_YELLOW_BRIGHT[0], COLOR_YELLOW_BRIGHT[1], COLOR_YELLOW_BRIGHT[2], int(lerp(0, 200, current_speed / max_speed_warp)))
            ring_color = (ring_color[0], ring_color[1], ring_color[2], max(0, min(255, ring_color[3])))
            
            s_ring = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s_ring, ring_color, (ring_radius, ring_radius), ring_radius, 2)
            win.blit(s_ring, (WIDTH // 2 - ring_radius, HEIGHT // 2 - ring_radius))


        pygame.display.flip() 
        clock.tick(60) 

    pygame.quit()

if __name__ == "__main__":
    main()
