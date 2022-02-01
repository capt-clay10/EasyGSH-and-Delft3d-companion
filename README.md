# bct_file_generator_for_EasyGSH
The aim is to extract timeseries water level 2D information for any designed boundaries within the EasyGSH website (under the synoptic simulation, UnTRIM22, 1000m grid section.)
As of now it is a two part process

The first process requires the .bnd file and .grd file that one can generate from the Delft3D GUI
In this process the real world coordinates are extracted from these files and exported as a .csv file

The second process requires the mdf file, the waterlevel netcdf file from easygsh and the csv file created from process one.
This part generates the .bct file in the same name as the mdf file. As an overview this process uses the xarray module to select and extract the water level data , where the locations are specified by the process one csv file. The data is then stored in lists with the boundary name as keys, which is then looped with the header information and written in the required .bct format. 

Please run just the main.py file for results.
