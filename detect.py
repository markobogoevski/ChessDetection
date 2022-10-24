import os
import argparse
import pickle
from improved_neural_chessboard.LiveChess2FEN import custom_board_detection
from preprocessing import (blurs, crop, find_chesspiece_colors)
from piece_detection import test
from chess_draw import Chess


def detect(args=None):
    # The input is a folder of images for which we need to detect the fen and provide the UI
    #input = args.input
    input = 'testing/test_input'
    # The output folder will be used to store the steps taken.
    # output = args.output
    output = 'testing/test_output'
    os.makedirs(output, exist_ok=True)

    # Step 1. Detecting chessboards out of the images and finding the pieces
    print(f'Detecting chessboards.')
    custom_board_detection.main(input, output)

    # Step 2. Crop. Blur the images. Split the blurred images into a separate folder for each tile out of 64 (will be
    # used for determining piece color)
    print(f"Blurring and splitting images.")
    blurs.find_chesspiece_colors(output)
    crop.crop_images(output)

    # Step 3. Detecting chesspieces for each board. Inputs will be the pieces folders stacked. We will use the image
    # name to defer how to reconstruct each image.
    model_path = 'piece_detection/new_model/model/chess_piece_detection_model.h5'
    encoder_path = 'piece_detection/new_model/encoder/encoder.pkl'
    subdirs = os.listdir(output)
    image_dirs = [os.path.join(output, subdir) for subdir in subdirs]
    test_dirs = [os.path.join(image_dir, 'pieces') for image_dir in image_dirs]
    print("Detecting chess pieces.")
    test.test_multiple(model_path, encoder_path, test_dirs)

    # Step 4. Detecting chesscolors of pieces for each board and saving new dictionary
    find_chesspiece_colors.colorize_and_convert_multiple_game_dicts(output)

    # Step 5. Using the game dictionaries to launch up the UI with the games loaded and FEN generated per game.
    for image_dir in image_dirs:
        game_state_path = os.path.join(image_dir, 'game_state_colorized.pkl')
        with open(game_state_path, 'rb') as f:
            game_state = pickle.load(f)
        player = os.path.basename(image_dir).split('_player')[0]
        setup = Chess.ChessTable.convert_game_dict_to_list(game_state)
        table = Chess.ChessTable(player=player, board=setup, to_play='white')
        digital_image_output = os.path.join(image_dir, 'digital_table.jpg')
        fen_path = os.path.join(image_dir, 'fen.txt')
        print(f"Running board game editor simulation for {image_dir}.")
        table.simulate_chess_game(digital_image_output, fen_path)


if __name__ == "__main__":
    detect()
    # p = argparse.ArgumentParser(description='Convert chess game image to digital board.')
    #
    # p.add_argument('--input', type=str, help='input image (default: input.jpg)')
    # p.add_argument('--output', type=str, help='output folder path for saving intermediate steps')
    #
    # args = p.parse_args()
    # detect(args)
