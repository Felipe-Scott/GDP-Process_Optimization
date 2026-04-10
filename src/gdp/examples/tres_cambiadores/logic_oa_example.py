from pathlib import Path

from gdp.parser.gdp_parser import GDPParser
from gdp.execution.executor import GDPExecutor, PythonCallbackRegistry
from gdp.examples.tres_cambiadores.modelo import modelo
from gdp.simulators.com_hysys import COMHysysAdapter
from gdp.optimization.logic_oa import LogicOAContinuous
from gdp.optimization.objectives import tres_cambiadores_total_area_cost


def make_evaluator(model, registry, hysys):
    def evaluate(a1):
        executor = GDPExecutor(model, registry, hysys)
        executor.context.set("A1", a1)
        executor.context.set("Prob", {})
        return executor.run()

    return evaluate


def main():
    gdp_file = Path(__file__).with_name("Tres_Cambiadores_V2.gdp")

    parser = GDPParser()
    model = parser.parse(gdp_file.read_text())

    registry = PythonCallbackRegistry()
    registry.register("Modelo", modelo)

    hysys = COMHysysAdapter()
    hysys.connect()
    hysys.attach_active_case()

    evaluator = make_evaluator(model, registry, hysys)

    solver = LogicOAContinuous(
        evaluator=evaluator,
        objective=tres_cambiadores_total_area_cost,
    )

    result = solver.solve(x0=12.0, step=2.0, max_iter=10, lower_bound=5, upper_bound=20)

    print("\n=== LogicOA Result ===")
    print(f"Best A1: {result.best_x}")
    print(f"Best Objective: {result.best_objective}")

    print("\nIteration trace:")
    for it in result.iterations:
        print(f"k={it.iteration:02d} | A1={it.x_value:.2f} | obj={it.objective_value:.4f}")


if __name__ == "__main__":
    main()
