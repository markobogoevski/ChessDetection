import argparse
import urllib
import chess.pgn
import glob
import PIL.Image as Image
import re
import os
import requests
import json
import urllib.request
from pathlib import Path
import io

# Declare Globals
pgnMeta = ["Event", "Site", "Date", "Round", "White", "Black", "Result",
           "CurrentPosition", "Timezone", "ECO", "ECOURL", "UTDate", "UTCTime", "WhiteELO",
           "BlackELO", "Timecontrol", "Termination", "StartTime", "EndDate", "EndTime", "Link", "Moves"]
moveStartLine = 22  # Moves in chess.com PGNs typically start from the 22nd line for each game


def get_PGN(args):
    """This function accesses the chess.com public API and downloads all the PGNs to a folder"""
    user = args.user
    PGNDirectory = args.pgn_folder
    pgn_archive_links = requests.get("https://api.chess.com/pub/player/" + user + "/games/archives", verify=False)
    if not os.path.exists(PGNDirectory):
        os.makedirs(PGNDirectory)

    for url in json.loads(pgn_archive_links.content)["archives"]:
        filepath = PGNDirectory + "/" + url.split("/")[7] + url.split("/")[8] + '.pgn'
        my_file = Path(filepath)
        if not my_file.is_file():
            urllib.request.urlretrieve(url + '/pgn', filepath)


def create_dataset_for_folder():
    folder = 'dataset/replayed_fen_games'
    # PGNDirectory = args.pgn_folder
    pgn_files = glob.glob(folder + '/*.pgn')
    folder_base_names = [os.path.basename(pgn_file).split(".pgn")[0] for pgn_file in pgn_files]
    figure_counter = 0
    for pgn_file, folder_base_name in zip(pgn_files, folder_base_names):
        full_folder_input_path = f'dataset/own_camera_dataset_newest/{folder_base_name}/pieces'
        # read the game file and set board
        print(f'Processing game: {folder_base_name}.')
        full_folder_output_path = f'dataset/own_camera_dataset_newest/{folder_base_name}/processed'
        os.makedirs(full_folder_output_path, exist_ok=True)
        with open(pgn_file, 'r') as game_file:
            game = chess.pgn.read_game(game_file)
            board = game.board()
            for move_num, move in enumerate(game.mainline_moves()):
                print(f'Processing move {move_num}.')
                for i in range(64):  # For every square
                    piece = board.piece_at(i)  # Starts at bottom left
                    if piece is None:
                        # save image with empty label
                        figure = "empty"
                    else:
                        figure = str(piece)
                        # save image with piece.symbol() label
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
                    final_output_path = os.path.join(full_folder_output_path, figure)
                    os.makedirs(final_output_path, exist_ok=True)
                    figure = f'{figure}_{str(figure_counter)}'
                    figure_counter += 1  # Just to rename them different
                    filepath = os.path.join(final_output_path, f"{figure}.jpg")
                    # Using the square number, move number and game number we can find the exact image
                    image_input_name = f'{folder_base_name}_move_{str(move_num)}_square_{str(i)}.jpg'
                    full_image_input = os.path.join(full_folder_input_path, image_input_name)
                    image = Image.open(full_image_input)  # We open the image
                    image.save(filepath)  # We save it under

                board.push(move)


def getPGN(user, dir):
    """This function accesses the chess.com public API and downloads all the PGNs to a folder"""
    pgn_archive_links = requests.get("https://api.chess.com/pub/player/" + user + "/games/archives", verify=False)
    if not os.path.exists(dir):
        os.makedirs(dir)

    for url in json.loads(pgn_archive_links.content)["archives"]:
        filepath = dir + "/" + url.split("/")[7] + url.split("/")[8] + '.pgn'
        my_file = Path(filepath)
        if not my_file.is_file():
            urllib.request.urlretrieve(url + '/pgn', filepath)


def importPGNData(filepath):
    """This function returns the data read as a string"""
    with open(filepath) as f:
        return f.readlines()


def getEdgePoints(data):
    """This function returns the start and end indices for each game in the PGN"""
    ends = []
    starts = []
    for n, l in enumerate(data):
        if l.startswith("[Event"):
            if n != 0:
                ends.append(n - 1)
            starts.append(n)
        elif n == len(data) - 1:
            ends.append(n)

    return starts, ends


def grpGames(data, starts, ends):
    """This function groups games into individual lists based on the start and end index"""
    blocks = []
    for i in range(len(ends)):
        try:
            element = data[starts[i]: ends[i] + 1]
        except:
            print(i)
        if element not in blocks:
            blocks.append(element)
    return blocks


def mergeMoves(game):
    """This function cleans out the moves and other attributes, removes newlines and formats the list to be converted
    into a dictionary """
    firstmove = lastmove = -1
    for n, eachrow in enumerate(game):
        game[n] = game[n].replace('\n', '')
        try:
            if n <= moveStartLine - 2: game[n] = stripwhitespace(game[n]).split('~')[1].strip(']["')
        except:
            if n <= moveStartLine - 4: game[n] = stripwhitespace(game[n]).split('~')[1].strip(']["')
            pass
    return list(filter(None, game))


def stripwhitespace(text):
    lst = text.split('"')
    for i, item in enumerate(lst):
        if not i % 2:
            lst[i] = re.sub("\s+", "~", item)
    return '"'.join(lst)


def createGameDictLetsPlay(game_dict):
    """This is a helper function to address games under Lets Play events on chess.com.
    These events have a slightly different way of representation than the Live Chess events"""
    final_string_list = []
    for n, move in enumerate(game_dict["Moves"].split(" ")):
        if n % 3 == 0:  # every 3rd element is the move number
            if move == '1-0' or move == '0-1' or move == '1/2-1/2':
                final_string_list.append(move)
            else:
                movenum = n
        elif n == movenum + 2:
            if move == '1-0' or move == '0-1' or move == '1/2-1/2':
                None
            else:
                final_string_list.append(move)
        else:
            if move == '1-0' or move == '0-1' or move == '1/2-1/2':
                None
            else:
                final_string_list.append(move)

    game_dict['Moves'] = ' '.join(final_string_list)
    return game_dict


def createGameDictLiveChess(game_dict):
    """This is a helper function to address games under Live Chess events on chess.com."""
    try:
        final_string_list = []
        for n, move in enumerate(game_dict["Moves"].split(" ")):
            if '{' in move or '}' in move:
                None
            elif '...' in move:
                None
            elif '.' in move:
                final_string_list.append(move)
            else:
                final_string_list.append(move)

        game_dict['Moves'] = ' '.join(final_string_list)
    except:
        pass

    return game_dict


def createGameDict(games):
    allgames = []
    for gamenum, eachgame in enumerate(games):
        game_dict = dict(zip(pgnMeta, eachgame))
        movenum = 0
        if game_dict["Event"] == "Let's Play!":
            allgames.append(createGameDictLetsPlay(game_dict))
        else:
            allgames.append(createGameDictLiveChess(game_dict))

    return allgames


def process_games(games):
    processed_games = []
    for game in games:
        if 'Moves' not in game:
            continue
        # All are json format, need to convert to string and save
        final_string = []
        for key, value in dict(game).items():
            if key != 'Moves':
                final_string.append(f'[{key} "{value}"]')
        game_string = "\n".join(final_string) + "\n\n"
        game_string += game['Moves']
        processed_games.append(game_string)

    return processed_games


def main():
    users = ["bogulec", 'viktorfr770', "mi_da", "Frostwolf12",
             "mariomijatovic99"]  # The user for whom the script is intended to run
    pgn_dirs = [os.path.join("PGN_games", user) for user in users]
    output_dir = 'dataset/PGN_processed'
    os.makedirs(output_dir, exist_ok=True)
    for user, dir in zip(users, pgn_dirs):
        getPGN(user, dir)
        with os.scandir(dir) as pgndir:
            game_counter = 0
            for file in pgndir:
                print('*', end=" ")
                data = importPGNData(file)
                starts, ends = getEdgePoints(data)
                games = grpGames(data, starts, ends)
                games = list(map(mergeMoves, games))
                allgames = createGameDict(games)
                processed_games = process_games(allgames)
                for gamenum, game in enumerate(processed_games):
                    # Save the game to file
                    file_name = os.path.join(output_dir, f'{user}_game_{game_counter + 1}.pgn')
                    game_counter += 1
                    with open(file_name, 'w') as game_file:
                        game_file.write(game)
    print("Export Complete!")


if __name__ == "__main__":
    # print('{' in '{[%clk')
    # main()
    create_dataset_for_folder()
    #
    # p = argparse.ArgumentParser(description='Download all PGN games. Create chess dataset for piece detection.')
    #
    # p.add_argument('function', nargs=1, type=str, help='what function to run (default: get_PGN')
    # p.add_argument('--user', type=str, help='user to download games for')
    # p.add_argument('--pgn_folder', type=str, help='output path for pgn games')
    # args = p.parse_args()
    # function = str(args.function[0])
    #
    # functions = {'pgn_download': get_PGN,
    #              'create_dataset': create_dataset_for_folder}
    # functions[function](args)
