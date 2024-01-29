import subprocess
import numpy as np
import os

all_results = []
def FCReLU_simulation(ReLU_name,ReLU_title, InputValueIn):
    global all_results
    all_results.clear()
    circuit_input_value = InputValueIn.flatten()
    output_directory = 'output_files/'
    file_name = f'{ReLU_name}.cir'
    file_path = os.path.join(output_directory, file_name)
    with open(file_path, 'w') as cir_file:
        cir_file.write(ReLU_title)
        cir_file.write("\n")
        cir_file.write(".MODEL NMOS NMOS level=1\n")
        cir_file.write(".MODEL PMOS PMOS level=1\n")
        for index in range(len(circuit_input_value)):
            cir_file.write(f"V{index + 1} QRevOut{index + 1} 0 {circuit_input_value[index]}\n")
            cir_file.write(f"M{index + 1}Relu1 QRevOut{index + 1} 0 QM{index + 1}ReluN1 0 NMOS W=5u L=0.5u\n")
            cir_file.write(f"M{index + 1}Relu2 QM{index + 1}ReluN1 QRevOut{index + 1} 0 0 NMOS W=5u L=0.5u\n")
            cir_file.write(
                f"M{index + 1}Relu3 QM{index + 1}ReluOut 0 QRevOut{index + 1} QM{index + 1}ReluOut PMOS W=5u L=0.5u\n")
            cir_file.write(
                f"M{index + 1}Relu4 0 QRevOut{index + 1} QM{index + 1}ReluOut QM{index + 1}ReluOut PMOS W=5u L=0.5u\n")
            cir_file.write("\n")
        cir_file.write(".control\n")
        cir_file.write("op\n")
        for index in range(len(circuit_input_value)):
            cir_file.write(f" print QM{index + 1}ReluOut\n")
        cir_file.write(".endc\n")
        cir_file.write(".END")
    ngspice_command = 'ngspice'
    circuit_file = os.path.join(output_directory, f'{ReLU_name}.cir')
    command = [ngspice_command, '-b', circuit_file]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result)
    current_values = []
    for line in result.stdout.split('\n'):
        if line.startswith('qm'):
            parts = line.split('=')
            value_str = parts[1].strip()
            try:
                value = float(value_str)
                current_values.append(value)
            except ValueError:
                print(f"Error parsing value: {value_str}")
    all_results.append(current_values)
    result_matrix = np.array(all_results)
    return result_matrix