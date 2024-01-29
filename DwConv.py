import numpy as np
import subprocess
import os

def DwConv_simulation(Conv_name,Conv_title, InputValueIn, ConvValuePIn, ConvValueNIn, ConvPadding, ConvStride):
    all_results = []
    for ii in range(ConvValuePIn.shape[0]):

        InputValue = InputValueIn[ii, :, :]
        ConvValueP = ConvValuePIn[ii, 0, :, :]
        ConvValueN = ConvValueNIn[ii, 0, :, :]
        InputNumRows = len(InputValue)
        InputNumColumns = len(InputValue[0])
        InputExtended = np.zeros((InputNumRows + 2 * ConvPadding, InputNumColumns + 2 * ConvPadding),
                                 dtype=InputValue.dtype)
        InputExtended[ConvPadding:ConvPadding + InputNumRows,
        ConvPadding:ConvPadding + InputNumColumns] = InputValue
        InputExtendedRows = len(InputExtended)
        InputExtendedColumns = len(InputExtended[0])
        InputExtendedNum = InputExtendedRows * InputExtendedColumns
        ConvNumRows = len(ConvValueP)
        ConvNumColumns = len(ConvValueP[0])
        OutputNumRows = (InputExtendedRows - ConvNumRows) // ConvStride + 1
        OutputNumColumns = (InputExtendedColumns - ConvNumColumns) // ConvStride + 1
        OutputNum = OutputNumRows * OutputNumColumns
        flattenedInput = InputExtended.flatten()
        output_directory = 'output_files/'
        file_name = f'{Conv_name}{ii}.cir'
        file_path = os.path.join(output_directory, file_name)
        with open(file_path, 'w') as cir_file:
            cir_file.write(Conv_title)
            cir_file.write("\n")
            cir_file.write(".MODEL HP MEMR level=1 Ron=100 Roff=16k D=10N Mu=10F\n")
            for index, value in enumerate(flattenedInput):
                if (value != 0):
                    cir_file.write(f"VCQ{index + 1} CQInput{index + 1} 0 {value}\n")
            cir_file.write("\n")
            for index, value in enumerate(flattenedInput):
                if (value != 0):
                    value = -value
                    cir_file.write(f"VCW{index + 1} CWInput{index + 1} 0 {value}\n")
            cir_file.write("\n")
            coordinates = []
            blank = []
            for index in range(OutputNum):
                x = index // OutputNumRows
                y = index % OutputNumColumns
                coordinates.append((x, y))
            for x, y in coordinates:
                value = (x * InputExtendedColumns + y) * ConvStride
                blank.append(value)
            memristorArray = [[0 for _ in range(InputExtendedNum)] for _ in range(OutputNum)]
            convArray = [element for row in ConvValueP for element in row]
            groupNum = InputExtendedRows - ConvNumRows
            new_kernel = []
            for i in range(0, len(convArray), ConvNumRows):
                group = convArray[i:i + ConvNumRows]
                new_kernel.extend(group)
                if i + ConvNumRows < len(convArray):
                    new_kernel.extend([0] * groupNum)
            for i in range(len(memristorArray)):
                for j in range(len(memristorArray[i])):
                    if j >= blank[i] and j < blank[i] + len(new_kernel):
                        memristorArray[i][j] = new_kernel[j - blank[i]]
            result_dict = {}
            for i, row in enumerate(memristorArray):
                for j, value in enumerate(row):
                    if value != 0:
                        result_dict[(i, j)] = {'value': value, 'row': i + 1, 'col': j + 1}
            index = 1
            for position, info in result_dict.items():
                formatted_value = f"{info['value']:.10f}"
                if (formatted_value != '999999936.0000000000'):
                    cir_file.write(
                        f"NCQ{index} CQInput{info['col']} CQVMMOut{info['row']} HP wic={formatted_value}\n")
                index += 1
            cir_file.write("\n")
            convArray_N = [element for row in ConvValueN for element in row]
            new_kernel_N = []

            for i in range(0, len(convArray_N), ConvNumRows):
                group = convArray_N[i:i + ConvNumRows]
                new_kernel_N.extend(group)
                if i + ConvNumRows < len(convArray_N):
                    new_kernel_N.extend([0] * groupNum)
            for i in range(len(memristorArray)):
                for j in range(len(memristorArray[i])):
                    if j >= blank[i] and j < blank[i] + len(new_kernel_N):
                        memristorArray[i][j] = new_kernel_N[j - blank[i]]
            result_dict_n = {}
            for i, row in enumerate(memristorArray):
                for j, value in enumerate(row):
                    if value != 0:
                        result_dict_n[(i, j)] = {'value': value, 'row': i + 1, 'col': j + 1}
            index = 1
            for position, info in result_dict_n.items():
                formatted_value = f"{info['value']:.10f}"
                if (formatted_value != '999999936.0000000000'):
                    cir_file.write(
                        f"NCQN{index} CWInput{info['col']} CQVMMOut{info['row']} HP wic={formatted_value}\n")
                index = index + 1
            cir_file.write("\n")
            for index in range(info['row']):
                cir_file.write(f"VT{index + 1} CQVMMOut{index + 1} 0 0\n")
            cir_file.write(".control\n")
            cir_file.write("op\n")
            for index in range(info['row']):
                cir_file.write(f"print I(VT{index + 1})\n")
            cir_file.write(".endc\n")
            cir_file.write(".END")

        ngspice_command = 'ngspice'
        circuit_file = os.path.join(output_directory, f'{Conv_name}{ii}.cir')
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
        matrix = np.array(all_results)
    result_matrix = matrix.reshape(
        (-1, int(np.sqrt(len(matrix[0, :]))), int(np.sqrt(len(matrix[0, :])))))
    return result_matrix
