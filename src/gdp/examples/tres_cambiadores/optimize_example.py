from pathlib import Path

from gdp.parser.gdp_parser import GDPParser
from gdp.execution.executor import GDPExecutor, PythonCallbackRegistry
from gdp.examples.tres_cambiadores.modelo import modelo
from gdp.simulators.com_hysys import COMHysysAdapter
from gdp.optimization.bruteforce import brute_force_optimize
from gdp.optimization.objectives import tres_cambiadores_total_area_cost


def make_executor(model, registry, hysys):
    def run_for_a1(a1):
        executor = GDPExecutor(model, registry, hysys)
        executor.context.set("A1", a1)
        executor.context.set("Prob", {})
        return executor.run()

    return run_for_a1


def main():
    gdp_file = Path(__file__).with_name("Tres_Cambiadores_V2.gdp")

    parser = GDPParser()
    model = parser.parse(gdp_file.read_text())

    registry = PythonCallbackRegistry()
    registry.register("Modelo", modelo)

    hysys = COMHysysAdapter()
    hysys.connect()
    hysys.attach_active_case()

    executor_factory = make_executor(model, registry, hysys)

    best_a1, best_val, best_ctx = brute_force_optimize(
        executor_factory,
        tres_cambiadores_total_area_cost,
        a1_min=5,
        a1_max=20,
        step=1.0,
    )

    print("\n=== Optimization Result ===")
    print(f"Best A1: {best_a1}")
    print(f"Best Objective: {best_val}")
    print("Context:")
    for k, v in best_ctx.items():
        print(f"  {k} = {v}")


if __name__ == "__main__":
    main()
