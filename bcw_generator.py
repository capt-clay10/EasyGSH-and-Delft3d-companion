# -*- coding: utf-8 -*-
"""
The function to extract wave data from the netcdf file and create a bcw file
"""


def bcw_file_generator(
        boundaries_wave, nc_file_wave, mdw_file, start_time, end_time, step_wave, bcw_file_name):
    # %% Import packages
    import pandas as pd
    import numpy as np
    import os
    import csv
    import math

    try:
        import utm
    except ModuleNotFoundError as err:
        # Error handling
        print(
            str(err) + ' Module utm doesnt exist please install it in your environment,',
            'conda code: conda install - c conda-forge utm',
            'pip code: pip install utm')

    try:
        import xarray as xr
    except ModuleNotFoundError as err_4:
        # Error handling
        print(
            str(err_4) +
            ' This package also requires extra dependencies like netCDF4, h5netcdf and possibly scipy')

    # %% Set path

    # path_req = input('Enter the input/output path here (w/o quotation marks) : ')
    path = 'F:/test'
    os.chdir(path)

    # %% Create functions

    def convert_flt_to_sci_not(fltt, prec, exp_digits):
        s = "%.*e" % (prec, fltt)
        # print(f's: {s}')
        if s == 'nan':
            s = "%.*e" % (prec, 0)  # TODO: is it a good idea to replace nan with 0?
        mantissa, exp = s.split('e')
        # add 1 to digits as 1 is taken by sign +/-
        return "%se%+0*d" % (mantissa, exp_digits + 1, int(exp))

    def convert_list_to_sci_not(input_list, prec, exp_digits):
        converted = []
        for flt in input_list:
            sci = convert_flt_to_sci_not(fltt=flt, prec=prec, exp_digits=exp_digits)
            converted.append(sci)

        return converted

    def add_blank_pos_val(input_str, length_integral):
        """Add leading blank for positive value. Add leading blanks for numbers with less digits
        in integral than specified."""
        length_integral_wo_sign = len(input_str.split('.')[0])
        # print(f'Initial length: {length_integral_wo_sign}')

        output_str = input_str
        # print(f'Unchanged string: {output_str}')
        # blank_for_pos_added = False

        # if input_str[:1] != '-':
        #     output_str = f' {input_str}'
        #     print(f'String after addition of blank for positive: {output_str}')
        #     blank_for_pos_added = True

        while length_integral_wo_sign < length_integral:
            output_str = f' {output_str}'
            length_integral_wo_sign = len(output_str.split('.')[0])

        return output_str

    def extract_data_for_loc(dataset, dataframe_loc, output_dict):
        for index, row in dataframe_loc.iterrows():
            dataset_sel = dataset.sel(lon=row['lon'], lat=row['lat'], method="nearest")
            dataset_2 = dataset_sel.to_numpy()  # convert to sci_not?
            output_dict[row['boundaries']].append(dataset_2)  # automise boundary selection

    def value_from_txt_file(file, string_name):
        file1 = open(file, "r")
        for line in file1:
            # checking string is present in line or not
            if '=' in line:
                if string_name in line:
                    val = line.split('=')
                    string_val = val[1].strip()
                    break
                    file1.close()  # close file
                else:
                    print('{} is not in the file'.format(string_name))
        return string_val

    def convert_float_fstr(float_list, decimal_digits):
        string_list = []
        for fltt in float_list:
            new_format = format(fltt, '.{}f'.format(decimal_digits))
            string_list.append(new_format)
        return string_list

    # %% Open input files
    bnd_loc = pd.read_csv(boundaries_wave, names=['boundary', 'easting', 'northing'], )

    data = xr.open_dataset(nc_file_wave)

    # %% Extract information from mdw file

    ref_date_unedited = start_time  # because reference time is not reference date
    ref_date_unedited = start_time.split(' ')[0]
    ref_date = ref_date_unedited.replace('-', '')

    # %% Generate the time steps for bcw
    min_data_time_step = 20  # The time resolution of easyGsh dataset
    bcw_time_start = 0.0  # the format accepted in bcw files
    one_time_step_bcw = float(step_wave)

    # %% Configuring time step to adhere to the coupling interval
    if one_time_step_bcw <= 20:
        time_step_data = int(1)
    elif one_time_step_bcw > 20:
        time_step_data = int(one_time_step_bcw / min_data_time_step)

    dataset = data.sel(nMesh2_data_time=slice(start_time, end_time, time_step_data))

    sig_height = dataset['Mesh2_face_signifikante_Wellenhoehe_2d']
    peak_period = dataset['Mesh2_face_Peak_Wellenperiode_2d']
    dir_spread = dataset['Mesh2_face_Richtungsaufweitung_der_Wellen_2d']
    wave_dir_x = dataset['Mesh2_face_Wellenrichtungsvektor_x_2d']
    wave_dir_y = dataset['Mesh2_face_Wellenrichtungsvektor_y_2d']

    # %% Convert to geographic coordinates

    easting = bnd_loc['easting']
    northing = bnd_loc['northing']
    bnd = bnd_loc['boundary']
    # converting to a numpy array to suit the module 'UTM'
    easting = easting.to_numpy(dtype='float64')
    northing = northing.to_numpy(dtype='float64')
    bnd_loc_geo = utm.to_latlon(easting, northing, 32, 'N')  # convert to utm
    bnd_loc_geo = pd.DataFrame(bnd_loc_geo)  # convert tuple to dataframe
    bnd_loc_geo = bnd_loc_geo.T  # transpose the dataframe
    bnd_loc_geo.columns = ['lat', 'lon']
    bnd_loc_geo['boundaries'] = bnd  # adding the boundary names

    # %% Extract nautical direction from X & Y components

    extracted_x_y_dict = {}  # pre allocate dict
    for index, row in bnd_loc_geo.iterrows():
        extracted_x_y_dict[row['boundaries']] = []  # Create keys for the dict

    # Extract data and store in the preallocated dict
    extract_data_for_loc(dataset=wave_dir_x, dataframe_loc=bnd_loc_geo,
                         output_dict=extracted_x_y_dict)
    extract_data_for_loc(dataset=wave_dir_y, dataframe_loc=bnd_loc_geo,
                         output_dict=extracted_x_y_dict)

    # Vectorise single value functions so they can handle arrays.
    tan_inverse = np.vectorize(math.atan2)
    rad_to_deg = np.vectorize(math.degrees)

    # Convert the components into directions
    direction_dict = {}
    for key, value in extracted_x_y_dict.items():
        x = extracted_x_y_dict[key][0]
        y = extracted_x_y_dict[key][1]
        # use negative y and x to get nautical directions (clockwise)
        direction_with_neg = (rad_to_deg(tan_inverse(-y, -x))) + 180
        direction_dict[key] = direction_with_neg

    # %% create the time list for the swan file

    total_time_steps = len(direction_with_neg)  # get the max number of datapoints
    time_stop_bcw = (one_time_step_bcw * total_time_steps)  # calculate end point
    float_range = np.arange(bcw_time_start, time_stop_bcw,
                            one_time_step_bcw).tolist()  # create a range of the input time

    # convert the time list into the swan format that is '.2f'
    time_swan = convert_float_fstr(float_list=float_range, decimal_digits=2)

    # %% Extract other datasets

    extracted_dataset_dict = {}
    for index, row in bnd_loc_geo.iterrows():
        extracted_dataset_dict[row['boundaries']] = []  # Create keys for the dict

    extract_data_for_loc(dataset=sig_height, dataframe_loc=bnd_loc_geo,
                         output_dict=extracted_dataset_dict)

    extract_data_for_loc(dataset=peak_period, dataframe_loc=bnd_loc_geo,
                         output_dict=extracted_dataset_dict)

    extract_data_for_loc(dataset=dir_spread, dataframe_loc=bnd_loc_geo,
                         output_dict=extracted_dataset_dict)

    # %% delete the b values from the dictionary

    for k in list(extracted_dataset_dict.keys()):
        if k.split('_')[1] == 'b':
            del extracted_dataset_dict[k]

    # %% convert to swan format and to strings

    converted_dataset_dict = {}
    for key, value in extracted_dataset_dict.items():
        converted_dataset_dict[key] = []
        sig_height = extracted_dataset_dict[key][0]
        peak_period = extracted_dataset_dict[key][1]
        dir_spread = extracted_dataset_dict[key][2]
        # convert to swan format string
        converted_dataset_dict[key].append(convert_float_fstr(
            float_list=float_range, decimal_digits=2))
        converted_dataset_dict[key].append(
            convert_float_fstr(float_list=sig_height, decimal_digits=4))
        converted_dataset_dict[key].append(convert_float_fstr(
            float_list=peak_period, decimal_digits=4))
        converted_dataset_dict[key].append(convert_float_fstr(
            float_list=direction_dict[key], decimal_digits=4))
        converted_dataset_dict[key].append(
            convert_float_fstr(float_list=dir_spread, decimal_digits=4))

    # %% write the bcw file

    # calculate the length integral for time column

    length_integral_val = len((str(time_stop_bcw).split('.')[0]))

    try:
        os.remove(bcw_file_name)
    except FileNotFoundError:
        pass

    # records_in_table = 20  # TODO

    for key in converted_dataset_dict:
        bn_name = str(key)
        header_lines = [
            "location             '{}                 '".format(bn_name.split('_')[0]),
            "time-function        'non-equidistant'",
            "reference-time       {}".format(ref_date),
            "time-unit            'minutes'",
            "interpolation        'linear'",
            "parameter            'time                  '                   unit '[min]'",
            "parameter            'WaveHeight'                               unit '[m]'",
            "parameter            'Period'                                   unit '[s]'",
            "parameter            'Direction'                                unit '[N^o]'",
            "parameter            'DirSpreading'                             unit '[-]'"]
        # TODO: Check if DirSpreading is actually cosine or directional standard deviation

        with open(bcw_file_name, 'a', newline='') as f:
            for one_line in header_lines:
                f.write(one_line)
                # f.write('\r\n')
                f.write('\n')

            csv_writer = csv.writer(f, lineterminator='\n')  # lineterminator avoids carriage return
            count = 0
            bnd_data_list = converted_dataset_dict[key]
            for row in bnd_data_list[0]:
                # if count < 10:  # TODO: Remove this line after testing
                # Set values to write, add leading blank for positive values
                # TODO: Adapt for longer periods
                time_val = add_blank_pos_val(
                    input_str=bnd_data_list[0][count], length_integral=length_integral_val)
                sig_height = add_blank_pos_val(input_str=bnd_data_list[1][count], length_integral=2)
                peak_period = add_blank_pos_val(
                    input_str=bnd_data_list[2][count], length_integral=2)
                direction = add_blank_pos_val(input_str=bnd_data_list[3][count], length_integral=4)
                dir_spread = add_blank_pos_val(input_str=bnd_data_list[4][count], length_integral=3)

                # Generate row content as single string
                row_str = f'{time_val} {sig_height} {peak_period} {direction} {dir_spread}'

                # Write row to file
                csv_writer.writerow([row_str])

                count += 1
