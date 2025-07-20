import pygame, random, sys

# Initialize Pygame
pygame.init()
width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Colorful Snake Game")
clock = pygame.time.Clock()
block = 20

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED   = (255,0,0)
YELLOW= (255,255,0)

# Rainbow theme
rainbow_colors = [(148,0,211),(75,0,130),(0,0,255),(0,255,0),(255,255,0),(255,127,0),(255,0,0)]
theme = "pink"  # Options: pink, green, blue, rainbow

# Snake setup - FIXED: Properly grid-aligned positions
snake_body = [[100, 40], [80, 40], [60, 40]]  # Changed from Y=50 to Y=40 (grid-aligned)
direction = "RIGHT"

def generate_safe_position(occupied_positions):
    """Generate a position that doesn't overlap with occupied positions"""
    while True:
        pos = [random.randrange(0, width//block)*block, random.randrange(0, height//block)*block]
        if pos not in occupied_positions:
            return pos

# Generate initial positions safely - FIXED: Avoid overlaps
occupied = snake_body.copy()
apple_pos = generate_safe_position(occupied)
occupied.append(apple_pos)
banana_pos = generate_safe_position(occupied)
occupied.append(banana_pos)
bomb_pos = generate_safe_position(occupied)

# Load assets (with .jpg images)
try:
    apple_img  = pygame.transform.scale(pygame.image.load("assets/apple.jpg").convert_alpha(), (block, block))
    banana_img = pygame.transform.scale(pygame.image.load("assets/banana.jpg").convert_alpha(), (block, block))
    bomb_img   = pygame.transform.scale(pygame.image.load("assets/bomb.jpg").convert_alpha(), (block, block))
    # Load maze background image
    maze_background = pygame.transform.scale(pygame.image.load("assets/maze_background.jpg").convert(), (width, height))
except pygame.error as e:
    print(f"Error loading image: {e}")
    # Create colored rectangles as fallback
    apple_img = pygame.Surface((block, block))
    apple_img.fill(RED)
    banana_img = pygame.Surface((block, block))
    banana_img.fill(YELLOW)
    bomb_img = pygame.Surface((block, block))
    bomb_img.fill(BLACK)
    maze_background = pygame.Surface((width, height))
    maze_background.fill((50, 50, 50))  # Dark gray background

# Load sounds (.mp3)
try:
    pygame.mixer.init()
    pygame.mixer.music.load("assets/background.mp3")
    pygame.mixer.music.play(-1)
    eat_sound = pygame.mixer.Sound("assets/eat.mp3")
except pygame.error:
    print("Audio files not found, continuing without sound")
    eat_sound = None

game_over = False
score = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != "DOWN":
                direction = "UP"
            elif event.key == pygame.K_DOWN and direction != "UP":
                direction = "DOWN"
            elif event.key == pygame.K_LEFT and direction != "RIGHT":
                direction = "LEFT"
            elif event.key == pygame.K_RIGHT and direction != "LEFT":
                direction = "RIGHT"
            elif event.key == pygame.K_t:
                if theme == "pink": theme = "green"
                elif theme == "green": theme = "blue"
                elif theme == "blue": theme = "rainbow"
                else: theme = "pink"

    if not game_over:
        # Move the snake
        head_x, head_y = snake_body[0]
        if direction == "UP": head_y -= block
        elif direction == "DOWN": head_y += block
        elif direction == "LEFT": head_x -= block
        elif direction == "RIGHT": head_x += block

        # Wrap around screen edges - FIXED: Ensure grid alignment
        head_x = (head_x % width)
        head_y = (head_y % height)

        new_head = [head_x, head_y]
        
        # Check self collision BEFORE adding new head
        if new_head in snake_body:
            game_over = True
            continue
            
        snake_body.insert(0, new_head)

        # Check fruit collisions - FIXED: Proper collision detection
        ate_apple = (head_x == apple_pos[0] and head_y == apple_pos[1])
        ate_banana = (head_x == banana_pos[0] and head_y == banana_pos[1])
        
        # Snake growth logic
        if ate_apple or ate_banana:
            if eat_sound:
                eat_sound.play()
            score += 10
            
            # Generate new positions avoiding snake body
            occupied = snake_body.copy()
            
            if ate_apple:
                apple_pos = generate_safe_position(occupied)
                occupied.append(apple_pos)
            if ate_banana:
                banana_pos = generate_safe_position(occupied)
                occupied.append(banana_pos)
                
            # Relocate bomb to a safe position
            occupied.extend([apple_pos, banana_pos])
            bomb_pos = generate_safe_position(occupied)
            
            # Don't remove tail - let snake grow!
        else:
            # Remove tail only if no fruit was eaten
            snake_body.pop()

        # Check bomb collision
        if head_x == bomb_pos[0] and head_y == bomb_pos[1]:
            game_over = True

    # Handle game over state
    if game_over:
        # Draw background first
        screen.blit(maze_background, (0, 0))
        
        # Game over messages
        font = pygame.font.SysFont(None, 48)
        small_font = pygame.font.SysFont(None, 24)
        
        msg = font.render("Game Over!", True, RED)
        score_msg = font.render(f"Final Score: {score}", True, WHITE)
        restart_msg = small_font.render("Press SPACE to restart or ESC to quit", True, WHITE)
        
        # Center the messages
        screen.blit(msg, (width//2 - msg.get_width()//2, height//2 - 60))
        screen.blit(score_msg, (width//2 - score_msg.get_width()//2, height//2 - 10))
        screen.blit(restart_msg, (width//2 - restart_msg.get_width()//2, height//2 + 40))
        
        pygame.display.flip()
        
        # Wait for user input
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Restart game with proper grid alignment
                        snake_body = [[100, 40], [80, 40], [60, 40]]
                        direction = "RIGHT"
                        
                        # Generate safe positions for restart
                        occupied = snake_body.copy()
                        apple_pos = generate_safe_position(occupied)
                        occupied.append(apple_pos)
                        banana_pos = generate_safe_position(occupied)
                        occupied.append(banana_pos)
                        bomb_pos = generate_safe_position(occupied)
                        
                        game_over = False
                        score = 0
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
    else:
        # Draw everything in the correct order
        # 1. Background first
        screen.blit(maze_background, (0, 0))
        
        # 2. Draw fruits and bomb
        screen.blit(apple_img, apple_pos)
        screen.blit(banana_img, banana_pos)
        screen.blit(bomb_img, bomb_pos)

        # 3. Draw the snake on top
        for i, pos in enumerate(snake_body):
            if theme == "rainbow":
                color = rainbow_colors[i % len(rainbow_colors)]
            elif theme == "green":
                color = (0,255,0)
            elif theme == "blue":
                color = (0,150,255)
            else:
                color = (255,105,180)  # Pink
            
            pygame.draw.rect(screen, color, (pos[0], pos[1], block, block))
            # Add border for better visibility
            pygame.draw.rect(screen, BLACK, (pos[0], pos[1], block, block), 2)

        # 4. Draw score and instructions
        font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 24)
        
        score_text = font.render(f"Score: {score}", True, WHITE)
        length_text = small_font.render(f"Length: {len(snake_body)}", True, WHITE)
        theme_text = small_font.render("Press 'T' to change theme", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(length_text, (10, 45))
        screen.blit(theme_text, (10, height - 30))

        pygame.display.update()
        clock.tick(8)
