import os
import tensorflow as tf
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Define the path to the test dataset and the trained model
base_dir = base_directory
test_dir = os.path.join(base_dir, 'Test')
model_path = "best_fire_detection_model_32x32.h5"  # Path to your saved model file

# Load the test dataset
test_ds = tf.keras.preprocessing.image_dataset_from_directory(
    test_dir,
    image_size=(32, 32),  # Ensure image size matches training size
    batch_size=128,
    shuffle=False,  # Ensure consistent ordering for evaluation
    label_mode='binary'  # Binary labels (0 for Fire, 1 for No Fire due to alphabetical order)
)

# Load the trained model
model = tf.keras.models.load_model(model_path)

# Evaluate the model on the test dataset
test_loss, test_acc = model.evaluate(test_ds)
print(f"Test accuracy: {test_acc:.2f}")

# Initialize arrays to store true labels and predictions
y_true = []
y_pred = []

# Collect true labels and predictions
for images, labels in test_ds:
    preds = model.predict(images)  # Get predictions
    y_true.extend(labels.numpy())  # Append true labels
    y_pred.extend((preds > 0.5).astype(int).flatten())  # Append predicted labels (binary 0 or 1)

# Convert lists to numpy arrays for analysis
y_true = np.array(y_true)
y_pred = np.array(y_pred)

# Print actual counts for debugging
print(f"Total images: {len(y_true)}")
print(f"Total predicted 'Fire': {(y_pred == 1).sum()}, Total predicted 'No Fire': {(y_pred == 0).sum()}")
print(f"Total true 'Fire': {(y_true == 1).sum()}, Total true 'No Fire': {(y_true == 0).sum()}")

# Confusion Matrix
confusion_mtx = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(confusion_mtx, annot=True, fmt='d', cmap='Blues', xticklabels=['No Fire', 'Fire'], yticklabels=['No Fire', 'Fire'])
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

# Classification Report
print("Classification Report:")
print(classification_report(y_true, y_pred, target_names=['No Fire', 'Fire']))
