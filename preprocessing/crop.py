import os
from PIL import Image
from numpy import asarray
import numpy as np
import cv2


def crop_image(image, image_output_path):
    image = Image.open(image)
    M = int(np.ceil((image.size[0]) / 8))
    N = image.size[1] // 8
    image = asarray(image)
    tiles = [image[max(0, x):x + M, max(0, y):y + N]
             for x in range(0, image.shape[0], M)
             for y in range(0, image.shape[1], N)]
    tile_num = 0
    for tile in tiles:
        tile_image = Image.fromarray(tile)
        final_output_path = os.path.join(image_output_path, f'tile_{tile_num}.jpg')
        tile_image.save(final_output_path)
        tile_num += 1


def crop_image_with_orientation(image, output_name, output_dir, orientation):
    image = Image.open(image)
    os.makedirs(output_dir, exist_ok=True)
    M = int(np.ceil((image.size[0]) / 8))
    N = image.size[1] // 8
    image = np.array(image)
    tiles = [image[max(0, x):x + M, max(0, y):y + N]
             for x in range(0, image.shape[0], M)
             for y in range(0, image.shape[1], N)]
    for row_ind in range(8):
        for col_ind in range(8):
            counter = row_ind*8 + col_ind
            tile = tiles[counter]

            # Here we need to take into account the orientation to fix up the name
            if orientation is not None:
                new_row_ind = 0
                new_col_index = 0
                # We need to define the mappings here
                if orientation == 'front':
                    new_row_ind = 7 - row_ind
                    new_col_index = col_ind
                elif orientation == 'left':
                    new_row_ind = 7 - col_ind
                    new_col_index = 7 - row_ind
                elif orientation == 'behind':
                    new_row_ind = row_ind
                    new_col_index = 7 - col_ind
                elif orientation == 'right':
                    new_row_ind = col_ind
                    new_col_index = row_ind

                square_number = new_row_ind * 8 + new_col_index
                out_loc = str(output_dir) + "/" + str(output_name) + "_square_" + str(square_number) + ".jpg"

                rgb = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
                cv2.imwrite(out_loc, rgb)


def crop_images(image_folder):
    # This is the folder containing all of the image subdirectories
    # We read all subdirectories and append the morph transform image here
    subdirs = os.listdir(image_folder)
    subdirs = [os.path.join(image_folder, subdir) for subdir in subdirs]
    for image_dir in subdirs:
        input_image_detected = os.path.join(image_dir, 'chesstable.jpg')
        input_image_morph = os.path.join(image_dir, 'morph_chesstable.jpg')
        crop_out_folder = os.path.join(image_dir, 'cropped')
        crop_pieces_folder = os.path.join(image_dir, 'pieces/predict')
        os.makedirs(crop_out_folder, exist_ok=True)
        os.makedirs(crop_pieces_folder, exist_ok=True)
        crop_image(input_image_detected, crop_pieces_folder)
        crop_image(input_image_morph, crop_out_folder)


if __name__ == "__main__":
    crop_folder = 'result_crop'
    image_path = 'bogulec_game_1_test_move_4_blurred.jpg'
    image_output_path = os.path.join(crop_folder, image_path.split('.jpg')[0])
    os.makedirs(image_output_path, exist_ok=True)
    crop_image(image_path, image_output_path)
