import os
from Cleaner import Cleaner


class RenameCleaner(Cleaner):
    """Handles renaming files with problematic characters in their names."""
    def __init__(self, directories, config, state):
        super().__init__(directories, config, state)
        self.problematic_chars = config.get("problematic_chars", ":\".;*?$#'|\\")
        self.substitute_char = config.get("substitute_char", ".")

    def run(self):
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
                        if self.state.always_rename:
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
                                self.state.always_rename = True
                                try:
                                    os.rename(old_path, new_path)
                                    print("Renamed to:", new_path)
                                except Exception as e:
                                    print("Error renaming file:", old_path, e)
                            else:
                                print("Left unchanged:", old_path)
