import os
import tensorflow as tf
from keras import layers, models
import matplotlib.pyplot as plt
import numpy as np

# Set environment variable to avoid OpenMP warnings
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Define the base directory for the dataset
base_dir = base_directory

# Load the training dataset
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    os.path.join(base_dir, 'Train'),
    image_size=(32, 32),  # Resize images to 32x32
    batch_size=64,
    shuffle=True,
    label_mode='binary'
)

# Load the validation dataset
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    os.path.join(base_dir, 'Validation'),
    image_size=(32, 32),  # Resize images to 32x32
    batch_size=64,
    shuffle=True,
    label_mode='binary'
)

# Function to count the number of images per class in a dataset
def count_images_per_class(dataset):
    fire_count = 0
    no_fire_count = 0

    for _, labels in dataset:
        fire_count += (labels == 1).numpy().sum()  # Count 'Fire' images
        no_fire_count += (labels == 0).numpy().sum()  # Count 'No Fire' images

    return no_fire_count, fire_count

# Count images in training dataset
train_no_fire_count, train_fire_count = count_images_per_class(train_ds)

# Count images in validation dataset
val_no_fire_count, val_fire_count = count_images_per_class(val_ds)

# Print the counts
print(f"Training Dataset: No Fire = {train_no_fire_count}, Fire = {train_fire_count}")
print(f"Validation Dataset: No Fire = {val_no_fire_count}, Fire = {val_fire_count}")

# Total number of images in the training dataset
total_train_images = train_no_fire_count + train_fire_count

# Compute class weights for training dataset
class_weights = {
    0: total_train_images / (2 * train_no_fire_count),  # Weight for 'No Fire' class
    1: total_train_images / (2 * train_fire_count)      # Weight for 'Fire' class
}

# Print the computed class weights
print(f"Class Weights: {class_weights}")

# Define the data augmentation pipeline
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),  # Flip images randomly
    layers.RandomRotation(0.2),  # Rotate images by up to 20%
    layers.RandomZoom(0.1),  # Zoom in/out by up to 10%
    layers.RandomContrast(0.2),  # Adjust contrast by up to 20%
])

# Define the base model (Custom CNN for 32x32 images)
base_model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.GlobalAveragePooling2D()  # Replace Flatten with GAP to reduce overfitting
])

# Build the model architecture
model = models.Sequential([
    data_augmentation,  # Data Augmentation Layer
    layers.Rescaling(1./255),  # Rescale pixel values to [0, 1]
    base_model,  # Feature extraction base model
    layers.Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001)),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(1, activation='sigmoid')  # Output layer for binary classification
])

# Define a learning rate schedule
learning_rate = tf.keras.optimizers.schedules.CosineDecay(
    initial_learning_rate=1e-3,  # Higher initial learning rate for smaller model
    decay_steps=20000,
    alpha=0.01
)

# Compile the model
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
              loss='binary_crossentropy',
              metrics=['accuracy'])

# Define callbacks
callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=50, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=30, min_lr=1e-7),
    tf.keras.callbacks.ModelCheckpoint("best_fire_detection_model_32x32.h5", monitor='val_loss', save_best_only=True)
]

# Train the model with computed class weights
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=200,
    callbacks=callbacks,
    class_weight=class_weights  # Pass the dynamically computed class weights
)

# Plot accuracy and loss over epochs
plt.figure(figsize=(12, 5))

# Plot accuracy
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.title('Accuracy over Epochs')

# Plot loss
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.title('Loss over Epochs')

plt.show()

