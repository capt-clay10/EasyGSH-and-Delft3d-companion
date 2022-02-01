"""Read DELFT3D grd and bnd file to extract coordinates for boundary start / end points ."""
# Notes to self:
# Usually (?) N corresponds to +/-x, M corresponds to +/-y
# ETA = n. There are 2*N ETA records in total:
# 1st set of N ETA records contains M x coordinates, 2nd contains M y coordinates

import output_methods
import extract_from_d3d_files
import os
import time
import bct_generator

t = time.time()


# %% Input data process 1
path_req = input('Enter the input/output path here (w/o quotation marks) : ')
path = path_req  # 'F:/test'
os.chdir(path)

grid_req = input('Enter name of the grid file : ')
grid_input = grid_req

bnd_req = input('Enter name of the bnd file : ')
bnd_input = bnd_req


# %% Input data process 2
# boundary_req = input('Enter the name of the csv file generated from process one : ')
# boundaries = boundary_req  # 'test.csv'  # File generated from the bnd coordinates script

nc_file_req = input('Enter the NetCDF file name : ')
nc_file = nc_file_req  # '2015_1000m_waterlevel_2D.nc'

mdf_file_req = input('Enter the mdf file name : ')
mdf_file = mdf_file_req  # 'test.mdf'

start_time_req = input('Enter the start time in the format YYYY-mm-dd HH:MM:SS : ')
start_time = start_time_req  # '2015-02-01 00:00:00'
# TODO: automate extraction # this is used to slice the nc_file

end_time_req = input('Enter the end time in the format YYYY-mm-dd HH:MM:SS : ')
end_time = end_time_req  # '2015-02-14 00:00:00'
# TODO: automate extraction # this is used to slice the nc_file

step_req = input(
    'Enter time step to extract data (max resolution is 20mins) format 20 : ')
step = float(step_req)  # 2.0000000e+001  # 20 minute step # max resolution for gsh data


# %% output file

name_with_dot = mdf_file.partition('.')  # Use mdf file to extract bct file and output file
name_until_dot = name_with_dot[0]
bct_file = '{}.bct'.format(name_until_dot)
path_out_file = '{}.csv'.format(name_until_dot)

# %% Create the csv file

bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(path_bnd=bnd_input)

coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(path_grd=grid_input,
                                                                              request_list=bnd_grd_indices_output)

output_methods.write_bnd_coord_ascii(
    bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)


# %% Create the bct file

boundaries = path_out_file  # the csv file generated from process one

bct = bct_generator.bct_file_generator(
    boundaries, nc_file, mdf_file, start_time, end_time, step, bct_file)

# %% end the time lapse
print('The process of extracting water level has now completed in : ')
elapsed = time.time() - t
print(str(elapsed) + " sec")
