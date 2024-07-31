# -*- coding: utf-8 -*-
"""
Converting COSMO files to Delft3D format
"""


def create_wind_fields_cosmo(grid_ed_path, cosmo_db_utm_path, cosmo_files_path,
                             file_name, ref_time):

    import os
    import numpy as np
    import scipy.io
    from scipy.interpolate import griddata
    import datetime as dt
    import cfgrib
    from tqdm import tqdm

    # %% Functions

    # Function to process the COSMO data and write it to files

    def process_data(year, cosmo_dir, X, Y, xcos, ycos, files, REF):
        # List all UV and PS files in the COSMO directory
        A = [f for f in os.listdir(os.path.join(
            cosmo_dir, 'UV')) if f.endswith('.grb')]
        B = [f for f in os.listdir(os.path.join(
            cosmo_dir, 'PS')) if f.endswith('.grb')]

        for i in tqdm(range(0, len(A) // 2), desc='Extracting wind and pressure fields', total=(len(A) // 2), leave=True, mininterval=0.1):
            # Define file paths for U, V, and PS components
            WU_file = os.path.join(cosmo_dir, 'UV/', 'U_' + A[i][2:])
            WV_file = os.path.join(
                cosmo_dir, 'UV/', 'V_' + A[i + len(A) // 2][2:])
            PS_file = os.path.join(cosmo_dir, 'PS/', B[i])

            # Open GRIB files using cfgrib
            WU = cfgrib.open_dataset(WU_file)
            WV = cfgrib.open_dataset(WV_file)
            PS = cfgrib.open_dataset(PS_file)

            for kk in range(len(WU.time)):
                # Process U component
                DATA_U = WU.u10.values[kk]
                DATA_U = DATA_U.T
                wnd_cosu = DATA_U[mm1:mm2, nn1:nn2]

                U = griddata((xcos.flatten(), ycos.flatten()),
                             wnd_cosu.flatten(), (X, Y), method='linear')
                U[np.isnan(U)] = 9999.00

                # Process V component
                DATA_V = WV.v10.values[kk]
                DATA_V = DATA_V.T
                wnd_cosv = DATA_V[mm1:mm2, nn1:nn2]
                V = griddata((xcos.flatten(), ycos.flatten()),
                             wnd_cosv.flatten(), (X, Y), method='linear')
                V[np.isnan(V)] = 9999.00

                # Process pressure component
                DATA_P = PS.sp.values[kk]
                DATA_P = DATA_P.T
                ps_cos = DATA_P[mm1:mm2, nn1:nn2]
                P = griddata((xcos.flatten(), ycos.flatten()),
                             ps_cos.flatten(), (X, Y), method='linear') / 100
                P[np.isnan(P)] = 9999.00

                # Calculate time difference and format time string
                T = WU.time.values[kk].astype('datetime64[s]').tolist()
                diff = round((T - REF).total_seconds() / 3600)
                t = f'TIME = {diff} hours since {REF.strftime("%Y-%m-%d %H:%M:%S")} +00:00 '

                # Write time header to files
                for key in ['amu', 'amv', 'amp', 'xwind', 'ywind']:
                    files[key].write(f'{t}\n')

                # Write data to files
                write_data(files['amu'], U, a, b)
                write_data(files['amv'], V, a, b)
                write_data(files['amp'], P, a, b, is_pressure=True)
                write_data(files['xwind'], U, a, b)
                write_data(files['ywind'], V, a, b)

    def write_data(fid, data, a, b, is_pressure=False):
        if is_pressure:
            Fa = '%6.2f'
            Fb = ' %7.2f'
            Fc = ' %7.2f\r'
        else:
            Fa = '%6.2f'
            Fb = ' %7.2f'
            Fc = ' %7.2f\r'

        Fb1 = ''.join([Fb] * (b - 2))
        Zeil = [Fa + Fb1 + Fc]
        Fd = '%6.2f'
        ZeilP = [Fd + Fb1 + Fc]

        for jj in range(a):
            if jj == 0:
                fid.write(Zeil[0] % tuple(data[jj, :]))
            else:
                fid.write(ZeilP[0] % tuple(data[jj, :]))

    # %% Manual inputs

    # Load the Delft3D equidistant grid file
    grid_ed = scipy.io.loadmat(grid_ed_path)

    # Load COSMO UTM coordinates
    cosmo_db_utm = scipy.io.loadmat(cosmo_db_utm_path)

    # Set paths and reference datetime
    dir_cosmo = cosmo_files_path

    REF = dt.datetime.strptime(ref_time, '%Y-%m-%d %H:%M:%S')
    yr = REF.year

    # Define indexes for COSMO data slicing
    mm1, mm2, nn1, nn2 = 381, 431, 476, 519

    # %% start code

    X = grid_ed['data']['X'][0][0][:-1, :-1]  # Extract X coordinates
    Y = grid_ed['data']['Y'][0][0][:-1, :-1]  # Extract Y coordinates

    xcos = cosmo_db_utm['xx_utm']
    ycos = cosmo_db_utm['yy_utm']

    # Open files for writing processed data
    files = {
        'amu': open(os.path.join(dir_cosmo, f'{file_name}.amu'), 'w+'),
        'amv': open(os.path.join(dir_cosmo, f'{file_name}.amv'), 'w+'),
        'amp': open(os.path.join(dir_cosmo, f'{file_name}.amp'), 'w+'),
        'xwind': open(os.path.join(dir_cosmo, f'xwind_{file_name}.wnd'), 'w+'),
        'ywind': open(os.path.join(dir_cosmo, f'ywind_{file_name}.wnd'), 'w+')
    }

    # Replace zero values in X and Y with NaN
    X[X == 0] = np.nan
    Y[Y == 0] = np.nan
    a, b = X.shape  # Get the shape of the grid

    # Define headers for different data files
    HEADER = {
        'amu': [
            'FileVersion = 1.03',
            'Filetype = meteo_on_equidistant_grid',
            'NODATA_value = 9999.00',
            'n_cols = 47',
            'n_rows = 36',
            'grid_unit = m',
            'x_llcorner = 269907',
            'y_llcorner = 5899222',
            'dx = 6000',
            'dy = 6000',
            'n_quantity = 1',
            'quantity1 = x_wind',
            'unit1 = m s-1'
        ],
        'amv': [
            'FileVersion = 1.03',
            'Filetype = meteo_on_equidistant_grid',
            'NODATA_value = 9999.00',
            'n_cols = 47',
            'n_rows = 36',
            'grid_unit = m',
            'x_llcorner = 269907',
            'y_llcorner = 5899222',
            'dx = 6000',
            'dy = 6000',
            'n_quantity = 1',
            'quantity1 = y_wind',
            'unit1 = m s-1'
        ],
        'amp': [
            'FileVersion = 1.03',
            'Filetype = meteo_on_equidistant_grid',
            'NODATA_value = 9999.00',
            'n_cols = 47',
            'n_rows = 36',
            'grid_unit = m',
            'x_llcorner = 269907',
            'y_llcorner = 5899222',
            'dx = 6000',
            'dy = 6000',
            'n_quantity = 1',
            'quantity1 = air_pressure',
            'unit1 = mbar'
        ],
        'xwind': [
            'FileVersion = 1.03',
            'Filetype = meteo_on_equidistant_grid',
            'NODATA_value = 9999.00',
            'n_cols = 47',
            'n_rows = 36',
            'grid_unit = m',
            'x_llcorner = 269907',
            'y_llcorner = 5899222',
            'dx = 6000',
            'dy = 6000',
            'n_quantity = 1',
            'quantity1 = x_wind',
            'unit1 = m s-1'
        ],
        'ywind': [
            'FileVersion = 1.03',
            'Filetype = meteo_on_equidistant_grid',
            'NODATA_value = 9999.00',
            'n_cols = 47',
            'n_rows = 36',
            'grid_unit = m',
            'x_llcorner = 269907',
            'y_llcorner = 5899222',
            'dx = 6000',
            'dy = 6000',
            'n_quantity = 1',
            'quantity1 = y_wind',
            'unit1 = m s-1'
        ]
    }

    for key in HEADER.keys():
        for line in HEADER[key]:
            files[key].write(line + '\n')

    # %% Run the data processing for the year
    process_data(yr, dir_cosmo, X, Y, xcos, ycos, files, REF)

    # Close files
    for f in files.values():
        f.close()

    print('The wind and pressure field files have been generated')
