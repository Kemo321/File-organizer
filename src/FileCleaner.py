from Empty import EmptyFileCleaner
from Temp import TempFileCleaner
from Duplicate import DuplicateFileCleaner
from Same import SameNameFileCleaner
from Attribute import AttributeCleaner
from Rename import RenameCleaner
import sys
from dataclasses import dataclass


@dataclass
class CleanerState:
    """Manages shared state flags for cleaner operations."""
    always_delete: bool = False
    always_chmod: bool = False
    always_rename: bool = False


class FileCleaner:
    """Orchestrates file cleaning operations based on the specified mode."""
    def __init__(self, directories, config, mode):
        self.directories = directories
        self.config = config
        self.mode = mode
        self.state = CleanerState()
        self.operations = {
            'empty': EmptyFileCleaner(directories, config, self.state),
            'temp': TempFileCleaner(directories, config, self.state),
            'dups': DuplicateFileCleaner(directories, config, self.state),
            'same': SameNameFileCleaner(directories, config, self.state),
            'attrib': AttributeCleaner(directories, config, self.state),
            'rename': RenameCleaner(directories, config, self.state),
        }
        self.operation_order = ['empty', 'temp', 'dups', 'same', 'attrib', 'rename']

    def run(self):
        """Executes the specified cleaning operation or all operations if mode is 'all'."""
        if self.mode == 'all':
            for op_name in self.operation_order:
                self.operations[op_name].run()
        else:
            op = self.operations.get(self.mode)
            if op:
                op.run()
            else:
                print("Unknown mode:", self.mode)
                sys.exit(1)
