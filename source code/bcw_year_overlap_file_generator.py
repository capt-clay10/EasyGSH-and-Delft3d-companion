# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 09:41:46 2023

@author: AG-Admin
"""

# -*- coding: utf-8 -*-
"""
The function to extract wave data from the netcdf file and create a bcw file
"""


def bcw_year_overlap_file_generator(
        boundaries_wave, nc_file_wave_year1, nc_file_wave_year2, mdw_file, start_time, end_time, step_wave, bcw_file_name):
    # %% Import packages
    from datetime import timedelta
    from datetime import datetime
    import pandas as pd
    import numpy as np
    import os
    import csv
    import math
    import statistics as st
    import utm
    import xarray as xr
    from scipy import interpolate

    # %% Create functions

    def convert_flt_to_sci_not(fltt, prec, exp_digits):
        s = "%.*e" % (prec, fltt)
        # print(f's: {s}')
        if s == 'nan':
            # TODO: is it a good idea to replace nan with 0?
            s = "%.*e" % (prec, 0)
        mantissa, exp = s.split('e')
        # add 1 to digits as 1 is taken by sign +/-
        return "%se%+0*d" % (mantissa, exp_digits + 1, int(exp))

    def convert_list_to_sci_not(input_list, prec, exp_digits):
        converted = []
        for flt in input_list:
            sci = convert_flt_to_sci_not(
                fltt=flt, prec=prec, exp_digits=exp_digits)
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

    def extract_data_for_loc(dataset_1, dataset_2,  dataframe_loc, output_dict):
        for index, row in dataframe_loc.iterrows():
            attri = dataset_1
            dataset_1_sel = dataset_1.sel(
                lon=row['lon'], lat=row['lat'], method="nearest")
            data_1 = dataset_1_sel.to_numpy()

            dataset_2_sel = dataset_2.sel(
                lon=row['lon'], lat=row['lat'], method="nearest")
            data_2 = dataset_2_sel.to_numpy()

            dataset_combine = np.concatenate([data_1, data_2])

            bnd_name = bnd_loc_geo.iloc[index, 2]
            nan = 0
            for j in dataset_combine:

                if np.isnan(j):
                    nan += 1
                elif not np.isnan(j):
                    nan = nan

            if nan > 2 and bnd_name[-1] != 'b':
                print(
                    f'Nan value present in {bnd_name[0:-2]} {nan} times in {attri.attrs["long_name"][0:-9]}')
            mean = np.nanmean(dataset_combine)
            dataset_combine = np.nan_to_num(dataset_combine, nan=mean)
            output_dict[row['boundaries']].append(dataset_combine)

    def extract_dir_data_for_loc(dataset_1, dataset_2, dataframe_loc, output_dict):

        for index, row in dataframe_loc.iterrows():
            bnd_name = bnd_loc_geo.iloc[index, 2]

            attri = dataset_1
            dataset_1_sel = dataset_1.sel(
                lon=row['lon'], lat=row['lat'], method="nearest")
            data_1 = dataset_1_sel.to_numpy()

            dataset_2_sel = dataset_2.sel(
                lon=row['lon'], lat=row['lat'], method="nearest")
            data_2 = dataset_2_sel.to_numpy()

            dataset_combine = np.concatenate([data_1, data_2])

            # Identify nan values and print them
            nan = 0
            for j in dataset_combine:

                if np.isnan(j) or j == - 0.017452405765652657 or j == 0.9998477101325989:
                    nan += 1
                elif not np.isnan(j):
                    nan = nan

            if nan > 2 and bnd_name[-1] != 'b':
                print(
                    f'Nan value present in '
                    f'{bnd_name[0:-2]} {nan} times in {attri.attrs["long_name"][0:-9]}')

            # treating the nan
            if np.count_nonzero(np.isnan(dataset_combine)) == len(dataset_combine):
                to_calculate_1 = dataset_combine[~(np.isnan(dataset_combine))]
                replace = np.mean(to_calculate_1)
            elif np.count_nonzero(np.isnan(dataset_combine)) < (len(dataset_combine)):
                to_calculate_1 = dataset_combine[~(np.isnan(dataset_combine))]
                replace = st.mode(to_calculate_1)  # Claculate mode

            dataset_combine = np.nan_to_num(dataset_combine, nan=replace)

            # Replace not nan but empty numbers with mode of the dataset
            for i in dataset_combine:
                if i == -0.017452405765652657:  # one of those empty values
                    to_calculate = dataset_combine[np.where(
                        dataset_combine != -0.017452405765652657)]
                    # median = np.median(to_calculate)
                    mode = st.mode(to_calculate)
                    # mean_1 = np.mean(dataset_2, where=(dataset_2 != -0.017452405765652657))
                    dataset_combine = np.where((dataset_combine > -0.01745242) &
                                               (dataset_combine < -0.01745240), mode, dataset_combine)
                    # output_dict[row['boundaries']].append(dataset_3)  # automise boundary selection
                elif i == 0.9998477101325989:
                    to_calculate = dataset_combine[np.where(
                        dataset_combine != 0.9998477101325989)]
                    # median = np.median(to_calculate)
                    mode = st.mode(to_calculate)
                    # mean_1 = np.mean(dataset_2, where=(dataset_2 != 0.9998477101325989))
                    dataset_combine = np.where((dataset_combine > 0.99984) & (
                        dataset_combine < 0.99985), mode, dataset_combine)

            output_dict[row['boundaries']].append(
                dataset_combine)  # automise boundary selection

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

    print(".")
    # %% Open input files
    bnd_loc = pd.read_csv(boundaries_wave, names=[
                          'boundary', 'easting', 'northing'], )

    data_1 = xr.open_dataset(nc_file_wave_year1)

    # extract the end of the first dataset
    end_data_1 = data_1.nMesh2_data_time[-1]

    data_2 = xr.open_dataset(nc_file_wave_year2)

    print(".")

    # %% Extract information from mdw file

    ref_date_unedited = start_time  # because reference time is not reference date
    ref_date_unedited = start_time.split(' ')[0]
    ref_date = ref_date_unedited.replace('-', '')
    print(".")

    # %% Generate the time steps for bcw
    min_data_time_step = 20  # The time resolution of easyGsh dataset
    bcw_time_start = 0.0  # the format accepted in bcw files
    one_time_step_bcw = float(step_wave)
    print(".")
    # %% Configuring time step to adhere to the coupling interval
    if one_time_step_bcw <= 20:
        time_step_data = int(1)
    elif one_time_step_bcw > 20:
        time_step_data = int(one_time_step_bcw / min_data_time_step)
    print(".")
    # %% Correcting for 12 hour time difference in gsh

    time_start = start_time
    time_end = end_time
    date_format_str = "%Y-%m-%d %H:%M:%S"

    # create datetime object from timestamp string
    extracted_time = datetime.strptime(time_start, date_format_str)
    n = -12  # Set the observed time to be one hour back

    start_time_lag = extracted_time + timedelta(hours=n)

    # Convert datetime object to string in specific format
    start_time_lag = start_time_lag.strftime("%Y-%m-%d %H:%M:%S")

    ##
    # create datetime object from timestamp string
    extracted_time = datetime.strptime(time_end, date_format_str)

    end_time_lag = extracted_time + timedelta(hours=n)

    # Convert datetime object to string in specific format
    end_time_lag = end_time_lag.strftime("%Y-%m-%d %H:%M:%S")

    # %% openning two datasets

    dataset_1 = data_1.sel(nMesh2_data_time=slice(
        start_time_lag, end_data_1, time_step_data))

    sig_height_1 = dataset_1['Mesh2_face_signifikante_Wellenhoehe_2d']
    peak_period_1 = dataset_1['Mesh2_face_Peak_Wellenperiode_2d']
    dir_spread_1 = dataset_1['Mesh2_face_Richtungsaufweitung_der_Wellen_2d']
    wave_dir_x_1 = dataset_1['Mesh2_face_Wellenrichtungsvektor_x_2d']
    wave_dir_y_1 = dataset_1['Mesh2_face_Wellenrichtungsvektor_y_2d']

    dataset_2 = data_2.sel(nMesh2_data_time=slice(
        end_data_1, end_time_lag, time_step_data))

    sig_height_2 = dataset_2['Mesh2_face_signifikante_Wellenhoehe_2d']
    peak_period_2 = dataset_2['Mesh2_face_Peak_Wellenperiode_2d']
    dir_spread_2 = dataset_2['Mesh2_face_Richtungsaufweitung_der_Wellen_2d']
    wave_dir_x_2 = dataset_2['Mesh2_face_Wellenrichtungsvektor_x_2d']
    wave_dir_y_2 = dataset_2['Mesh2_face_Wellenrichtungsvektor_y_2d']

    print("Time lag for bcw corrected")
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
    print(".")
    # %% Extract nautical direction from X & Y components

    extracted_x_y_dict = {}  # pre allocate dict
    for index, row in bnd_loc_geo.iterrows():
        extracted_x_y_dict[row['boundaries']] = []  # Create keys for the dict

    # %% test

    # %% calculate nautical wave direction

    # Extract data and store in the preallocated dict
    extract_dir_data_for_loc(dataset_1=wave_dir_x_1, dataset_2=wave_dir_x_2,  dataframe_loc=bnd_loc_geo,
                             output_dict=extracted_x_y_dict)
    extract_dir_data_for_loc(dataset_1=wave_dir_y_1, dataset_2=wave_dir_y_2, dataframe_loc=bnd_loc_geo,
                             output_dict=extracted_x_y_dict)

    # Vectorise single value functions so they can handle arrays.
    tan_inverse = np.vectorize(math.atan2)
    rad_to_deg = np.vectorize(math.degrees)

    # Convert the components into directions
    direction_dict = {}
    for key, value in extracted_x_y_dict.items():
        x = extracted_x_y_dict[key][0]
        y = extracted_x_y_dict[key][1]

        df = (pd.DataFrame([x, y])).transpose()
        df.columns = ['x', 'y']

        result = []
        for index, row in df.iterrows():
            x = df['x'][index]
            y = df['y'][index]
            if x > 0 and y > 0:
                rad = math.atan2(x, y)
                deg = math.degrees(rad)
                result.append(deg)
            elif x > 0 and y < 0:
                rad = math.atan2(-y, x)
                deg = (math.degrees(rad)) + 90
                result.append(deg)
            elif x < 0 and y < 0:
                rad = math.atan2(-x, -y)
                deg = (math.degrees(rad)) + 180
                result.append(deg)
            elif x < 0 and y > 0:
                rad = math.atan2(y, -x)
                deg = (math.degrees(rad)) + 270
                result.append(deg)

        result_corrected = [(direction + 180) % 360 for direction in result]
        direction_with_neg = result_corrected
        direction_dict[key] = direction_with_neg

    print("Wave direction calculated from x-y components according to nautical convention")

    # %% create the time list for the swan file

    # get the max number of datapoints
    total_time_steps = len(direction_with_neg)
    # calculate end point
    time_stop_bcw = (one_time_step_bcw * total_time_steps)
    float_range = np.arange(bcw_time_start, time_stop_bcw,
                            one_time_step_bcw).tolist()  # create a range of the input time

    # convert the time list into the swan format that is '.2f'
    time_swan = convert_float_fstr(float_list=float_range, decimal_digits=2)
    print(".")
    # %% Extract other datasets

    extracted_dataset_dict = {}
    for index, row in bnd_loc_geo.iterrows():
        # Create keys for the dict
        extracted_dataset_dict[row['boundaries']] = []

    extract_data_for_loc(dataset_1=sig_height_1, dataset_2=sig_height_2, dataframe_loc=bnd_loc_geo,
                         output_dict=extracted_dataset_dict)

    extract_data_for_loc(dataset_1=peak_period_1, dataset_2=peak_period_2, dataframe_loc=bnd_loc_geo,
                         output_dict=extracted_dataset_dict)

    extract_data_for_loc(dataset_1=dir_spread_1, dataset_2=dir_spread_2, dataframe_loc=bnd_loc_geo,
                         output_dict=extracted_dataset_dict)
    print("Wave parameter datasets extracted")
    # %% delete the b values from the dictionary

    for k in list(extracted_dataset_dict.keys()):
        if k.split('_')[1] == 'b':
            del extracted_dataset_dict[k]
    print(".")
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

    print("Converted to Delft3D wave module format")
    print(".")
    print('Writing file')
    print(".")
    print(".")
    print(".")
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
            "location             '{}                 '".format(
                bn_name.split('_')[0]),
            "time-function        'non-equidistant'",
            "reference-time       {}".format(ref_date),
            "time-unit            'minutes'",
            "interpolation        'linear'",
            "parameter            'time                  '                   unit '[min]'",
            "parameter            'WaveHeight'                               unit '[m]'",
            "parameter            'Period'                                   unit '[s]'",
            "parameter            'Direction'                                unit '[N^o]'",
            "parameter            'DirSpreading'                             unit '[deg]'"]
        # TODO: Check if DirSpreading is actually cosine or directional standard deviation

        with open(bcw_file_name, 'a', newline='') as f:
            for one_line in header_lines:
                f.write(one_line)
                # f.write('\r\n')
                f.write('\n')

            # lineterminator avoids carriage return
            csv_writer = csv.writer(f, lineterminator='\n')
            count = 0
            bnd_data_list = converted_dataset_dict[key]
            for row in bnd_data_list[0]:
                # if count < 10:  # TODO: Remove this line after testing
                # Set values to write, add leading blank for positive values
                # TODO: Adapt for longer periods
                time_val = add_blank_pos_val(
                    input_str=bnd_data_list[0][count], length_integral=length_integral_val)
                sig_height = add_blank_pos_val(
                    input_str=bnd_data_list[1][count], length_integral=2)
                peak_period = add_blank_pos_val(
                    input_str=bnd_data_list[2][count], length_integral=2)
                direction = add_blank_pos_val(
                    input_str=bnd_data_list[3][count], length_integral=4)
                dir_spread = add_blank_pos_val(
                    input_str=bnd_data_list[4][count], length_integral=3)

                # Generate row content as single string
                row_str = f'{time_val} {sig_height} {peak_period} {direction} {dir_spread}'

                # Write row to file
                csv_writer.writerow([row_str])

                count += 1
