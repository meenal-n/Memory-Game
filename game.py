import random
import pygame
import sys
from pygame.locals import *

# Constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
BOARD_WIDTH = 10
BOARD_HEIGHT = 7
BOX_SIZE = 40
GAP_SIZE = 10
FPS = 30
REVEAL_SPEED = 8

# Colors
BG_COLOR = (60, 60, 100)
BOX_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (0, 0, 255)
SHAPES = ['circle', 'square', 'triangle', 'diamond', 'lines', 'oval']
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 128, 0), (255, 0, 255)]

# Calculations
X_MARGIN = (WINDOW_WIDTH - (BOARD_WIDTH * (BOX_SIZE + GAP_SIZE))) // 2
Y_MARGIN = (WINDOW_HEIGHT - (BOARD_HEIGHT * (BOX_SIZE + GAP_SIZE))) // 2

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Memory Game')

def main():
    """Main game loop."""
    board = generate_board()
    revealed_boxes = create_revealed_boxes_data(False)

    start_game_animation(board)

    first_selection = None
    mouse_x, mouse_y = 0, 0  # Initialize mouse coordinates
    while True:
        mouse_clicked = False
        display_surface.fill(BG_COLOR)
        draw_board(board, revealed_boxes)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                mouse_clicked = True

        box_x, box_y = get_box_at_pixel(mouse_x, mouse_y)
        if box_x is not None and box_y is not None:
            if not revealed_boxes[box_x][box_y]:
                highlight_box(box_x, box_y)

            if not revealed_boxes[box_x][box_y] and mouse_clicked:
                reveal_boxes_animation(board, [(box_x, box_y)])
                revealed_boxes[box_x][box_y] = True

                if first_selection is None:
                    first_selection = (box_x, box_y)
                else:
                    # Match check
                    first_shape, first_color = get_symbol_and_color(board, first_selection[0], first_selection[1])
                    second_shape, second_color = get_symbol_and_color(board, box_x, box_y)

                    if first_shape != second_shape or first_color != second_color:
                        pygame.time.wait(1000)
                        cover_boxes_animation(board, [first_selection, (box_x, box_y)])
                        revealed_boxes[first_selection[0]][first_selection[1]] = False
                        revealed_boxes[box_x][box_y] = False
                    elif has_won(revealed_boxes):
                        game_won_animation(board)
                        pygame.time.wait(2000)
                        board = generate_board()
                        revealed_boxes = create_revealed_boxes_data(False)
                        start_game_animation(board)

                    first_selection = None

        pygame.display.update()
        clock.tick(FPS)



def generate_board():
    """Generate a shuffled board with symbols and colors."""
    symbols = []
    for color in COLORS:
        for shape in SHAPES:
            symbols.append((shape, color))
    random.shuffle(symbols)
    symbols = symbols[:BOARD_WIDTH * BOARD_HEIGHT // 2] * 2
    random.shuffle(symbols)

    board = []
    for x in range(BOARD_WIDTH):
        column = []
        for y in range(BOARD_HEIGHT):
            column.append(symbols.pop())
        board.append(column)
    return board


def create_revealed_boxes_data(val):
    """Create a 2D list indicating whether boxes are revealed."""
    return [[val] * BOARD_HEIGHT for _ in range(BOARD_WIDTH)]


def split_into_groups_of(group_size, the_list):
    """Split a list into groups of a given size."""
    return [the_list[i:i + group_size] for i in range(0, len(the_list), group_size)]


def get_top_left_of_box(box_x, box_y):
    """Get the top-left pixel coordinates of a box."""
    left = box_x * (BOX_SIZE + GAP_SIZE) + X_MARGIN
    top = box_y * (BOX_SIZE + GAP_SIZE) + Y_MARGIN
    return left, top


def get_box_at_pixel(x, y):
    """Return the box coordinates of a pixel."""
    for box_x in range(BOARD_WIDTH):
        for box_y in range(BOARD_HEIGHT):
            left, top = get_top_left_of_box(box_x, box_y)
            box_rect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
            if box_rect.collidepoint(x, y):
                return box_x, box_y
    return None, None


def draw_symbol(shape, color, box_x, box_y):
    """Draw a symbol at the given box."""
    left, top = get_top_left_of_box(box_x, box_y)
    center_x = left + BOX_SIZE // 2
    center_y = top + BOX_SIZE // 2

    if shape == 'circle':
        pygame.draw.circle(display_surface, color, (center_x, center_y), BOX_SIZE // 3)
    elif shape == 'square':
        pygame.draw.rect(display_surface, color, (left + 10, top + 10, BOX_SIZE - 20, BOX_SIZE - 20))
    elif shape == 'triangle':
        pygame.draw.polygon(display_surface, color, [(center_x, top + 10), (left + 10, top + BOX_SIZE - 10),
                                                     (left + BOX_SIZE - 10, top + BOX_SIZE - 10)])
    elif shape == 'diamond':
        pygame.draw.polygon(display_surface, color, [(center_x, top + 10), (left + 10, center_y),
                                                     (center_x, top + BOX_SIZE - 10), (left + BOX_SIZE - 10, center_y)])
    elif shape == 'lines':
        for i in range(0, BOX_SIZE, 4):
            pygame.draw.line(display_surface, color, (left, top + i), (left + i, top))
            pygame.draw.line(display_surface, color, (left + i, top + BOX_SIZE - 1), (left + BOX_SIZE - 1, top + i))
    elif shape == 'oval':
        pygame.draw.ellipse(display_surface, color, (left + 10, top + 20, BOX_SIZE - 20, BOX_SIZE - 40))


def draw_board(board, revealed_boxes):
    """Draw the board."""
    for box_x in range(BOARD_WIDTH):
        for box_y in range(BOARD_HEIGHT):
            left, top = get_top_left_of_box(box_x, box_y)
            if not revealed_boxes[box_x][box_y]:
                pygame.draw.rect(display_surface, BOX_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
            else:
                shape, color = get_symbol_and_color(board, box_x, box_y)
                draw_symbol(shape, color, box_x, box_y)


def highlight_box(box_x, box_y):
    """Highlight the box under the mouse."""
    left, top = get_top_left_of_box(box_x, box_y)
    pygame.draw.rect(display_surface, HIGHLIGHT_COLOR, (left - 5, top - 5, BOX_SIZE + 10, BOX_SIZE + 10), 4)


def start_game_animation(board):
    """Reveal all boxes briefly at the start."""
    covered_boxes = create_revealed_boxes_data(False)
    boxes = [(x, y) for x in range(BOARD_WIDTH) for y in range(BOARD_HEIGHT)]
    random.shuffle(boxes)
    box_groups = split_into_groups_of(8, boxes)

    draw_board(board, covered_boxes)
    for group in box_groups:
        reveal_boxes_animation(board, group)
        cover_boxes_animation(board, group)


def reveal_boxes_animation(board, boxes):
    """Reveal boxes with an animation."""
    for coverage in range(BOX_SIZE, -REVEAL_SPEED - 1, -REVEAL_SPEED):
        draw_boxes_covered(board, boxes, coverage)


def cover_boxes_animation(board, boxes):
    """Cover boxes with an animation."""
    for coverage in range(0, BOX_SIZE + REVEAL_SPEED, REVEAL_SPEED):
        draw_boxes_covered(board, boxes, coverage)


def draw_boxes_covered(board, boxes, coverage):
    """Draw covered or partially revealed boxes."""
    for box in boxes:
        left, top = get_top_left_of_box(box[0], box[1])
        pygame.draw.rect(display_surface, BG_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
        shape, color = get_symbol_and_color(board, box[0], box[1])
        draw_symbol(shape, color, box[0], box[1])
        if coverage > 0:
            pygame.draw.rect(display_surface, BOX_COLOR, (left, top, coverage, BOX_SIZE))
    pygame.display.update()
    clock.tick(FPS)


def get_symbol_and_color(board, box_x, box_y):
    """Get the symbol and color of a box."""
    return board[box_x][box_y]


def has_won(revealed_boxes):
    """Check if all boxes are revealed."""
    return all(all(row) for row in revealed_boxes)


def game_won_animation(board):
    """Play a simple animation when the player wins."""
    for color in [BG_COLOR, HIGHLIGHT_COLOR]:
        display_surface.fill(color)
        draw_board(board, create_revealed_boxes_data(True))
        pygame.display.update()
        pygame.time.wait(300)


if __name__ == '__main__':
    main()
