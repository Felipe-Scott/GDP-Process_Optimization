class HysysAdapter:
    """Abstract interface for HYSYS interaction."""

    def __init__(self):
        self.app = None
        self.case = None

    def connect(self):
        raise NotImplementedError

    def load_case(self, path):
        raise NotImplementedError

    def set_variable(self, name, value):
        raise NotImplementedError

    def get_variable(self, name):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError


class MockHysysAdapter(HysysAdapter):
    """Mock version for testing without HYSYS."""

    def __init__(self):
        super().__init__()
        self.state = {}

    def connect(self):
        return True

    def load_case(self, path):
        self.case = path

    def set_variable(self, name, value):
        self.state[name] = value

    def get_variable(self, name):
        return self.state.get(name, None)

    def run(self):
        return True
