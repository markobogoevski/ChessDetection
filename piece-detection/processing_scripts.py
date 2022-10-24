"""
We won't care about piece color as this will be infered using the tile color and whether a piece is on the tile
"""

import os
import chess.pgn
import glob
from PIL import Image
import shutil
import xml.etree.ElementTree as ET
import cv2
import pandas as pd




def remove_word_from_images(folder_path):
    files = glob.glob(folder_path + '/*.jpg')
    for file in files:
        new_name = str(file).replace('_test', '')
        os.rename(file, new_name)

def add_word_to_images(folder_path, word):
    files = glob.glob(folder_path + '/*.jpg')
    for file in files:
        basename = os.path.basename(file)
        new_path = os.path.join(folder_path,f'{word}_{basename}')
        os.rename(file, new_path)


def rename_from_drive(folder_path):
    # The tail of folder path name contains the game number
    file_tail = os.path.basename(folder_path)
    images = glob.glob(folder_path + '/*.jpg')
    folder_path = os.path.join(folder_path, 'raw')
    os.makedirs(folder_path, exist_ok=True)
    # Sort the images according to their names in descending order
    images = sorted(images, reverse=True)
    for move_number, image in enumerate(images):
        new_image_name = os.path.join(folder_path, f'{file_tail}_move_{move_number}.jpg')
        shutil.move(image, new_image_name)
        # Also rotate the image
        image_obj = Image.open(new_image_name)
        image_width, image_height = image_obj.size
        if image_width < image_height:  # Needs to rotate
            rotated = image_obj.rotate(90, expand=True)
            rotated.save(new_image_name)
        else:
            image_obj.save(new_image_name)


def map_piece_symbol(piece):
    if piece is None:
        figure = "empty"
    else:
        figure = str(piece)
        if figure.lower() == 'r':
            figure = 'rook'
        elif figure.lower() == 'n':
            figure = 'knight'
        elif figure.lower() == 'b':
            figure = 'bishop'
        elif figure.lower() == 'q':
            figure = 'queen'
        elif figure.lower() == 'k':
            figure = 'king'
        elif figure.lower() == 'p':
            figure = 'pawn'

    return figure


def process_own_dataset(input_path, output_path):
    """
    Here we will use the detect chess table model to extract 64 tiles per image. Then we will use the python chess api
    to walk through the games, get every move, and save each tile image as the piece label
    """
    os.makedirs(output_path, exist_ok=True)
    # Every game is named bogulec_game_{game_no}_move_{move_number}_tile_{tile_num}.jpg
    pgn_folder = 'dataset/replayed_fen_games'  # These are the games which were replayed on chess
    # Glob through all images
    images = glob.glob(input_path + '/*.jpg')
    # Glob through all pgn files
    pgn_game_files = glob.glob(pgn_folder + '/*.pgn')
    game_counter = 1
    # Read the game file and set board
    for file in pgn_game_files:
        file_tail = os.path.basename(file).split(".pgn")[0]  # Get name of game, will be used to associate with images
        print(f'Processing game: {file_tail}. ({game_counter}/{len(pgn_game_files)}).')
        game_counter += 1
        with open(file, 'r') as game_file:
            game = chess.pgn.read_game(game_file)
            board = game.board()
            for move_num, move in enumerate(game.mainline_moves()):
                for tile_num in range(64):
                    piece = board.piece_at(tile_num)
                    # Read image file
                    image_file = f'{file_tail}_move_{move_num}_tile_{tile_num}.jpg'
                    # Save image with label
                    label = map_piece_symbol(piece)
                    # new_image_name = f'{file_tail}_move_{move_num}_tile_{tile_num}_{label}.jpg'
                    # # Save to output folder
                    # path = os.path.join(output_path, new_image_name)
                    # image = Image.open(image_file)
                    # image.save(output_path)
                board.push(move)
    pass


def process_kaggle(input_path, output_path):
    """
    Here we need to use the xml annotations to find the label for the image and put them in the same place
    """
    os.makedirs(output_path, exist_ok=True)
    annotation_folder = os.path.join(input_path, 'annotations')
    images_folder = os.path.join(input_path, 'images')
    annotations = sorted(glob.glob(annotation_folder + '/*.xml'))
    images = sorted(glob.glob(images_folder + '/*.JPG'))
    counter = 0
    for annotation, image in zip(annotations, images):
        print(f"Processing annotation {annotation} for image {image}.")
        tree = ET.parse(annotation)
        root = tree.getroot()
        pieces = root.findall('object')
        for piece in pieces:
            label = piece.find('name').text.split('-')[1]
            bounding_box = piece.find('bndbox')
            xmin = int(bounding_box.find('xmin').text)
            xmax = int(bounding_box.find('xmax').text)
            ymin = int(bounding_box.find('ymin').text)
            ymax = int(bounding_box.find('ymax').text)
            actual_image = cv2.imread(image)
            roi = actual_image[ymin:ymax, xmin:xmax]
            image_output = os.path.join(output_path, label)
            os.makedirs(image_output, exist_ok=True)
            image_output = os.path.join(image_output, f'image_number_{counter}.jpg')
            counter += 1
            cv2.imwrite(image_output, roi)


def process_roboflow(input_path, output_path):
    """
    Here we have a representation of every image provided as a row in a excel file. We can use the bounding boxes for
    each label and image to extract the piece image from the whole image and save it with the corresponding label
    """
    os.makedirs(output_path, exist_ok=True)
    # Here we have test, train and valid folders but we will use all for labeling as training and make the split after
    # on the final set. All follow same structure
    folders = ['test', 'train', 'valid']
    counter = 0
    for folder in folders:
        print(f'Processing folder {folder}.')
        folder_input_path = os.path.join(input_path, folder)
        annotation = glob.glob(folder_input_path + '/*.csv')[0]  # Annotation file
        df = pd.read_csv(annotation, header=0)
        for index, row in df.iterrows():
            image_name = row['filename']
            print(f'Processing image {image_name}.')
            if '-' in row['class']:
                label = row['class'].split('-')[1]
            else:
                label = row['class']
            xmin = int(row['xmin'])
            xmax = int(row['xmax'])
            ymin = int(row['ymin'])
            ymax = int(row['ymax'])
            full_image_name_input = os.path.join(folder_input_path, image_name)
            actual_image = cv2.imread(full_image_name_input)
            roi = actual_image[ymin:ymax, xmin:xmax]
            image_output = os.path.join(output_path, label)
            os.makedirs(image_output, exist_ok=True)
            image_output = os.path.join(image_output, f'image_number_{counter}.jpg')
            counter += 1
            cv2.imwrite(image_output, roi)


if __name__ == "__main__":
    pass
    # rename_from_drive('dataset/own_camera_dataset_new/bogulec_game_8')
    # figures = ['bishop', 'knight', 'pawn', 'queen', 'rook', 'empty', 'king']
    # folders = [os.path.join('dataset/bakkenbaeck/processed', figure) for figure in figures]
    # for folder in folders:
    #     add_word_to_images(folder_path=folder, word='bakkenbaeck')
    # input_dataset_own = 'dataset/own_camera_dataset_new/bogulec_game_1_test/pieces'
    # output_dataset_own = 'dataset/own_camera_dataset_new/bogulec_game_1/processed'
    # process_own_dataset(input_dataset_own, output_dataset_own)
    #
    # input_dataset_kaggle = 'dataset/kaggle/Chess Detection/raw'
    # output_dataset_kaggle = 'dataset/kaggle/Chess Detection/processed'
    # process_kaggle(input_dataset_kaggle, output_dataset_kaggle)
    #
    # input_roboflow_dataset = 'dataset/roboflow/raw'
    # output_roboflow_dataset = 'dataset/roboflow/processed'
    # process_roboflow(input_roboflow_dataset, output_roboflow_dataset)
