import pickle
from matplotlib.pyplot import plot as plt
import shutil
import os
import glob
import tensorflow as tf
from keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input
from keras.models import load_model
from keras.callbacks import TensorBoard
from keras.metrics import categorical_accuracy
from keras.optimizer_v2.adam import Adam
from keras.preprocessing.image import ImageDataGenerator
from keras import models
from sklearn.utils import shuffle

IMAGE_WIDTH = 150
IMAGE_HEIGHT = 150


def split_data(input_folders, split, train_path, validation_path, test_path):
    # For every input folder we do a split of the files according to split variable

    # Remove folders inside train_path, validation_path and test_path if any
    figure_dirs_train = [x[0] for x in list(os.walk(train_path))[1:]]
    figure_dirs_validation = [x[0] for x in list(os.walk(validation_path))[1:]]
    for figure_dir_train in figure_dirs_train:
        shutil.rmtree(figure_dir_train)
    for figure_dir_validation in figure_dirs_validation:
        shutil.rmtree(figure_dir_validation)
    shutil.rmtree(test_path)
    os.makedirs(test_path, exist_ok=True)

    train_split = split[0]
    validation_split = train_split + split[1]

    for figure in input_folders:
        figure_label = os.path.basename(figure)
        print(f'Splitting data for figure {figure_label}.')

        images = list(glob.glob(figure + "/*.jpg"))
        print(f"Total images for figure {figure_label}: {len(images)}.")
        figure_data = shuffle(images)
        number_of_images = len(figure_data)
        train_index = int(train_split * number_of_images)
        train_data = figure_data[:train_index]
        validation_index = int(validation_split * number_of_images)
        validation_data = figure_data[train_index:validation_index]
        test_data = figure_data[validation_index:]
        figure_dir_train = os.path.join(train_path, figure_label)
        figure_dir_valid = os.path.join(validation_path, figure_label)

        os.makedirs(figure_dir_train, exist_ok=True)
        os.makedirs(figure_dir_valid, exist_ok=True)

        # Copying train data, validation and test data
        print(f'Copying training data for figure {figure_label}.')
        copy_count = 1
        for file in train_data:
            shutil.copy(file, figure_dir_train)
            copy_count += 1
        print(f'Copying validation data for figure {figure_label}.')
        copy_count = 1
        for file in validation_data:
            shutil.copy(file, figure_dir_valid)
            copy_count += 1
        print(f'Copying testing data for figure {figure_label}.')
        copy_count = 1
        for file in test_data:
            new_name = os.path.join(test_path, f'{figure_label}_{str(copy_count)}.jpg')
            shutil.copy(file, new_name)
            copy_count += 1


def train(input_data, processed_data_path, model_output, encoder_path, plots_path, num_epochs, split):
    # Getting input dirs
    input_dirs = [x[0] for x in list(os.walk(input_data))[1:]]

    # Creating output folders
    print("Creating needed output folders.")
    os.makedirs(model_output, exist_ok=True)
    os.makedirs(plots_path, exist_ok=True)
    os.makedirs(encoder_path, exist_ok=True)
    os.makedirs(processed_data_path, exist_ok=True)

    # Directories for our training, validation and test splits
    train_dir = os.path.join(processed_data_path, 'train')
    os.makedirs(train_dir, exist_ok=True)

    validation_dir = os.path.join(processed_data_path, 'validation')
    os.makedirs(validation_dir, exist_ok=True)

    test_dir = os.path.join(processed_data_path, 'test')
    test_dir = os.path.join(test_dir, 'to_predict')
    os.makedirs(test_dir, exist_ok=True)

    # Move files according to split. Should be commented out if data is already split and split ratio hasn't changed
    print(f"Starting to split data according to split: {split}.")
    #split_data(input_dirs, split, train_dir, validation_dir, test_dir)

    print("Preparing training data in proper format.")
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=40,
        shear_range=0.2,
        zoom_range=0.2,
        vertical_flip=True,
        horizontal_flip=True)
    valid_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(150, 150),
        batch_size=32,
        class_mode='categorical')
    validation_generator = valid_datagen.flow_from_directory(
        validation_dir,
        target_size=(150, 150),
        batch_size=32,
        class_mode='categorical')

    # Model
    # Here we specify image size, we can define this in preprocessing
    base_model = InceptionResNetV2(include_top=False, weights='imagenet', input_shape=(150, 150, 3))
    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(1024, activation='relu')(x)
    predictions = tf.keras.layers.Dense(7, activation='softmax')(x)  # New softmax layer
    model = models.Model(inputs=base_model.input, outputs=predictions)
    #
    # # Tensorboard for monitoring
    # tensorboard = TensorBoard(
    #     log_dir=plots,
    #     histogram_freq=0,
    #     write_graph=True,
    #     write_images=False,
    #     write_steps_per_second=False,
    #     update_freq="epoch",
    #     profile_batch=0,
    #     embeddings_freq=0,
    #     embeddings_metadata=None)

    # we chose to train the top 2 inception blocks
    # we will freeze the first 249 layers and unfreeze the rest
    for layer in model.layers[:249]:
        layer.trainable = False
    for layer in model.layers[249:]:
        layer.trainable = True
    #
    adam = Adam(lr=0.0001)
    print("Compiling model.")
    model.compile(adam, loss='categorical_crossentropy', metrics=[categorical_accuracy])
    print("Model summary: ")
    print(model.summary())

    print(f"Training model on {num_epochs} epochs with batch size of 32.")

    STEP_SIZE_TRAIN = train_generator.n // train_generator.batch_size
    STEP_SIZE_VALID = validation_generator.n // validation_generator.batch_size
    # Real time augmentation
    history = model.fit(train_generator, validation_data=validation_generator, steps_per_epoch=STEP_SIZE_TRAIN,
                        epochs=num_epochs, validation_steps=STEP_SIZE_VALID, callbacks=[tensorboard], verbose=1)
    print(f"Saving model.")
    model_path = os.path.join(model_output, 'chess_piece_detection_model.h5')
    # model.save(model_path, include_optimizer=True)
    model = load_model(model_path)

    # Save encoder
    labels = train_generator.class_indices
    labels = dict((v, k) for k, v in labels.items())
    with open(os.path.join(encoder_path, "encoder.pkl"), "wb") as f:
        pickle.dump(labels, f)

    score = model.evaluate_generator(validation_generator)
    print('Validation loss:', score[0])
    print('Validation accuracy:', score[1])


if __name__ == "__main__":
    input_data_path = 'dataset\\final_processed_dataset_mine_new'
    processed_data_path = 'dataset\\final_processed_dataset_mine_new_split'
    model_output_path = 'new_model/model'
    plots = 'new_model/plots'
    encoder_path = 'new_model/encoder'
    epochs = 50  # 5 for testing, 50 for true
    split = 0.8, 0.1, 0.1

    train(input_data_path, processed_data_path, model_output_path, encoder_path, plots, epochs, split)
