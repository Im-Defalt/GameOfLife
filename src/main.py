import pygame
import sys
import numpy as np

# Window and grid dimensions
GRID_WIDTH = 800
HEIGHT = 800
PANEL_WIDTH = 250
WINDOW_WIDTH = GRID_WIDTH + PANEL_WIDTH
ROWS = 50
COLS = 50
CELL_SIZE = GRID_WIDTH // COLS  # size of a single cell

# Colors used in the application
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50)

# Available cell colors
cell_colors = [("Green", GREEN), ("Red", RED), ("Blue", BLUE), ("Yellow", YELLOW)]

# Initialize pygame and set up basic graphics
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, HEIGHT))
pygame.display.set_caption("Game of Life")
font = pygame.font.SysFont(None, 30)
big_font = pygame.font.SysFont(None, 40)
title_font = pygame.font.SysFont(None, 90)
clock = pygame.time.Clock()

# Initialize the grid as a matrix of zeros (dead cells)
grid = np.zeros((ROWS, COLS), dtype=int)

# Default game settings
cell_color = GREEN
speed = 10  # refresh rate in FPS
wrap_enabled = True  # edge wrapping mode
draw_mode = True  # drawing mode (True) or erasing mode (False)

# Application state: start menu or game
START_MENU = 0
GAME = 1
app_state = START_MENU

# Sidebar button definitions in game mode
panel_buttons = {
    "color": pygame.Rect(GRID_WIDTH + 35, 230, 180, 40),
    "wrap": pygame.Rect(GRID_WIDTH + 35, 280, 180, 40),
    "draw_toggle": pygame.Rect(GRID_WIDTH + 35, 330, 180, 40),
}

# Button definitions in start menu
start_menu_buttons = {
    "color": pygame.Rect(WINDOW_WIDTH // 2 - 90, 410, 180, 40),
    "wrap": pygame.Rect(WINDOW_WIDTH // 2 - 90, 460, 180, 40),
    "start": pygame.Rect(WINDOW_WIDTH // 2 - 110, 200, 220, 60),
}

# Speed slider settings
slider_rect = pygame.Rect(GRID_WIDTH + 35, 430, 180, 10)
start_slider_rect = pygame.Rect(WINDOW_WIDTH // 2 - 90, 550, 180, 10)
slider_knob_radius = 8
min_speed = 1
max_speed = 60

# Draw a button with text
def draw_button(rect, text, selected=False):
    """
    Draws a button with the given text inside the specified rectangle.

    Args:
        rect (pygame.Rect): Rectangle area for the button.
        text (str): Text to display on the button.
        selected (bool): Whether the button is selected (highlighted). Default is False.
    """
    pygame.draw.rect(screen, GRAY if not selected else YELLOW, rect, border_radius=10)
    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)

# Draw the speed slider
def draw_speed_slider(current_speed, slider_rect):
    """
    Draws a slider to adjust the speed (FPS).

    Args:
        current_speed (int): Current simulation speed in frames per second.
        slider_rect (pygame.Rect): Area where the slider should be drawn.
    """
    pygame.draw.rect(screen, WHITE, slider_rect)
    rel_x = int((current_speed - min_speed) / (max_speed - min_speed) * slider_rect.width)
    knob_x = slider_rect.x + rel_x
    pygame.draw.circle(screen, RED, (knob_x, slider_rect.y + slider_rect.height // 2), slider_knob_radius)
    label = font.render(f"Speed: {current_speed} FPS", True, WHITE)
    screen.blit(label, (slider_rect.x, slider_rect.y - 25))

# Draw the settings sidebar in game mode
def draw_sidebar(color, speed, wrap, draw_mode, playing):
    """
    Draws the sidebar panel with game settings.

    Args:
        color (tuple): Current cell color.
        speed (int): Current simulation speed.
        wrap (bool): Whether edge wrapping is enabled.
        draw_mode (bool): Drawing mode (True) or erasing mode (False).
        playing (bool): Whether the simulation is currently running.
    """
    pygame.draw.rect(screen, DARK_GRAY, (GRID_WIDTH, 0, PANEL_WIDTH, HEIGHT))

    # Game state display (Play/Pause)
    status_text = "STATE: Play" if playing else "STATE: Pause"
    status_color = RED if playing else GREEN
    status_label = font.render(status_text, True, status_color)
    screen.blit(status_label, (GRID_WIDTH + 60, 180))

    # Color selection button
    draw_button(panel_buttons["color"], "Color")
    pygame.draw.rect(screen, color, (GRID_WIDTH + 180, 240, 20, 20))

    # Speed slider
    draw_speed_slider(speed, slider_rect)

    # Edge wrapping toggle button
    draw_button(panel_buttons["wrap"], f"Wrapping: {'Yes' if wrap else 'No'}")

    # Draw/Erase mode toggle button
    mode_text = "Mode: Draw" if draw_mode else "Mode: Erase"
    draw_button(panel_buttons["draw_toggle"], mode_text)

    # Keyboard shortcuts
    screen.blit(font.render("SPACE = Start/Pause", True, WHITE), (GRID_WIDTH + 24, 50))
    screen.blit(font.render("R = Reset the board", True, WHITE), (GRID_WIDTH + 30, 100))

# Draw the initial start menu screen
def draw_start_menu(color, speed, wrap):
    """
    Draws the initial configuration start menu.

    Args:
        color (tuple): Selected cell color.
        speed (int): Chosen simulation speed.
        wrap (bool): Whether grid wrapping is enabled.
    """
    screen.fill(DARK_GRAY)

    # Game title
    title = title_font.render("Game of Life", True, WHITE)
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 120)))

    # Settings subtitle
    subtitle = big_font.render("Initial configuration", True, WHITE)
    screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 370)))

    # Color selection button and preview
    draw_button(start_menu_buttons["color"], "Color")
    pygame.draw.rect(screen, color, (start_menu_buttons["color"].x + 140, start_menu_buttons["color"].y + 10, 20, 20))

    # Wrapping toggle and speed slider
    draw_button(start_menu_buttons["wrap"], f"Wrapping: {'Yes' if wrap else 'No'}")
    draw_speed_slider(speed, start_slider_rect)

    # Start game button
    pygame.draw.rect(screen, YELLOW, start_menu_buttons["start"], border_radius=10)
    start_label = big_font.render("Start Game", True, BLACK)
    screen.blit(start_label, start_label.get_rect(center=start_menu_buttons["start"].center))

# Draw the grid lines
def draw_grid():
    """
    Draws the grid lines on the game board.
    """
    for x in range(0, GRID_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (GRID_WIDTH, y))

# Draw active (living) cells
def draw_cells(grid, color):
    """
    Draws the active cells on the game board.

    Args:
        grid (np.ndarray): 2D array representing the state of each cell.
        color (tuple): Color to use for active cells.
    """
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row, col] == 1:
                pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Update the grid state based on the Game of Life rules
def update_grid(grid, wrap):
    """
    Updates the grid state based on Conway's Game of Life rules.

    Args:
        grid (np.ndarray): Current grid of cells.
        wrap (bool): Whether to apply edge wrapping (torus behavior).

    Returns:
        np.ndarray: New grid after one iteration.
    """
    new_grid = np.copy(grid)
    for row in range(ROWS):
        for col in range(COLS):
            alive_neighbors = 0
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if i == 0 and j == 0:
                        continue
                    r, c = row + i, col + j
                    if wrap:
                        r %= ROWS
                        c %= COLS
                        alive_neighbors += grid[r, c]
                    elif 0 <= r < ROWS and 0 <= c < COLS:
                        alive_neighbors += grid[r, c]

            # Game rules
            if grid[row, col] == 1 and (alive_neighbors < 2 or alive_neighbors > 3):
                new_grid[row, col] = 0  # cell dies
            elif grid[row, col] == 0 and alive_neighbors == 3:
                new_grid[row, col] = 1  # cell is born
    return new_grid

# Toggle a single cell's state (draw/erase)
def toggle_cell(grid, pos, draw_mode):
    """
    Changes the state of a cell based on drawing or erasing mode.

    Args:
        grid (np.ndarray): Cell grid.
        pos (tuple): Cursor position (x, y).
        draw_mode (bool): True if in drawing mode, False for erasing.
    """
    col = pos[0] // CELL_SIZE
    row = pos[1] // CELL_SIZE
    if 0 <= row < ROWS and 0 <= col < COLS:
        grid[row, col] = 1 if draw_mode else 0

# Main game loop
mouse_held = False  # whether the mouse is held down
playing = False  # whether the game is active
running = True  # whether the application is running

while running:
    screen.fill(BLACK)

    # Draw the appropriate view depending on the app state
    if app_state == START_MENU:
        draw_start_menu(cell_color, speed, wrap_enabled)
    elif app_state == GAME:
        draw_cells(grid, cell_color)
        draw_grid()
        draw_sidebar(cell_color, speed, wrap_enabled, draw_mode, playing)

    # Handle user events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = pygame.mouse.get_pos()

                # Handle clicks in the start menu
                if app_state == START_MENU:
                    if start_menu_buttons["color"].collidepoint(pos):
                        current_index = [c[1] for c in cell_colors].index(cell_color)
                        cell_color = cell_colors[(current_index + 1) % len(cell_colors)][1]
                    elif start_menu_buttons["wrap"].collidepoint(pos):
                        wrap_enabled = not wrap_enabled
                    elif start_menu_buttons["start"].collidepoint(pos):
                        app_state = GAME
                    elif start_slider_rect.collidepoint(pos):
                        rel_x = pos[0] - start_slider_rect.x
                        rel_x = max(0, min(rel_x, start_slider_rect.width))
                        speed = int(min_speed + (rel_x / start_slider_rect.width) * (max_speed - min_speed))

                # Handle clicks during the game
                elif app_state == GAME:
                    if pos[0] < GRID_WIDTH and not playing:
                        mouse_held = True
                        toggle_cell(grid, pos, draw_mode)
                    if not playing:
                        if panel_buttons["color"].collidepoint(pos):
                            current_index = [c[1] for c in cell_colors].index(cell_color)
                            cell_color = cell_colors[(current_index + 1) % len(cell_colors)][1]
                        elif panel_buttons["wrap"].collidepoint(pos):
                            wrap_enabled = not wrap_enabled
                        elif panel_buttons["draw_toggle"].collidepoint(pos):
                            draw_mode = not draw_mode
                        elif slider_rect.collidepoint(pos):
                            rel_x = pos[0] - slider_rect.x
                            rel_x = max(0, min(rel_x, slider_rect.width))
                            speed = int(min_speed + (rel_x / slider_rect.width) * (max_speed - min_speed))

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_held = False

        elif event.type == pygame.MOUSEMOTION:
            if mouse_held and not playing and app_state == GAME:
                toggle_cell(grid, pygame.mouse.get_pos(), draw_mode)
            elif not playing and pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if app_state == START_MENU and start_slider_rect.collidepoint(pos):
                    rel_x = pos[0] - start_slider_rect.x
                    rel_x = max(0, min(rel_x, start_slider_rect.width))
                    speed = int(min_speed + (rel_x / start_slider_rect.width) * (max_speed - min_speed))
                elif app_state == GAME and slider_rect.collidepoint(pos):
                    rel_x = pos[0] - slider_rect.x
                    rel_x = max(0, min(rel_x, slider_rect.width))
                    speed = int(min_speed + (rel_x / slider_rect.width) * (max_speed - min_speed))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and app_state == GAME:
                playing = not playing  # pause/resume game
            elif event.key == pygame.K_r and app_state == GAME:
                grid = np.zeros((ROWS, COLS), dtype=int)  # reset the board

    # Update the grid if the game is active
    if app_state == GAME and playing:
        grid = update_grid(grid, wrap_enabled)

    pygame.display.flip()
    clock.tick(speed if app_state == GAME else 60)

# End of application
pygame.quit()
sys.exit()
