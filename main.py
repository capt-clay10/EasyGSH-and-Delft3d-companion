"""RUN THIS FILE"""
# %% import modules
import output_methods
import extract_from_d3d_files
import os
import time
import bct_generator
import bcw_generator
import mdw_writer
from datetime import datetime
from datetime import timedelta


if __name__ == '__main__':

    t = time.time()  # start the time counter

    # %% Input data process 1
    path_req = input('Enter the input/output path here (w/o quotation marks) : ')
    path = path_req  # 'F:/test'
    os.chdir(path)
    print('.')
    print('.')
    print('.')
    print("Please read carefully the input criteria",
          "and choose which file you would like")
    print()
    print('Type of files offered:',
          'For all files, type 1',
          'For bct file, type 2',
          'For bcw file, type 3',
          'For boundary location csv file, type 4',
          'For boundary location and mdw file, type 5', sep='\n')
    print()
    req = input("Enter number : ")
    print('.')
    print('.')
    print('.')
    choice = float(req)
    # %% CHOICE 1
    if choice == 1:
        # load time extracting function
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
                    # else:
                        # print('{} is not in the file'.format(string_name))
            return string_val

        print("Please read carefully the input criteria,",
              "some requests are for the wave grid while some for flow")

        grid_req = input('Enter name of the Flow grid file : ')
        grid_input = grid_req

        bnd_req = input('Enter name of the Flow bnd file : ')
        bnd_input = bnd_req

        grid_wave_req = input('Enter name of the Wave grid file : ')
        grid_wave_input = grid_wave_req

        bnd_wave_req = input('Enter name of the Wave bnd file : ')
        bnd_wave_input = bnd_wave_req

        nc_file_req = input('Enter the Water level NetCDF file name : ')
        nc_file = nc_file_req  # '2015_1000m_waterlevel_2D.nc'

        mdf_file_req = input('Enter the mdf file name : ')
        mdf_file = mdf_file_req  # 'test.mdf'

        nc_file_wave_req = input('Enter the Wave NetCDF file name : ')
        nc_file_wave = nc_file_wave_req  # '2015_1000m_wave_2D.nc'

        mdw_file_req = input('Enter the mdw file name : ')
        mdw_file = mdw_file_req  # 'test.mdw'

        # request for time step
        step_req = input(
            'Enter time step to extract water level data (max resolution is 20 mins) format 20 : ')
        step = float(step_req)  # 2.0000000e+001  # 20 minute step # max resolution for gsh data

        step_wave_req = input(
            'Enter time step to extract WAVE data (max resolution is 20 mins, should be multiples of 20) format 20 : ')
        step_wave = float(step_wave_req)

        # Extract start and end time from mdf file
        string1 = 'Tstart'
        tstart_val = value_from_txt_file(file=mdf_file, string_name=string1)
        string2 = 'Tstop'
        tstop_val = value_from_txt_file(file=mdf_file, string_name=string2)
        string3 = 'Itdate'  # reference time
        ref_time_unedited = value_from_txt_file(file=mdf_file, string_name=string3)
        start = float(tstart_val)  # from mdf file
        stop = float(tstop_val)  # from mdf file
        ref_time = ref_time_unedited[1:11]
        reference_time = ref_time.replace('-', '')  # remove the hyphen for the bct file format
        # extract start time and end time from mdf
        time_start = ref_time+" 00:00:00"  # Assuming it always starts at 00
        date_format_str = "%Y-%m-%d %H:%M:%S"
        # Calculate number of hours between ref time and sim time
        start_time_steps = int(start/60)  # to convert minutes to hours
        end_time_steps = int(stop/60)
        # create datetime object from timestamp string
        extracted_time = datetime.strptime(time_start, date_format_str)
        start_time = extracted_time + timedelta(hours=start_time_steps)
        # Convert datetime object to string in specific format
        start_time = start_time .strftime("%Y-%m-%d %H:%M:%S")
        end_time = extracted_time + timedelta(hours=end_time_steps)
        end_time = end_time .strftime("%Y-%m-%d %H:%M:%S")
        print('.')
        print('.')
        print('.')
        print('.')
        print("1 of 6")
        # %% output files
        # Use mdf file to extract bct file name and output file
        name_with_dot = mdf_file.partition('.')
        name_until_dot = name_with_dot[0]
        bct_file_name = '{}.bct'.format(name_until_dot)
        path_out_file = '{}.csv'.format(name_until_dot)

        # Use mdw file to extract bcw file name and output file
        wave_name_with_dot = mdw_file.partition('.')
        wave_name_until_dot = wave_name_with_dot[0]
        bcw_file = '{}.bcw'.format(wave_name_until_dot)
        wave_path_out_file = '{}.csv'.format(wave_name_until_dot)
        print('.')
        print("2 of 6")
        print('.')
        print('.')
        # %% Create the csv file for flow boundaries
        bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(path_bnd=bnd_input)

        coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_input,
            request_list=bnd_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)
        print('.')
        print('.')
        print('.')
        print('The process of creating',
              'the boundary location csv file for flow is completed - 3 of 6')
        print('.')
        print('.')
        print('.')

        # %% Create the csv file for wave boundaries
        bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
            path_bnd=bnd_wave_input)

        coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_wave_input,
            request_list=bnd_wave_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)
        print('.')
        print('.')
        print('.')
        print('The process of creating',
              ' the boundary location csv file for Wave is completed - 4 of 6')

        # %% Create the bct file
        boundaries = path_out_file  # the csv file generated from process one
        bct = bct_generator.bct_file_generator(
            boundaries=boundaries, nc_file=nc_file, mdf_file=mdf_file, step=step,
            bct_file_name=bct_file_name)

        t_2 = time.time()

        # %% end the time counter
        print('.')
        print('The process of extracting water level has now completed in : ')
        elapsed = time.time() - t
        print(str(elapsed) + " sec - 5 of 6")

        # %% Create the bcw file
        boundaries_wave = wave_path_out_file
        bcw = bcw_generator.bcw_file_generator(
            boundaries_wave=boundaries_wave, nc_file_wave=nc_file_wave, mdw_file=mdw_file, start_time=start_time,
            end_time=end_time, step_wave=step_wave, bcw_file_name=bcw_file)

        print('.')
        print('The process of extracting wave boundary conditions has now completed in : ')
        elapsed = time.time() - t_2
        print(str(elapsed) + " sec - 6 of 6")
        print('.')
        print('.')
        print('.')
        # %% Write the new mdw file
        mdw_writer.write_mdw_file(mdw_file=mdw_file, boundaries_wave=boundaries_wave)
        print('New mdw file created')
        print('.')
        elapsed_final = time.time() - t
        print(f'Total time taken for both files is {elapsed_final/60} mins')

    # %% CHOICE 2
    elif choice == 2:
        grid_req = input('Enter name of the Flow grid file : ')
        grid_input = grid_req

        bnd_req = input('Enter name of the Flow bnd file : ')
        bnd_input = bnd_req

        nc_file_req = input('Enter the NetCDF file name : ')
        nc_file = nc_file_req  # '2015_1000m_waterlevel_2D.nc'

        mdf_file_req = input('Enter the mdf file name : ')
        mdf_file = mdf_file_req  # 'test.mdf'

        step_req = input(
            'Enter time step to extract data (max resolution is 20mins) format 20 : ')
        step = float(step_req)  # 20 minute step # max resolution for gsh data

        # %% output files
        name_with_dot = mdf_file.partition('.')  # Use mdf file to extract bct file and output file
        name_until_dot = name_with_dot[0]
        bct_file_name = '{}.bct'.format(name_until_dot)
        path_out_file = '{}.csv'.format(name_until_dot)
        print('.')
        print("1 of 3")

        # %% Create the csv file for flow boundaries
        bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(path_bnd=bnd_input)

        coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_input,
            request_list=bnd_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)
        print('.')
        print('.')
        print('.')
        print('The process of creating',
              'the boundary location csv file for flow is completed - 2 of 3')

        # %% Create the bct file
        boundaries = path_out_file  # the csv file generated from process one
        bct = bct_generator.bct_file_generator(
            boundaries=boundaries, nc_file=nc_file, mdf_file=mdf_file, step=step,
            bct_file_name=bct_file_name)

        # %% end the time counter
        print('.')
        print('The process of extracting water level has now completed in : ')
        elapsed = time.time() - t
        print(str(elapsed) + " sec - 3 of 3")
    # %% CHOICE 3
    elif choice == 3:
        # %% BCW section input files
        grid_wave_req = input('Enter name of the Wave grid file : ')
        grid_wave_input = grid_wave_req

        bnd_wave_req = input('Enter name of the Wave bnd file : ')
        bnd_wave_input = bnd_wave_req

        nc_file_wave_req = input('Enter the NetCDF file name : ')
        nc_file_wave = nc_file_wave_req  # '2015_1000m_wave_2D.nc'

        mdw_file_req = input('Enter the mdw file name : ')
        mdw_file = mdw_file_req  # 'test.mdw'

        start_time_req = input(
            'Enter the simulation start time in the format YYYY-mm-dd HH:MM:SS : ')
        start_time = start_time_req  # '2015-02-01 00:00:00'

        end_time_req = input('Enter the simulation end time in the format YYYY-mm-dd HH:MM:SS : ')
        end_time = end_time_req  # '2015-03-14 00:00:00'

        step_wave_req = input(
            'Enter time step to extract WAVE data (max resolution is 20mins, should be multiples of 20) format 20 : ')

        # 2.0000000e+001  # 20 minute step # max resolution for gsh data
        step_wave = float(step_wave_req)

        # %% bcw output file
        # Use mdw file to extract bcw file and output file
        wave_name_with_dot = mdw_file.partition('.')
        wave_name_until_dot = wave_name_with_dot[0]
        bcw_file = '{}.bcw'.format(wave_name_until_dot)
        wave_path_out_file = '{}.csv'.format(wave_name_until_dot)
        print('.')
        print("1 of 3")

        # %% Create the csv file for wave boundaries
        bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
            path_bnd=bnd_wave_input)

        coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_wave_input,
            request_list=bnd_wave_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)
        print('.')
        print('.')
        print('.')
        print('The process of creating',
              ' the boundary location csv file for wave is completed - 2 of 3')
        print('.')
        print('.')
        print('.')
        print('Initiating wave parameter extraction')

        # %% Create the bcw file
        boundaries_wave = wave_path_out_file
        bcw = bcw_generator.bcw_file_generator(
            boundaries_wave=boundaries_wave, nc_file_wave=nc_file_wave, mdw_file=mdw_file, start_time=start_time,
            end_time=end_time, step_wave=step_wave, bcw_file_name=bcw_file)
        print('.')
        print('The process of extracting wave boundary conditions has now completed in : ')
        elapsed = time.time() - t
        print(str(elapsed) + " sec - 3 of 3")
        print('.')
        print('.')
        # %% Write the new mdw file
        mdw_writer.write_mdw_file(mdw_file=mdw_file, boundaries_wave=boundaries_wave)
        print('New mdw file created')
    # %% CHOICE 4
    elif choice == 4:
        grid_req = input('Enter name of the grid file : ')
        grid_input = grid_req

        bnd_req = input('Enter name of the bnd file : ')
        bnd_input = bnd_req

        # Use grid file to extract bct file and output file
        wave_name_with_dot = grid_input.partition('.')
        wave_name_until_dot = wave_name_with_dot[0]
        wave_path_out_file = '{}.csv'.format(wave_name_until_dot)
        print('.')
        print("1 of 2")

        # %% Create the csv file for wave boundaries
        bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
            path_bnd=bnd_input)

        coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_input,
            request_list=bnd_wave_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)
        print('.')
        print('.')
        print('.')
        print('The process of creating',
              ' the boundary location csv file is completed - 2 of 2')
    elif choice == 5:
        grid_req = input('Enter name of the grid file : ')
        grid_input = grid_req

        bnd_req = input('Enter name of the bnd file : ')
        bnd_input = bnd_req

        mdw_file_req = input('Enter the mdw file name : ')
        mdw_file = mdw_file_req  # 'test.mdw'

        # Use grid file to extract bct file and output file
        wave_name_with_dot = grid_input.partition('.')
        wave_name_until_dot = wave_name_with_dot[0]
        wave_path_out_file = '{}.csv'.format(wave_name_until_dot)
        print('.')
        print("1 of 3")

        # %% Create the csv file for wave boundaries
        bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
            path_bnd=bnd_input)

        coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_input,
            request_list=bnd_wave_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)
        print('.')
        print('.')
        print('.')
        print('The process of creating',
              ' the boundary location csv file is completed - 2 of 3')

        # %% create mdw file
        boundaries_wave = wave_path_out_file
        mdw_writer.write_mdw_file(mdw_file=mdw_file, boundaries_wave=boundaries_wave)
        print('New mdw file created')

    else:
        print("You probably din't insert the number right, Please run again! ")
