from sklearn.model_selection import train_test_split
import shutil
import os
import logging

logging.basicConfig(level=logging.INFO)


def test_train_split(output_dir: str, label: str = "shrubs"):
    """
    Splits the dataset into training and testing sets based on the indices of image and label files.
    Assumes that image and label files are named in a consistent format with an index (e.g., 'shrubs_0.tif') - but the prefix can be different.
    For our background images, there's only one label (negative_0.tif) - make sure it's included in the training set!
    """
    # Get list of image and label files
    image_files = [
        os.path.join(output_dir, "images", f)
        for f in os.listdir(os.path.join(output_dir, "images"))
    ]
    label_files = [
        os.path.join(output_dir, "labels", f)
        for f in os.listdir(os.path.join(output_dir, "labels"))
    ]

    # Extract the index from the filename (assuming format like 'shrubs_index.tif')
    def get_index(filename):
        return int(os.path.basename(filename).split("_")[-1].split(".")[0])

    image_indices = [get_index(f) for f in image_files]
    label_indices = [get_index(f) for f in label_files]

    # Ensure the indices match between images and labels
    if sorted(image_indices) != sorted(label_indices):
        raise ValueError("Indices of image and label files do not match.")

    # Create a combined list of indices to split
    all_indices = sorted(list(set(image_indices)))

    # Split the indices
    train_indices, test_indices = train_test_split(
        all_indices, test_size=0.2, random_state=42
    )

    # Create train and test directories
    train_dir = os.path.join(output_dir, "train")
    test_dir = os.path.join(output_dir, "test")
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(train_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(train_dir, "labels"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "labels"), exist_ok=True)

    # Function to move files based on index and type
    def move_files(indices, source_dir, dest_dir):
        for index in indices:
            image_filename = f"{label}_{index}.tif"
            label_filename = f"{label}_{index}.tif"

            source_image_path = os.path.join(source_dir, "images", image_filename)
            source_label_path = os.path.join(source_dir, "labels", label_filename)

            dest_image_path = os.path.join(dest_dir, "images", image_filename)
            dest_label_path = os.path.join(dest_dir, "labels", label_filename)

            if os.path.exists(source_image_path):
                shutil.move(source_image_path, dest_image_path)
            else:
                logging.info(
                    f"Warning: Image file not found for index {index}: {source_image_path}"
                )

            if os.path.exists(source_label_path):
                shutil.move(source_label_path, dest_label_path)
            else:
                logging.info(
                    f"Warning: Label file not found for index {index}: {source_label_path}"
                )

    # Move files to train and test directories
    move_files(train_indices, output_dir, train_dir)
    move_files(test_indices, output_dir, test_dir)

    logging.info(
        f"Data split into train ({len(train_indices)} samples) and test ({len(test_indices)} samples)."
    )
    logging.info(f"Files moved to {train_dir} and {test_dir}.")
