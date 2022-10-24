import argparse
import gc
import glob
import os
import utils

print("<<< \x1b[5;32;40m neural-chessboard \x1b[0m >>>")

from config import *
from utils import ImageObject
from slid import pSLID, SLID, slid_tendency  # == step 1
from laps import LAPS  # == step 2
from llr import LLR, llr_pad  # == step 3

from keras import backend as K
import cv2;

load = cv2.imread
save = cv2.imwrite


# NC_SCORE = -1

################################################################################

def layer():
    global NC_LAYER, NC_IMAGE  # , NC_SCORE

    #  print(utils.ribb("==", sep="="))
    #  print(utils.ribb("[%d] LAYER " % NC_LAYER, sep="="))
    # print(utils.ribb("==", sep="="), "\n")

    # --- 1 step --- find all possible lines (that makes sense) ----------------
    #  print(utils.ribb(utils.head("SLID"), utils.clock(), "--- 1 step "))
    segments = pSLID(NC_IMAGE['main'])
    raw_lines = SLID(NC_IMAGE['main'], segments)
    lines = slid_tendency(raw_lines)

    # --- 2 step --- find interesting intersections (potentially a mesh grid) --
    # print(utils.ribb(utils.head("LAPS"), utils.clock(), "--- 2 step "))
    points = LAPS(NC_IMAGE['main'], lines)
    # print(abs(49 - len(points)), NC_SCORE)
    # if NC_SCORE != -1 and abs(49 - len(points)) > NC_SCORE * 4: return
    # NC_SCORE = abs(49 - len(points))

    # --- 3 step --- last layer reproduction (for chessboard corners) ----------
    #   print(utils.ribb(utils.head(" LLR"), utils.clock(), "--- 3 step "))
    inner_points = LLR(NC_IMAGE['main'], points, lines)
    four_points = llr_pad(inner_points, NC_IMAGE['main'])  # padcrop

    # --- 4 step --- preparation for next layer (deep analysis) ----------------
    #   print(utils.ribb(utils.head("   *"), utils.clock(), "--- 4 step "))
    # print(four_points)
    # Extend image
    four_points[0][0] = max(four_points[0][0] + 15, 0)  # Top right go right
    four_points[0][1] = max(four_points[0][1] - 15, 0)  # Go up
    four_points[1][0] = max(four_points[1][0] + 15, 0)  # Bottom right go right
    # four_points[1][1] = max(four_points[1][1] - 20, 0)  # Go down
    # four_points[2][0] = max(four_points[2][0] - 15, 0)  # Bottom left go left
    # four_points[2][1] = max(four_points[2][1] + 15, 0)  # Go down
    # four_points[3][0] = max(four_points[3][0] - 15, 0)  # Top left go left
    four_points[3][1] = max(four_points[3][1] - 15, 0)  # Go up
    # print(f'Extended points: {four_points}')
    try:
        NC_IMAGE.crop(four_points)
    except:
        print("Enters exception")
        NC_IMAGE.crop(inner_points)

    print("\n")


################################################################################

def detect(args):
    global NC_LAYER, NC_IMAGE, NC_CONFIG

    if not os.path.isfile(args.input):
        utils.errn("error: the file \"%s\" does not exits" % args.input)

    NC_IMAGE, NC_LAYER = ImageObject(load(args.input)), 0
    for _ in range(NC_CONFIG['layers']):
        NC_LAYER += 1
        layer()
    save(f"test/out/{os.path.basename(args.input)}", NC_IMAGE['orig'])

    print("DETECT: %s" % args.input)


def detect_whole_set(args):
    global NC_LAYER, NC_IMAGE, NC_CONFIG

    input_set_path = args.input
    output_set_path = args.output
    os.makedirs(output_set_path, exist_ok=True)
    images = glob.glob(input_set_path + "/*.jpg")
    image_counter = 1
    for image in images:
        tail = os.path.basename(image).split(".jpg")[0]
        print(f"Processing image {tail}. ({image_counter}/{len(images)})")
        output_path = os.path.join(output_set_path, tail)+".jpg"
        try:
            NC_IMAGE, NC_LAYER = ImageObject(load(image)), 0
            for _ in range(NC_CONFIG['layers']):
                NC_LAYER += 1
                layer()
        except Exception:
            output_path = os.path.join(output_set_path, tail+"_skip.jpg")
        save(output_path, NC_IMAGE['orig'])


def dataset(args):
    print("DATASET: use dataset.py")


def train(args):
    print("TRAIN: use train.py")


def test(args):
    files = glob.glob('test/in/*.jpg')
    os.makedirs("test/out", exist_ok=True)

    for iname in files:
        oname = iname.replace('in', 'out')
        args.input = iname
        args.output = oname
        detect(args)

    print("TEST: %d images" % len(files))


################################################################################

if __name__ == "__main__":
    utils.reset()

    p = argparse.ArgumentParser(description='Find, crop and create FEN from image.')

    p.add_argument('mode', nargs=1, type=str, help='detect | dataset | train')
    p.add_argument('--input', type=str, help='input image (default: input.jpg)')
    p.add_argument('--output', type=str, help='output path (default: output.jpg)')

    os.system("rm -rf test/steps; mkdir test/steps")

    args = p.parse_args()
    mode = str(args.mode[0])
    modes = {'detect': detect,
             'detect_set': detect_whole_set,
             'dataset': dataset,
             'train': train,
             'test': test}

    if mode not in modes.keys():
        utils.errn("Some error? %s)" % mode)

    modes[mode](args)
    print(utils.clock(), "done")
    K.clear_session()
    gc.collect()
