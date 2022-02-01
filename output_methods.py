import csv
import extract_from_d3d_files


def write_bnd_coord_ascii(bnd_data_list, out_path):
    """Write ASCII file based on bnd file.
    Contains one row per start / end point with corresponding x & y coordinates."""

    with open(out_path, 'w', newline='') as out_file:
        csv_writer = csv.writer(out_file)
        for boundary in bnd_data_list:
            bnd_point_a = f"{boundary['bnd_name']}_a"
            bnd_point_b = f"{boundary['bnd_name']}_b"
            csv_writer.writerow([bnd_point_a, boundary['x_a'], boundary['y_a']])
            csv_writer.writerow([bnd_point_b, boundary['x_b'], boundary['y_b']])

    print('ASCII file of boundary coordinates created.')


def write_grd_to_gis(path_grd, out_path):
    """Write content grd file to some GIS-readable format"""

    # Read grid file
    x_values, y_values, m, n, missing_value = extract_from_d3d_files.read_grd(path_grd=path_grd)

    with open(out_path, 'w', newline='') as out_file:
        csv_writer = csv.writer(out_file)

        csv_writer.writerow(['m', 'n', 'x', 'y'])

        for x_value_list_by_n in x_values:
            n_index = int(x_value_list_by_n[0])
            m_index = 0
            for x_value_for_m in x_value_list_by_n:
                if m_index > 0 and x_value_for_m != missing_value:
                    y_value = y_values[n_index-1][m_index]  # extract y value

                    # write m, n, x, y to file
                    csv_writer.writerow([m_index, n_index, x_value_for_m, y_value])
                    # csv_writer.writerow(
                    #    [str(m_index), str(n_index), str(x_value_for_m), str(y_value)])  # write m, n, x, y to file

                m_index += 1

    print('ASCII file of boundary coordinates created.')
