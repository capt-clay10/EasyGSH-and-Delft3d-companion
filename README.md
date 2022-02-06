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


## As of now it is a three part process [ Please run just the main.py file for results.]

### The User can choose if they want to create both files or either one or just the boundary location csv

The first process requires the .bnd file and .grd file that one can generate from the Delft3D GUI.

In this process the real world coordinates are extracted from these files and exported as a .csv file (boundary location csv). **You get 2 CSV's one for flow boundaries and one for wave boundaries**

The second process requires the mdf file, the waterlevel netcdf file from easygsh and the csv file created from process one.
This part generates the .bct file in the same name as the mdf file. As an overview this process uses the xarray module to select and extract the water level data , where the locations are specified by the process one csv file. The data is then stored in lists with the boundary name as keys, which is then looped with the header information and written in the required .bct format. 

The third process requires mdw file, the wave netcdf file from easygsh and the wave_csv generated from process one. It then creates a bcw file in the same fashion.
**Important thing to note is, this code replicates the file format for a wave model with uniform wave boundary conditions along one boundary line for multiple time points.**

### Information about the BCW file

**The direction is between -180 to 180 , in the nautical convention and the angle is from y to x as opposed to x to y (see wikipedia fig 1 : https://en.wikipedia.org/wiki/Atan2)**

#### The creator of this script recommends the following steps to create and use the bcw file:

1) Use the flow gui to make boundaries on your wave grid (**boundary name should be the same as your wave boundary name**) and save the wave.bnd file. ***NOTE: Use this opportunity to make several boundaries this will create the effect of space varying conditions. (atleast 2km in length))***
2) Use the now generated wave.bnd file and the wave.grd in the script to generate the boundary_location.csv
3) Now open the boundaries section in the wave gui and manually set the boundaries (**same names as step1**) with the x-y coordinates generated in the csv file
4) You can now run the scrip to generate the bcw file. **Check for nans in the file, some boundaries might not have data**
5) Once completed, open the mdw file and add the key word as in the manual with the appropriate format (TSeriesFile= wave.bcw)      
6) In the mdw file , in the section Boundaries, look for and delete the lines with Wave Height, Peak period, Direction and Directional spread.          

***NOTE: The creators will at some point automate steps 2 ,3 and 6***


