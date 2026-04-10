from pathlib import Path

from gdp.parser.gdp_parser import GDPParser
from gdp.execution.runtime import GDPExecutor, PythonCallbackRegistry
from gdp.examples.tres_cambiadores.modelo import modelo
from gdp.simulators.com_hysys import COMHysysAdapter


def main():
    gdp_file = Path(__file__).with_name("Tres_Cambiadores_V2.gdp")

    parser = GDPParser()
    model = parser.parse(gdp_file.read_text())

    registry = PythonCallbackRegistry()
    registry.register("Modelo", modelo)

    hysys = COMHysysAdapter()
    hysys.connect()
    hysys.attach_active_case()

    executor = GDPExecutor(model, registry, hysys)
    results = executor.run()

    print("Execution context after callbacks:")
    for k, v in results.items():
        print(f"  {k} = {v}")


if __name__ == "__main__":
    main()
