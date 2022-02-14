""" Combine modules to extract coordinates of boundaries and then extract water level information
for the same.
and wave data : significant height, direction , peak period, directional spread"""

# Notes to self:
# Usually (?) N corresponds to +/-x, M corresponds to +/-y
# ETA = n. There are 2*N ETA records in total:
# 1st set of N ETA records contains M x coordinates, 2nd contains M y coordinates
# just trying pycharm

import output_methods
import extract_from_d3d_files
import os
import time
import bct_generator
import bcw_generator
if __name__ == '__main__':

    t = time.time()  # start the time counter

    # %% Input data process 1
    path_req = input('Enter the input/output path here (w/o quotation marks) : ')
    path = path_req  # 'F:/test'
    os.chdir(path)
    print("Please read carefully the input criteria, ",
          " and choose which file you would like")

    req = input("For both files(1), for bct(2), for bcw(3) and for bnd_loc.csv(4) : ")
    choice = float(req)

    if choice == 1:
        print("Please read carefully the input criteria, ",
              " some are for the wave grid while some for flow")

        grid_req = input('Enter name of the Flow grid file : ')
        grid_input = grid_req

        bnd_req = input('Enter name of the Flow bnd file : ')
        bnd_input = bnd_req

        grid_wave_req = input('Enter name of the Wave grid file : ')
        grid_wave_input = grid_wave_req

        bnd_wave_req = input('Enter name of the Wave bnd file : ')
        bnd_wave_input = bnd_wave_req

        nc_file_req = input('Enter the NetCDF file name : ')
        nc_file = nc_file_req  # '2015_1000m_waterlevel_2D.nc'

        mdf_file_req = input('Enter the mdf file name : ')
        mdf_file = mdf_file_req  # 'test.mdf'

        nc_file_wave_req = input('Enter the NetCDF file name : ')
        nc_file_wave = nc_file_wave_req  # '2015_1000m_wave_2D.nc'

        mdw_file_req = input('Enter the mdw file name : ')
        mdw_file = mdw_file_req  # 'test.mdw'

        start_time_req = input(
            'Enter the simulation start time in the format YYYY-mm-dd HH:MM:SS : ')
        start_time = start_time_req  # '2015-03-01 00:00:00'
        # TODO: automate extraction # this is used to slice the nc_file

        end_time_req = input('Enter the simulation end time in the format YYYY-mm-dd HH:MM:SS : ')
        end_time = end_time_req  # '2015-03-14 00:00:00'
        # TODO: automate extraction # this is used to slice the nc_file

        step_req = input(
            'Enter time step to extract data (max resolution is 20 mins) format 20 : ')
        step = float(step_req)  # 2.0000000e+001  # 20 minute step # max resolution for gsh data

        step_wave_req = input(
            'Enter time step to extract WAVE data (max resolution is 20 mins, should be multiples of 20) format 20 : ')

        # 2.0000000e+001  # 20 minute step # max resolution for gsh data
        step_wave = float(step_wave_req)

        # %% output files
        name_with_dot = mdf_file.partition('.')  # Use mdf file to extract bct file and output file
        name_until_dot = name_with_dot[0]
        bct_file_name = '{}.bct'.format(name_until_dot)
        path_out_file = '{}.csv'.format(name_until_dot)

        # Use mdf file to extract bct file and output file
        wave_name_with_dot = mdw_file.partition('.')
        wave_name_until_dot = wave_name_with_dot[0]
        bcw_file = '{}.bcw'.format(wave_name_until_dot)
        wave_path_out_file = '{}.csv'.format(wave_name_until_dot)

        # %% Create the csv file for flow boundaries
        bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(path_bnd=bnd_input)

        coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_input,
            request_list=bnd_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)

        print('The process of creating',
              ' the boundary location csv file for flow is completed')

        # %% Create the csv file for wave boundaries
        bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
            path_bnd=bnd_wave_input)

        coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_wave_input,
            request_list=bnd_wave_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)

        print('The process of creating',
              ' the boundary location csv file for Wave is completed')

        # %% Create the bct file
        boundaries = path_out_file  # the csv file generated from process one
        bct = bct_generator.bct_file_generator(
            boundaries=boundaries, nc_file=nc_file, mdf_file=mdf_file, start_time=start_time, end_time=end_time, step=step,
            bct_file_name=bct_file_name)

        # %% end the time counter
        print('The process of extracting water level has now completed in : ')
        elapsed = time.time() - t
        print(str(elapsed) + " sec")

        # %% Create the bcw file
        boundaries_wave = wave_path_out_file
        bcw = bcw_generator.bcw_file_generator(
            boundaries_wave=boundaries_wave, nc_file_wave=nc_file_wave, mdw_file=mdw_file, start_time=start_time,
            end_time=end_time, step_wave=step_wave, bcw_file_name=bcw_file)

        # %%
        print('The process of extracting wave boundary conditions has now completed in : ')
        elapsed = time.time() - t
        print(str(elapsed) + " sec")

    elif choice == 2:
        grid_req = input('Enter name of the Flow grid file : ')
        grid_input = grid_req

        bnd_req = input('Enter name of the Flow bnd file : ')
        bnd_input = bnd_req

        nc_file_req = input('Enter the NetCDF file name : ')
        nc_file = nc_file_req  # '2015_1000m_waterlevel_2D.nc'

        mdf_file_req = input('Enter the mdf file name : ')
        mdf_file = mdf_file_req  # 'test.mdf'

        start_time_req = input(
            'Enter the simulation start time in the format YYYY-mm-dd HH:MM:SS : ')
        start_time = start_time_req  # '2015-03-14 00:00:00'
        # TODO: automate extraction # this is used to slice the nc_file

        end_time_req = input('Enter the simulation end time in the format YYYY-mm-dd HH:MM:SS : ')
        end_time = end_time_req  # '2015-02-14 00:00:00'
        # TODO: automate extraction # this is used to slice the nc_file

        step_req = input(
            'Enter time step to extract data (max resolution is 20mins) format 20 : ')
        step = float(step_req)  # 20 minute step # max resolution for gsh data

        # %% output files
        name_with_dot = mdf_file.partition('.')  # Use mdf file to extract bct file and output file
        name_until_dot = name_with_dot[0]
        bct_file_name = '{}.bct'.format(name_until_dot)
        path_out_file = '{}.csv'.format(name_until_dot)

        # %% Create the csv file for flow boundaries
        bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(path_bnd=bnd_input)

        coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_input,
            request_list=bnd_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)

        print('The process of creating',
              ' the boundary location csv file for flow is completed')

        # %% Create the bct file
        boundaries = path_out_file  # the csv file generated from process one
        bct = bct_generator.bct_file_generator(
            boundaries=boundaries, nc_file=nc_file, mdf_file=mdf_file, start_time=start_time, end_time=end_time, step=step,
            bct_file_name=bct_file_name)

        # %% end the time counter
        print('The process of extracting water level has now completed in : ')
        elapsed = time.time() - t
        print(str(elapsed) + " sec")

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
        start_time = start_time_req  # '2015-03-01 00:00:00'
        # TODO: automate extraction # this is used to slice the nc_file

        end_time_req = input('Enter the simulation end time in the format YYYY-mm-dd HH:MM:SS : ')
        end_time = end_time_req  # '2015-03-14 00:00:00'
        # TODO: automate extraction # this is used to slice the nc_file

        step_wave_req = input(
            'Enter time step to extract WAVE data (max resolution is 20mins, should be multiples of 20) format 20 : ')

        # 2.0000000e+001  # 20 minute step # max resolution for gsh data
        step_wave = float(step_wave_req)

        # %% bcw output file
        # Use mdf file to extract bct file and output file
        wave_name_with_dot = mdw_file.partition('.')
        wave_name_until_dot = wave_name_with_dot[0]
        bcw_file = '{}.bcw'.format(wave_name_until_dot)
        wave_path_out_file = '{}.csv'.format(wave_name_until_dot)

        # %% Create the csv file for wave boundaries
        bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
            path_bnd=bnd_wave_input)

        coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_wave_input,
            request_list=bnd_wave_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)

        print('The process of creating',
              ' the boundary location csv file for wave is completed')

        # %% Create the bcw file
        boundaries_wave = wave_path_out_file
        bcw = bcw_generator.bcw_file_generator(
            boundaries_wave=boundaries_wave, nc_file_wave=nc_file_wave, mdw_file=mdw_file, start_time=start_time,
            end_time=end_time, step_wave=step_wave, bcw_file_name=bcw_file)

        # %%
        print('The process of extracting wave boundary conditions has now completed in : ')
        elapsed = time.time() - t
        print(str(elapsed) + " sec")

    elif choice == 4:
        grid_req = input('Enter name of the grid file : ')
        grid_input = grid_req

        bnd_req = input('Enter name of the bnd file : ')
        bnd_input = bnd_req

        # Use grid file to extract bct file and output file
        wave_name_with_dot = grid_input.partition('.')
        wave_name_until_dot = wave_name_with_dot[0]
        wave_path_out_file = '{}.csv'.format(wave_name_until_dot)

        # %% Create the csv file for wave boundaries
        bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
            path_bnd=bnd_input)

        coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
            path_grd=grid_input,
            request_list=bnd_wave_grd_indices_output)

        output_methods.write_bnd_coord_ascii(
            bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)

        print('The process of creating',
              ' the boundary location csv file is completed')
    else:
        print("You probably din't insert the number right, Please run again! ")
