import os
import time


def create_test_structure(base_dir="test_dir"):
    """
    Creates a test directory structure with files for testing the cleaning script.

    The structure will include:
      - An empty file.
      - A temporary file (.tmp).
      - Duplicate files with identical content.
      - Files with the same name but different modification times.
      - A file with problematic characters in its name.
      - A file with non-standard permissions.

      test_dir/
        ├── bad_permissions.txt       # File with wrong permissions (0777)
        ├── problematic:file?name.txt # File with problematic characters
        ├── subdir1/
        │   ├── empty.txt             # Empty file
        │   ├── temp_file.tmp         # Temporary file (.tmp)
        │   ├── duplicate.txt         # Duplicate file (content same as duplicate_copy.txt)
        │   └── same.txt              # Older version of same named file
        └── subdir2/
            ├── duplicate_copy.txt    # Duplicate file (same content as duplicate.txt)
            └── same.txt              # Newer version of same named file
    """
    # Create base directory and subdirectories
    os.makedirs(base_dir, exist_ok=True)
    subdirs = ["subdir1", "subdir2"]
    for sub in subdirs:
        os.makedirs(os.path.join(base_dir, sub), exist_ok=True)

    # 1. Create an empty file in subdir1
    empty_file = os.path.join(base_dir, "subdir1", "empty.txt")
    with open(empty_file, "w") as f:
        pass  # empty file

    # 2. Create a temporary file (.tmp) in subdir1
    temp_file = os.path.join(base_dir, "subdir1", "temp_file.tmp")
    with open(temp_file, "w") as f:
        f.write("This is a temporary file.")

    # 3. Create duplicate files (same content, different names/locations)
    duplicate_content = "This is duplicate content."
    dup_file1 = os.path.join(base_dir, "subdir1", "duplicate.txt")
    dup_file2 = os.path.join(base_dir, "subdir2", "duplicate_copy.txt")
    with open(dup_file1, "w") as f:
        f.write(duplicate_content)
    with open(dup_file2, "w") as f:
        f.write(duplicate_content)

    # 4. Create files with the same name in subdir1 and subdir2 with different modification times
    same_name1 = os.path.join(base_dir, "subdir1", "same.txt")
    same_name2 = os.path.join(base_dir, "subdir2", "same.txt")
    with open(same_name1, "w") as f:
        f.write("Version 1: older content.")
    # Pause to ensure a different modification time
    time.sleep(1)
    with open(same_name2, "w") as f:
        f.write("Version 2: newer content.")

    # 5. Create a file with problematic characters in the name in the base directory
    problematic_file = os.path.join(base_dir, "problematic:file?name.txt")
    with open(problematic_file, "w") as f:
        f.write("File with problematic characters in its name.")

    # 6. Create a file with incorrect permissions (e.g., 0777 instead of the desired 0644)
    perm_file = os.path.join(base_dir, "bad_permissions.txt")
    with open(perm_file, "w") as f:
        f.write("This file has non-standard permissions.")
    os.chmod(perm_file, 0o777)

    print("Test directory structure created in:", os.path.abspath(base_dir))


if __name__ == "__main__":
    create_test_structure()
