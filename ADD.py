import numpy as np
import subprocess
import os

def Add_simulation(Add_name,Add_title, InputValueInOne,InputValueInTwo):
    all_results = []
    for ii in range(InputValueInOne.shape[0]):
        InputValueOne = InputValueInOne[ii, :, :]
        InputValueTwo = InputValueInTwo[ii, :, :]
        InputValueOne=InputValueOne.ravel()
        InputValueOne= InputValueOne.tolist()
        circuit_output_number = len(InputValueOne)
        InputValueTwo = InputValueTwo.ravel()
        InputValueTwo = InputValueTwo.tolist()

        output_directory = 'output_files/'
        file_name = f'{Add_name}{ii}.cir'
        file_path = os.path.join(output_directory, file_name)
        with open(file_path, 'w') as cir_file:
            cir_file.write(Add_title)
            cir_file.write("\n")
            cir_file.write(".include IDEALOPAMP.mod\n")
            cir_file.write("V+ V+ 0 15V\n")
            cir_file.write("V- V- 0 -15V\n")
            for index, voltage in enumerate(InputValueOne, start=1):
                cir_file.write(f"VIONE{index} IONEInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, voltage in enumerate(InputValueTwo, start=1):
                cir_file.write(f"VITWO{index} ITWOInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, voltage in enumerate(InputValueOne, start=1):
                cir_file.write(f"RONE{index} IONEInput{index} ADDIN{index} 1\n")
            cir_file.write("\n")
            for index, voltage in enumerate(InputValueOne, start=1):
                cir_file.write(f"RTWO{index} ITWOInput{index} ADDIN{index} 1\n")
            cir_file.write("\n")
            for index, voltage in enumerate(InputValueOne, start=1):
                cir_file.write(f"XU{index} 0 ADDIN{index} V+ V- ADDOUT{index} IDEALOPAMP\n")
            cir_file.write("\n")
            for index, voltage in enumerate(InputValueOne, start=1):
                cir_file.write(f"RF{index} ADDIN{index} ADDOUT{index} 1\n")
            cir_file.write("\n")
            for index, voltage in enumerate(InputValueOne, start=1):
                cir_file.write(f"RRevADDOUT{index} ADDOUT{index} RevIN{index} 1\n")
            cir_file.write("\n")
            for index, voltage in enumerate(InputValueOne, start=1):
                cir_file.write(f"RRevOUT{index} RevIN{index} RevOUT{index} 1\n")
            cir_file.write("\n")
            for index, voltage in enumerate(InputValueOne, start=1):
                cir_file.write(f"XURev{index} 0 RevIN{index} V+ V- RevOUT{index} IDEALOPAMP\n")
            cir_file.write("\n")
            cir_file.write(".control\n")
            cir_file.write("op\n")
            for index in range(circuit_output_number):
                cir_file.write(f"print RevOUT{index + 1}\n")
            cir_file.write(".endc\n")
            cir_file.write(".END")
        ngspice_command = 'ngspice'
        circuit_file = os.path.join(output_directory, f'{Add_name}{ii}.cir')
        command = [ngspice_command, '-b', circuit_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        current_values = []
        for line in result.stdout.split('\n'):
            if line.startswith('revout'):
                parts = line.split('=')
                value_str = parts[1].strip()
                try:
                    value = float(value_str)
                    current_values.append(value)
                except ValueError:
                    print(f"Error parsing value: {value_str}")
        all_results.append(current_values)
        result_matrix = np.array(all_results)
        result_matrix = result_matrix.reshape((-1, int(np.sqrt(len(result_matrix[0, :]))), int(np.sqrt(len(result_matrix[0, :])))))
    return result_matrix
