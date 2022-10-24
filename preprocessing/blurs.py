import argparse
import glob
import os

import numpy as np
import cv2


def find_chesssquare_color(img_input, img_output):
    img = cv2.imread(img_input, 0)
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    _, img_binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(img_output, img_binary)


def find_chesspiece_color(img_input, img_output):
    img = cv2.imread(img_input, 0)
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    _, img_binary = cv2.threshold(blur, 115, 255, cv2.THRESH_BINARY)

    img_binary_inverted = cv2.bitwise_not(img_binary)

    # remove noise
    morph_kernel = np.ones((15, 15), np.uint8)
    output = cv2.morphologyEx(img_binary_inverted, cv2.MORPH_CLOSE, morph_kernel)
    cv2.imwrite(img_output, output)


def find_chesspiece_colors(image_folder):
    # This is the folder containing all of the image subdirectories
    # We read all subdirectories and append the morph transform image here
    subdirs = os.listdir(image_folder)
    subdirs = [os.path.join(image_folder, subdir) for subdir in subdirs]
    for image_dir in subdirs:
        input_image = os.path.join(image_dir, 'chesstable.jpg')
        output_image = os.path.join(image_dir, 'morph_chesstable.jpg')
        find_chesspiece_color(input_image, output_image)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Use image preprocessing to derive square and piece color.')

    p.add_argument('function', nargs=1, type=str, help='what function to run (default: find_chesssquare_color')
    p.add_argument('--input', type=str, help='input image (default: input.jpg)')
    p.add_argument('--output', type=str, help='output path (default: output.jpg)')
    args = p.parse_args()
    function = str(args.function[0])

    functions = {'find_chesssquare_color': find_chesssquare_color,
                 'find_chesspiece_color': find_chesspiece_color}
    functions[function](args.input, args.output)
