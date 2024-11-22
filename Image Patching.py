import cv2
import os
import numpy as np

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def detect_red_dot(block):
    # Convert to HSV color space to isolate red tones more effectively
    hsv_block = cv2.cvtColor(block, cv2.COLOR_RGB2HSV)

    # Define range for red tones in HSV 
    lower_red1 = np.array([0, 100, 80])    
    upper_red1 = np.array([15, 255, 255])   
    lower_red2 = np.array([160, 100, 80])  
    upper_red2 = np.array([179, 255, 255])

    # Create masks for red pixels in both ranges
    mask_red1 = cv2.inRange(hsv_block, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv_block, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # Find contours of red areas
    contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Define a minimum area for a contour to be considered a red dot
    min_dot_area = 1 

    # Check if any contour meets the minimum dot area
    for contour in contours:
        if cv2.contourArea(contour) >= min_dot_area:
            return True  # Red dot
    return False  # No red dot

def break_image_into_grid(image_rgb, image_name, output_folder, grid_size=(16, 16)):
    height, width, _ = image_rgb.shape
    block_height = height // grid_size[0]
    block_width = width // grid_size[1]

    # Create a subfolder for the blocks specific to this image
    image_subfolder = os.path.join(output_folder, f'blocks_{image_name}')

    # Check if this image has already been processed
    if os.path.exists(image_subfolder):
        print(f"Image {image_name} has already been processed. Skipping.")
        return

    # Create the directory if not existing
    create_directory(image_subfolder)

    # Loop through the image and extract blocks
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            y_start = i * block_height
            y_end = y_start + block_height
            x_start = j * block_width
            x_end = x_start + block_width

            block = image_rgb[y_start:y_end, x_start:x_end]

            # Detect red dots in the block
            has_fire = detect_red_dot(block)
            label = "fire_block" if has_fire else "no_fire_block"

            # Save block with the label and original image name
            block_filename = os.path.join(image_subfolder, f'{label}_{image_name}_{i}_{j}.jpg')
            cv2.imwrite(block_filename, cv2.cvtColor(block, cv2.COLOR_RGB2BGR))

    print(f"Image {image_name} broken into blocks and saved in {image_subfolder}")

def process_images(input_folder, output_folder):
    create_directory(output_folder)
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

    for image_file in image_files:
        input_image_path = os.path.join(input_folder, image_file)
        image_rgb = cv2.imread(input_image_path)
        if image_rgb is None:
            print(f"Failed to load {image_file}. Skipping.")
            continue

        # Convert BGR to RGB for consistency
        image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
        image_name = os.path.splitext(image_file)[0]

        # Process and save image blocks
        break_image_into_grid(image_rgb, image_name, output_folder)

    print(f"All images from {input_folder} processed and saved in {output_folder}.")

# Updated directories for your project structure
input_folder = user_home_directory\Fires\Unprocessed"
output_folder = user_home_directory\Fires\Processed"

# Process all images in the input folder
process_images(input_folder, output_folder)
