import os
from Cleaner import Cleaner


class AttributeCleaner(Cleaner):
    """Handles correction of file permissions to a desired mode."""
    def __init__(self, directories, config, state):
        super().__init__(directories, config, state)
        self.desired_mode_str = config.get("desired_mode", "rw-r--r--")
        self.desired_mode = self.parse_mode(self.desired_mode_str)

    @staticmethod
    def parse_mode(mode_str):
        """Converts a symbolic file mode (e.g., 'rw-r--r--') into an integer (e.g., 0o644)."""
        if len(mode_str) != 9:
            print("Invalid mode format:", mode_str)
            return None
        first, second, third = mode_str[0:3], mode_str[3:6], mode_str[6:9]

        def parse_part(part):
            part_int = 0
            if part[0] == "r":
                part_int += 4
            if part[1] == "w":
                part_int += 2
            if part[2] == "x":
                part_int += 1
            return part_int

        return 0o100 * parse_part(first) + 0o10 * parse_part(second) + parse_part(third)

    def run(self):
        if self.desired_mode is None:
            print("Cannot proceed: invalid format for desired_mode in configuration.")
            return
        for d in self.directories:
            for root, _, files in os.walk(d):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        current_mode = os.stat(file_path).st_mode & 0o777
                    except Exception as e:
                        print("Error getting attributes for", file_path, e)
                        continue
                    if current_mode != self.desired_mode:
                        print("\nFile:", file_path)
                        print("Current permissions:", oct(current_mode), "Expected:", oct(self.desired_mode))
                        if self.state.always_chmod:
                            os.chmod(file_path, self.desired_mode)
                            print("Permissions changed:", file_path)
                        else:
                            choice = input("Change permissions? (y - yes, n - no, a - always change): ")
                            if choice.lower() == 'y':
                                os.chmod(file_path, self.desired_mode)
                                print("Permissions changed:", file_path)
                            elif choice.lower() == 'a':
                                self.state.always_chmod = True
                                os.chmod(file_path, self.desired_mode)
                                print("Permissions changed:", file_path)
                            else:
                                print("Left unchanged:", file_path)
