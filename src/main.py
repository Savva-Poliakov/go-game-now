import sys
import os
import pygame
from go_rules import GoBoard
from ai import GoEngine, list_levels


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), '..', relative_path)


WOOD_COLOR = (220, 179, 92)
LINE_COLOR = (40, 30, 10)
BLACK_STONE = (20, 20, 20)
WHITE_STONE = (245, 245, 245)
TEXT_COLOR = (30, 20, 10)
BUTTON_COLOR = (180, 140, 70)
BUTTON_HOVER = (200, 160, 90)
MARGIN = 40
WINDOW_SIZE = 640
ICON_PATH = resource_path("assets/logo.ico")
MUSIC_PATH = resource_path("assets/bgm.mp3")
MUSIC_VOLUME = 0.35

STAR_POINTS = {
    9: [(2, 2), (2, 6), (6, 2), (6, 6), (4, 4)],
    13: [(3, 3), (3, 9), (9, 3), (9, 9), (6, 6)],
    19: [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), (15, 3), (15, 9), (15, 15)]
}


def cell_size(board_size):
    return (WINDOW_SIZE - 2 * MARGIN) / (board_size - 1)


def board_to_pixel(x, y, board_size):
    size = cell_size(board_size)
    return MARGIN + x * size, MARGIN + y * size


def pixel_to_board(px, py, board_size):
    size = cell_size(board_size)
    x = round((px - MARGIN) / size)
    y = round((py - MARGIN) / size)
    if 0 <= x < board_size and 0 <= y < board_size:
        return x, y
    return None


def draw_board(screen, board):
    screen.fill(WOOD_COLOR)
    size = board.size
    for i in range(size):
        start = board_to_pixel(i, 0, size)
        end = board_to_pixel(i, size - 1, size)
        pygame.draw.line(screen, LINE_COLOR, start, end, 1)
        start = board_to_pixel(0, i, size)
        end = board_to_pixel(size - 1, i, size)
        pygame.draw.line(screen, LINE_COLOR, start, end, 1)
    for (sx, sy) in STAR_POINTS.get(size, []):
        px, py = board_to_pixel(sx, sy, size)
        pygame.draw.circle(screen, LINE_COLOR, (int(px), int(py)), 4)
    for y in range(size):
        for x in range(size):
            stone = board.board[y][x]
            if stone is not None:
                px, py = board_to_pixel(x, y, size)
                color = BLACK_STONE if stone == 'black' else WHITE_STONE
                radius = cell_size(size) / 2 - 2
                pygame.draw.circle(screen, color, (int(px), int(py)), int(radius))
                pygame.draw.circle(screen, LINE_COLOR, (int(px), int(py)), int(radius), 1)


def draw_text(screen, font, text, pos, color=TEXT_COLOR):
    surface = font.render(text, True, color)
    screen.blit(surface, pos)


def draw_button(screen, font, rect, label, hover):
    color = BUTTON_HOVER if hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, LINE_COLOR, rect, 2)
    text_surface = font.render(label, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


def selection_screen(screen, font, title, options):
    clock = pygame.time.Clock()
    columns = 5
    button_w = 100
    button_h = 40
    gap = 10
    start_x = (WINDOW_SIZE - (columns * button_w + (columns - 1) * gap)) / 2
    start_y = 120
    buttons = []
    for index, option in enumerate(options):
        row = index // columns
        col = index % columns
        x = start_x + col * (button_w + gap)
        y = start_y + row * (button_h + gap)
        buttons.append((pygame.Rect(x, y, button_w, button_h), option))
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, option in buttons:
                    if rect.collidepoint(mouse_pos):
                        return option
        screen.fill(WOOD_COLOR)
        draw_text(screen, font, title, (MARGIN, 50))
        for rect, option in buttons:
            hover = rect.collidepoint(mouse_pos)
            draw_button(screen, font, rect, str(option), hover)
        pygame.display.flip()
        clock.tick(30)


def game_over_screen(screen, font, board):
    score = board.calculate_score()
    winner = 'Black' if score['black'] > score['white'] else 'White'
    if score['black'] == score['white']:
        winner = 'Draw'
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return
        screen.fill(WOOD_COLOR)
        draw_text(screen, font, "Game over", (MARGIN, 60))
        draw_text(screen, font, f"Black: {score['black']}", (MARGIN, 120))
        draw_text(screen, font, f"White: {score['white']}", (MARGIN, 160))
        draw_text(screen, font, f"Winner: {winner}", (MARGIN, 200))
        draw_text(screen, font, "Click to exit", (MARGIN, 260))
        pygame.display.flip()
        clock.tick(30)


def run_game(screen, font, board_size, ai_level, player_color):
    board = GoBoard(board_size)
    engine = GoEngine(ai_level)
    ai_color = board.opponent(player_color)
    clock = pygame.time.Clock()
    pass_button = pygame.Rect(WINDOW_SIZE - 180, WINDOW_SIZE - 40, 80, 30)
    resign_button = pygame.Rect(WINDOW_SIZE - 90, WINDOW_SIZE - 40, 80, 30)
    while not board.game_over:
        if board.current_player == ai_color:
            move = engine.choose_move(board, ai_color)
            if move is None:
                board.pass_turn()
            else:
                board.play_move(move[0], move[1], ai_color)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and board.current_player == player_color:
                if pass_button.collidepoint(event.pos):
                    board.pass_turn()
                elif resign_button.collidepoint(event.pos):
                    board.resign(player_color)
                else:
                    coords = pixel_to_board(event.pos[0], event.pos[1], board.size)
                    if coords is not None:
                        board.play_move(coords[0], coords[1], player_color)
        draw_board(screen, board)
        draw_button(screen, font, pass_button, "Pass", pass_button.collidepoint(pygame.mouse.get_pos()))
        draw_button(screen, font, resign_button, "Resign", resign_button.collidepoint(pygame.mouse.get_pos()))
        draw_text(screen, font, f"Turn: {board.current_player}", (MARGIN, 10))
        pygame.display.flip()
        clock.tick(30)
    game_over_screen(screen, font, board)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Go Game Now")
    try:
        icon = pygame.image.load(ICON_PATH)
        pygame.display.set_icon(icon)
    except pygame.error:
        pass
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass
    font = pygame.font.SysFont("arial", 20)
    while True:
        board_size = selection_screen(screen, font, "Select board size", [9, 13, 19])
        ai_level = selection_screen(screen, font, "Select AI level", list_levels())
        player_color = selection_screen(screen, font, "Play as", ["black", "white"])
        run_game(screen, font, board_size, ai_level, player_color)


if __name__ == "__main__":
    main()
