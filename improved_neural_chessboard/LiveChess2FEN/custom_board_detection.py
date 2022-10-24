"""
Executes the detection of a chessboard.
"""
"""
Processes input boards and their transformation to individual pieces.
Useful when testing the detectboard module or to create images for a
dataset.
"""
import glob
import os
import re
import shutil

import cv2
from tqdm import tqdm

from lc2fen.detectboard import detect_board
from lc2fen.fen import fen_to_board, rotate_board_fen2image
from lc2fen.split_board import split_square_board_image, split_board_image
from preprocessing.crop import crop_image_with_orientation


def regenerate_data_state(input, output):
    """
    Regenerates the state of the data directory.

    Deletes all files and subdirectories in 'data_path/boards/output',
    'data_path/boards/debug_steps' and 'data_path/pieces'. Regenerates
    these directories and the pieces subdirectories.

    :param data_path: Path to the 'data' folder. For example: '../data'.
    """
    images = glob.glob(input + '/*.jpg')
    base_image_names = [os.path.basename(image).split('.')[0] for image in images]
    # We will name the subfolders according to the images
    for base_image_name in base_image_names:
        image_subfolder = os.path.join(output, base_image_name)
        os.makedirs(image_subfolder, exist_ok=True)
        # Creating pieces folder
        pieces_folder = os.path.join(image_subfolder, 'pieces/predict')
        os.makedirs(pieces_folder, exist_ok=True)


def split_detected_square_boards(data_path):
    """
    Splits all detected .jpg boards in 'data_path/boards/output' into
    individual pieces in 'data_path/pieces' classifying them
    by fen. Line i of .fen file corresponds to board i .jpg. Fen file
    must be in 'data_path/boards/input'.

    :param data_path: Path to the 'data' folder. For example: '../data'.
    """

    def natural_key(text):
        return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]

    detected_boards = sorted(glob.glob(data_path + '/boards/output/*.jpg'),
                             key=natural_key)
    print("DETECTED: %d boards" % len(detected_boards))

    fen_file = glob.glob(data_path + '/boards/input/*.fen')
    if len(fen_file) != 1:
        raise ValueError("Only one fen file must be in input directory")

    with open(fen_file[0], 'r') as fen_fd:
        for detected_board in detected_boards:
            # Next line without '\n' split by spaces
            line = fen_fd.readline()[:-1].split()
            if len(line) != 2:
                raise ValueError("All lines in fen file must have the format "
                                 "'fen orientation'")

            board_labels = rotate_board_fen2image(fen_to_board(line[0]),
                                                  line[1])
            name = os.path.splitext(os.path.basename(detected_board))[0]
            split_square_board_image(detected_board, name,
                                     data_path + '/pieces', board_labels)


def create_move_orientation_mapper(total_number_of_moves):
    images_per_orientation = 5  # 5 from each side
    orientation_order = ['front', 'left', 'behind', 'right']
    number_orientations = len(orientation_order)
    number_of_whole_sets_of_rotations = total_number_of_moves // (images_per_orientation * number_orientations)
    remainder_set_rotations = total_number_of_moves % (images_per_orientation * number_orientations)
    final_mapper = dict()
    for whole_set_number in range(number_of_whole_sets_of_rotations):
        for orientation_index in range(number_orientations):
            orientation = orientation_order[orientation_index]
            orientation_list = [whole_set_number * images_per_orientation * number_orientations
                                + orientation_index * images_per_orientation + move_no
                                for move_no in range(0, images_per_orientation)]
            for move in orientation_list:
                final_mapper[move] = orientation

    # Now to deal with the remainders
    moves_left = remainder_set_rotations
    orientations_left = moves_left // images_per_orientation
    for orientation_index in range(orientations_left):  # Still full orientations
        orientation = orientation_order[orientation_index]
        orientation_list = [number_of_whole_sets_of_rotations * images_per_orientation * number_orientations
                            + orientation_index * images_per_orientation + move_no
                            for move_no in range(0, images_per_orientation)]
        for move in orientation_list:
            final_mapper[move] = orientation

    moves_left -= orientations_left * images_per_orientation

    remaining_orientation_index = orientations_left
    orientation_list = [number_of_whole_sets_of_rotations * images_per_orientation * number_orientations
                        + remaining_orientation_index * images_per_orientation + move_no
                        for move_no in range(0, moves_left + 1)]
    for move in orientation_list:
        final_mapper[move] = orientation_order[remaining_orientation_index]

    return final_mapper


def process_input_boards(data_path):
    """
    Detects all boards in 'data_path/boards/input' and stores the
    results in 'data_path/boards/output'.

    :param data_path: Path to the 'data' folder. For example: '../data'.
    """

    def natural_key(text):
        return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]

    input_boards = sorted(glob.glob(data_path + '/raw/*.jpg'),
                          key=natural_key)

    print("INPUT: %d boards" % len(input_boards), flush=True)
    # Here we get to know the total amount of moves and map them to the orientation
    # We define the orientation of the image upfront. We do 5 moves of each side always until we exhaust
    # the moves (5 front, 5 left, 5 behind, 5 right etc. in clockwise fashion)
    # This way we can always map the squares to the original chess com coordinates
    orientation_mapper = create_move_orientation_mapper(total_number_of_moves=len(input_boards))
    for input_board in tqdm(input_boards):
        output_board = input_board.replace('raw', 'improved_raw_table')
        input_image = cv2.imread(input_board)
        # Here we get the move number from the name of the image
        try:
            #image_object = detect_board.detect(input_image, output_board)
           # _, square_corners = detect_board.compute_corners(image_object)
            name = os.path.splitext(os.path.basename(input_board))[0]
            move_number = int(name.split('move_')[1])
            orientation = orientation_mapper[move_number]
            crop_image_with_orientation(output_board, name, data_path + '/pieces', orientation=orientation)
        except Exception as e:
            print(str(e))
            # if square_corners is None:
            #     output_board = output_board.split(".jpg")[0] + '_skip.jpg'
            #     cv2.imwrite(output_board, input_image)


def process_tables(input, output):
    def natural_key(text):
        return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]

    input_boards = sorted(glob.glob(input + '/*.jpg'),
                          key=natural_key)
    print("INPUT: %d boards" % len(input_boards), flush=True)
    for input_board in tqdm(input_boards):
        print(f'Processing {os.path.basename(input_board)}.')
        move_name = os.path.basename(input_board).split('.')[0]
        move_folder = os.path.join(output, move_name)
        table_path = os.path.join(move_folder, 'chesstable.jpg')
        pieces_path = os.path.join(move_folder, 'pieces/predict')
        input_image = cv2.imread(input_board)
        # Here we get the move number from the name of the image
        try:
            detect_board.detect(input_image, table_path)
            # _, square_corners = detect_board.compute_corners(image_object)
            # split_board_image(input_image, square_corners, move_name, pieces_path)
        except Exception as e:
            print(str(e))
            print(f"Please retry with a new image for {input_board}.")


def main(input, output):
    regenerate_data_state(input, output)
    process_tables(input, output)


def process_set(data_path):
    os.makedirs(os.path.join(data_path, 'improved_raw_table'), exist_ok=True)
    process_input_boards(data_path)


if __name__ == "__main__":
    game_numbers = ['1', '2', '5', '24', '33']
    #game_numbers = ['33']
    data_paths = [f'../../piece_detection/dataset/own_camera_dataset_newest/bogulec_game_{game_number}'
                  for game_number in game_numbers]
    for data_path in data_paths:
        print(f'Processing {data_path}.')
        process_set(data_path)
