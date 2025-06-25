import pygame
import random
import math
import time

# --- Global Constants & Configuration ---
WIDTH, HEIGHT = 1200, 800  # Wider screen for more immersive view
NUM_STARS = 500  # More stars for a denser field
FOG_COLOR = (5, 5, 15)  # Very dark blue-purple for deep space
WARP_SPEED_THRESHOLD = 50  # Speed at which warp effect kicks in (no longer directly used but good for context)
MAX_STAR_SIZE = 5
MIN_STAR_SIZE = 0.5
STAR_PROJECTION_DISTANCE = 400 # 'Focal length' for star perspective

# Camera & World Settings
CAMERA_DEFAULT_Z = 300
CAMERA_NEAR_CLIP = 1.0 # Objects closer than this are clipped
CAMERA_FAR_CLIP = 5000.0 # Objects further than this are clipped or fade out
WORLD_SIZE = 2000 # Defines the bounds of our 3D world (for star reset, etc.)

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
COLOR_RED = (255, 0, 0) # Added missing color definition

# --- Pygame Initialization ---
pygame.init()
# Double buffering for smoother animation, HWSURFACE for potential hardware acceleration
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("Project Starflight: Hyperspace Initiative v.2035")
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
    # Rotate around Y-axis
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y # Corrected Y-rotation
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

    return (projected_x, projected_y, size_factor) # Return size factor for depth-based effects

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
        self.z = random.uniform(CAMERA_DEFAULT_Z + 10, CAMERA_FAR_CLIP - 100)
        self.size = self.initial_size # Reset to original size
        self.trail_length = 0
        self.trail_alpha = 255

    def update(self, delta_z, warp_factor=0.0):
        """Updates the star's position and visual properties based on speed and warp factor."""
        self.z += delta_z # Move relative to camera
        
        # Apply additional speed boost during warp
        self.z -= delta_z * warp_factor * 10 
        
        # Warp effect: adjust trail length, alpha, and size
        if warp_factor > 0.1:
            self.trail_length = lerp(self.trail_length, MAX_STAR_SIZE * 20 * warp_factor, 0.1)
            self.trail_alpha = lerp(self.trail_alpha, 50, 0.1)
            self.size = lerp(self.size, MAX_STAR_SIZE * 2, 0.1)
        else:
            self.trail_length = lerp(self.trail_length, 0, 0.1)
            self.trail_alpha = lerp(self.trail_alpha, 255, 0.1)
            # Lerp back to original size when not warping
            self.size = lerp(self.size, self.initial_size, 0.1) 

        # Reset if star passes camera or goes too far
        if self.z < CAMERA_NEAR_CLIP or self.z > CAMERA_FAR_CLIP:
            # If it went too far, reset to the far end
            if self.z > CAMERA_FAR_CLIP:
                self.z = CAMERA_NEAR_CLIP + WORLD_SIZE + random.uniform(0, WORLD_SIZE) # Reset to far, but still behind camera
            else: # If it passed by (z < near clip), reset to far end
                self.z = CAMERA_FAR_CLIP - 100 - random.uniform(0, WORLD_SIZE) # Place it clearly visible, but far

    def draw(self, win, camera_pos):
        """Draws the star and its warp trail."""
        projected = project_point((self.x, self.y, self.z), camera_pos[0], camera_pos[1], camera_pos[2], WIDTH // 2, HEIGHT // 2, STAR_PROJECTION_DISTANCE)

        if projected is None: return # Star is clipped

        px, py, size_factor = projected
        
        # Smooth size based on projection and current star size
        current_size = max(0.5, self.size * size_factor)

        # Fading based on distance and trail alpha
        alpha = int(lerp(0, 255, size_factor) * (self.trail_alpha / 255))
        # Ensure alpha is within valid range [0, 255]
        alpha = max(0, min(255, alpha)) 
        star_color = (self.base_color[0], self.base_color[1], self.base_color[2], alpha)

        # Draw the main star point (use `pygame.SRCALPHA` for per-pixel alpha blending)
        s = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, star_color, (int(current_size), int(current_size)), int(current_size / 2))
        win.blit(s, (int(px - current_size), int(py - current_size)))

        # Draw warp trail
        if self.trail_length > 0.5:
            # Calculate trail end point behind the star
            trail_end_z = self.z + self.trail_length 
            
            # Project the trail end point
            projected_trail_end = project_point((self.x, self.y, trail_end_z), camera_pos[0], camera_pos[1], camera_pos[2], WIDTH // 2, HEIGHT // 2, STAR_PROJECTION_DISTANCE)

            if projected_trail_end:
                tx, ty, _ = projected_trail_end
                # Faded trail color
                trail_color = (self.base_color[0], self.base_color[1], self.base_color[2], int(alpha * 0.5)) 
                # Ensure trail color alpha is valid
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
            world_z = center_z + i * self.spacing # Calculate world Z for this line segment
            
            # Fade and thin lines based on distance
            distance_from_camera = abs(world_z - center_z)
            alpha = max(0, 255 - int(distance_from_camera / 10))
            line_thickness = max(1, 3 - int(distance_from_camera / 200))
            
            line_color = (COLOR_DARK_GREY[0], COLOR_DARK_GREY[1], COLOR_DARK_GREY[2] + int(alpha * 0.1), alpha)
            # Ensure alpha is within valid range
            line_color = (line_color[0], line_color[1], line_color[2], max(0, min(255, line_color[3])))

            # Project two points on the line (left and right edges of the screen view)
            p1 = project_point((-WORLD_SIZE, self.plane_y_offset, world_z), center_x, center_y, center_z, WIDTH // 2, HEIGHT // 2)
            p2 = project_point((WORLD_SIZE, self.plane_y_offset, world_z), center_x, center_y, center_z, WIDTH // 2, HEIGHT // 2)

            if p1 and p2:
                # Use a surface for alpha blending lines
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(s, line_color, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), line_thickness)
                win.blit(s, (0,0))

        # Vertical lines
        for i in range(-self.num_lines // 2, self.num_lines // 2 + 1):
            world_x = center_x + i * self.spacing # Lines move with camera X
            
            # Fade and thin lines based on distance
            distance_from_camera_x = abs(world_x - center_x)
            alpha_x = max(0, 255 - int(distance_from_camera_x / 10))
            line_thickness_x = max(1, 3 - int(distance_from_camera_x / 200))

            line_color_x = (COLOR_DARK_GREY[0] + int(alpha_x * 0.1), COLOR_DARK_GREY[1], COLOR_DARK_GREY[2], alpha_x)
            # Ensure alpha is within valid range
            line_color_x = (line_color_x[0], line_color_x[1], line_color_x[2], max(0, min(255, line_color_x[3])))

            # Project two points on the line (from front to back of visible plane)
            p1 = project_point((world_x, self.plane_y_offset, CAMERA_NEAR_CLIP + center_z), center_x, center_y, center_z, WIDTH // 2, HEIGHT // 2)
            p2 = project_point((world_x, self.plane_y_offset, CAMERA_FAR_CLIP + center_z), center_x, center_y, center_z, WIDTH // 2, HEIGHT // 2)

            if p1 and p2:
                # Use a surface for alpha blending lines
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
        pass # To be overridden by subclasses for animation

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
        
        projected_vertices = []
        for v in transformed_vertices:
            proj = project_point(v, center_x, center_y, center_z, WIDTH // 2, HEIGHT // 2)
            projected_vertices.append(proj)

        # Basic Back-Face Culling and Z-sorting (per face)
        drawable_faces = []
        for i, face in enumerate(self.faces):
            # Calculate average Z-depth of the face for sorting
            # Only consider faces where all vertices are visible
            if all(projected_vertices[v_idx] is not None for v_idx in face):
                face_avg_z = sum(transformed_vertices[v_idx][2] for v_idx in face) / len(face)
                drawable_faces.append((face_avg_z, i)) # Store (avg_z, original_index)

        drawable_faces.sort(key=lambda x: x[0], reverse=True) # Sort from furthest to closest

        for avg_z, face_idx in drawable_faces:
            face = self.faces[face_idx]
            color = self.get_face_color(face_idx, transformed_vertices) # Get color with lighting
            
            # Draw only if all points of the projected face are valid
            projected_face_points = [projected_vertices[v_idx] for v_idx in face]
            if all(p is not None for p in projected_face_points):
                # Extract (x,y) from (x,y,size_factor) tuple
                points_2d = [(p[0], p[1]) for p in projected_face_points]
                
                # Create a surface for alpha blending the polygon
                # Determine bounds for the surface to optimize drawing
                min_x = min(p[0] for p in points_2d)
                max_x = max(p[0] for p in points_2d)
                min_y = min(p[1] for p in points_2d)
                max_y = max(p[1] for p in points_2d)

                surf_width = int(max_x - min_x) + 2 # +2 for border
                surf_height = int(max_y - min_y) + 2
                
                if surf_width > 0 and surf_height > 0:
                    s = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
                    # Adjust points to be relative to the new surface's top-left corner
                    relative_points_2d = [(p[0] - min_x + 1, p[1] - min_y + 1) for p in points_2d] # +1 for border offset
                    
                    pygame.draw.polygon(s, color, relative_points_2d, 0)
                    pygame.draw.lines(s, (0, 0, 0), True, relative_points_2d, 1) # Thin black border
                    win.blit(s, (int(min_x), int(min_y)))


    def get_face_color(self, face_idx, transformed_vertices):
        """Calculates the color of a face with simple lighting.
        Note: For accurate lighting, face normals should be dynamically calculated
        from the transformed vertices and then used for dot product with light direction.
        The current 'normals' array assumes an unrotated base shape."""
        
        # Simple light direction (top-left-front)
        light_direction = (1, 1, -1) 
        
        # Predefined normals for a cube (simplistic for demonstration)
        normals = [
            (0, 0, -1),   # Front face
            (0, 0, 1),    # Back face
            (0, -1, 0),   # Bottom face
            (0, 1, 0),    # Top face
            (1, 0, 0),    # Right face
            (-1, 0, 0)    # Left face
        ]
        
        # Ensure face_idx is within bounds
        if face_idx < len(normals):
            face_normal = normals[face_idx]
        else:
            # Fallback for composite objects or if normals array is smaller than faces
            # In a real engine, you'd calculate this from the face's vertices
            face_normal = (0,0,0) # Default to no lighting influence

        # Calculate dot product to determine light intensity
        # Normalize light_direction for correct dot product
        light_dir_len = math.sqrt(light_direction[0]**2 + light_direction[1]**2 + light_direction[2]**2)
        if light_dir_len > 0:
            norm_light_direction = (light_direction[0]/light_dir_len, light_direction[1]/light_dir_len, light_direction[2]/light_dir_len)
        else:
            norm_light_direction = (0,0,0)

        dot_product = (face_normal[0] * norm_light_direction[0] + 
                       face_normal[1] * norm_light_direction[1] + 
                       face_normal[2] * norm_light_direction[2])
        
        # Simple diffuse lighting model: intensity based on angle to light
        # Clamp between a minimum brightness (0.2) and full brightness (1.0)
        light_intensity = max(0.2, min(1.0, dot_product)) 
        
        # Apply base color and lighting
        base_r, base_g, base_b = self.color
        
        # Apply a subtle gradient for faces to show depth/material
        # This is an arbitrary aesthetic choice, not based on physics
        gradient_factor = 1.0 - (face_idx / len(self.faces) * 0.2) 
        
        final_r = int(base_r * light_intensity * gradient_factor)
        final_g = int(base_g * light_intensity * gradient_factor)
        final_b = int(base_b * light_intensity * gradient_factor)
        
        # Clamp color components to [0, 255]
        final_r = max(0, min(255, final_r))
        final_g = max(0, min(255, final_g))
        final_b = max(0, min(255, final_b))

        return (final_r, final_g, final_b)


class Cube(Base3DObject):
    """A simple 3D cube object."""
    def __init__(self, position, size, color=(200, 200, 0)):
        super().__init__(position, size, color)
        s = 0.5 # Unit cube size, before scaling
        self.vertices = [
            (-s, -s, -s), ( s, -s, -s), ( s, s, -s), (-s, s, -s),   # Front face vertices (0-3)
            (-s, -s, s), ( s, -s, s), ( s, s, s), (-s, s, s)        # Back face vertices (4-7)
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
            (0, s, 0),       # Apex (0)
            (-s, -s, -s),    # Base Front-Left (1)
            (s, -s, -s),     # Base Front-Right (2)
            (s, -s, s),      # Base Back-Right (3)
            (-s, -s, s)      # Base Back-Left (4)
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
        
        # Determine base color based on which part the face belongs to
        main_body_faces_end = len(self.main_body_faces)
        left_wing_faces_end = main_body_faces_end + len(self.left_wing_faces)
        right_wing_faces_end = left_wing_faces_end + len(self.right_wing_faces)
        
        if face_idx < main_body_faces_end: # Main body
            base_color = (150, 150, 255) # Blueish-purple
        elif face_idx < left_wing_faces_end: # Left wing
            base_color = (100, 100, 180) # Darker blueish-purple
        elif face_idx < right_wing_faces_end: # Right wing
            base_color = (100, 100, 180) # Darker blueish-purple
        else: # Cockpit (or other parts)
            base_color = (80, 80, 120) # Even darker, for cockpit glass effect

        # Simple light source for pulsing effect (not based on actual normals)
        # This creates a visual effect rather than physically accurate lighting
        light_intensity = 0.8 + math.sin(time.time() * 3 + face_idx * 0.5) * 0.2 # Slight pulsing light
        light_intensity = max(0.5, min(1.0, light_intensity)) # Clamp intensity

        final_r = int(base_color[0] * light_intensity)
        final_g = int(base_color[1] * light_intensity)
        final_b = int(base_color[2] * light_intensity)

        # Clamp color components to [0, 255]
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
        if self.current_lifetime <= 0: return # Don't draw dead particles

        projected = project_point((self.x, self.y, self.z), camera_pos[0], camera_pos[1], camera_pos[2], WIDTH // 2, HEIGHT // 2)
        if projected is None: return # Particle is clipped

        px, py, size_factor = projected
        current_size = max(0.5, self.size * size_factor)

        # Calculate alpha based on remaining lifetime
        alpha = int(255 * (self.current_lifetime / self.lifetime))
        alpha = max(0, min(255, alpha)) # Clamp alpha
        particle_color = (self.color[0], self.color[1], self.color[2], alpha)
        
        if current_size > 0.5:
            # Use a surface for alpha blended circles
            s = pygame.Surface((int(current_size * 2), int(current_size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, particle_color, (int(current_size), int(current_size)), int(current_size / 2))
            win.blit(s, (int(px - current_size), int(py - current_size)))


class ParticleSystem:
    """Manages a collection of particles, used for effects like engine trails."""
    def __init__(self, source_pos_relative, max_particles, color, size_range, velocity_range, lifetime_range, emission_rate):
        # source_pos_relative is (relative_x, relative_y, relative_z) from the parent object's origin
        self.source_pos_relative = source_pos_relative 
        self.max_particles = max_particles
        self.particles = []
        self.color = color
        self.size_range = size_range
        self.velocity_range = velocity_range # (min_vx, max_vx, min_vy, max_vy, min_vz, max_vz)
        self.lifetime_range = lifetime_range
        self.emission_rate = emission_rate # particles per second
        self.time_since_last_emission = 0

    def update(self, dt, parent_pos, parent_rotation, camera_delta_z):
        """Updates particle system, emitting new particles and updating existing ones."""
        self.time_since_last_emission += dt

        # Emit new particles based on emission rate and delta time
        particles_to_emit = int(self.time_since_last_emission * self.emission_rate)
        for _ in range(particles_to_emit):
            if len(self.particles) < self.max_particles:
                # Calculate world position of particle source by rotating and translating
                # the relative source position based on the parent object's state
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
        
        # Deduct time from the emission accumulator
        self.time_since_last_emission -= particles_to_emit / self.emission_rate

        # Update existing particles and remove dead ones
        live_particles = []
        for p in self.particles:
            p.update(dt, camera_delta_z)
            if p.current_lifetime > 0:
                live_particles.append(p)
        self.particles = live_particles

    def draw(self, win, camera_pos):
        """Draws all active particles, sorting them by Z-depth for correct rendering."""
        # Sort particles by Z-depth for proper drawing order (further first)
        self.particles.sort(key=lambda p: p.z, reverse=True)
        for p in self.particles:
            p.draw(win, camera_pos)

# --- Main Game Loop ---
def main():
    stars = [Star() for _ in range(NUM_STARS)]
    ground_plane = GroundPlane()
    
    # 3D Objects in the scene
    objects = []
    objects.append(Cube((200, 50, 500), 100, COLOR_RED))
    objects.append(Pyramid((-300, 0, 700), 80, COLOR_GREEN_NEON))
    # This ShipModel represents a stationary 'station' or large object in the world
    station_scale = 150 # Define the scale here
    objects.append(ShipModel((0, 0, 1000), station_scale, (200,200,255))) 

    # Camera State
    camera_x, camera_y, camera_z = 0.0, 0.0, 0.0 # World coordinates (floats for smooth movement)
    camera_target_x, camera_target_y = 0.0, 0.0 # For smooth horizontal/vertical movement
    camera_lerp_factor = 3.0 # How quickly camera smooths to target (per second)
    
    # Player speed
    current_speed = 0.0 # Forward/Backward speed
    target_speed = 0.0
    max_speed_normal = 200 # Max speed when not warping (units/second)
    max_speed_warp = 1500 # Max speed when warping (units/second)
    acceleration = 100 # Units/second^2
    deceleration = 200 # Units/second^2
    strafe_speed_base = 200 # Units/second
    vertical_speed_base = 100 # Units/second

    warp_mode_active = False
    warp_factor = 0.0 # 0.0 to 1.0, controls intensity of warp effect

    # Engine particle systems
    # Source pos is relative to ShipModel's origin (0,0,0) after its own scaling.
    # The (X,Y,Z) values need to be relative to the ship's overall dimensions,
    # so multiply by the station_scale.
    engine_left_ps = ParticleSystem(
        (-0.8 * station_scale, -0.1 * station_scale, 0.8 * station_scale), # Approx back-left of ship
        500, COLOR_ORANGE, (1, 4), (-10, 10, -10, 10, 50, 100), (0.5, 1.5), 1000 # Increased emission rate
    )
    engine_right_ps = ParticleSystem(
        (0.8 * station_scale, -0.1 * station_scale, 0.8 * station_scale), # Approx back-right of ship
        500, COLOR_ORANGE, (1, 4), (-10, 10, -10, 10, 50, 100), (0.5, 1.5), 1000 # Increased emission rate
    )


    # User input states
    keys = {
        'forward': False, 'backward': False, 'left': False, 'right': False,
        'up': False, 'down': False, 'warp': False
    }

    last_time = time.time()
    running = True

    while running:
        dt = time.time() - last_time # Delta time for frame-rate independent movement
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
                if event.key == pygame.K_e: # Warp toggle
                    keys['warp'] = not keys['warp']
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w: keys['forward'] = False
                if event.key == pygame.K_s: keys['backward'] = False
                if event.key == pygame.K_a: keys['left'] = False
                if event.key == pygame.K_d: keys['right'] = False
                if event.key == pygame.K_SPACE: keys['up'] = False
                if event.key == pygame.K_LSHIFT: keys['down'] = False
                # No 'pass' needed here, as the toggle is handled on KEYDOWN

        # --- Update Game State ---
        
        # Speed control and warp effect
        if keys['warp']:
            target_speed = max_speed_warp
            warp_factor = lerp(warp_factor, 1.0, 5.0 * dt) # Smoothly activate warp effect (faster transition)
        else:
            target_speed = max_speed_normal
            warp_factor = lerp(warp_factor, 0.0, 5.0 * dt) # Smoothly deactivate warp effect (faster transition)

        if keys['forward']:
            current_speed = min(target_speed, current_speed + acceleration * dt)
        elif keys['backward']:
            current_speed = max(-max_speed_normal / 2, current_speed - acceleration * dt) # Can go backward, but slower
        else:
            # Decelerate when no forward/backward input
            if current_speed > 0:
                current_speed = max(0.0, current_speed - deceleration * dt)
            elif current_speed < 0:
                current_speed = min(0.0, current_speed + deceleration * dt)
        
        # Calculate camera's Z movement based on current speed
        camera_delta_z = current_speed * dt 
        camera_z += camera_delta_z # Directly update camera_z for continuous motion

        # Strafe left/right
        if keys['left']: 
            camera_target_x -= strafe_speed_base * dt
        if keys['right']: 
            camera_target_x += strafe_speed_base * dt
        
        # Vertical movement
        if keys['up']: 
            camera_target_y -= vertical_speed_base * dt
        if keys['down']: 
            camera_target_y += vertical_speed_base * dt

        # Smooth camera X and Y movement (LERP to target)
        camera_x = lerp(camera_x, camera_target_x, camera_lerp_factor * dt)
        camera_y = lerp(camera_y, camera_target_y, camera_lerp_factor * dt)
        
        # Keep camera X and Y within reasonable bounds for the ground plane effect
        camera_x = max(-WORLD_SIZE, min(WORLD_SIZE, camera_x))
        camera_y = max(-WORLD_SIZE / 2, min(WORLD_SIZE / 2, camera_y)) # Adjusted Y bounds

        # Update stars and objects
        for star in stars:
            star.update(camera_delta_z, warp_factor)
        
        for obj in objects:
            obj.update(dt) # Pass raw dt for consistent animation speed

        # Update particle systems, using the station's position and rotation
        ship = next((obj for obj in objects if isinstance(obj, ShipModel)), None)
        if ship:
            engine_left_ps.update(dt, (ship.x, ship.y, ship.z), (ship.angle_x, ship.angle_y, ship.angle_z), camera_delta_z)
            engine_right_ps.update(dt, (ship.x, ship.y, ship.z), (ship.angle_x, ship.angle_y, ship.angle_z), camera_delta_z)

        # --- Drawing ---
        win.fill(FOG_COLOR) # Deep space background

        # Layered effects for atmosphere/nebula (approximate)
        # These are drawn from bottom to top to simulate depth
        for i in range(5):
            alpha = int(lerp(0, 50, i / 4.0)) # Alpha increases as we go up
            color = (COLOR_BLUE_DEEP[0], COLOR_BLUE_DEEP[1], COLOR_BLUE_DEEP[2], alpha)
            # Ensure alpha is valid for drawing
            color = (color[0], color[1], color[2], max(0, min(255, alpha)))

            # Create semi-transparent rects that fade towards the horizon
            s = pygame.Surface((WIDTH, HEIGHT // 5 * (i + 1)), pygame.SRCALPHA)
            pygame.draw.rect(s, color, (0, 0, WIDTH, HEIGHT // 5 * (i + 1)))
            win.blit(s, (0, HEIGHT - (HEIGHT // 5) * (i + 1)))


        camera_current_pos = (camera_x, camera_y, camera_z)

        # Draw elements in a rough back-to-front order
        # (This is simplified; proper Z-buffering/sorting is complex)
        
        # Stars (furthest back)
        for star in stars:
            star.draw(win, camera_current_pos)

        # Ground Plane
        ground_plane.draw(win, camera_current_pos)
        
        # 3D Objects
        # Collect all drawable polygons from objects, then sort them by their average Z-depth
        all_polygons_to_draw = []
        for obj in objects:
            transformed_vertices = []
            for v in obj.vertices:
                rotated_v = rotate_point_3d(v, obj.angle_x, obj.angle_y, obj.angle_z)
                transformed_vertices.append((rotated_v[0] * obj.scale + obj.x, 
                                             rotated_v[1] * obj.scale + obj.y, 
                                             rotated_v[2] * obj.scale + obj.z))
            
            projected_vertices = []
            for v_world in transformed_vertices:
                proj = project_point(v_world, camera_x, camera_y, camera_z, WIDTH // 2, HEIGHT // 2)
                projected_vertices.append(proj)

            for i, face in enumerate(obj.faces):
                # Only add face to draw list if all its projected vertices are valid (not clipped)
                if all(projected_vertices[v_idx] is not None for v_idx in face):
                    face_avg_z = sum(transformed_vertices[v_idx][2] for v_idx in face) / len(face)
                    points_2d = [(projected_vertices[v_idx][0], projected_vertices[v_idx][1]) for v_idx in face]
                    color = obj.get_face_color(i, transformed_vertices)
                    all_polygons_to_draw.append((face_avg_z, color, points_2d))
        
        all_polygons_to_draw.sort(key=lambda x: x[0], reverse=True) # Sort furthest to closest

        for z_depth, color, points_2d in all_polygons_to_draw:
            if len(points_2d) >= 3: # Ensure it's a valid polygon (at least 3 vertices)
                # Drawing polygons with alpha requires a surface with SRCALPHA
                min_x = min(p[0] for p in points_2d)
                max_x = max(p[0] for p in points_2d)
                min_y = min(p[1] for p in points_2d)
                max_y = max(p[1] for p in points_2d)

                # Add a small buffer for lines
                surf_width = int(max_x - min_x) + 2 
                surf_height = int(max_y - min_y) + 2
                
                if surf_width > 0 and surf_height > 0:
                    s = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
                    relative_points_2d = [(p[0] - min_x + 1, p[1] - min_y + 1) for p in points_2d] 
                    
                    pygame.draw.polygon(s, color, relative_points_2d, 0) # Fill polygon
                    pygame.draw.lines(s, (0, 0, 0), True, relative_points_2d, 1) # Thin black border
                    win.blit(s, (int(min_x), int(min_y)))


        # Particle effects (drawn last so they are on top of objects)
        engine_left_ps.draw(win, camera_current_pos)
        engine_right_ps.draw(win, camera_current_pos)

        # --- UI/HUD (Futuristic Telemetry) ---
        font = pygame.font.Font(None, 24) # Default font, size 24
        
        speed_text = f"SPEED: {current_speed:.1f} U/S" # Units per second
        speed_color = COLOR_GREEN_NEON if warp_factor > 0.5 else COLOR_CYAN_LIGHT
        speed_render = font.render(speed_text, True, speed_color)
        win.blit(speed_render, (10, 10))

        warp_status_text = "WARP: ACTIVE" if warp_factor > 0.5 else "WARP: STANDBY"
        warp_status_color = COLOR_YELLOW_BRIGHT if warp_factor > 0.5 else COLOR_LIGHT_GREY
        warp_status_render = font.render(warp_status_text, True, warp_status_color)
        win.blit(warp_status_render, (10, 40))
        
        # A simple crosshair
        crosshair_color = COLOR_CYAN_LIGHT
        pygame.draw.line(win, crosshair_color, (WIDTH // 2 - 10, HEIGHT // 2), (WIDTH // 2 + 10, HEIGHT // 2), 2)
        pygame.draw.line(win, crosshair_color, (WIDTH // 2, HEIGHT // 2 - 10), (WIDTH // 2, HEIGHT // 2 + 10), 2)
        pygame.draw.circle(win, crosshair_color, (WIDTH // 2, HEIGHT // 2), 4, 1)

        pygame.display.flip() # Update the full display Surface to the screen
        clock.tick(60) # Limit frame rate to 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()