import os
from Cleaner import Cleaner


class SameNameFileCleaner(Cleaner):
    """Handles files with the same name, keeping the newest version."""
    def __init__(self, directories, config, state):
        super().__init__(directories, config, state)

    def run(self):
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
                    continue
                master = files[0]
                print("\nFiles with name:", name)
                print("Retained version (newest):", master)
                for older in files[1:]:
                    try:
                        mtime = os.stat(older).st_mtime
                        print("Older version:", older, " (mtime:", mtime, ")")
                        if self.state.always_delete:
                            os.remove(older)
                            print("Deleted:", older)
                        else:
                            choice = input("Delete this older version? (y - yes, n - no, a - always delete): ")
                            if choice.lower() == 'y':
                                os.remove(older)
                                print("Deleted:", older)
                            elif choice.lower() == 'a':
                                self.state.always_delete = True
                                os.remove(older)
                                print("Deleted:", older)
                            else:
                                print("Left unchanged:", older)
                    except Exception as e:
                        print("Error deleting file", older, e)
