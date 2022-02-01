"""Read DELFT3D grd file and generate GIS-readable output."""

import output_methods
import qgis_proc

# TODO: Set to False / remove after testing
test = True

print('Process started.')

# Input
if test:
    # Test input
    directory = 'D:\\CAUcloud\\prog\\data\\'
    filename_grd = 'rif.grd'
    filename_grd_points = 'grd_gis.csv'
    directory = 'D:\\CAUcloud\\Share\\D3D_share\\'
    filename_grd = 'overall_wave.grd'
    crs_epsg = '25832'
    filename_grd_points = 'overall_wave_grd_points.csv'
    filename_grd_m_lines = 'overall_wave_grd_m_lines.gpkg'
    filename_grd_n_lines = 'overall_wave_grd_n_lines.gpkg'
    path_grd_input = f'{directory}{filename_grd}'
    path_grd_points = f'{directory}{filename_grd_points}'
    path_grd_m_lines = f'{directory}{filename_grd_m_lines}'
    path_grd_n_lines = f'{directory}{filename_grd_n_lines}'
else:
    # User input
    path_grd_input = input('Path to grd file (including file name): ')
    path_grd_points = input('Path to output grid points file (including file name): ')
    path_grd_m_lines = input('Path to output grid m lines file (including file name): ')
    path_grd_n_lines = input('Path to output grid n lines file (including file name): ')
    crs_epsg = input('EPSG code of coordinate system: ')


output_methods.write_grd_to_gis(path_grd=path_grd_input, out_path=path_grd_points)
qgis_proc.create_grd_lines(grid_points=path_grd_points, crs=crs_epsg, order_field='m', group_field='n',
                           out_path=path_grd_n_lines)
qgis_proc.create_grd_lines(grid_points=path_grd_points, crs=crs_epsg, order_field='n', group_field='m',
                           out_path=path_grd_m_lines)
# TODO: Clip on grid enclosure
