import glob
import os
from PIL import Image
import numpy as np
import pickle


def switch_color(color):
    if color == 'white':
        return 'black'
    return 'white'


def get_empty_square_color(empty_square_image):
    distribution = get_square_color_dist(empty_square_image)
    # Get the most frequent color
    dominant_color = distribution[-1][1]
    return dominant_color


def get_square_color_dist(square_image):
    width, height = 150, 150
    image = Image.open(square_image)
    image = image.resize((width, height), resample=0)
    # Get colors from image object
    pixels = image.getcolors(width * height)
    # Sort them by count number(first element of tuple)
    sorted_pixels = sorted(pixels, key=lambda t: t[0])
    return sorted_pixels


def main(tile_folder, game):
    tiles = glob.glob(tile_folder + '/*.jpg')
    # Find an empty tile and get it from the tile folder
    empty_found = False
    first_empty = 0
    for row_num in range(len(game)):
        for col_num in range(len(game[row_num])):
            if game[row_num][col_num] == 'empty':
                empty_found = True
                break
            first_empty += 1
        if empty_found:
            break

    # Get the tile with the empty square to find its color
    empty_square_image = os.path.join(tile_folder, f'tile_{str(first_empty)}.jpg')
    row_of_square = first_empty // 8
    color_of_empty_square = get_empty_square_color(empty_square_image)

    # Now since we know which row and which column the color of the square is, we can find others
    top_left_color = 'white'
    if color_of_empty_square == 0:  # Black
        if row_of_square % 2 == 0 and first_empty % 2 == 0 or \
                row_of_square % 2 == 1 and first_empty % 2 == 1:  # Top left is black
            top_left_color = 'black'
    else:  # White
        if row_of_square % 2 == 1 and first_empty % 2 == 0 or \
                row_of_square % 2 == 0 and first_empty % 2 == 1:  # Top left is black
            top_left_color = 'black'

    # Because we did a binary blur, inverting the colors, black is actually white and other way around
    top_left_color = switch_color(top_left_color)
    print(f'Top left is : {top_left_color}.')

    # Now since we have the color of the first square, we can color all other tiles just by following pattern
    tile_colors = dict()
    for tile_row in range(8):
        for tile_col in range(8):
            tile_number = tile_row * 8 + tile_col
            tile_colors[str(tile_number)] = top_left_color
            if tile_col != 7:  # if its not the end of the row, change the color
                top_left_color = switch_color(top_left_color)
    # print(f"Tile colors: {tile_colors}.")

    # To find the colors of the pieces, we can use the information on the tile of the color and whether there is a piece
    # on the square or not. If a black piece is on a white field, then the blurred version of that tile would have
    # mashed up colors of black and white. If a piece of the same color is on the field as the field itself, the color
    # would still be >95% same as the dominant one.
    piece_colors = dict()  # We will label them as tile_number: piece with color
    threshold = 0.87  # This can be changed or ML learned
    for image_tile in sorted(tiles, key=lambda name: int(name.split('.jpg')[0].split('tile_')[1]), reverse=False):
        color_dist = get_square_color_dist(image_tile)
        tile_num = os.path.basename(image_tile).split('.jpg')[0].split('tile_')[1]
        tile_color = tile_colors[tile_num]
        # Get two last values from color distribution and check their counts
        dominant_color_count = color_dist[-1][0]
        second_dominant_color_count = color_dist[-2][0] if len(color_dist) != 1 else None
        ratio = float(dominant_color_count) / float(second_dominant_color_count + dominant_color_count) \
            if second_dominant_color_count is not None else 1
        # print(f'Color distribution for tile {tile_num}. Dominant color times: {dominant_color_count}. '
        #       f'Second dominant color count: {second_dominant_color_count}. Ratio dominant vs second dominant: {np.round(ratio, 3)}.')
        row_index = int(tile_num) // 8
        col_index = int(tile_num) % 8
        piece = game[row_index][col_index]
        if piece == 'empty':
            piece_colors[tile_num] = 'empty'
        else:
            if tile_color == 'white' and ratio < threshold:
                piece_colors[tile_num] = f'black_{piece}'
            elif tile_color == 'white' and ratio >= threshold:
                piece_colors[tile_num] = f'white_{piece}'
            elif tile_color == 'black' and ratio < threshold:
                piece_colors[tile_num] = f'white_{piece}'
            else:
                piece_colors[tile_num] = f'black_{piece}'

    # print(f'Final colors of pieces: {piece_colors}')
    return piece_colors, tile_colors


def convert_game_state_dict_to_list(game_state_dict_path):
    with open(game_state_dict_path, 'rb') as f:
        game_state = pickle.load(f)
    # 0 is top left, 63 is bottom right
    game_state_list = list(np.zeros(shape=(8, 8), dtype=object))
    for square_num, figure in sorted(game_state.items(), key=lambda item: int(item[0]), reverse=False):
        row_num = int(square_num) // 8
        col_num = int(square_num) % 8
        game_state_list[row_num][col_num] = figure
    return game_state_list


def colorize_and_convert_multiple_game_dicts(images_folder):
    print("Colorizing game states.")
    subdirs = os.listdir(images_folder)
    image_dirs = [os.path.join(images_folder, subdir) for subdir in subdirs]
    game_states = [os.path.join(image_dir, 'game_state_pre_coloring.pkl') for image_dir in image_dirs]
    game_state_lists = [convert_game_state_dict_to_list(game_state) for game_state in game_states]
    tile_folders = [os.path.join(image_dir, 'cropped') for image_dir in image_dirs]
    modified_dictionaries = [main(tile_folder, game_state_list)
                             for tile_folder, game_state_list in zip(tile_folders, game_state_lists)]
    for image_dir, modified_dictionary in zip(image_dirs, modified_dictionaries):
        new_dict_path = os.path.join(image_dir, 'game_state_colorized.pkl')
        with open(new_dict_path, 'wb') as f:
            pickle.dump(modified_dictionary[0], f)


if __name__ == "__main__":
    tile_folder = f'result_crop/bogulec_game_1_test_move_4_blurred'
    # This would be the result from the model besides the colors of the pieces where top left is tile 0
    # bottom right is tile 63
    game = [
        ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'empty', 'rook'],
        ['pawn', 'pawn', 'pawn', 'empty', 'pawn', 'pawn', 'pawn', 'pawn'],
        ['empty', 'empty', 'empty', 'empty', 'empty', 'knight', 'empty', 'empty'],
        ['empty', 'empty', 'empty', 'pawn', 'empty', 'empty', 'empty', 'empty'],
        ['empty', 'empty', 'empty', 'pawn', 'empty', 'pawn', 'empty', 'empty'],
        ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
        ['pawn', 'pawn', 'pawn', 'empty', 'pawn', 'empty', 'pawn', 'pawn'],
        ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']]
    piece_colors, tile_colors = main(tile_folder, game)
