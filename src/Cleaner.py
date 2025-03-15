class Cleaner:
    """ Base class for all cleaners. """
    def __init__(self, directories, config, state):
        self.directories = directories
        self.config = config
        self.state = state

    def run(self):
        raise NotImplementedError("Subclasses must implement this method.")
