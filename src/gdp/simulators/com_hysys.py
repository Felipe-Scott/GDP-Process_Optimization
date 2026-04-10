try:
    import win32com.client as win32
except Exception:  # pragma: no cover - optional dependency
    win32 = None


class COMHysysAdapter:
    """Thin wrapper around Aspen HYSYS COM/ActiveX interface (Windows only)."""

    def __init__(self, visible: bool = True):
        self.visible = visible
        self.app = None
        self.case = None

    def connect(self):
        if win32 is None:
            raise RuntimeError("win32com is not available. Install pywin32 on Windows.")
        self.app = win32.Dispatch("HYSYS.Application")
        self.app.Visible = self.visible
        return self.app

    def attach_active_case(self):
        if self.app is None:
            self.connect()
        self.case = self.app.ActiveDocument
        return self.case

    def load_case(self, path: str):
        if self.app is None:
            self.connect()
        self.case = self.app.SimulationCases.Open(path)
        return self.case

    def run(self):
        if self.case is None:
            raise RuntimeError("No HYSYS case loaded or attached")
        flowsheet = self.case.Flowsheet
        solver = flowsheet.Solver
        solver.CanSolve = True
        return True

    # ---- helpers (to be expanded per project needs) ----
    def get_stream(self, name: str):
        return self.case.Flowsheet.MaterialStreams.Item(name)

    def get_operation(self, name: str):
        return self.case.Flowsheet.Operations.Item(name)
