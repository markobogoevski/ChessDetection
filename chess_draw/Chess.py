import os
from enum import Enum
import pygame
import pyperclip
import numpy as np
import webbrowser

square_size = 100
white_square_color = (240, 217, 181)
black_square_color = (181, 136, 99)
buttons_size = 50
offset = buttons_size // 2
vertical_offset_up = square_size + buttons_size + offset + 10
vertical_offset_down = square_size + offset
offset_x = 25


class ChessPiece(Enum):
    EMPTY = 'empty'
    WHITE_PAWN = 'P'
    BLACK_PAWN = 'p'
    WHITE_KNIGHT = 'N'
    BLACK_KNIGHT = 'n'
    WHITE_BISHOP = 'B'
    BLACK_BISHOP = 'b'
    WHITE_ROOK = 'R'
    BLACK_ROOK = 'r'
    WHITE_QUEEN = 'Q'
    BLACK_QUEEN = 'q'
    WHITE_KING = 'K'
    BLACK_KING = 'k'
    POINTER = 'pointer'
    REMOVE = 'remove'


#
# # Sample board start white
# start_board_white = [
#     ['black_rook', 'black_horse', 'black_bishop', 'black_queen', 'black_king', 'black_bishop', 'black_knight',
#      'black_rook'],
#     ['black_pawn', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn'],
#     ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
#     ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
#     ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
#     ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
#     ['white_rook', 'white_horse', 'white_bishop', 'white_queen', 'white_king', 'white_bishop', 'white_knight',
#      'white_rook'],
#     ['white_pawn', 'white_pawn', 'white_pawn', 'white_pawn', 'white_pawn', 'white_pawn', 'white_pawn', 'white_pawn']]
#
# # Sample board start black
# start_board_black = [
#     ['white_rook', 'white_horse', 'white_bishop', 'white_king', 'white_queen', 'white_bishop', 'white_knight',
#      'white_rook'],
#     ['white_pawn', 'white_pawn', 'white_pawn', 'white_pawn', 'white_pawn', 'white_pawn', 'white_pawn', 'white_pawn'],
#     ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
#     ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
#     ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
#     ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
#     ['black_pawn', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn', 'black_pawn'],
#     ['black_rook', 'black_horse', 'black_bishop', 'black_king', 'black_queen', 'black_bishop', 'black_knight',
#      'black_rook']]


# Sample board start white
start_board_white_enum = [
    [ChessPiece.BLACK_ROOK, ChessPiece.BLACK_KNIGHT, ChessPiece.BLACK_BISHOP, ChessPiece.BLACK_QUEEN,
     ChessPiece.BLACK_KING, ChessPiece.BLACK_BISHOP, ChessPiece.BLACK_KNIGHT, ChessPiece.BLACK_ROOK],
    [ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN,
     ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN],
    [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY,
     ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
    [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY,
     ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
    [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY,
     ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
    [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY,
     ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
    [ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN,
     ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN],
    [ChessPiece.WHITE_ROOK, ChessPiece.WHITE_KNIGHT, ChessPiece.WHITE_BISHOP, ChessPiece.WHITE_QUEEN,
     ChessPiece.WHITE_KING, ChessPiece.WHITE_BISHOP, ChessPiece.WHITE_KNIGHT, ChessPiece.WHITE_ROOK]]

# Sample board start black
start_board_black_enum = [
    [ChessPiece.WHITE_ROOK, ChessPiece.WHITE_KNIGHT, ChessPiece.WHITE_BISHOP, ChessPiece.WHITE_KING,
     ChessPiece.WHITE_QUEEN, ChessPiece.WHITE_BISHOP, ChessPiece.WHITE_KNIGHT, ChessPiece.WHITE_ROOK],
    [ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN,
     ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN],
    [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY,
     ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
    [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY,
     ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
    [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY,
     ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
    [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY,
     ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
    [ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN,
     ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN],
    [ChessPiece.BLACK_ROOK, ChessPiece.BLACK_KNIGHT, ChessPiece.BLACK_BISHOP, ChessPiece.BLACK_KING,
     ChessPiece.BLACK_QUEEN, ChessPiece.BLACK_BISHOP, ChessPiece.BLACK_KNIGHT, ChessPiece.BLACK_ROOK]]

editor_list_black = [ChessPiece.POINTER, ChessPiece.BLACK_KING, ChessPiece.BLACK_QUEEN, ChessPiece.BLACK_ROOK,
                     ChessPiece.BLACK_BISHOP, ChessPiece.BLACK_KNIGHT, ChessPiece.BLACK_PAWN, ChessPiece.REMOVE]
editor_list_white = [ChessPiece.POINTER, ChessPiece.WHITE_KING, ChessPiece.WHITE_QUEEN, ChessPiece.WHITE_ROOK,
                     ChessPiece.WHITE_BISHOP, ChessPiece.WHITE_KNIGHT, ChessPiece.WHITE_PAWN, ChessPiece.REMOVE]


class ChessTable:
    def __init__(self, player='white', board=None, to_play='white'):
        self.board_list = start_board_white_enum
        self.left_top_color = 'white'
        if player == 'black':
            self.board_list = start_board_black_enum
        if board:
            self.board_list = board
        self.to_play = to_play
        self.num_rows = 8
        self.num_cols = 8
        self.player = player
        self.squares = []
        self.board_editor_list_black = []
        self.board_editor_list_white = []
        for num_col in range(self.num_cols):
            self.board_editor_list_black.append(ChessEditorSquare(num_col, editor_list_black[num_col],
                                                                  player, mode='black'))
            self.board_editor_list_white.append(ChessEditorSquare(num_col, editor_list_white[num_col],
                                                                  player, mode='white'))

    def set_board_from_list(self, board_list):
        for num_row in range(self.num_rows):
            row_list = []
            for num_col in range(self.num_cols):
                # Instantiate a chess square to this spot
                if (num_row % 2 == 0 and num_col % 2 == 0) or (num_row % 2 != 0 and num_col % 2 != 0):
                    square_color = white_square_color
                else:
                    square_color = black_square_color
                table_index = num_row * self.num_rows + num_col
                model_index = (self.num_rows - num_row - 1) * self.num_cols + num_col
                row_list.append(ChessSquare(num_row, num_col, square_color,
                                            table_index, model_index, board_list[num_row][num_col]))
            self.squares.append(row_list)

    def get_square_under_mouse(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) - pygame.Vector2((offset_x, vertical_offset_down))
        mouse_pos_editor_top = pygame.Vector2(pygame.mouse.get_pos()) - pygame.Vector2((offset_x, 10))
        mouse_pos_editor_bottom = pygame.Vector2(pygame.mouse.get_pos()) - \
                                  pygame.Vector2((offset_x, vertical_offset_down + square_size * 8 + 10))
        # 0,0 -> top left, 0,9 -> bottom left, 7,0 -> top right, 7,9 -> bottom right
        x_editor_top, y_editor_top = [int(v // square_size) for v in mouse_pos_editor_top]
        x_editor_bottom, y_editor_bottom = [int(v // square_size) for v in mouse_pos_editor_bottom]
        x, y = [int(v // square_size) for v in mouse_pos]
        try:
            if 0 <= x <= 7 and 0 <= y <= 7:  # Inside chess table
                return self.squares[y][x], x, y
            if 0 <= x_editor_top <= 7 and y_editor_top == 0:  # Top array
                if self.player == 'white':
                    return self.board_editor_list_black[x_editor_top], x_editor_top, y_editor_top
                else:
                    return self.board_editor_list_white[x_editor_top], x_editor_top, y_editor_top
            if 0 <= x_editor_bottom <= 7 and y_editor_bottom == 0:  # Bottom array
                if self.player == 'white':
                    return self.board_editor_list_white[x_editor_bottom], x_editor_bottom, y_editor_bottom
                else:
                    return self.board_editor_list_black[x_editor_bottom], x_editor_bottom, y_editor_bottom
        except IndexError:
            pass
        return None, None, None

    def drag_n_drop(self, surface, selected_piece, font):
        if selected_piece:
            piece, x, y = self.get_square_under_mouse()
            piece = selected_piece[0].piece.value
            color = (255, 255, 255) if str(piece).isupper() else (0, 0, 0)
            type = str(piece).lower()
            s1 = font.render(type[0], True, pygame.Color(color))
            s2 = font.render(type[0], True, pygame.Color('darkgrey'))
            pos = pygame.Vector2(pygame.mouse.get_pos())
            surface.blit(s2, s2.get_rect(center=pos + (1, 1)))
            surface.blit(s1, s1.get_rect(center=pos))
            if isinstance(selected_piece[0], ChessSquare):
                selected_rect = pygame.Rect(offset_x + selected_piece[1] * square_size,
                                            vertical_offset_down + selected_piece[2] * square_size, square_size,
                                            square_size)
                pygame.draw.line(surface, pygame.Color('black'), selected_rect.center, pos)
                return x, y
            else:
                if x is not None and y is not None:
                    if self.player == 'white' and selected_piece[0].mode == 'white' or \
                            self.player == 'black' and selected_piece[0].mode == 'white':  # Top
                        selected_rect = pygame.Rect(selected_piece[1] * square_size + offset_x, 10,
                                                    square_size, square_size)
                    else:  # Bottom
                        selected_rect = pygame.Rect(selected_piece[1] * square_size + offset_x, vertical_offset_down + 10 + 8 * square_size,
                                         square_size, square_size)
                    pygame.draw.line(surface, pygame.Color('black'), selected_rect.center, pos)
                    return x, y

    def fen_button_clicked(self, mouse_x, mouse_y, fen_button):
        return fen_button.collidepoint((mouse_x, mouse_y))

    def simulate_chess_game(self, image_output, fen_output):
        pygame.init()
        surface = pygame.display.set_mode(
            (offset_x * 2 + square_size * 8, square_size * 8 + vertical_offset_up + vertical_offset_down),
            0, 32)
        surface.fill((0, 0, 0))
        pygame.display.set_caption('Chess game')  # You will pass the input image here
        font = pygame.font.SysFont('', 64)
        clock = pygame.time.Clock()
        fen_button = pygame.Rect(offset_x,
                                 vertical_offset_up + square_size * 8 + vertical_offset_down - buttons_size - 10,
                                 buttons_size * 4, buttons_size)
        button_text_font = pygame.font.SysFont('', 24)
        fen_button_text = button_text_font.render('Analyze', 1, (0, 0, 0))
        button_prompt_font = pygame.font.SysFont('', 20)
        fen_prompt = pygame.Rect(fen_button.x + fen_button.width + 10, fen_button.y,
                                 surface.get_width() - 2 * offset_x - 10 - fen_button.width, buttons_size)
        selected_square = None
        drop_pos = None
        remove_mode = False
        self.set_board_from_list(self.board_list)
        fen = self.convert_state_to_fen_string()
        fen_prompt_text = button_prompt_font.render(f'FEN:   {fen}', 1, (0, 0, 0))
        pyperclip.copy(fen)
        while True:
            square, x, y = self.get_square_under_mouse()
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    pygame.image.save(surface, image_output)
                    return
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if square is not None and square.piece is not None \
                            and square.piece.value != ChessPiece.EMPTY.value:
                        selected_square = square, x, y
                if e.type == pygame.MOUSEBUTTONUP:
                    mouse_press_x, mouse_press_y = pygame.mouse.get_pos()
                    if selected_square is not None:
                        if isinstance(selected_square[0], ChessSquare):
                            if drop_pos is not None and (offset_x <= mouse_press_x <= square_size * 8 + offset_x and
                                                         vertical_offset_down <= mouse_press_y <=
                                                         vertical_offset_down + square_size * 8):
                                square, old_x, old_y = selected_square
                                new_x, new_y = drop_pos
                                if remove_mode:
                                    self.squares[new_y][new_x].piece = ChessPiece.EMPTY
                                else:
                                    if old_x != new_x or old_y != new_y:
                                        self.squares[new_y][new_x].piece = square.piece
                                        self.squares[old_y][old_x].piece = ChessPiece.EMPTY
                        else:
                            if selected_square[0].piece.value == ChessPiece.REMOVE.value:
                                remove_mode = True
                                selected_square = None
                                continue
                            elif selected_square[0].piece.value == ChessPiece.POINTER.value:
                                remove_mode = False
                            if not remove_mode:
                                if drop_pos is not None and (offset_x <= mouse_press_x <= square_size * 8 + offset_x and
                                                             vertical_offset_down <= mouse_press_y <=
                                                             vertical_offset_down + square_size * 8):
                                    square, old_x, old_y = selected_square
                                    new_x, new_y = drop_pos
                                    self.squares[new_y][new_x].piece = square.piece
                    if self.fen_button_clicked(mouse_press_x, mouse_press_y, fen_button):
                        fen = self.convert_state_to_fen_string()
                        fen_string = f'FEN:   {fen}'
                        with open(fen_output, 'w') as f:
                            f.writelines(fen_string)
                        fen_prompt_text = button_prompt_font.render(fen_string, 1, (0, 0, 0))
                        pyperclip.copy(fen)
                        fen_url_string = '_'.join(fen.split(' '))
                        webbrowser.open(f'https://lichess.org/analysis/standard/{fen_url_string}')
                    selected_square = None
                    drop_pos = None

            surface.fill((0, 0, 0))
            self.draw_table(surface)
            self.draw_editor(surface)
            pygame.draw.rect(surface, (255, 255, 255), fen_button, 0)
            surface.blit(fen_button_text, (fen_button.x + fen_button.width // 2 - fen_button_text.get_width() // 2,
                                           fen_button.y + fen_button.height // 2 - fen_button_text.get_height() // 2))
            pygame.draw.rect(surface, (255, 255, 255), fen_prompt, 0)
            surface.blit(fen_prompt_text, (fen_prompt.x + 20, fen_prompt.y +
                                           fen_prompt.height // 2 - fen_prompt_text.get_height() // 2))
            mouse_press_x, mouse_press_y = pygame.mouse.get_pos()
            if x is not None:
                if isinstance(square, ChessSquare):
                    rect = (
                        x * square_size + offset_x, vertical_offset_down + y * square_size, square_size, square_size)
                else:
                    if self.player == 'white' and square.mode == 'white' or \
                            self.player == 'black' and square.mode == 'white':  # Top
                        rect = (x * square_size + offset_x, 10 + y * square_size, square_size, square_size)
                    else:  # Bottom
                        rect = (x * square_size + offset_x, vertical_offset_down + 10 + 8 * square_size,
                                square_size, square_size)
                pygame.draw.rect(surface, (255, 0, 0, 50), rect, 2)

            if remove_mode:
                pygame.draw.rect(surface, (255, 0, 0, 50), self.board_editor_list_black[-1].rect, 2)
                pygame.draw.rect(surface, (255, 0, 0, 50), self.board_editor_list_white[-1].rect, 2)
            if not remove_mode:
                pygame.draw.rect(surface, (255, 0, 0, 50), self.board_editor_list_black[0].rect, 2)
                pygame.draw.rect(surface, (255, 0, 0, 50), self.board_editor_list_white[0].rect, 2)
            if fen_button.collidepoint(mouse_press_x, mouse_press_y):
                rect = (fen_button.topleft[0], fen_button.topleft[1], fen_button.width, fen_button.height)
                pygame.draw.rect(surface, (255, 0, 0, 100), rect, 5)
            drop_pos = self.drag_n_drop(surface, selected_square, font)
            pygame.display.flip()
            clock.tick(60)

    def draw_table(self, surface):
        for num_row in range(self.num_rows):
            for num_col in range(self.num_cols):
                self.squares[num_row][num_col].draw(surface)

    def draw_editor(self, surface):
        for num_col in range(self.num_cols):
            self.board_editor_list_black[num_col].draw(surface)
            self.board_editor_list_white[num_col].draw(surface)

    def print_table(self):
        print(f'Printing table. Player: {self.player}.\n\n')
        for num_row in range(self.num_rows):
            print(f"Row: {num_row}: ")
            for num_col in range(self.num_cols):
                self.squares[num_row][num_col].print()
            print(f'\n')

    def white_can_castle_king_side(self):
        if self.player == 'black' and \
                (self.squares[0][3].piece.value == ChessPiece.WHITE_KING.value) and \
                (self.squares[0][0].piece.value == ChessPiece.WHITE_ROOK.value):
            return True
        if self.player == 'white' and \
                (self.squares[7][4].piece.value == ChessPiece.WHITE_KING.value) and \
                (self.squares[7][7].piece.value == ChessPiece.WHITE_ROOK.value):
            return True
        return False

    def white_can_castle_queen_side(self):
        if self.player == 'black' and \
                (self.squares[0][3].piece.value == ChessPiece.WHITE_KING.value) and \
                (self.squares[0][7].piece.value == ChessPiece.WHITE_ROOK.value):
            return True
        if self.player == 'white' and \
                (self.squares[7][0].piece.value == ChessPiece.WHITE_ROOK.value) and \
                (self.squares[7][4].piece.value == ChessPiece.WHITE_KING.value):
            return True
        return False

    def black_can_castle_king_side(self):
        if self.player == 'black' and \
                (self.squares[7][0].piece.value == ChessPiece.BLACK_ROOK.value) and \
                (self.squares[7][3].piece.value == ChessPiece.BLACK_KING.value):
            return True
        if self.player == 'white' and \
                (self.squares[0][4].piece.value == ChessPiece.BLACK_KING.value) and \
                (self.squares[0][7].piece.value == ChessPiece.BLACK_ROOK.value):
            return True
        return False

    def black_can_castle_queen_side(self):
        if self.player == 'black' and \
                (self.squares[7][3].piece.value == ChessPiece.BLACK_KING.value) and \
                (self.squares[7][6].piece.value == ChessPiece.BLACK_ROOK.value):
            return True
        if self.player == 'white' and \
                (self.squares[0][1].piece.value == ChessPiece.BLACK_ROOK.value) and \
                (self.squares[0][5].piece.value == ChessPiece.BLACK_KING.value):
            return True
        return False

    def convert_state_to_fen_string(self):
        start_fen = '/////// w KQkq - 0 1'
        fen_parts = start_fen.split('/')
        fen_parts[-1] = fen_parts[-1].split(" ")[0]
        for row in reversed(range(self.num_rows)):
            num_empty_in_row = 0
            for col in reversed(range(self.num_cols)):
                if self.squares[row][col].piece.value == ChessPiece.EMPTY.value:
                    num_empty_in_row += 1
                    if col == 0:
                        fen_parts[self.num_rows - row - 1] = f'{fen_parts[self.num_rows - row - 1]}' \
                                                             f'{str(num_empty_in_row)}'
                else:
                    # There is a figure here so write the number of empty
                    if num_empty_in_row != 0:
                        fen_parts[self.num_rows - row - 1] = f'{fen_parts[self.num_rows - row - 1]}' \
                                                             f'{str(num_empty_in_row)}'
                    # Then write the figure
                    fen_parts[self.num_rows - row - 1] = f'{fen_parts[self.num_rows - row - 1]}' \
                                                         f'{str(self.squares[row][col].piece.value)}'

                    num_empty_in_row = 0

        fen_string = "/".join(fen_parts) + ' '
        fen_string += 'w ' if self.to_play == 'white' else 'b '
        at_least_one_castle = False
        if self.white_can_castle_king_side():
            at_least_one_castle = True
            fen_string += 'K'
        if self.white_can_castle_queen_side():
            at_least_one_castle = True
            fen_string += 'Q'
        if self.black_can_castle_king_side():
            at_least_one_castle = True
            fen_string += 'k'
        if self.black_can_castle_queen_side():
            at_least_one_castle = True
            fen_string += 'q'
        if not at_least_one_castle:
            fen_string += '-'

        fen_string += ' - '  # En passant?
        fen_string += '0 1'

        return fen_string

    @staticmethod
    def convert_game_dict_to_list(game_state):
        # 0 is top left, 63 is bottom right
        game_state_list = list(np.zeros(shape=(8, 8), dtype=object))
        for square_num, figure in sorted(game_state.items(), key=lambda item: int(item[0]), reverse=False):
            row_num = int(square_num) // 8
            col_num = int(square_num) % 8
            game_state_list[row_num][col_num] = ChessSquare.map_figure_to_enum(figure)
        return game_state_list


class ChessSquare:
    def __init__(self, num_row, num_col, color, table_index, model_index, piece):
        self.num_row = num_row
        self.num_col = num_col
        self.color = color
        self.table_index = table_index
        self.model_index = model_index
        self.piece = piece
        self.size = square_size

    def set_rectangle(self):
        top_left_point = (offset_x + self.num_col * self.size, vertical_offset_down + self.num_row * self.size)
        size = (self.size, self.size)
        return pygame.Rect(top_left_point, size)

    def set_figure_image(self):
        figure = None
        if self.piece != ChessPiece.EMPTY:
            piece_image = self.get_image_for_piece()
            figure = pygame.image.load(piece_image).convert_alpha()
            figure = pygame.transform.scale(figure, (square_size, square_size))
        return figure

    def get_image_for_piece(self):
        if str(self.piece.value).isupper():
            # White
            if self.color == white_square_color:
                return os.path.join(r'F:\Jupyter notebooks\Chess\chess_draw\images', f'w_w{str(self.piece.value.lower())}.PNG')
            else:
                return os.path.join(r'F:\Jupyter notebooks\Chess\chess_draw\images', f'b_w{str(self.piece.value.lower())}.PNG')
        else:
            # Black
            if self.color == white_square_color:
                return os.path.join(r'F:\Jupyter notebooks\Chess\chess_draw\images', f'w_b{str(self.piece.value.lower())}.PNG')
            else:
                return os.path.join(r'F:\Jupyter notebooks\Chess\chess_draw\images', f'b_b{str(self.piece.value.lower())}.PNG')

    def draw(self, surface):
        rect = self.set_rectangle()
        figure = self.set_figure_image()
        pygame.draw.rect(surface, self.color, rect)
        if figure is not None:
            surface.blit(figure, rect.topleft)

    def print(self):
        print(f"{self.color} ({str(self.num_row)},{str(self.num_col)}) -> "
              f"{str(self.table_index)}/{str(self.model_index)} {self.piece.value}")

    @staticmethod
    def map_figure_to_enum(figure):
        parts = figure.split('_')
        if len(parts) == 1:
            return ChessPiece.EMPTY
        else:
            color = parts[0]
            figure = parts[1]
            if color == 'white':
                if figure == 'rook':
                    return ChessPiece.WHITE_ROOK
                elif figure == 'knight':
                    return ChessPiece.WHITE_KNIGHT
                elif figure == 'bishop':
                    return ChessPiece.WHITE_BISHOP
                elif figure == 'king':
                    return ChessPiece.WHITE_KING
                elif figure == 'pawn':
                    return ChessPiece.WHITE_PAWN
                else:
                    return ChessPiece.WHITE_QUEEN
            else:
                if figure == 'rook':
                    return ChessPiece.BLACK_ROOK
                elif figure == 'knight':
                    return ChessPiece.BLACK_KNIGHT
                elif figure == 'bishop':
                    return ChessPiece.BLACK_BISHOP
                elif figure == 'king':
                    return ChessPiece.BLACK_KING
                elif figure == 'pawn':
                    return ChessPiece.BLACK_PAWN
                else:
                    return ChessPiece.BLACK_QUEEN


class ChessEditorSquare:
    def __init__(self, num, piece, player, mode):
        self.num = num
        self.piece = piece
        self.player = player
        self.mode = mode
        self.color = (107, 107, 107)
        self.size = square_size

    def set_rectangle(self):
        if self.player == 'white':
            # Draw white down and black up
            if self.mode == 'white':
                # White
                top_left_point = (offset_x + self.num * self.size, vertical_offset_down + 8 * self.size + offset)
            else:
                # Black
                top_left_point = (offset_x + self.num * self.size, 10)
        else:
            # Draw white down and black up
            if self.mode == 'white':
                # White
                top_left_point = (offset_x + self.num * self.size, 10)
            else:
                # Black
                top_left_point = (offset_x + self.num * self.size, vertical_offset_down + 8 * self.size + 10)
        size = (self.size, self.size)
        return pygame.Rect(top_left_point, size)

    def set_figure_image(self):
        piece_image = self.get_image_for_piece()
        figure = pygame.image.load(piece_image).convert_alpha()
        figure = pygame.transform.scale(figure, (square_size, square_size))
        return figure

    def get_image_for_piece(self):
        if str(self.piece.value) == ChessPiece.POINTER.value:
            # Pointer
            return os.path.join(r'F:\Jupyter notebooks\Chess\chess_draw\images', 'pointer.PNG')
        if str(self.piece.value) == ChessPiece.REMOVE.value:
            # Remove
            return os.path.join(r'F:\Jupyter notebooks\Chess\chess_draw\images', 'remove.PNG')
        if str(self.piece.value).isupper():
            # White
            if self.color == white_square_color:
                return os.path.join(r'F:\Jupyter notebooks\Chess\chess_draw\images', f'e_w{str(self.piece.value.lower())}.PNG')
            else:
                return os.path.join(r'F:\Jupyter notebooks\Chess\chess_draw\images', f'e_w{str(self.piece.value.lower())}.PNG')
        else:
            # Black
            if self.color == white_square_color:
                return os.path.join(r'F:\Jupyter notebooks\Chess\chess_draw\images', f'e_b{str(self.piece.value.lower())}.PNG')
            else:
                return os.path.join(r'F:\Jupyter notebooks\Chess\chess_draw\images', f'e_b{str(self.piece.value.lower())}.PNG')

    def draw(self, surface):
        self.rect = self.set_rectangle()
        figure = self.set_figure_image()
        pygame.draw.rect(surface, self.color, self.rect)
        if figure is not None:
            surface.blit(figure, self.rect.topleft)


if __name__ == "__main__":
    # white_table = ChessTable()  # White board
    # black_table = ChessTable(player='black')
    # white_table.draw_table('white_table.png')
    # black_table.draw_table('black_table.png')
    test_setup = [[ChessPiece.WHITE_ROOK, ChessPiece.EMPTY, ChessPiece.WHITE_BISHOP, ChessPiece.WHITE_KING,
                   ChessPiece.WHITE_QUEEN, ChessPiece.EMPTY, ChessPiece.WHITE_KNIGHT, ChessPiece.WHITE_ROOK],
                  [ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN, ChessPiece.EMPTY,
                   ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.WHITE_PAWN, ChessPiece.WHITE_PAWN],
                  [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.WHITE_KNIGHT, ChessPiece.WHITE_PAWN,
                   ChessPiece.EMPTY, ChessPiece.WHITE_PAWN, ChessPiece.EMPTY, ChessPiece.EMPTY],
                  [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.WHITE_BISHOP, ChessPiece.EMPTY,
                   ChessPiece.WHITE_PAWN, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
                  [ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY,
                   ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
                  [ChessPiece.EMPTY, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_KNIGHT, ChessPiece.EMPTY,
                   ChessPiece.BLACK_PAWN, ChessPiece.EMPTY, ChessPiece.EMPTY, ChessPiece.EMPTY],
                  [ChessPiece.BLACK_PAWN, ChessPiece.BLACK_BISHOP, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN,
                   ChessPiece.EMPTY, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN, ChessPiece.BLACK_PAWN],
                  [ChessPiece.EMPTY, ChessPiece.BLACK_KING, ChessPiece.BLACK_ROOK, ChessPiece.EMPTY,
                   ChessPiece.BLACK_QUEEN, ChessPiece.BLACK_BISHOP, ChessPiece.BLACK_KNIGHT, ChessPiece.BLACK_ROOK]]
    test_table = ChessTable(player='black', board=test_setup, to_play='white')
    fen_output = 'fen.txt'
    test_table.simulate_chess_game('test_table.png', fen_output)
