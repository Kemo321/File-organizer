import os
from Cleaner import Cleaner


class TempFileCleaner(Cleaner):
    """Handles the detection and deletion of temporary files."""
    def __init__(self, directories, config, state):
        super().__init__(directories, config, state)
        self.temp_extensions = config.get("temp_extensions", [".tmp", "~"])

    def run(self):
        for d in self.directories:
            for root, _, files in os.walk(d):
                for file in files:
                    if any(file.endswith(ext) for ext in self.temp_extensions):
                        file_path = os.path.join(root, file)
                        print("\nTemporary file:", file_path)
                        if self.state.always_delete:
                            os.remove(file_path)
                            print("Deleted:", file_path)
                        else:
                            choice = input("Delete? (y - yes, n - no, a - always delete): ")
                            if choice.lower() == 'y':
                                os.remove(file_path)
                                print("Deleted:", file_path)
                            elif choice.lower() == 'a':
                                self.state.always_delete = True
                                os.remove(file_path)
                                print("Deleted:", file_path)
                            else:
                                print("Left unchanged:", file_path)
