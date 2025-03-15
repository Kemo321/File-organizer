import os
from FileCleaner import FileCleaner
from Parser import ArgParser


class CleanerState:
    """Manages shared state flags for cleaner operations."""
    def __init__(self):
        self.always_delete = False
        self.always_chmod = False
        self.always_rename = False


def read_config():
    """Reads configuration from '.clean_files' in the current directory, using defaults if absent."""
    config_path = ".clean_files"
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
                            config["temp_extensions"] = [ext.strip() for ext in value.split(",") if ext.strip()]
        except Exception as e:
            print("Error reading configuration file:", e)
    return config


def main():
    arg_parser = ArgParser()
    args = arg_parser.parse()
    config = read_config()
    mode = args.mode if args.mode else 'all'
    cleaner = FileCleaner(args.directories, config, mode)
    cleaner.run()


if __name__ == "__main__":
    main()
