import json
import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl

# Load knowledge from JSON
with open("knowledge.json", "r") as file:
    knowledge = json.load(file)["knowledge"]

# Define fuzzy variables dynamically based on JSON data
fuzzy_variables = {}

for var_name, memberships in knowledge.items():
    universe_range = []
    for params in memberships.values():
        universe_range.extend(params)
    
    # Determine the range of the universe
    min_range, max_range = min(universe_range), max(universe_range)
    step = 0.1 if isinstance(min_range, int) else 0.01
    fuzzy_variables[var_name] = ctrl.Antecedent(np.arange(min_range, max_range + step, step), var_name)

    # Add membership functions dynamically
    for label, params in memberships.items():
        fuzzy_variables[var_name][label] = fuzz.trimf(fuzzy_variables[var_name].universe, params)

# Define fuzzy output variable for economic condition
kondisi_ekonomi = ctrl.Consequent(np.arange(0, 11, 1), 'kondisi_ekonomi')
kondisi_ekonomi['buruk'] = fuzz.trimf(kondisi_ekonomi.universe, [0, 0, 3])
kondisi_ekonomi['normal'] = fuzz.trimf(kondisi_ekonomi.universe, [2, 5, 8])
kondisi_ekonomi['baik'] = fuzz.trimf(kondisi_ekonomi.universe, [7, 10, 10])

# Define rules dynamically based on fuzzy variables
rules = [
    ctrl.Rule(fuzzy_variables['inflasi']['tinggi'] & fuzzy_variables['pengangguran']['tinggi'], kondisi_ekonomi['buruk']),
    ctrl.Rule(fuzzy_variables['inflasi']['rendah'] & fuzzy_variables['pertumbuhan_ekonomi']['positif'], kondisi_ekonomi['baik']),
    ctrl.Rule(fuzzy_variables['defisit_anggaran']['sedang'] & fuzzy_variables['investasi_asing']['tinggi'], kondisi_ekonomi['normal']),
    ctrl.Rule(fuzzy_variables['inflasi']['sedang'] & fuzzy_variables['pengangguran']['sedang'], kondisi_ekonomi['normal']),
    ctrl.Rule(fuzzy_variables['pertumbuhan_ekonomi']['negatif'] & fuzzy_variables['investasi_asing']['rendah'], kondisi_ekonomi['buruk']),
    ctrl.Rule(fuzzy_variables['pertumbuhan_ekonomi']['positif'] & fuzzy_variables['investasi_asing']['tinggi'], kondisi_ekonomi['baik']),
    ctrl.Rule(fuzzy_variables['defisit_anggaran']['rendah'] & fuzzy_variables['inflasi']['rendah'], kondisi_ekonomi['baik']),
    ctrl.Rule(fuzzy_variables['defisit_anggaran']['tinggi'] | fuzzy_variables['pengangguran']['tinggi'], kondisi_ekonomi['buruk']),
    ctrl.Rule(fuzzy_variables['kepuasan_konsumen']['tinggi'] & fuzzy_variables['stabilitas_harga']['stabil'], kondisi_ekonomi['baik']),
    ctrl.Rule(fuzzy_variables['kepuasan_konsumen']['rendah'] | fuzzy_variables['stabilitas_harga']['tidak_stabil'], kondisi_ekonomi['buruk']),
    ctrl.Rule(fuzzy_variables['ipm']['tinggi'] & fuzzy_variables['investasi_asing']['tinggi'], kondisi_ekonomi['baik']),
    ctrl.Rule(fuzzy_variables['ipm']['rendah'] | fuzzy_variables['stabilitas_harga']['fluktuatif'], kondisi_ekonomi['buruk']),
    ctrl.Rule(fuzzy_variables['ekspor']['tinggi'] & fuzzy_variables['impor']['rendah'], kondisi_ekonomi['baik']),
    ctrl.Rule(fuzzy_variables['nilai_tukar']['lemah'] | fuzzy_variables['cadangan_devisa']['rendah'], kondisi_ekonomi['buruk'])
]

# Create and simulate the fuzzy system
kbs_ctrl = ctrl.ControlSystem(rules)
kbs = ctrl.ControlSystemSimulation(kbs_ctrl)

# Request input from the user
def get_user_input():
    print("Masukkan nilai untuk variabel berikut:")
    inputs = {}
    for var_name, var_obj in fuzzy_variables.items():
        min_val, max_val = var_obj.universe[0], var_obj.universe[-1]
        inputs[var_name] = float(input(f"{var_name.capitalize().replace('_',' ' )} ({min_val:.0f} hingga {max_val:.0f}): "))
    return inputs

# Get user input
user_inputs = get_user_input()

# Set inputs to the fuzzy system
for var_name, value in user_inputs.items():
    kbs.input[var_name] = value

# Compute output
try:
    kbs.compute()
    kondisi = kbs.output['kondisi_ekonomi']
    print(f"\nKondisi Ekonomi (nilai): {kondisi:.2f}")
    if kondisi <= 3:
        print("Kondisi Ekonomi: Buruk")
    elif kondisi <= 7:
        print("Kondisi Ekonomi: Normal")
    else:
        print("Kondisi Ekonomi: Baik")
except KeyError:
    print("Tidak ada aturan yang terpicu. Kondisi Ekonomi default: Normal (5.0)")
