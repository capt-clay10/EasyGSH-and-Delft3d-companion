# bct_bcw_file_generator_for_EasyGSH

This code creates files for the Delft3D module
1) To extract timeseries water level 2D information for any designed boundaries within the EasyGSH model domain  (data found under the synoptic simulation, UnTRIM22, 1000m grid section.)
2) To extract time series wave/Sea-state data 2D (significant height, peak period, direction, directional spread) for any designed boundaries within the EasyGSH model domain (data found under the synoptic simulation, UnTRIM22, 1000m grid section.)

### Packages used in this project

csv 
numpy 
OS 
pandas 
processing.core.Processing 
processing 
sys 
qgis.core 
time 
utm 
xarray 


## As of now it is a three part process

The first process requires the .bnd file and .grd file that one can generate from the Delft3D GUI
In this process the real world coordinates are extracted from these files and exported as a .csv file. **You get 2 CSV's one for flow boundaries and one for wave boundaries**

The second process requires the mdf file, the waterlevel netcdf file from easygsh and the csv file created from process one.
This part generates the .bct file in the same name as the mdf file. As an overview this process uses the xarray module to select and extract the water level data , where the locations are specified by the process one csv file. The data is then stored in lists with the boundary name as keys, which is then looped with the header information and written in the required .bct format. 

The third process requires mdw file, the wave netcdf file from easygsh and the wave_csv generated from process one.

Please run just the main.py file for results.
