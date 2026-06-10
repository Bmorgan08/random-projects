import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import cv2

# --- Initial vertical keystone scales ---
TOP_LEFT = (-1.0, 1.0)    # (x, y) scale for top-left corner
TOP_RIGHT = (1.0, 1.0)   # (x, y) scale for top-right corner
BOTTOM_RIGHT = (1.0, -1.0) # (x, y) scale for bottom-right corner
BOTTOM_LEFT = (-1.0, -1.0)  # (x, y) scale for bottom-left corner
SCALE_STEP = 0.01  # amount to change per key press

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((0,0), DOUBLEBUF | OPENGL | FULLSCREEN)
pygame.display.set_caption("Vertical Keystone Fullscreen Demo")

# OpenGL setup
glEnable(GL_TEXTURE_2D)
texture_id = glGenTextures(1)

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Failed to open webcam/video")
    exit()

def update_texture(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.ascontiguousarray(frame, dtype=np.uint8)
    h, w, _ = frame.shape

    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, frame)

def draw_quad(top_left, top_right, bottom_right, bottom_left):
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    # Top-left
    glTexCoord2f(0, 0)
    glVertex2f(top_left[0], top_left[1])
    # Top-right
    glTexCoord2f(1, 0)
    glVertex2f(top_right[0], top_right[1])
    # Bottom-right
    glTexCoord2f(1, 1)
    glVertex2f(bottom_right[0], bottom_right[1])
    # Bottom-left
    glTexCoord2f(0, 1)
    glVertex2f(bottom_left[0], bottom_left[1])

    glEnd()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            k = event.key
            if k == K_ESCAPE:
                running = False
                break
            elif k == K_w:  # Move top edge up
                TOP_LEFT = (TOP_LEFT[0], TOP_LEFT[1] + SCALE_STEP)
                break
            elif k == K_s:  # Move top edge down
                TOP_LEFT = (TOP_LEFT[0], TOP_LEFT[1] - SCALE_STEP)
                break
            elif k == K_a:  # Move left edge left
                TOP_LEFT = (TOP_LEFT[0] - SCALE_STEP, TOP_LEFT[1])
                break
            elif k == K_d:  # Move right edge right
                TOP_LEFT = (TOP_LEFT[0] + SCALE_STEP, TOP_LEFT[1])
                break
            elif k == K_i:  # Move bottom edge up
                TOP_RIGHT = (TOP_RIGHT[0], TOP_RIGHT[1] + SCALE_STEP)
                break
            elif k == K_k:  # Move bottom edge down
                TOP_RIGHT = (TOP_RIGHT[0], TOP_RIGHT[1] - SCALE_STEP)
                break
            elif k == K_j:  # Move left edge right
                TOP_RIGHT = (TOP_RIGHT[0] - SCALE_STEP, TOP_RIGHT[1])
                break
            elif k == K_l:  # Move right edge left
                TOP_RIGHT = (TOP_RIGHT[0] + SCALE_STEP, TOP_RIGHT[1])
                break
            elif k == K_UP:  # Move bottom edge up
                BOTTOM_LEFT = (BOTTOM_LEFT[0], BOTTOM_LEFT[1] + SCALE_STEP)
                break
            elif k == K_DOWN:  # Move bottom edge down
                BOTTOM_LEFT = (BOTTOM_LEFT[0], BOTTOM_LEFT[1] - SCALE_STEP)
                break
            elif k == K_LEFT:  # Move bottom edge left
                BOTTOM_LEFT = (BOTTOM_LEFT[0] - SCALE_STEP, BOTTOM_LEFT[1])
                break
            elif k == K_RIGHT:  # Move bottom edge right
                BOTTOM_LEFT = (BOTTOM_LEFT[0] + SCALE_STEP, BOTTOM_LEFT[1])
                break
            elif k == K_z: 
                BOTTOM_RIGHT = (BOTTOM_RIGHT[0], BOTTOM_RIGHT[1] + SCALE_STEP)
                break
            elif k == K_x:
                BOTTOM_RIGHT = (BOTTOM_RIGHT[0], BOTTOM_RIGHT[1] - SCALE_STEP)
                break
            elif k == K_c:
                BOTTOM_RIGHT = (BOTTOM_RIGHT[0] - SCALE_STEP, BOTTOM_RIGHT[1])
                break
            elif k == K_v:
                BOTTOM_RIGHT = (BOTTOM_RIGHT[0] + SCALE_STEP, BOTTOM_RIGHT[1])
                break

            elif k == K_t:
                print("Current corner scales:")
                print(f"  TOP_LEFT: {TOP_LEFT}")
                print(f"  TOP_RIGHT: {TOP_RIGHT}")
                print(f"  BOTTOM_RIGHT: {BOTTOM_RIGHT}")
                print(f"  BOTTOM_LEFT: {BOTTOM_LEFT}")

            elif k == K_f:
                #set to laurens preferences
                TOP_LEFT = (-0.8599999999999999, 0.39999999999999947)
                TOP_RIGHT = (1.0, 0.39999999999999947)
                BOTTOM_RIGHT = (1.0, -0.99)
                BOTTOM_LEFT = (-0.99, -0.99)

            elif k == K_g:
                #set to my preferences
                TOP_LEFT = (-0.7999999999999998, 0.26999999999999935)
                TOP_RIGHT = (0.7599999999999998, 0.26999999999999935)
                BOTTOM_RIGHT = (0.7899999999999998, -0.6699999999999993)
                BOTTOM_LEFT = (-0.8899999999999998, -0.6699999999999993)


    ret, frame = cap.read()
    if not ret:
        break

    update_texture(frame)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_quad(TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT)
    pygame.display.flip()
    pygame.time.wait(10)

cap.release()
pygame.quit()