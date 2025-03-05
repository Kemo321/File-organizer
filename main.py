import os
import sys
import hashlib
from parser import ArgParser


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


class FileCleaner:
    def __init__(self, directories, config):
        self.directories = directories
        self.config = config
        self.desired_mode_str = config.get("desired_mode", "rw-r--r--")
        self.desired_mode = self.parse_mode(self.desired_mode_str)
        self.problematic_chars = config.get("problematic_chars", ":\".;*?$#'|\\")
        self.substitute_char = config.get("substitute_char", ".")
        self.temp_extensions = config.get("temp_extensions", [".tmp", "~"])
        # Flags for interactive operations
        self.always_delete = False
        self.always_chmod = False
        self.always_rename = False

    @staticmethod
    def parse_mode(mode_str):
        """
        Converts a symbolic file mode (e.g., "rw-r--r--") into an integer (e.g., 0o644).
        Assumes the string has exactly 9 characters.
        """
        if len(mode_str) != 9:
            print("Invalid mode format:", mode_str)
            return None
        mode = 0
        for i, ch in enumerate(mode_str):
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
                continue
            else:
                print("Unknown character in mode:", ch)
        return mode

    @staticmethod
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

    def process_empty_files(self):
        """
        Searches for empty files and offers to delete them.
        """
        for d in self.directories:
            for root, _, files in os.walk(d):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if os.path.getsize(file_path) == 0:
                            print("\nEmpty file:", file_path)
                            if self.always_delete:
                                os.remove(file_path)
                                print("Deleted:", file_path)
                            else:
                                choice = input("Delete? (y - yes, n - no, a - always delete): ")
                                if choice.lower() == 'y':
                                    os.remove(file_path)
                                    print("Deleted:", file_path)
                                elif choice.lower() == 'a':
                                    self.always_delete = True
                                    os.remove(file_path)
                                    print("Deleted:", file_path)
                                else:
                                    print("Left unchanged:", file_path)
                    except Exception as e:
                        print("Error processing file", file_path, e)

    def process_temp_files(self):
        """
        Searches for temporary files based on extensions and offers to delete them.
        """
        for d in self.directories:
            for root, _, files in os.walk(d):
                for file in files:
                    file_path = os.path.join(root, file)
                    if any(file.endswith(ext) for ext in self.temp_extensions):
                        print("\nTemporary file:", file_path)
                        if self.always_delete:
                            os.remove(file_path)
                            print("Deleted:", file_path)
                        else:
                            choice = input("Delete? (y - yes, n - no, a - always delete): ")
                            if choice.lower() == 'y':
                                os.remove(file_path)
                                print("Deleted:", file_path)
                            elif choice.lower() == 'a':
                                self.always_delete = True
                                os.remove(file_path)
                                print("Deleted:", file_path)
                            else:
                                print("Left unchanged:", file_path)

    def process_duplicates(self):
        """
        Searches for duplicate files (based on identical content)
        and offers to delete copies (keeping the oldest file).
        """
        file_hashes = {}
        for d in self.directories:
            for root, _, files in os.walk(d):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_hash = self.hash_file(file_path)
                    if file_hash:
                        file_hashes.setdefault(file_hash, []).append(file_path)
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
                        if self.always_delete:
                            os.remove(duplicate)
                            print("Deleted:", duplicate)
                        else:
                            choice = input("Delete this copy? (y - yes, n - no, a - always delete): ")
                            if choice.lower() == 'y':
                                os.remove(duplicate)
                                print("Deleted:", duplicate)
                            elif choice.lower() == 'a':
                                self.always_delete = True
                                os.remove(duplicate)
                                print("Deleted:", duplicate)
                            else:
                                print("Left unchanged:", duplicate)
                    except Exception as e:
                        print("Error deleting duplicate", duplicate, e)

    def process_same_name(self):
        """
        Searches for files with the same name (regardless of directory).
        Within a group of files sharing the same name, the newest version is retained,
        and the older files are offered for deletion.
        """
        name_dict = {}
        for d in self.directories:
            for root, _, files in os.walk(d):
                for file in files:
                    file_path = os.path.join(root, file)
                    name_dict.setdefault(file, []).append(file_path)
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
                        if self.always_delete:
                            os.remove(older)
                            print("Deleted:", older)
                        else:
                            choice = input("Delete this older version? (y - yes, n - no, a - always delete): ")
                            if choice.lower() == 'y':
                                os.remove(older)
                                print("Deleted:", older)
                            elif choice.lower() == 'a':
                                self.always_delete = True
                                os.remove(older)
                                print("Deleted:", older)
                            else:
                                print("Left unchanged:", older)
                    except Exception as e:
                        print("Error deleting file", older, e)

    def process_attributes(self):
        """
        Checks file permissions and offers to change them to the mode specified in the configuration.
        """
        for d in self.directories:
            for root, _, files in os.walk(d):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        current_mode = os.stat(file_path).st_mode & 0o777
                    except Exception as e:
                        print("Error getting attributes for", file_path, e)
                        continue
                    if current_mode is not None and current_mode != self.desired_mode:
                        print("\nFile:", file_path)
                        print("Current permissions:", oct(current_mode), "Expected:", oct(self.desired_mode))
                        if self.always_chmod:
                            os.chmod(file_path, self.desired_mode)
                            print("Permissions changed:", file_path)
                        else:
                            choice = input("Change permissions? (y - yes, n - no, a - always change): ")
                            if choice.lower() == 'y':
                                os.chmod(file_path, self.desired_mode)
                                print("Permissions changed:", file_path)
                            elif choice.lower() == 'a':
                                self.always_chmod = True
                                os.chmod(file_path, self.desired_mode)
                                print("Permissions changed:", file_path)
                            else:
                                print("Left unchanged:", file_path)

    def process_rename(self):
        """
        Checks file names – if they contain problematic characters,
        offers to replace them with the substitute character.
        """
        for d in self.directories:
            for root, _, files in os.walk(d):
                for file in files:
                    new_file = file
                    for ch in self.problematic_chars:
                        if ch in new_file:
                            new_file = new_file.replace(ch, self.substitute_char)
                    if new_file != file:
                        old_path = os.path.join(root, file)
                        new_path = os.path.join(root, new_file)
                        print("\nFile with problematic name:", old_path)
                        print("Proposed new name:", new_path)
                        if self.always_rename:
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
                                self.always_rename = True
                                try:
                                    os.rename(old_path, new_path)
                                    print("Renamed to:", new_path)
                                except Exception as e:
                                    print("Error renaming file:", old_path, e)
                            else:
                                print("Left unchanged:", old_path)

    def process_all(self):
        """
        Runs all operations sequentially.
        """
        self.process_empty_files()
        self.process_temp_files()
        self.process_duplicates()
        self.process_same_name()
        self.process_attributes()
        self.process_rename()


def main():
    arg_parser = ArgParser()
    args = arg_parser.parse()
    config = read_config()
    cleaner = FileCleaner(args.directories, config)

    if args.mode is None:
        print("No mode specified. Executing all operations...\n")
        cleaner.process_all()
    else:
        if args.mode == "empty":
            cleaner.process_empty_files()
        elif args.mode == "temp":
            cleaner.process_temp_files()
        elif args.mode == "dups":
            cleaner.process_duplicates()
        elif args.mode == "same":
            cleaner.process_same_name()
        elif args.mode == "attrib":
            if cleaner.desired_mode is None:
                print("Error: invalid format for desired_mode in configuration.")
            else:
                cleaner.process_attributes()
        elif args.mode == "rename":
            cleaner.process_rename()
        else:
            print("Unknown mode:", args.mode)
            sys.exit(1)


if __name__ == "__main__":
    main()
