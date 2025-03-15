import hashlib
import os
from Cleaner import Cleaner


class DuplicateFileCleaner(Cleaner):
    """Handles the detection and deletion of duplicate files based on content."""
    def __init__(self, directories, config, state):
        super().__init__(directories, config, state)

    @staticmethod
    def hash_file(file_path):
        """Computes and returns the MD5 checksum of the file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print("Error hashing file", file_path, e)
            return None

    def run(self):
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
                    continue
                master = files[0]
                print("\nDuplicates found for file (oldest retained):", master)
                for duplicate in files[1:]:
                    try:
                        mtime = os.stat(duplicate).st_mtime
                        print("Copy:", duplicate, " (mtime:", mtime, ")")
                        if self.state.always_delete:
                            os.remove(duplicate)
                            print("Deleted:", duplicate)
                        else:
                            choice = input("Delete this copy? (y - yes, n - no, a - always delete): ")
                            if choice.lower() == 'y':
                                os.remove(duplicate)
                                print("Deleted:", duplicate)
                            elif choice.lower() == 'a':
                                self.state.always_delete = True
                                os.remove(duplicate)
                                print("Deleted:", duplicate)
                            else:
                                print("Left unchanged:", duplicate)
                    except Exception as e:
                        print("Error deleting duplicate", duplicate, e)
