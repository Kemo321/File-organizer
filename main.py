#!/usr/bin/env python3
import os
import sys
import hashlib


def read_config():
    """
    Reads the configuration from the file $HOME/.clean_files.
    If the file does not exist, default values are used.
    """
    home = os.environ.get("HOME", ".")
    config_path = os.path.join(home, ".clean_files")
    # Default values
    config = {
        "desired_mode": "rw-r--r--",
        "problematic_chars": ":\".;*?$#'|\\",
        "substitute_char": ".",
        "temp_extensions": [".tmp", "~"]
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if key == "desired_mode":
                            config["desired_mode"] = value
                        elif key == "problematic_chars":
                            config["problematic_chars"] = value
                        elif key == "substitute_char":
                            config["substitute_char"] = value
                        elif key == "temp_extensions":
                            # Split by comma and remove empty elements
                            config["temp_extensions"] = [ext.strip() for ext in value.split(",") if ext.strip()]
        except Exception as e:
            print("Error reading configuration file:", e)
    return config


def parse_mode(mode_str):
    """
    Converts a symbolic file mode (e.g., "rw-r--r--") into an integer (e.g., 0o644).
    Assumes the string has exactly 9 characters.
    """
    if len(mode_str) != 9:
        print("Invalid mode format:", mode_str)
        return None
    mode = 0
    # Indices: 0-2 (owner), 3-5 (group), 6-8 (others)
    for i, ch in enumerate(mode_str):
        # Calculate bit shift:
        # for owner (i=0,1,2): shift 6,5,4
        # for group (i=3,4,5): shift 6-(i-3)
        # for others (i=6,7,8): shift 6-(i-6)
        if i < 3:
            shift = 6 - i
        elif i < 6:
            shift = 6 - (i - 3)
        else:
            shift = 6 - (i - 6)
        if ch == 'r':
            mode |= (4 << shift)
        elif ch == 'w':
            mode |= (2 << shift)
        elif ch == 'x':
            mode |= (1 << shift)
        elif ch == '-':
            pass
        else:
            print("Unknown character in mode:", ch)
    return mode


def get_file_mode(file_path):
    """
    Returns the file mode (permission mask) as an octal number.
    """
    try:
        return os.stat(file_path).st_mode & 0o777
    except Exception as e:
        print("Error getting attributes for", file_path, e)
        return None


def process_empty_files(directories):
    """
    Searches for empty files and offers to delete them.
    """
    global_always_delete = False
    for d in directories:
        for root, _, files in os.walk(d):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getsize(file_path) == 0:
                        print("\nEmpty file:", file_path)
                        if global_always_delete:
                            os.remove(file_path)
                            print("Deleted:", file_path)
                        else:
                            choice = input("Delete? (y - yes, n - no, a - always delete): ")
                            if choice.lower() == 'y':
                                os.remove(file_path)
                                print("Deleted:", file_path)
                            elif choice.lower() == 'a':
                                global_always_delete = True
                                os.remove(file_path)
                                print("Deleted:", file_path)
                            else:
                                print("Left unchanged:", file_path)
                except Exception as e:
                    print("Error processing file", file_path, e)


def process_temp_files(directories, temp_extensions):
    """
    Searches for temporary files based on extensions and offers to delete them.
    """
    global_always_delete = False
    for d in directories:
        for root, _, files in os.walk(d):
            for file in files:
                file_path = os.path.join(root, file)
                if any(file.endswith(ext) for ext in temp_extensions):
                    print("\nTemporary file:", file_path)
                    if global_always_delete:
                        os.remove(file_path)
                        print("Deleted:", file_path)
                    else:
                        choice = input("Delete? (y - yes, n - no, a - always delete): ")
                        if choice.lower() == 'y':
                            os.remove(file_path)
                            print("Deleted:", file_path)
                        elif choice.lower() == 'a':
                            global_always_delete = True
                            os.remove(file_path)
                            print("Deleted:", file_path)
                        else:
                            print("Left unchanged:", file_path)


def hash_file(file_path):
    """
    Computes and returns the MD5 checksum of the file.
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print("Error hashing file", file_path, e)
        return None


def process_duplicates(directories):
    """
    Searches for duplicate files (based on identical content)
    and offers to delete copies (keeping the oldest file).
    """
    file_hashes = {}
    for d in directories:
        for root, _, files in os.walk(d):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = hash_file(file_path)
                if file_hash:
                    file_hashes.setdefault(file_hash, []).append(file_path)
    global_always_delete = False
    for h, files in file_hashes.items():
        if len(files) > 1:
            try:
                files.sort(key=lambda f: os.stat(f).st_mtime)
            except Exception as e:
                print("Error sorting duplicates for:", files, e)
            master = files[0]
            print("\nDuplicates found for file (oldest retained):", master)
            for duplicate in files[1:]:
                try:
                    mtime = os.stat(duplicate).st_mtime
                    print("Copy:", duplicate, " (mtime:", mtime, ")")
                    if global_always_delete:
                        os.remove(duplicate)
                        print("Deleted:", duplicate)
                    else:
                        choice = input("Delete this copy? (y - yes, n - no, a - always delete): ")
                        if choice.lower() == 'y':
                            os.remove(duplicate)
                            print("Deleted:", duplicate)
                        elif choice.lower() == 'a':
                            global_always_delete = True
                            os.remove(duplicate)
                            print("Deleted:", duplicate)
                        else:
                            print("Left unchanged:", duplicate)
                except Exception as e:
                    print("Error deleting duplicate", duplicate, e)


def process_same_name(directories):
    """
    Searches for files with the same name (regardless of directory).
    Within a group of files sharing the same name, the newest version is retained,
    and the older files are offered for deletion.
    """
    name_dict = {}
    for d in directories:
        for root, _, files in os.walk(d):
            for file in files:
                file_path = os.path.join(root, file)
                name_dict.setdefault(file, []).append(file_path)
    global_always_delete = False
    for name, files in name_dict.items():
        if len(files) > 1:
            try:
                files.sort(key=lambda f: os.stat(f).st_mtime, reverse=True)
            except Exception as e:
                print("Error sorting files with name", name, e)
            master = files[0]
            print("\nFiles with name:", name)
            print("Retained version (newest):", master)
            for older in files[1:]:
                try:
                    mtime = os.stat(older).st_mtime
                    print("Older version:", older, " (mtime:", mtime, ")")
                    if global_always_delete:
                        os.remove(older)
                        print("Deleted:", older)
                    else:
                        choice = input("Delete this older version? (y - yes, n - no, a - always delete): ")
                        if choice.lower() == 'y':
                            os.remove(older)
                            print("Deleted:", older)
                        elif choice.lower() == 'a':
                            global_always_delete = True
                            os.remove(older)
                            print("Deleted:", older)
                        else:
                            print("Left unchanged:", older)
                except Exception as e:
                    print("Error deleting file", older, e)


def process_attributes(directories, desired_mode):
    """
    Checks file permissions and offers to change them to the mode specified in the configuration.
    """
    global_always_chmod = False
    for d in directories:
        for root, _, files in os.walk(d):
            for file in files:
                file_path = os.path.join(root, file)
                current_mode = get_file_mode(file_path)
                if current_mode is not None and current_mode != desired_mode:
                    print("\nFile:", file_path)
                    print("Current permissions:", oct(current_mode), "  Expected:", oct(desired_mode))
                    if global_always_chmod:
                        os.chmod(file_path, desired_mode)
                        print("Permissions changed:", file_path)
                    else:
                        choice = input("Change permissions? (y - yes, n - no, a - always change): ")
                        if choice.lower() == 'y':
                            os.chmod(file_path, desired_mode)
                            print("Permissions changed:", file_path)
                        elif choice.lower() == 'a':
                            global_always_chmod = True
                            os.chmod(file_path, desired_mode)
                            print("Permissions changed:", file_path)
                        else:
                            print("Left unchanged:", file_path)


def process_rename(directories, problematic_chars, substitute_char):
    """
    Checks file names – if they contain problematic characters,
    offers to replace them with the substitute character.
    """
    global_always_rename = False
    for d in directories:
        for root, _, files in os.walk(d):
            for file in files:
                new_file = file
                for ch in problematic_chars:
                    if ch in new_file:
                        new_file = new_file.replace(ch, substitute_char)
                if new_file != file:
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(root, new_file)
                    print("\nFile with problematic name:", old_path)
                    print("Proposed new name:", new_path)
                    if global_always_rename:
                        try:
                            os.rename(old_path, new_path)
                            print("Renamed to:", new_path)
                        except Exception as e:
                            print("Error renaming file:", old_path, e)
                    else:
                        choice = input("Rename? (y - yes, n - no, a - always rename): ")
                        if choice.lower() == 'y':
                            try:
                                os.rename(old_path, new_path)
                                print("Renamed to:", new_path)
                            except Exception as e:
                                print("Error renaming file:", old_path, e)
                        elif choice.lower() == 'a':
                            global_always_rename = True
                            try:
                                os.rename(old_path, new_path)
                                print("Renamed to:", new_path)
                            except Exception as e:
                                print("Error renaming file:", old_path, e)
                        else:
                            print("Left unchanged:", old_path)


def main():
    if len(sys.argv) < 3:
        print("Usage: python clean_files.py <mode> <directory1> [directory2 ...]")
        print("Available modes: empty, temp, dups, same, attrib, rename")
        sys.exit(1)
    mode = sys.argv[1]
    directories = sys.argv[2:]
    config = read_config()
    desired_mode_str = config.get("desired_mode", "rw-r--r--")
    desired_mode = parse_mode(desired_mode_str)
    problematic_chars = config.get("problematic_chars", ":\".;*?$#'|\\")
    substitute_char = config.get("substitute_char", ".")
    temp_extensions = config.get("temp_extensions", [".tmp", "~"])

    if mode == "empty":
        process_empty_files(directories)
    elif mode == "temp":
        process_temp_files(directories, temp_extensions)
    elif mode == "dups":
        process_duplicates(directories)
    elif mode == "same":
        process_same_name(directories)
    elif mode == "attrib":
        if desired_mode is None:
            print("Error: invalid format for desired_mode in configuration.")
        else:
            process_attributes(directories, desired_mode)
    elif mode == "rename":
        process_rename(directories, problematic_chars, substitute_char)
    else:
        print("Unknown mode:", mode)
        sys.exit(1)


if __name__ == "__main__":
    main()
