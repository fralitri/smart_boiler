# custom_components/smart_boiler/const.py
DOMAIN = "smart_boiler"

GAS_TYPES = {
    "NAT. G20": {"calorific_value": 10.7, "unit": "m3/h"},  # Potere calorifico in kWh/m³
    "Città G110": {"calorific_value": 4.5, "unit": "m3/h"},  # Potere calorifico in kWh/m³
    "G.P.L. G31": {"calorific_value": 13.8, "unit": "kg/h"},  # Potere calorifico in kWh/kg
}