import subprocess
import numpy as np
import os

all_results = []
def HardSwish_simulation(hardswish_name,hardswish_title, InputValueIn):
    global all_results 
    all_results.clear()
    InputShape0=InputValueIn.shape[0]
    InputShape1=InputValueIn.shape[1]
    InputShape2=InputValueIn.shape[2]
    FilesNumber = InputValueIn.shape[0]
    circuit_input_value = InputValueIn.flatten()
    output_directory = 'output_files/'
    for ii in range(FilesNumber):
        file_name = f'{hardswish_name}{ii}.cir'
        file_path = os.path.join(output_directory, file_name)
        InputValue_two_d_array = InputValueIn[ii]
        InputValue_flattened_array = InputValue_two_d_array.ravel()
        with open(file_path, 'w') as cir_file:
            cir_file.write(hardswish_title)
            cir_file.write("\n")
            cir_file.write(".MODEL NMOS NMOS level=1\n")
            cir_file.write(".MODEL PMOS PMOS level=1\n")
            cir_file.write(".include IDEALOPAMP.mod\n")
            cir_file.write(".model limit5 limit(in_offset=0 gain=1 out_lower_limit=-5.0 out_upper_limit=6 limit_range=0.10 fraction=FALSE)\n")
            cir_file.write("V+ V+ 0 15V\n")
            cir_file.write("V- V- 0 -15V\n")
            cir_file.write("V3 Constant 0 3\n")
            for index, voltage in enumerate(InputValue_flattened_array, start=1):
                cir_file.write(f"Vin{index} Input{index} 0 {voltage}\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"RInput{index+1} Input{index+1} AddInput{index+1} 1\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"RConstant{index+1} Constant AddInput{index+1} 1\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"XU{index+1} 0 AddInput{index+1} V+ V- AddOutput{index+1} IDEALOPAMP\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"Rf{index+1} AddOutput{index+1} AddInput{index+1} 1\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"Rr{index+1} AddOutput{index+1} RevInput{index+1} 1\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"Rrout{index+1} RevInput{index+1} ReluIn{index+1} 1\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"XURev{index+1} 0 RevInput{index+1} V+ V- ReluIn{index+1} IDEALOPAMP\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"M{index + 1}Relu1 ReluIn{index+1} 0 QM{index + 1}ReluN1 0 NMOS W=5u L=0.5u\n")
                cir_file.write(f"M{index + 1}Relu2 QM{index + 1}ReluN1 ReluIn{index+1} 0 0 NMOS W=5u L=0.5u\n")
                cir_file.write(f"M{index + 1}Relu3 QM{index + 1}ReluOut 0 ReluIn{index+1} QM{index + 1}ReluOut PMOS W=5u L=0.5u\n")
                cir_file.write(f"M{index + 1}Relu4 0 ReluIn{index+1} QM{index + 1}ReluOut QM{index + 1}ReluOut PMOS W=5u L=0.5u\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"a{index + 1} QM{index + 1}ReluOut lout{index + 1} limit5\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"Rdiv{index + 1} lout{index + 1} Indiv{index + 1} 6\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"Rdivis{index + 1} Indiv{index + 1} Outdiv{index + 1} 1\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"XUdiv{index+1} 0 Indiv{index + 1} V+ V- Outdiv{index + 1} IDEALOPAMP\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"RdivR{index + 1} Outdiv{index + 1} IndivR{index + 1} 1\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"RdivisR{index + 1} OutdivP{index + 1} IndivR{index + 1} 1\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"XUdivR{index+1} 0 IndivR{index + 1} V+ V- OutdivP{index + 1} IDEALOPAMP\n")
            cir_file.write("\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f"Eprod{index+1} Outx{index + 1} 0 VALUE={{V(OutdivP{index + 1},0)* V(Input{index+1},0)}}\n")
            cir_file.write("\n")
            cir_file.write(".control\n")
            cir_file.write("op\n")
            for index in range(len(InputValue_flattened_array)):
                cir_file.write(f" print Outx{index + 1}\n")
            cir_file.write(".endc\n")
            cir_file.write(".END")
        ngspice_command = 'ngspice'
        circuit_file = os.path.join(output_directory, f'{hardswish_name}{ii}.cir')
        command = [ngspice_command, '-b', circuit_file]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        current_values = []
        for line in result.stdout.split('\n'):
            if line.startswith('outx'):
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
         (InputShape0,InputShape1,InputShape2))
    return result_matrix