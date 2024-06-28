# -*- coding: utf-8 -*-
"""
To add sea level change to the .bct file generated from the algorithm
"""
import numpy as np
import pandas as pd
import os


def add_wl(bct_file, sea_level_change, constant=False):

    def data_extract(file_path):

        with open(file_path, 'r') as file:
            for _ in range(10):
                next(file)  # Skip the first 10 lines

            eleventh_line = next(file).strip()

            # Extract each word from the 11th line
            words = eleventh_line.split()

            number_of_data_lines = int(words[1])

        return number_of_data_lines

    def count_lines(file_path, target_line):

        with open(file_path, 'r') as file:
            line_count = 0
            for line in file:
                if target_line in line:
                    line_count += 1
        return line_count

    def copy_lines(source_file, destination_file, num_lines_start, num_lines_end):

        with open(source_file, 'r') as source:
            lines = source.readlines()

        lines_to_copy = lines[num_lines_start:num_lines_end]

        with open(destination_file, 'a') as destination:
            destination.writelines(lines_to_copy)

    def read_lines_after_offset(file_path, num_lines, offset):

        with open(file_path, 'r') as file:
            # Skip the specified offset lines
            for _ in range(offset):
                next(file)

            # Read the next 'num_lines' lines and store them in a list
            lines_after_offset = []
            for _ in range(num_lines):
                line = next(file).strip()
                lines_after_offset.append(line)

            # Create DataFrame with three columns
            df = pd.DataFrame([line.split() for line in lines_after_offset])

            return df

    def write_dataframe_to_text(df, file_path):
        # Convert the DataFrame to a string without column headers
        df_str = df.to_string(index=False, header=False)

        # Manually add a space before every row
        df_str = '\n'.join([' ' + row for row in df_str.split('\n')])

        # Write the modified string to the text file
        with open(file_path, 'a') as file:
            file.write(df_str + '\n')

    def convert_flt_to_sci_not(fltt, prec, exp_digits):
        s = "%.*e" % (prec, fltt)
        # print(f's: {s}')
        if s == 'nan':
            s = "%.*e" % (prec, 0)
        mantissa, exp = s.split('e')
        # print(f'mantissa: {mantissa}')
        # print(f'exp: {exp}')
        # add 1 to digits as 1 is taken by sign +/-
        return "%se%+0*d" % (mantissa, exp_digits + 1, int(exp))

    def convert_list_to_sci_not(input_list, prec, exp_digits):
        converted = []
        for flt in input_list:
            sci = convert_flt_to_sci_not(
                fltt=flt, prec=prec, exp_digits=exp_digits)
            converted.append(sci)

        return converted

    def interpolate(start, end, steps):
        step_size = (end - start) / (steps - 1)
        interpolated_values = [start + i * step_size for i in range(steps)]
        return interpolated_values

    # extract intervals
    file_path = bct_file
    data_lines = data_extract(file_path)

    target_line = "interpolation"
    total_lines = count_lines(file_path, target_line)

    # calculate in which rows the data and the headers start
    start_text = []
    end_text = []
    start_text.append(0)
    end_text.append(11)
    for i in range(0, total_lines-1):
        text_s = end_text[i] + data_lines
        start_text.append(text_s)
        text_e = text_s + 11
        end_text.append(text_e)

    start_data = []
    end_data = []
    start_data.append(11)
    first_end = data_lines + end_text[0]
    end_data.append(first_end)
    for i in range(0, total_lines-1):
        data_s = end_data[i] + 11
        start_data.append(data_s)
        data_e = data_s + data_lines
        end_data.append(data_e)

    #  Add the sea level to the water level
    if constant is False:
        wl_change = interpolate(0, sea_level_change, data_lines)
    else:
        wl_change = np.full(data_lines, sea_level_change)

    #  write a new bct file
    name_with_dot = bct_file.partition('.')
    name_until_dot = name_with_dot[0]
    file_name = '{}_wl_changed.bct'.format(name_until_dot)

    destination_file_path = file_name

    # Write the water level file again
    try:
        os.remove(destination_file_path)
    except FileNotFoundError:
        pass

    for st, et, sd, ed in zip(start_text, end_text, start_data, end_data):
        # manage the header
        copy_lines(file_path, destination_file_path, st, et)
        # manage the df
        # extract the df
        df = read_lines_after_offset(file_path, data_lines, offset=sd)
        # add water level for both columns
        df[1] = pd.to_numeric(df[1])
        df[1] = df[1] + wl_change
        df[1] = convert_list_to_sci_not(input_list=df[1],
                                        prec=7, exp_digits=3)

        df[2] = pd.to_numeric(df[2])
        df[2] = df[2] + wl_change
        df[2] = convert_list_to_sci_not(input_list=df[2],
                                        prec=7, exp_digits=3)
        # write the df into the file
        write_dataframe_to_text(df, destination_file_path)
