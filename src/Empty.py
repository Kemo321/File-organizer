import os
from Cleaner import Cleaner


class EmptyFileCleaner(Cleaner):
    """Handles the detection and deletion of empty files."""
    def __init__(self, directories, config, state):
        self.directories = directories
        self.config = config
        self.state = state

    def run(self):
        for d in self.directories:
            for root, _, files in os.walk(d):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if os.path.getsize(file_path) == 0:
                            print("\nEmpty file:", file_path)
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
                    except Exception as e:
                        print("Error processing file", file_path, e)
