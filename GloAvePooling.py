import numpy as npimport
import subprocess
import os
def GloAvePooling_simulation(GAPool_name,GAPool_title, InputValueIn):
    all_results = []
    for ii in range(InputValueIn.shape[0]):
        InputValue = InputValueIn[ii, :, :]
        InputNumRows = len(InputValue)
        InputNumColumns = len(InputValue[0])
        InputNum=InputNumRows*InputNumColumns
        values = 1 / (15900 * 1 / InputNum) - 1 / 159
        flattenedInput = InputValue.flatten()
        output_directory = 'output_files/'
        file_name = f'{GAPool_name}{ii}.cir'
        file_path = os.path.join(output_directory, file_name)
        with open(file_path, 'w') as cir_file:
            cir_file.write(GAPool_title)
            cir_file.write("\n")
            cir_file.write(".MODEL HP MEMR level=1 Ron=100 Roff=16k D=10N Mu=10F")
            cir_file.write("\n")
            for index, value in enumerate(flattenedInput):
                cir_file.write(f"V{index+1} Input{index+1} 0 {value}\n")
            cir_file.write("\n")
            for index in range(InputNum):
                cir_file.write(f"N{index + 1} Input{index + 1} Out1 HP wic={values}\n")
            cir_file.write("\n")
            cir_file.write(f"VT1 Out1 0 0\n")
            cir_file.write(".control\n")
            cir_file.write("op\n")
            cir_file.write(f" print I(VT1)\n")
            cir_file.write(".endc\n")
            cir_file.write(".END")
        ngspice_command = 'ngspice'
        circuit_file = os.path.join(output_directory, f'{GAPool_name}{ii}.cir')
        command = [ngspice_command, '-b', circuit_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        current_values = []
        for line in result.stdout.split('\n'):
            if line.startswith('i(vt'):
                parts = line.split('=')
                value_str = parts[1].strip()
                try:
                    value = float(value_str)
                    current_values.append(value)
                except ValueError:
                    print(f"Error parsing value: {value_str}")
        all_results.append(current_values)
        result_matrix = np.array(all_results)
        result_matrix = result_matrix.reshape((-1,int(np.sqrt(len(result_matrix[0, :]))), int(np.sqrt(len(result_matrix[0, :])))))
    return result_matrix

