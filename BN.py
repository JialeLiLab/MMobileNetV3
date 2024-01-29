import numpy as np
import subprocess
import os

def BN_simulation(BN_name,BN_title, InputValueIn, BNBiasVoltage,BNEXIn, BNWeightIn,BNValueIn,BNBiasPIn,BNBiasNIn):
    all_results = []
    FilesNumber=InputValueIn.shape[0]
    BNEXIn=np.array([np.full((InputValueIn.shape[1],InputValueIn.shape[2]), element) for element in BNEXIn])
    BNWeightIn = np.array([np.full((InputValueIn.shape[1],InputValueIn.shape[2]), element) for element in BNWeightIn])
    BNValueIn = np.array([np.full((InputValueIn.shape[1],InputValueIn.shape[2]), element) for element in BNValueIn])
    BNBiasPIn= np.array([np.full((InputValueIn.shape[1],InputValueIn.shape[2]), element) for element in BNBiasPIn])
    BNBiasNIn= np.array([np.full((InputValueIn.shape[1],InputValueIn.shape[2]), element) for element in BNBiasNIn])
    for ii in range(FilesNumber):
        InputValue_two_d_array = InputValueIn[ii]
        InputValue_flattened_array = InputValue_two_d_array.ravel()
        BNEXIn_two_d_array = BNEXIn[ii]
        BNEXIn_flattened_array = BNEXIn_two_d_array.ravel()
        BNWeightIn_two_d_array = BNWeightIn[ii]
        BNWeightIn_flattened_array = BNWeightIn_two_d_array.ravel()
        BNValueIn_two_d_array = BNValueIn[ii]
        BNValueIn_flattened_array = BNValueIn_two_d_array.ravel()

        BNBiasPIn_two_d_array = BNBiasPIn[ii]
        BNBiasPIn_flattened_array = BNBiasPIn_two_d_array.ravel()
        BNBiasNIn_two_d_array = BNBiasNIn[ii]
        BNBiasNIn_flattened_array = BNBiasNIn_two_d_array.ravel()

        circuit_output_number=InputValueIn.shape[1]*InputValueIn.shape[2]
        output_directory = 'output_files/'
        file_name = f'{BN_name}{ii}.cir'
        file_path = os.path.join(output_directory, file_name)
        with open(file_path, 'w') as cir_file:
            cir_file.write(BN_title)
            cir_file.write("\n")
            cir_file.write(".MODEL HP MEMR level=1 Ron=100 Roff=16k D=10N Mu=10F\n")
            cir_file.write(".include IDEALOPAMP.mod\n")
            cir_file.write("V+ V+ 0 15V\n")
            cir_file.write("V- V- 0 -15V\n")
            cir_file.write(f"VB b 0 {BNBiasVoltage}\n")
            NBNBiasVoltage = -BNBiasVoltage
            cir_file.write(f"VNB nb 0 {NBNBiasVoltage}\n")
            for index, voltage in enumerate(InputValue_flattened_array, start=1):
                cir_file.write(f"VIP{index} IPInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, voltage in enumerate(InputValue_flattened_array, start=1):
                voltage=-voltage
                cir_file.write(f"VIN{index} INInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, voltage in enumerate(BNEXIn_flattened_array, start=1):
                cir_file.write(f"VEP{index} EPInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, voltage in enumerate(BNEXIn_flattened_array, start=1):
                voltage=-voltage
                cir_file.write(f"VEN{index} ENInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, value in enumerate(BNValueIn_flattened_array):
                if(value>0):
                    cir_file.write(f"NI{index+1} INInput{index+1} VMMOut{index+1} HP wic=-0.0062264150943396\n")
                    cir_file.write(f"NE{index+1} EPInput{index + 1} VMMOut{index + 1} HP wic=-0.0062264150943396\n")
                if(value<0):
                    cir_file.write(f"NI{index + 1} IPInput{index + 1} VMMOut{index + 1} HP wic=-0.0062264150943396\n")
                    cir_file.write(f"NE{index + 1} ENInput{index + 1} VMMOut{index + 1} HP wic=-0.0062264150943396\n")
            cir_file.write("\n")
            for index in range(circuit_output_number):
                cir_file.write(f"XU{index+1} 0 VMMOut{index + 1} V+ V- OPOut{index + 1} IDEALOPAMP\n")
            cir_file.write("\n")
            for index in range(circuit_output_number):
                cir_file.write(f"Rf{index+1} OPOut{index + 1} VMMOut{index + 1} 1\n")
            cir_file.write("\n")
            for index, value in enumerate(BNWeightIn_flattened_array):
                cir_file.write(f"NV{index + 1} OPOut{index + 1} VOut{index + 1} HP wic={value}\n")
            cir_file.write("\n")
            for index, value in enumerate(BNBiasPIn_flattened_array):
                if (value != '999999936.0000000000'):
                    cir_file.write(f"NBP{index + 1} b VOut{index + 1} HP wic={value}\n")
            cir_file.write("\n")
            for index, value in enumerate(BNBiasNIn_flattened_array):
                if (value != '999999936.0000000000'):
                    cir_file.write(f"NBN{index + 1} nb VOut{index + 1} HP wic={value}\n")
            cir_file.write("\n")
            for index in range(circuit_output_number):
                cir_file.write(f" VT{index + 1} VOut{index + 1} 0 0\n")
            cir_file.write("\n")
            cir_file.write(".control\n")
            cir_file.write("op\n")
            for index in range(circuit_output_number):
                cir_file.write(f" print I(VT{index+1})\n")
                # cir_file.write(f"print OPOut{index + 1}\n")
            cir_file.write(".endc\n")
            cir_file.write(".END")
        ngspice_command = 'ngspice'
        circuit_file = os.path.join(output_directory, f'{BN_name}{ii}.cir')
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
    result_matrix = result_matrix.reshape(
        (-1, int(np.sqrt(len(result_matrix[0, :]))), int(np.sqrt(len(result_matrix[0, :])))))
    return result_matrix
