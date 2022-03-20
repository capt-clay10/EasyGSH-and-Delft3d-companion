# bct_bcw_file_generator_for_EasyGSH

This code creates files for the Delft3D module
1) To extract timeseries water level 2D information for any designed boundaries within the EasyGSH model domain  (data found under the synoptic simulation, UnTRIM22, 1000m grid section.)
2) To extract time series wave/Sea-state data 2D (significant height, peak period, direction, directional spread) for any designed boundaries within the EasyGSH model domain (data found under the synoptic simulation, UnTRIM22, 1000m grid section.)

### Packages used in this project

* csv 
* datetime
* numpy 
* OS 
* pandas 
* sys 
* time 
* utm 
* xarray 

# UPDATES

* The script now also writes an mdw file with extracted xy boundary coordinates.
* No need to add start time and end time for generating both the bct and bcw file together, it extracts it now directly from the .mdf file. *(To be noted, if you wish to create just the bcw file, you still need to give this information)*
* The script now performs a check for nan values in the dataset and displays boundaries containing more than **2** nan values.
* The script at this stage replaces the nan values with the **mode** of values within that boundary.

# Working on

* Creating a GUI interface

## As of now it is a three part process [ Please run just the main.py file for results.]

### The User can choose if they want to create both files or either one or just the boundary location csv

The first process requires the .bnd file and .grd file that one can generate from the Delft3D GUI.

In this process the real world coordinates are extracted from these files and exported as a .csv file (boundary location csv). **You get 2 CSV's one for flow boundaries and one for wave boundaries**

The second process requires the mdf file, the waterlevel netcdf file from easygsh and the csv file created from process one.
This part generates the .bct file in the same name as the mdf file. As an overview this process uses the xarray module to select and extract the water level data , where the locations are specified by the process one csv file. The data is then stored in lists with the boundary name as keys, which is then looped with the header information and written in the required .bct format. 

The third process requires mdw file, the wave netcdf file from easygsh and the wave_csv generated from process one. It then creates a bcw file in the same fashion.
**Important thing to note is, this code replicates the file format for a wave model with uniform wave boundary conditions along one boundary line for multiple time points.**

### Information about the BCW file

**The direction is between 0-360 , in the nautical convention and the angle is from y to x as opposed to x to y (see wikipedia fig 1 : https://en.wikipedia.org/wiki/Atan2)**
**The directional spread is in degrees**

#### The creator of this script recommends the following steps to create and use the bcw file:

1) Use the flow gui to make boundaries on your wave grid (**boundary name should be the same as your wave boundary name**) and save the wave.bnd file. ***NOTE: Use this opportunity to make several boundaries this will create the effect of space varying conditions. (atleast 2km in length))***
2) Use the now generated wave.bnd file and the wave.grd in the script to generate the boundary_location.csv
3) You can now run the script to generate the bcw file and the new mdw file.
4) Once completed, open the mdw file and add the key word as in the manual with the appropriate format (TSeriesFile= wave.bcw)               

* NOTE: The creators will at some point automate steps 2 ,3 and 6 
    * Also calculation of the frequency bins and directinal bins might be added


