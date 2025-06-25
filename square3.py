import pygame
import random
import math

# Window setup
WIDTH, HEIGHT = 800, 600
NUM_STARS = 100

# Colors
WHITE = (255, 255, 255)
CYAN = (0, 200, 255)
YELLOW = (200, 200, 0)

class Star:
    def __init__(self):
        self.x = random.uniform(-1000, 1000)
        self.y = random.uniform(-1000, 1000)
        self.z = random.uniform(1, 1000)
        self.size = random.uniform(1, 3)

    def update(self):
        self.z -= 5
        if self.z < 1:
            self.z = 1000
            self.x = random.uniform(-1000, 1000)
            self.y = random.uniform(-1000, 1000)

    def project(self, win):
        factor = 200 / (200 - self.z + 0.001)
        x = self.x * factor + WIDTH//2
        y = self.y * factor + HEIGHT//2
        size = self.size * factor
        pygame.draw.rect(win, WHITE, (x, y, size, size))

def draw_3d_square(win, angle, scale):
    size = 60 * scale
    points = [[-size, -size, 200],
              [ size, -size, 200],
              [ size,  size, 200],
              [-size,  size, 200]]

    projected = []
    for x, y, z in points:
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        x, z = x * cos_a - z * sin_a, x * sin_a + z * cos_a
        factor = 200 / (200 - z + 0.001)
        projected.append((x * factor + WIDTH//2 - 200, y * factor + HEIGHT//2))

    pygame.draw.polygon(win, YELLOW, projected, 2)

def draw_3d_cube(win, angle_x, angle_y, angle_z, scale):
    size = 100 * scale
    vertices = [[-size, -size, -size], [ size, -size, -size], [ size,  size, -size], [-size,  size, -size],
                [-size, -size,  size], [ size, -size,  size], [ size,  size,  size], [-size,  size,  size]]

    projected = []
    for x, y, z in vertices:
        # rotation around X
        cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
        # rotation around Y
        cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
        x, z = x * cos_y - z * sin_y, x * sin_y + z * cos_y
        # rotation around Z
        cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
        # projection
        factor = 200 / (200 - z + 0.001)
        projected.append((x * factor + WIDTH//2 + 200, y * factor + HEIGHT//2))

    faces = [
        (0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (1,2,6,5), (0,3,7,4)
    ]
    for face in faces:
        pygame.draw.polygon(win, CYAN, [projected[i] for i in face])

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    stars = [Star() for _ in range(NUM_STARS)]

    angle_x = angle_y = angle_z = 0.0
    angle_square = 0.0
    scale = 1.0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        # Rotate with arrows
        if keys[pygame.K_LEFT]: angle_y -= 0.03
        if keys[pygame.K_RIGHT]: angle_y += 0.03
        if keys[pygame.K_UP]: angle_x -= 0.03
        if keys[pygame.K_DOWN]: angle_x += 0.03
        # Scale
        if keys[pygame.K_w]: scale += 0.01
        if keys[pygame.K_s]: scale -= 0.01
        scale = max(0.1, min(3.0, scale))
        # Quit with ESC
        if keys[pygame.K_ESCAPE]: running = False

        win.fill((0, 0, 0))

        for star in stars:
            star.update()
            star.project(win)

        draw_3d_square(win, angle_square, scale)
        draw_3d_cube(win, angle_x, angle_y, angle_z, scale)

        angle_square += 0.02
        angle_z += 0.01

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
