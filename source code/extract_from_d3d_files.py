def extract_bnd_grd_indices(path_bnd):
    """Read DELFT3D bnd file to extract m / n indices for boundary start / end points."""
    bnd_data = []

    with open(path_bnd, newline='') as bnd_file:
        file_content = bnd_file.read()
        record_list = file_content.split('\n')

        record_count = 0
        # Write content of each line to bnd_data as list
        for record in record_list:
            # Only execute for non-empty lines
            if record != '':
                # Create list of values in current line (boundary name excluded due to whitespaces, added in next step)
                # 20 is maximum length of boundary name (fixed-length strings)
                bnd_data.append(record[21:].split())
                # Insert boundary name in list (whitespaces handled)
                bnd_data[record_count].insert(0, record[:20].strip())

            record_count += 1

        bnd_grd_indices = []
        bnd_count = 0
        # Extract M and N coordinates for boundaries
        for boundary in bnd_data:
            # Indices:  0: bnd name, 1: bnd type, 2: data type, 3: m index begin, 4: n index begin,
            #           5: m index end, 6: n index end, 7: reflection coefficient, ...
            bnd_grd_indices.append({'bnd_name': boundary[0], 'm_a': int(boundary[3]), 'n_a': int(boundary[4]),
                                    'm_b': int(boundary[5]), 'n_b': int(boundary[6])})

            bnd_count += 1
        return bnd_grd_indices


def read_grd(path_grd):
    """Read grid file."""

    # Create lists to store the organised x / y values
    x_values = []
    y_values = []

    with open(path_grd, newline='') as grd_file:
        file_content = grd_file.read()
        record_list = file_content.split('ETA=')

        record_count = 0
        for record in record_list:

            # Handle header lines: Look for Missing Value & and grid dimensions m, n given therein.
            if record_count == 0:
                record_split = record.split('\r\n')

                # Check if 'Missing value' exists. Else it is 0.
                header_row_to_be_tested_for_missing_value = record_split[-4].split()
                if header_row_to_be_tested_for_missing_value[0] == 'Missing':
                    missing_value = header_row_to_be_tested_for_missing_value[3]
                else:
                    missing_value = 0

                # Read grid dimensions.
                grd_dimensions = record_split[-3].split()
                m = int(grd_dimensions[0])
                n = int(grd_dimensions[1])
                print(f'Grid dimensions: M = 1...{m}, N = 1...{n}.')

            # x values
            if record_count in range(1, n + 1):
                record_split = record.split()
                x_values.append(record_split)

            # Store y values
            if record_count in range(n + 1, 2*n + 1):
                record_split = record.split()
                y_values.append(record_split)

            record_count += 1

    return x_values, y_values, m, n, missing_value


def extract_coord_from_d3d_grd(path_grd, request_list):
    """Read DELFT3D grd file to extract x / y coordinates for specified grid indices."""
    def substitute_outlying_index(index_request, index_max, is_m_index):
        """Substitute those bnd indices, which are outside grid by 1, with closest grid index."""
        if index_request == index_max + 1:
            if is_m_index:  # set index name string for print statement
                index_name = 'm'
            else:
                index_name = 'n'
            # print(
            #     f'Requested {index_name} index {index_request} substituted for max {index_name} index {index_max}.')

            index_request = index_max  # action down here due to print statement

        return index_request

    inputs_valid = True  # Initialise variable. Used to check whether requested grid indices are within grid range

    # Read input request list to check if valid
    m_request_list = []
    n_request_list = []
    for bnd_dict in request_list:
        m_request_list.extend([bnd_dict['m_a'], bnd_dict['m_b']])
        n_request_list.extend([bnd_dict['n_a'], bnd_dict['n_b']])

    # Read grid file
    x_values, y_values, m, n, _ = read_grd(path_grd=path_grd)

    # Check whether requested grid indices are within grid range or 1 outside. TODO: Only for water level?
    for m_request in m_request_list:
        if m_request not in range(1, m + 1):  # TODO: What if none or only one index in file? Error message?
            if m_request == m + 1:
                inputs_valid = True  # no change, just for readability
                # print('For m index outside grid range (by 1 cell): Closest grid coordinate will be used.')
            else:
                inputs_valid = False
    for n_request in n_request_list:
        if n_request not in range(1, n + 1):
            if n_request == n + 1:
                inputs_valid = True  # no change, just for readability
                # print('For n index outside grid range (by 1 cell): Closest grid coordinate will be used.')
            else:
                inputs_valid = False

    # Extract x and y coordinates for input m and n value
    if inputs_valid:

        bnd_dict_count = 0
        for bnd_dict in request_list:
            # Define requested M and N values
            m_a_request = bnd_dict['m_a']
            m_b_request = bnd_dict['m_b']
            n_a_request = bnd_dict['n_a']
            n_b_request = bnd_dict['n_b']

            # Substitute bnd indices just outside grid with closest grid index
            m_a_request = substitute_outlying_index(
                index_request=m_a_request, index_max=m, is_m_index=True)
            m_b_request = substitute_outlying_index(
                index_request=m_b_request, index_max=m, is_m_index=True)
            n_a_request = substitute_outlying_index(
                index_request=n_a_request, index_max=n, is_m_index=False)
            n_b_request = substitute_outlying_index(
                index_request=n_b_request, index_max=n, is_m_index=False)

            # Extract x values
            # Extract x values
            bnd_dict['x_a'] = float(x_values[n_a_request - 1][m_a_request])
            if bnd_dict['x_a'] == 0:
                # if grid is cut and substitution logic above doesn't work
                bnd_dict['x_a'] = float(x_values[n_a_request - 2][m_a_request - 1])

            bnd_dict['x_b'] = float(x_values[n_b_request - 1][m_b_request])
            if bnd_dict['x_b'] == 0:
                bnd_dict['x_b'] = float(x_values[n_b_request - 2][m_b_request - 1])

            # Extract y values
            bnd_dict['y_a'] = float(y_values[n_a_request - 1][m_a_request])
            if bnd_dict['y_a'] == 0:
                bnd_dict['y_a'] = float(y_values[n_a_request - 2][m_a_request - 1])

            bnd_dict['y_b'] = float(y_values[n_b_request - 1][m_b_request])
            if bnd_dict['y_b'] == 0:
                bnd_dict['y_b'] = float(y_values[n_b_request - 2][m_b_request - 1])

            bnd_dict_count += 1

        # Rename the extended input list
        bnd_data_list = request_list

        return bnd_data_list  # TODO: Is that how you handle function output? None in else case.

    else:
        print('ERROR: At least one m / n index outside of grid range + 1. Check input.')
