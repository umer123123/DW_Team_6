import pgzrun
import pygame
import random

# Screen dimensions
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
player = Actor("player", (100, HEIGHT - 60))
player.dy = 0  # Vertical velocity

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

# Load images
background = pygame.image.load("images/background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Resize obstacles for normal mode
original_obstacle1 = pygame.image.load("images/obstacle.png")
small_obstacle1 = pygame.transform.scale(original_obstacle1, (40, 40))
pygame.image.save(small_obstacle1, "images/obstacle_small.png")

original_obstacle2 = pygame.image.load("images/obstacle2.png")
small_obstacle2 = pygame.transform.scale(original_obstacle2, (40, 40))
pygame.image.save(small_obstacle2, "images/obstacle2_small.png")

# Resize obstacles for colorblind mode
original_cb_obstacle1 = pygame.image.load("images/cb_obstacle1.png")  # Alternate obstacle 1
small_cb_obstacle1 = pygame.transform.scale(original_cb_obstacle1, (40, 40))
pygame.image.save(small_cb_obstacle1, "images/cb_obstacle1_small.png")

original_cb_obstacle2 = pygame.image.load("images/cb_obstacle2.png")  # Alternate obstacle 2
small_cb_obstacle2 = pygame.transform.scale(original_cb_obstacle2, (40, 40))
pygame.image.save(small_cb_obstacle2, "images/cb_obstacle2_small.png")

# Resize heart power-up
original_heart = pygame.image.load("images/heart.png")
small_heart = pygame.transform.scale(original_heart, (30, 30))
pygame.image.save(small_heart, "images/heart_small.png")


def reset_game():
    """Resets the game to the initial state."""
    global player, obstacles, hearts, score, game_over, spawn_counter, heart_counter, obstacle_type, is_running_sound_playing, lives

    player.pos = (100, HEIGHT - 60)
    player.dy = 0
    obstacles.clear()
    hearts.clear()
    score = 0
    spawn_counter = 0
    heart_counter = 0
    game_over = False
    obstacle_type = 0  # Reset obstacle alternation
    lives = 3  # Reset lives

    sounds.start.play()  # Play game start sound
    sounds.running.play(-1)  # Start running sound again
    is_running_sound_playing = True


def update():
    """Updates game state every frame."""
    global spawn_counter, heart_counter, score, game_over, obstacle_type, is_running_sound_playing, lives

    if not game_started or game_over:
        return  # Don't update game if it's not started or game over

    # Apply gravity
    player.dy += grav
    player.y += player.dy

    # Keep player on screen
    if player.y > HEIGHT - 60:
        player.y = HEIGHT - 60
        player.dy = 0

        # Play running sound if not already playing
        if not is_running_sound_playing:
            sounds.running.play(-1)
            is_running_sound_playing = True

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
                obstacles.append(Actor("cb_obstacle1_small", (WIDTH, HEIGHT - 60)))  # Colorblind obstacle 1
                obstacle_type = 1
            else:
                obstacles.append(Actor("cb_obstacle2_small", (WIDTH, HEIGHT - 60)))  # Colorblind obstacle 2
                obstacle_type = 0
        else:
            if obstacle_type == 0:
                obstacles.append(Actor("obstacle_small", (WIDTH, HEIGHT - 60)))  # Normal obstacle 1
                obstacle_type = 1
            else:
                obstacles.append(Actor("obstacle2_small", (WIDTH, HEIGHT - 60)))  # Normal obstacle 2
                obstacle_type = 0

    # Spawn hearts randomly
    heart_counter += 1
    if heart_counter >= heart_spawn_time:
        heart_counter = 0
        if random.random() < 0.5:  # 50% chance to spawn a heart
            hearts.append(Actor("heart_small", (WIDTH, HEIGHT - 100)))  # Heart appears higher

    # Collision detection - Obstacles
    for obstacle in obstacles:
        if player.colliderect(obstacle):
            obstacles.remove(obstacle)  # Remove obstacle on collision
            lives -= 1  # Lose a life
            sounds.crash.play()  # Play crash sound

            if lives <= 0:  # If lives run out, game over
                game_over = True
                sounds.running.stop()  # Stop running sound
                sounds.gameover.play()  # Play game over sound

    # Collision detection - Hearts (Power-up)
    for heart in hearts:
        if player.colliderect(heart):
            hearts.remove(heart)  # Remove heart when collected
            if lives < 3:  # Only increase life if it's less than 3
                lives += 1
                sounds.powerup.play()  # Play heart collection sound

    # Score keeping
    score += 1


def draw():
    """Renders the game objects."""
    screen.surface.blit(background, (0, 0))  # Draw background (unchanged)

    if not game_started:
        screen.draw.text("Press ENTER to Start", center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=40)
        return

    # Draw score
    score_color = "blue" if colorblind_mode else "white"
    screen.draw.text(f"Score: {score}", (10, 10), color=score_color, fontsize=30)

    # Draw Lives (Hearts on screen)
    for i in range(lives):
        heart_color = "blue" if colorblind_mode else "red"
        screen.blit("heart_small", (WIDTH - 100 + (i * 30), 10))

    player.draw()
    for obstacle in obstacles:
        obstacle.draw()
    for heart in hearts:
        heart.draw()

    if game_over:
        game_over_color = "blue" if colorblind_mode else "red"
        screen.draw.text(
            "Game Over! Press ENTER to Restart",
            center=(WIDTH // 2, HEIGHT // 2),
            color=game_over_color,
            fontsize=40,
        )

    # Display colorblind mode status
    mode_text = "Colorblind Mode: ON" if colorblind_mode else "Colorblind Mode: OFF"
    screen.draw.text(mode_text, (WIDTH - 200, 10), color="white", fontsize=20)


def on_key_down(key):
    """Handles player input."""
    global game_started, game_over, is_running_sound_playing, colorblind_mode

    if key == keys.RETURN and not game_started:  # Start game when ENTER is pressed
        game_started = True
        reset_game()  # Restart the game variables

    if key == keys.SPACE and player.y == HEIGHT - 60 and game_started:
        player.dy = jump_power
        sounds.jump.play()  # Play jump sound
        sounds.running.stop()  # Stop running sound when jumping
        is_running_sound_playing = False  # Running stops when jumping

    if key == keys.RETURN and game_over:  # Restart game when ENTER is pressed
        game_over = False  # Reset game state
        game_started = True
        reset_game()  # Restart after game over

    if key == keys.C:  # Toggle colorblind mode
        colorblind_mode = not colorblind_mode
        # Update existing obstacles to the new type
        for obstacle in obstacles:
            if colorblind_mode:
                if obstacle_type == 0:
                    obstacle.image = "cb_obstacle1_small"
                else:
                    obstacle.image = "cb_obstacle2_small"
            else:
                if obstacle_type == 0:
                    obstacle.image = "obstacle_small"
                else:
                    obstacle.image = "obstacle2_small"


pgzrun.go()
# ////// obstacle changes