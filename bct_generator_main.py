# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 11:58:37 2022

@author: sungw765
"""

mdf_file = 'test.mdf'
string4 = 'Flhis'  # history file for history step


def convert_flt_to_sci_not(flt, prec, exp_digits):
    s = "%.*e" % (prec, flt)
    # print(f's: {s}')
    if s == 'nan':
        s = "%.*e" % (prec, 0)  # TODO: is it a good idea to replace nan with 0?
    mantissa, exp = s.split('e')
    # print(f'mantissa: {mantissa}')
    # print(f'exp: {exp}')
    # add 1 to digits as 1 is taken by sign +/-
    return "%se%+0*d" % (mantissa, exp_digits + 1, int(exp))


file1 = open(mdf_file, "r")
for line in file1:
    # checking string is present in line or not
    if string4 in line:
        values_4 = line.split('=')
        time_step = values_4[1].strip()
        time_step_2 = time_step.split(' ')
        step_time = time_step_2[1].strip()
        break
        file1.close()  # close file

step_float = float(step_time)
step = float(convert_flt_to_sci_not(flt=step_float, prec=7, exp_digits=3))


# def write_bnd_data_ascii(bnd_data_list, out_path):
#     """Write ASCII file as input for bct file.
#     Contains rows for (1) time, (2) wl at point a, (3) wl at point b."""

#     with open(out_path, 'w', newline='') as out_file:
#         csv_writer = csv.writer(out_file)
#         count = 0
#         for row in bnd_data_list[0]:
#             # Set values to write, add leading blank for positive values
#             time_val = add_blank_pos_val(input_str=bnd_data_list[0][count])
#             wl_a = add_blank_pos_val(input_str=bnd_data_list[1][count])
#             wl_b = add_blank_pos_val(input_str=bnd_data_list[2][count])

#             # Generate row content as single string
#             row_str = f'{time_val} {wl_a} {wl_b}'

#             # Write row to file
#             csv_writer.writerow([row_str])

#             count += 1

#     out_file = out_path.split('\\')[-1]
#     print(f'ASCII file written as {out_file}')
# print(f'ASCII file written to {out_path}')
