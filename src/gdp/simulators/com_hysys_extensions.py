class TresCambiadoresMixin:
    def set_exchanger_ua(self, name, value):
        ua = self.case.Flowsheet.Operations.Item(name)
        ua.GoalValue = value

    def read_tres_cambiadores_state(self):
        heater = self.case.Flowsheet.Operations.Item("Heater")
        cooler = self.case.Flowsheet.Operations.Item("Cooler")

        return {
            "Tinhot": heater.FeedTemperatureValue,
            "Touthot": heater.ProductTemperatureValue,
            "Tcoldin": cooler.FeedTemperatureValue,
            "Tcoldout": cooler.ProductTemperatureValue,
            "Q2": heater.DutyValue,
            "Q3": cooler.DutyValue,
        }
