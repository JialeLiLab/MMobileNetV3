import numpy as np
import subprocess
import os
def Pooling_simulation(Poll_name,Poll_title, InputValueIn, PoolingValue,PoolingStride):
    all_results = []
    for ii in range(InputValueIn.shape[0]):
        InputValue = InputValueIn[ii, :, :]
        InputNumRows = len(InputValue)
        InputNumColumns = len(InputValue[0])
        InputNum=InputNumRows*InputNumColumns
        PoolingNumRows = len(PoolingValue)
        PoolingNumColumns = len(PoolingValue[0])
        OutputNumRows=(InputNumRows-PoolingNumRows)//PoolingStride+1
        OutputNumColumns=(InputNumColumns-PoolingNumColumns)//PoolingStride+1
        OutputNum=OutputNumRows*OutputNumColumns
        flattenedInput = InputValue.flatten()
        output_directory = 'output_files/'
        file_name = f'{Poll_name}{ii}.cir'
        file_path = os.path.join(output_directory, file_name)
        with open(file_path, 'w') as cir_file:
            cir_file.write(Poll_title)
            cir_file.write("\n")
            cir_file.write(".MODEL HP MEMR level=1 Ron=100 Roff=16k D=10N Mu=10F")
            cir_file.write("\n")
            cir_file.write("VB b 0 1\n")
            for index, value in enumerate(flattenedInput):
                cir_file.write(f"VCQ{index+1} CQInput{index+1} 0 {value}\n")
            cir_file.write("\n")
            PoolingCoordinates = []
            PoolingBlank = []
            for index in range(OutputNum):
                x = index // OutputNumRows
                y = index % OutputNumColumns
                PoolingCoordinates.append((x, y))
            for x, y in PoolingCoordinates:
                value = (x * InputNumColumns + y)*PoolingStride
                PoolingBlank.append(value)
            PoolingMemristorArray = [[0 for _ in range(InputNum)] for _ in range(OutputNum)]
            PoolingArray = [element for row in PoolingValue for element in row]
            PoolingGroupNum = InputNumRows - PoolingNumRows
            Pooling_new_kernel = []
            for i in range(0, len(PoolingArray), PoolingNumRows):
                group = PoolingArray[i:i + PoolingNumRows]
                Pooling_new_kernel.extend(group)
                if i + PoolingNumRows < len(PoolingArray):
                    Pooling_new_kernel.extend([0] * PoolingGroupNum)
            for i in range(len(PoolingMemristorArray)):
                    for j in range(len(PoolingMemristorArray[i])):
                        if j >= PoolingBlank[i] and j < PoolingBlank[i] + len(Pooling_new_kernel):
                            PoolingMemristorArray[i][j] = Pooling_new_kernel[j - PoolingBlank[i]]
            for row in PoolingMemristorArray:
                Pooling_result_dict = {}
            for i, row in enumerate(PoolingMemristorArray):
                for j, value in enumerate(row):
                    if value != 0:
                            Pooling_result_dict[(i, j)] = {'value': value, 'row': i+1, 'col': j+1}
                index = 1
            for position, info in Pooling_result_dict.items():
                    cir_file.write(f" NCQ{index} CQInput{info['col']} CQVMMOut{info['row']} HP wic={info['value']}\n")
                    index=index+1
            cir_file.write("\n")
            for index in range(info['row']):
                cir_file.write(f" VT{index+1} CQVMMOut{index+1} 0 0\n")
            cir_file.write(".control\n")
            cir_file.write("op\n")
            for index in range(info['row']):
                cir_file.write(f" print I(VT{index+1})\n")
            cir_file.write(".endc\n")
            cir_file.write(".END")
        ngspice_command = 'ngspice'
        circuit_file = os.path.join(output_directory, f'{Poll_name}{ii}.cir')
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

