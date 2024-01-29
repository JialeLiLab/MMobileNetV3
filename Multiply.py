import numpy as np
import subprocess
import os

def Multiply_simulation(Multiply_name,Multiply_title, InputValueInOne,InputValueInTwo):
    all_results = []
    for ii in range(InputValueInOne.shape[0]):
        InputValueOne = InputValueInOne[ii, :, :]
        InputValueTwo= InputValueInTwo[ii, :, :]
        InputValueOne=InputValueOne.ravel()
        InputValueOne= InputValueOne.tolist()
        InputValueTwo = InputValueTwo.ravel()
        InputValueTwo = InputValueTwo.tolist()
        circuit_output_number=len(InputValueTwo)
        output_directory = 'output_files/'
        file_name = f'{Multiply_name}{ii}.cir'
        file_path = os.path.join(output_directory, file_name)
        with open(file_path, 'w') as cir_file:
            cir_file.write(Multiply_title)
            cir_file.write("\n")
            cir_file.write(".model limit5 limit(in_offset=0 gain=1 out_lower_limit=-5.0 out_upper_limit=6 limit_range=0.10 fraction=FALSE)\n")
            for index, voltage in enumerate(InputValueOne, start=1):
                cir_file.write(f"VIONE{index} IONEInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, voltage in enumerate(InputValueTwo, start=1):
                cir_file.write(f"VITWO{index} ITWOInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index in range(circuit_output_number):
                cir_file.write(f"Eprod{index + 1} Out{index + 1} 0 VALUE={{V(IONEInput1,0)* V(ITWOInput{index + 1},0)}}\n")
            cir_file.write("\n")
            cir_file.write(".control\n")
            cir_file.write("op\n")
            for index in range(circuit_output_number):
                cir_file.write(f"print Out{index + 1}\n")
            cir_file.write(".endc\n")
            cir_file.write(".END")
        ngspice_command = 'ngspice'
        circuit_file = os.path.join(output_directory, f'{Multiply_name}{ii}.cir')
        command = [ngspice_command, '-b', circuit_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        current_values = []
        for line in result.stdout.split('\n'):
            if line.startswith('out'):
                parts = line.split('=')
                value_str = parts[1].strip()
                try:
                    value = float(value_str)
                    current_values.append(value)
                except ValueError:
                    print(f"Error parsing value: {value_str}")
        all_results.append(current_values)
        result_matrix = np.array(all_results)
        result_matrix = result_matrix.reshape(
            (-1, int(np.sqrt(len(result_matrix[0, :]))), int(np.sqrt(len(result_matrix[0, :])))))
    return result_matrix
