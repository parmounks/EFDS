import os
import shutil
import random

# Define base directory
base_dir = base_directory
dataset_dir = os.path.join(base_dir, 'Dataset')
processed_dir = os.path.join(base_dir, 'Fires', 'Processed')  # Directory with processed images and subdirectories

# Create dataset directory structure, deleting any existing Dataset folder
def create_dataset_dirs(base_path):
    # Delete the existing Dataset folder if it exists
    if os.path.exists(base_path):
        print(f"Deleting existing dataset directory: {base_path}")
        shutil.rmtree(base_path)
        
    # Now recreate the Dataset folder and its subdirectories
    splits = ['Train', 'Validation', 'Test']
    categories = ['B - Fire', 'A - No Fire']

    for split in splits:
        for category in categories:
            os.makedirs(os.path.join(base_path, split, category), exist_ok=True)
    print(f"Created new dataset directory structure at: {base_path}")

# Collect all fire and no_fire images from the processed directory and its subdirectories
def collect_image_files(source_dir):
    fire_files = []
    no_fire_files = []
    
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.startswith("fire_block"):
                fire_files.append(os.path.join(root, file))
            elif file.startswith("no_fire_block"):
                no_fire_files.append(os.path.join(root, file))
    
    return fire_files, no_fire_files

# Split images into train, validation, and test sets
def split_data(files, dest_dir, category, split_ratios=(0.7, 0.15, 0.15)):
    random.shuffle(files)

    num_files = len(files)
    num_train = int(split_ratios[0] * num_files)
    num_val = int(split_ratios[1] * num_files)

    # Split into train, val, and test
    train_files = files[:num_train]
    val_files = files[num_train:num_train + num_val]
    test_files = files[num_train + num_val:]

    # Paths for each split
    train_dir = os.path.join(dest_dir, 'Train', category)
    val_dir = os.path.join(dest_dir, 'Validation', category)
    test_dir = os.path.join(dest_dir, 'Test', category)

    for file in train_files:
        shutil.copy(file, os.path.join(train_dir, os.path.basename(file)))
    for file in val_files:
        shutil.copy(file, os.path.join(val_dir, os.path.basename(file)))
    for file in test_files:
        shutil.copy(file, os.path.join(test_dir, os.path.basename(file)))

# Call the function to create the dataset directories
create_dataset_dirs(dataset_dir)

# Collect fire and no_fire images from all subdirectories under Processed
fire_files, no_fire_files = collect_image_files(processed_dir)

# Split and organize the Fire images
print("Organizing Fire dataset...")
split_data(fire_files, dataset_dir, 'B - Fire')

# Split and organize the No Fire images
print("Organizing No Fire dataset...")
split_data(no_fire_files, dataset_dir, 'A - No Fire')

print("Dataset creation and organization completed.")
