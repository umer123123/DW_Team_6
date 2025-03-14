import streamlit as st
import pygame
import random
import numpy as np
import io
from PIL import Image
import time

# Initialize Pygame
pygame.init()

# Screen size
WIDTH = 800
HEIGHT = 400

# Game states
game_started = False
game_over = False
score = 0
lives = 3  # Player starts with 3 lives
is_running_sound_playing = False  # Track running sound state
colorblind_mode = False  # Track colorblind mode

# Player attributes
player = pygame.image.load("images/player.png")
player_rect = player.get_rect()
player_rect.x = 100
player_rect.y = HEIGHT - 60
player_dy = 0  # Vertical velocity

grav = 0.5  # Gravity
jump_power = -15  # Jump strength

# Obstacles & Hearts
obstacles = []
hearts = []
obstacle_speed = 5
obstacle_spawn_time = 90  # Frames before spawning a new obstacle
heart_spawn_time = 400  # Frames before a heart appears
spawn_counter = 0
heart_counter = 0
obstacle_type = 0  # Toggle between 0 (obstacle1) and 1 (obstacle2)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Game loop
def reset_game():
    global player_rect, obstacles, hearts, score, game_over, spawn_counter, heart_counter, obstacle_type, is_running_sound_playing, lives
    player_rect.x = 100
    player_rect.y = HEIGHT - 60
    obstacles.clear()
    hearts.clear()
    score = 0
    spawn_counter = 0
    heart_counter = 0
    game_over = False
    obstacle_type = 0  # Reset obstacle alternation
    lives = 3  # Reset lives

def game_update():
    global spawn_counter, heart_counter, score, game_over, obstacle_type, is_running_sound_playing, lives
    if not game_started or game_over:
        return  # Don't update game if it's not started or game over

    # Apply gravity
    global player_rect, player_dy
    player_dy += grav
    player_rect.y += player_dy

    # Keep player on screen
    if player_rect.y > HEIGHT - 60:
        player_rect.y = HEIGHT - 60
        player_dy = 0

    # Move obstacles & hearts
    for obstacle in obstacles:
        obstacle.x -= obstacle_speed

    for heart in hearts:
        heart.x -= obstacle_speed

    # Remove off-screen objects
    obstacles[:] = [ob for ob in obstacles if ob.x > -50]
    hearts[:] = [heart for heart in hearts if heart.x > -50]

    # Spawn obstacles alternately
    spawn_counter += 1
    if spawn_counter >= obstacle_spawn_time:
        spawn_counter = 0
        if colorblind_mode:
            if obstacle_type == 0:
                obstacles.append(pygame.Rect(WIDTH, HEIGHT - 60, 40, 40))  # Colorblind obstacle 1
                obstacle_type = 1
            else:
                obstacles.append(pygame.Rect(WIDTH, HEIGHT - 60, 40, 40))  # Colorblind obstacle 2
                obstacle_type = 0
        else:
            if obstacle_type == 0:
                obstacles.append(pygame.Rect(WIDTH, HEIGHT - 60, 40, 40))  # Normal obstacle 1
                obstacle_type = 1
            else:
                obstacles.append(pygame.Rect(WIDTH, HEIGHT - 60, 40, 40))  # Normal obstacle 2
                obstacle_type = 0

    # Spawn hearts randomly
    heart_counter += 1
    if heart_counter >= heart_spawn_time:
        heart_counter = 0
        if random.random() < 0.5:  # 50% chance to spawn a heart
            hearts.append(pygame.Rect(WIDTH, HEIGHT - 100, 30, 30))  # Heart appears higher

    # Collision detection - Obstacles
    global lives
    for obstacle in obstacles:
        if player_rect.colliderect(obstacle):
            obstacles.remove(obstacle)  # Remove obstacle on collision
            lives -= 1  # Lose a life
            if lives <= 0:  # If lives run out, game over
                game_over = True

    # Collision detection - Hearts (Power-up)
    for heart in hearts:
        if player_rect.colliderect(heart):
            hearts.remove(heart)  # Remove heart when collected
            if lives < 3:  # Only increase life if it's less than 3
                lives += 1

    # Score keeping
    score += 1

def game_draw():
    screen.fill((0, 0, 0))  # Fill the screen with black

    # Draw score
    screen.blit(player, player_rect)
    for obstacle in obstacles:
        pygame.draw.rect(screen, (255, 0, 0), obstacle)  # Draw red obstacles

    for heart in hearts:
        pygame.draw.rect(screen, (0, 255, 0), heart)  # Draw green hearts

    # Draw lives (Hearts on screen)
    for i in range(lives):
        pygame.draw.circle(screen, (255, 0, 0), (WIDTH - 100 + (i * 30), 30), 15)

    if game_over:
        game_over_text = pygame.font.SysFont("Arial", 30).render("Game Over! Press ENTER to Restart", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    # Convert the screen to a format Streamlit can display
    pygame.image.save(screen, "game_frame.png")
    img = Image.open("game_frame.png")
    return img

# Streamlit App

st.title("Pygame Zero on Streamlit")

col1, col2 = st.columns([3, 1])

# Game Start or Game Over check
if not game_started:
    st.text("Press 'Enter' to Start")
else:
    st.text(f"Score: {score}  Lives: {lives}")
    if game_over:
        st.text("Game Over! Press 'Enter' to Restart")

# Handle user input for movement
user_input = st.text_input("Press 'Space' to jump", key="input")

if user_input == 'enter':
    if not game_started:
        game_started = True
        reset_game()
    else:
        if game_over:
            game_over = False
            reset_game()

if user_input == 'space' and player_rect.y == HEIGHT - 60 and game_started:
    player_dy = jump_power

# Update and draw the game
game_update()

# Get and display the frame
img = game_draw()

# Show image on Streamlit
col1.image(img, caption="Game Frame", use_column_width=True)

# Refresh at the right speed
time.sleep(0.05)
