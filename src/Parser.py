import argparse


class ArgParser:
    """
    Encapsulates command-line argument parsing using argparse.
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="File cleaning and organizing tool using built-in modules and classes."
        )
        self.parser.add_argument(
            "mode",
            nargs="?",
            choices=["empty", "temp", "dups", "same", "attrib", "rename", "all"],
            help="Operation mode: empty, temp, dups, same, attrib, rename, all. If not provided, all operations will be executed."
        )
        self.parser.add_argument(
            "directories",
            nargs="+",
            help="Directories to process"
        )

    def parse(self):
        """Parses command-line arguments and returns them."""
        return self.parser.parse_args()
