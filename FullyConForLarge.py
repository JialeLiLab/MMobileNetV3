import numpy as np
import subprocess
import os
def FullyConForLarge_simulation(FC_name,FC_title, InputValueIn, FCBiasVoltage,FCValuePIn, FCValueNIn,FCBiasPIn, FCBiasNIn):
    all_results = []
    circuit_input_value=InputValueIn.ravel()
    circuit_input_value= circuit_input_value.tolist()
    circuit_input_number = FCValuePIn.shape[1]
    circuit_output_number = FCValuePIn.shape[0]
    flat_list = [item for sublist in FCValuePIn for item in sublist]
    total_elements = len(flat_list)
    size = total_elements // circuit_output_number
    divided_arrays = [flat_list[i * size:(i + 1) * size] for i in range(circuit_output_number - 1)]
    divided_arrays.append(flat_list[(circuit_output_number - 1) * size:])
    FCValuePIn = np.array(divided_arrays)
    flat_list = [item for sublist in FCValueNIn for item in sublist]
    total_elements = len(flat_list)
    size = total_elements // circuit_output_number
    divided_arrays = [flat_list[i * size:(i + 1) * size] for i in range(circuit_output_number - 1)]
    divided_arrays.append(flat_list[(circuit_output_number - 1) * size:])
    FCValueNIn = np.array(divided_arrays)
    for ii in range(circuit_output_number):
        output_directory = 'output_files/'
        file_name = f'{FC_name}{ii}.cir'
        file_path = os.path.join(output_directory, file_name)
        with open(file_path, 'w') as cir_file:
            cir_file.write(FC_title)
            cir_file.write("\n")
            cir_file.write(".MODEL HP MEMR level=1 Ron=100 Roff=16k D=10N Mu=10F\n")
            cir_file.write(f"VB b 0 {FCBiasVoltage}\n")
            NFCBiasVoltage = -FCBiasVoltage
            cir_file.write(f"VNB nb 0 {NFCBiasVoltage}\n")
            for index, voltage in enumerate(circuit_input_value, start=1):
                cir_file.write(f"VQ{index} QInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, voltage in enumerate(circuit_input_value, start=1):
                voltage=-voltage
                cir_file.write(f"VW{index} WInput{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index, value in enumerate(FCValuePIn[ii, :]):
                formatted_value = f"{value:.10f}"
                if (formatted_value != '999999936.0000000000'):
                    cir_file.write(f"NQ{index+1} QInput{index+1 } QVMMOut{ii+1} HP wic={formatted_value}\n")
            cir_file.write("\n")
            for index, value in enumerate(FCValueNIn[ii, :]):
                formatted_value = f"{value:.10f}"
                if (formatted_value != '999999936.0000000000'):
                    cir_file.write(f"NQN{index+1} WInput{index+1 } QVMMOut{ii+1} HP wic={formatted_value}\n")
            cir_file.write("\n")
            if (FCBiasPIn[ii] != '999999936.0000000000'):
                cir_file.write(f"NQB{ii} b QVMMOut{ii + 1} HP wic={FCBiasPIn[ii]}\n")
            cir_file.write("\n")
            if (FCBiasNIn[ii] != '999999936.0000000000'):
                cir_file.write(f"NQNB{ii} nb QVMMOut{ii + 1} HP wic={FCBiasNIn[ii]}\n")
            cir_file.write("\n")
            cir_file.write(f" VT{ii + 1} QVMMOut{ii + 1} 0 0\n")
            cir_file.write(".control\n")
            cir_file.write("op\n")
            cir_file.write(f" print I(VT{ii+1})\n")
            cir_file.write(".endc\n")
            cir_file.write(".END")
        ngspice_command = 'ngspice'
        circuit_file = os.path.join(output_directory, f'{FC_name}{ii}.cir')
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
            (circuit_output_number, InputValueIn.shape[1], InputValueIn.shape[2]))
    return result_matrix
