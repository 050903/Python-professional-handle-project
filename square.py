import pygame
import random
import math
import os

# Window dimensions
WIDTH, HEIGHT = 800, 600
NUM_STARS = 100

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
        pygame.draw.rect(win, (255, 255, 255), (x, y, size, size))

def draw_rotating_cube(win, angle_x, angle_y, angle_z):
    size = 100
    vertices = [
        [-size, -size, -size],
        [ size, -size, -size],
        [ size,  size, -size],
        [-size,  size, -size],
        [-size, -size,  size],
        [ size, -size,  size],
        [ size,  size,  size],
        [-size,  size,  size],
    ]
    projected = []

    for x, y, z in vertices:
        # Rotation around X
        cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
        # Rotation around Y
        cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
        x, z = x * cos_y - z * sin_y, x * sin_y + z * cos_y
        # Rotation around Z
        cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z

        # Projection
        factor = 200 / (200 - z + 0.001)
        x_proj = x * factor + WIDTH//2
        y_proj = y * factor + HEIGHT//2
        projected.append((x_proj, y_proj))

    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7),
    ]

    for start, end in edges:
        pygame.draw.line(win, (0, 200, 255), projected[start], projected[end], 2)

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    stars = [Star() for _ in range(NUM_STARS)]

    angle_x = angle_y = angle_z = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        win.fill((0, 0, 0))

        # Draw stars
        for star in stars:
            star.update()
            star.project(win)

        # Draw rotating cube
        draw_rotating_cube(win, angle_x, angle_y, angle_z)

        # Increment rotation angles
        angle_x += 0.01
        angle_y += 0.02
        angle_z += 0.015

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
    # os.system("python galaxy.py")  # optional autorun
