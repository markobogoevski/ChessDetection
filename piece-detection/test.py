import pickle
import os
import numpy as np
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator
from keras.applications.inception_resnet_v2 import preprocess_input
from sklearn.metrics import precision_score, accuracy_score, f1_score, recall_score, \
    classification_report, confusion_matrix
import pandas as pd


def test(model, test_path, encoder_path):
    print(f"Running on test directory ({test_path}).")
    # Making test datagen and generator
    test_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )

    test_generator = test_datagen.flow_from_directory(
        test_path,
        target_size=(150, 150),
        batch_size=1,
        class_mode=None,
        shuffle=False)
    test_generator.reset()

    # Loading encoder
    print('Loading encoder.')
    encoder_path = os.path.join(encoder_path, 'encoder.pkl')
    with open(encoder_path, 'rb') as f:
        enc = pickle.load(f)

    # Loading model
    print('Loading model.')
    model_path = os.path.join(model, 'chess_piece_detection_model.h5')
    model = load_model(model_path)
    model.summary()

    print('Generating predictions')
    STEP_SIZE_TEST = test_generator.n // test_generator.batch_size
    predictions = model.predict_generator(test_generator, steps=STEP_SIZE_TEST, verbose=1)
    predicted_class_indices = np.argmax(predictions, axis=1)
    labels = enc
    predictions = [labels[k] for k in predicted_class_indices]
    # Now because we have the test_generator.filenames, we can use them to find out scores
    y_test = [os.path.basename(filename).split('_')[0] for filename in test_generator.filenames]

    print(f'Getting scores.')
    # Gets tp/(tp+fp) for class
    precision_score_per_class = precision_score(y_test, predictions, average=None)
    # Gets total tp/(tp+fp)
    precision_score_total = precision_score(y_test, predictions, average='micro')

    # Gets tp/(tp+fp) for class
    total_accuracy = accuracy_score(y_test, predictions)

    # Gets tp/(tp+fp) for class
    f1_per_class = f1_score(y_test, predictions, average=None)
    # Gets total tp/(tp+fp)
    f1_total = f1_score(y_test, predictions, average='micro')

    # Gets tp/(tp+fp) for class
    recall_per_class = recall_score(y_test, predictions, average=None)
    # Gets total tp/(tp+fp)
    recall_total = precision_score(y_test, predictions, average='micro')

    print(f'Precision per class: {precision_score_per_class}.')
    print(f'Precision total: {precision_score_total}.')
    print(f'Accuracy total: {total_accuracy}.')
    print(f'F1 per class: {f1_per_class}.')
    print(f'F1 total: {f1_total}.')
    print(f'Recall per class: {recall_per_class}.')
    print(f'Recall total: {recall_total}.')
    print(f'Classfication report: {classification_report(y_test, predictions)}.')
    print(f'Confusion matrix: {confusion_matrix(y_test, predictions)}.')


def test_multiple(model, encoder, test_dirs):
    print(f"Running on test sets.")

    # Making test datagen and generator
    test_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )

    # Loading encoder
    print('Loading encoder.')
    with open(encoder, 'rb') as f:
        enc = pickle.load(f)

    # Loading model
    print('Loading model.')
    model = load_model(model)

    print('Generating predictions')
    for test_dir in test_dirs:
        test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=(150, 150),
            batch_size=1,
            class_mode=None,
            shuffle=False)
        test_generator.reset()

        parent = os.path.dirname(test_dir)
        print(f'Running predictions for {test_dir}.')
        STEP_SIZE_TEST = test_generator.n // test_generator.batch_size
        predictions = model.predict_generator(test_generator, steps=STEP_SIZE_TEST, verbose=1)
        predicted_class_indices = np.argmax(predictions, axis=1)
        labels = enc
        predictions = [labels[k] for k in predicted_class_indices]
        # We now need to pickle a dictionary explaining the game state
        file_order = test_generator.filenames
        game_state = dict()
        for prediction, file in zip(predictions, file_order):
            square_number = os.path.basename(file).split('tile_')[1].split('.jpg')[0]
            game_state[str(square_number)] = prediction

        # Pickle the game state in the parent of the test dir
        game_state_file = os.path.join(parent, 'game_state_pre_coloring.pkl')
        with open(game_state_file, 'wb') as f:
            pickle.dump(game_state, f)


if __name__ == "__main__":
    model_path = 'new_model/model'
    test_path = 'dataset/final_processed_dataset_mine_new_split/test'
    encoder_path = 'new_model/encoder'
    test(model_path, test_path, encoder_path)
