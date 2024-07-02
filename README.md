# Generate/alter input/boundary condition files for Delft3D4 using the EasyGSH dataset
# Identify representative period by wind (Soares et al., 2024) (pending...)
# Use the standalone GUI EasyD3D


Source of easygsh data  **https://mdi-de.baw.de/easygsh/Easy_Viewer_syn.html#home**

Citations for using data : **Hagen, R., Plüß, A., Schrage, N., Dreier, N. (2020): EasyGSH-DB: Themengebiet - synoptische Hydrodynamik. Bundesanstalt für Wasserbau. https://doi.org/10.48437/02.2020.K2.7000.0004**
Please read the source document to understand how these datasets are generated, some quick points.
* The data provided are the results of a numerical simulation gridded over 1km and provided every 20 minutes. 
* The numerical modeling approach used to generate the data utilizes annually updated bathymetry, tidal dynamics simulated by the Untrim2 modeling system, using tidal constituents at the open boundaries (corrected for external surge), waves computed using a combination of the model UnK (Schneggenburger et al., 2000) and SWAN for near-shore physical processes. **This code does not extract SWAN-generated data**

**This code creates files for the Delft3D4 module**
1) To extract time-series water level 2D information for any designed boundaries within the EasyGSH model domain  (data found under the synoptic simulation, UnTRIM2, 1000m grid section.)
2) To extract time series wave/Sea-state data 2D (significant height, peak period, direction, directional spread) for any designed boundaries within the EasyGSH model domain (data found under the synoptic simulation, UnTRIM2, 1000m grid section.)

**Important notes on the code function**
* The code uses bilinear interpolation to extract water level and wave data for a concerned point.
* Please check the extent of your grid and the EasyGSH dataset limits before using the code, it has to fall within the limits of EasyGSH
* The wave direction is calculated according to Nautical convention and is in From-orientation
* The selection of a representative period is based on the algorithm explained in Soares et al. 2024 (pending)

### Packages used in this project

* ast
* csv 
* datetime
* math
* numpy 
* os
* pandas
* scipy
* statistics
* sys 
* time
* tqdm
* utm 
* xarray


# Working on

* Adding variability in wave parameters for climate change scenarios. 
* Adding integration with COSMO wind field files.


### Two choices are presented, you can run the <ins>main.py</ins> script in your Python environment to extract your files or use the standalone GUI <ins>EasyD3d.exe</ins>, alternatively, the gui_improved.py script is also provided in case you want to make changes to the source code and make a new GUI. One can use Pyinstaller or Auto-py-to-exe to convert the <ins>gui.py</ins> to the executable GUI EasyD3d. 

* Snippet of the GUI
![easyd3d](https://github.com/capt-clay10/bct-bcw-mdw-grd_to_CSV_file_generator-for-EasyGSH-Delft3D/assets/98163811/4a652544-84f0-40bb-b9bb-f176ae528d7c)



### Information about the BCW file

**An important thing to note is that this code replicates the file format for a SWAN wave model with uniform wave boundary conditions along one boundary line for multiple time points. so essentially if you make several boundaries one can create a space and time-varying effect**

**The direction is between 0-360, in the nautical convention**
**The directional spread is in degrees**

#### The creator of this script recommends the following steps to create and use the bcw file:

1) Use the Delft3d flow GUI to make boundaries on your wave grid (**boundary name should be the same as your wave boundary name**) and save the wave.bnd file. ***NOTE: Use this opportunity to make several boundaries this will create the effect of space-varying conditions. (at least 2km in length))***
2) Use the now-generated wave.bnd file and the wave.grd in the script to generate the boundary_location.csv
3) You can now run the script to generate the bcw file and the new mdw file.
4) Once completed, open the mdw file and add the keyword as in the manual with the appropriate format (**TSeriesFile= wave.bcw**)

* Note, first make a mdw file with a dummy boundary, since the code reads the .mdw file to look for the term 'Boundary' to store the boundary information
* Please use a boundary naming convention without underscore so for example when amking the wave.bnd file name the boundaries as North1 instead of North_1. 

### As a personal note from a fellow modeller ###
Always validate results yourself!
