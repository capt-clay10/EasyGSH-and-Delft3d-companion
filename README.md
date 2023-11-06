# Generate .bct and .bcw file for Delft3D4 using EasyGSH dataset
Source of data  **https://mdi-de.baw.de/easygsh/Easy_Viewer_syn.html#home**
Citations for using data : **Hagen, R., Plüß, A., Schrage, N., Dreier, N. (2020): EasyGSH-DB: Themengebiet - synoptische Hydrodynamik. Bundesanstalt für Wasserbau. https://doi.org/10.48437/02.2020.K2.7000.0004**
Please read the source document to understand how these datasets are generated, some quick points.
* The data provided are the results of a numerical simulation gridded over 1km and provided every 20 minutes. 
* The numerical modeling approach used to generate the data utilizes annually updated bathymetry, tidal dynamics simulated by the Untrim2 modeling system using tidal constituents at the open boundaries (corrected for external surge), waves computed using a combination of the model UnK (Schneggenburger et al., 2000) and SWAN for near-shore physical processes. **This code does not extract SWAN-generated data**

**This code creates files for the Delft3D4 module**
1) To extract time-series water level 2D information for any designed boundaries within the EasyGSH model domain  (data found under the synoptic simulation, UnTRIM2, 1000m grid section.)
2) To extract time series wave/Sea-state data 2D (significant height, peak period, direction, directional spread) for any designed boundaries within the EasyGSH model domain (data found under the synoptic simulation, UnTRIM2, 1000m grid section.)

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
* New Standalone GUI added for windows (EasyD3d.exe)
* Add desired sea level rise to extracted water level time series (.bct files)
* The script can extract boundary conditions for overlapping years. ( for example: when your simulation runs over 2003 December to 2004- January)
* The script now also writes an mdw file with extracted xy boundary coordinates.
* No need to add start time and end time for generating both the .bct and .bcw file together, it extracts it now directly from the .mdf file. *(To be noted, if you wish to create just the .bcw file, you still need to give this information)*.
* The script now performs a check for nan values in the dataset and displays boundaries containing more than **2** nan values.
* The script at this stage replaces the nan values with the **mode** of values within that boundary.

# Working on

* Adding variability in wave parameters for climate change scenarios. 
* Adding integration with COSMO wind field files.
* Better handling NaN values ( currently the nan values are replaced by mode values)

# Two choices are presented, you can run the **main.py** script in your python environment to extract your files or use the standalone GUI **EasyD3d.exe**, alternatively, the gui.py script is also provided in case you want to make changes to the source code and make a new GUI. One can use Pyinstaller or Auto-py-to-exe to convert the **gui.py** to the executable GUI EasyD3d. 

* Snippet of the GUI
![easyd3d](https://github.com/capt-clay10/bct-bcw-mdw-grd_to_CSV_file_generator-for-EasyGSH-Delft3D/assets/98163811/4a652544-84f0-40bb-b9bb-f176ae528d7c)

**An important thing to note is, that this code replicates the file format for a SWAN wave model with uniform wave boundary conditions along one boundary line for multiple time points. so essentially if you make several boundaries one can create a space and time-varying effect**

### Information about the BCW file

**The direction is between 0-360, in the nautical convention**
**The directional spread is in degrees**

#### The creator of this script recommends the following steps to create and use the bcw file:

1) Use the Delft3d flow GUI to make boundaries on your wave grid (**boundary name should be the same as your wave boundary name**) and save the wave.bnd file. ***NOTE: Use this opportunity to make several boundaries this will create the effect of space varying conditions. (at least 2km in length))***
2) Use the now generated wave.bnd file and the wave.grd in the script to generate the boundary_location.csv
3) You can now run the script to generate the bcw file and the new mdw file.
4) Once completed, open the mdw file and add the keyword as in the manual with the appropriate format (**TSeriesFile= wave.bcw**)

### As a personal note from a fellow modeller ###
Always validate results yourself!



