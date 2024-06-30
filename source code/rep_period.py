def identify_rep_period(file_input, quad, spd, start_time_total, end_time_total, frequency,
                        start_time, end_time):

    from sklearn.metrics import r2_score
    import pandas as pd
    import numpy as np
    from sklearn import preprocessing
    from scipy.stats import pearsonr
    import os
    import re
    import matplotlib.pyplot as plt
    from sklearn.metrics import mean_absolute_error as mae
    from sklearn.metrics import mean_squared_error as mse
    from tqdm import tqdm

    # %% functions

    def classify_wind_data(dataframe_in, start_time, end_time, dir_sector, speed_class):
        """
        This function takes in a dataframe with 2 columns with names speed and dir
        This function needs a start time and end time to slice the input dataframe
        This function needs a list of directional sectors thata are of interest
        example : ['SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
        It will produce the result in the same order
        This function needs a list of speed classes of interest (0-11)
        example = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        It then computes the number of instances and weightage for the input parameters (sector,class)
        It has three outputs
        1) A dataframe where the input is classified according to the provided parameters (sector,class)
        2) A dataframe with speed information ( freq, weightage)
        3) A dataframe with directional information ( freq, weightage)

        example use
        start_time = "1975-01-01 00:00:00"
        end_time = "2018-12-31 00:00:00"

        quad = ['SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
        spd = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        dir_speed_total , df_dir , df_speed = combine_wind_dat(obs_data_all, start_time,
                                                               end_time,quad,spd)

        """
        quad = dir_sector
        spd = speed_class
        obs_data_all = dataframe_in

        # Obs_data_all should be date speed dir columns
        # extract data for selected time span
        req_dat = obs_data_all.loc[start_time: end_time]
        data_dir = req_dat['dir']  # seggregate the data
        data_speed = req_dat['speed']

        # Complete binning of the dir data for all sectors

        df_dir = pd.DataFrame(data_dir)  # convert to df
        # name the sectors
        directional_sectors = np.array(
            'N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW N'.split())
        # choose the bin sizes
        directional_bins = np.arange(11.25, 360, 22.5)
        # Assign each direction an orientation
        df_dir['orientation'] = directional_sectors[np.digitize(
            df_dir['dir'], directional_bins)]

        # Complete binning of the speed data for all classes

        df_spd = pd.DataFrame(data_speed)
        # name the classes
        speed_class = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        # choose the bin sze here taking the standardized beaufort scale
        bins_speed = np.asarray(
            [0.5, 1.5, 3.3, 5.5, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4])
        # Assign each speed a class
        df_spd['class'] = speed_class[np.digitize(df_spd['speed'], bins_speed)]

        # read the choice of user
        # combine the two parameter
        dir_speed = [df_dir, df_spd]
        dir_speed = pd.concat(dir_speed, axis=1)
        # slice first for directional choice
        dir_speed = dir_speed[dir_speed['orientation'].isin(
            quad)]
        dir_speed = dir_speed[dir_speed['class'].isin(
            spd)]

        # count occurences

        # Count the occurences/bin frequencies for the asked orientations
        dir_class = pd.DataFrame(dir_speed.iloc[:, [0, 1]])
        # Group all orientations ( this is done to combine both Norths)
        df2 = dir_class.groupby('orientation').count()
        reorderlist = quad
        df_direction = df2.reindex(reorderlist)
        # when the freq window is too small its possible there is no data for some orientation
        # to avoid problems in normalizing
        df_direction = df_direction.fillna(0)

        # Count the occurences/bin frequencies for the asked classes
        speed_class = pd.DataFrame(dir_speed.iloc[:, [2, 3]])
        speed_class = speed_class.groupby('class').count()
        df_speed = speed_class
        # Check and add missing speed classes as 0
        df_speed = df_speed.reset_index()
        class_s = (df_speed['class']).tolist()
        list = spd
        missing_class = []  # preallocate
        for i in list:  # range extends from 0 to 11 on the beaufort scale
            # Check if the classes are in the dataframe
            if i in class_s:
                pass  # if yes then pass over it
            else:
                # if no then make a note of the missing one
                missing_class.append(i)

        if len(missing_class) != 0:  # check notes to find the missing one if any
            # if classes are missing make a list with the empty rows
            lists = []
            for j in missing_class:
                new_pair = [j, 0]
                lists.append(new_pair)

            missing_vals = pd.DataFrame(lists)  # convert the list to a df
            missing_vals.columns = ['class', 'speed']
            # Combine the missing dataframe with the original
            df = pd.concat([df_speed, missing_vals])
            df = df.sort_values(by=['class'])
            df = df.reset_index(drop=True)
            df_speed = df.set_index('class')

        else:  # if nothing is missing
            df_speed = df_speed.set_index('class')

        # Count the occurences in the combined dataframe
        dir_speed = dir_speed.groupby(['orientation', 'class']).count()
        dir_speed = dir_speed.reset_index()

        # Normalise/ weightage by occurence for direction
        dir_array = np.asarray(df_direction['dir'])
        df_direction['norm'] = np.transpose(
            preprocessing.normalize([dir_array], norm='l2'))
        df_direction['weightage'] = (
            df_direction['dir'] / df_direction['dir'].sum()) * 100
        df_direction = (df_direction.iloc[:, [1, 2]])

        # Normalise/ weightage by occurence for speed
        spd_array = np.asarray(df_speed['speed'])
        df_speed['norm'] = np.transpose(
            preprocessing.normalize([spd_array], norm='l2'))
        df_speed['weightage'] = (
            df_speed['speed'] / df_speed['speed'].sum()) * 100
        df_speed = (df_speed.iloc[:, [1, 2]])

        return dir_speed, df_direction, df_speed

    def classify_wind_data_all_params(dataframe_in, start_time, end_time):
        """
        This function takes in a dataframe with 2 columns with names speed and dir
        This function needs a start time and end time to slice the input dataframe
        This function is used to identify the similarity without omission of directional sectors or classes
        It then computes the number of instances and weightage for the input parameters (sector,class)
        It has three outputs
        1) A dataframe where the input is classified according to the provided parameters (sector,class)
        2) A dataframe with speed information ( freq, weightage)
        3) A dataframe with directional information ( freq, weightage)

        example use
        start_time = "1975-01-01 00:00:00"
        end_time = "2018-12-31 00:00:00"

        dir_speed_total , df_dir , df_speed = combine_wind_dat(obs_data_all, start_time,
                                                               end_time)

        """
        quad = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
                'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        spd = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        obs_data_all = dataframe_in

        # Obs_data_all should be date speed dir columns
        # extract data for selected time span
        req_dat = obs_data_all.loc[start_time: end_time]
        data_dir = req_dat['dir']  # seggregate the data
        data_speed = req_dat['speed']

        # Complete binning of the dir data for all sectors

        df_dir = pd.DataFrame(data_dir)  # convert to df
        # name the sectors
        directional_sectors = np.array(
            'N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW N'.split())
        # choose the bin sizes
        directional_bins = np.arange(11.25, 360, 22.5)
        # Assign each direction an orientation
        df_dir['orientation'] = directional_sectors[np.digitize(
            df_dir['dir'], directional_bins)]

        # Complete binning of the speed data for all classes

        df_spd = pd.DataFrame(data_speed)
        # name the classes
        speed_class = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        # choose the bin sze here taking the standardized beaufort scale
        bins_speed = np.asarray(
            [0.5, 1.5, 3.3, 5.5, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4])
        # Assign each speed a class
        df_spd['class'] = speed_class[np.digitize(df_spd['speed'], bins_speed)]

        # read the choice of user
        # combine the two parameter
        dir_speed = [df_dir, df_spd]
        dir_speed = pd.concat(dir_speed, axis=1)
        # slice first for directional choice
        dir_speed = dir_speed[dir_speed['orientation'].isin(
            quad)]
        dir_speed = dir_speed[dir_speed['class'].isin(
            spd)]

        # count occurences

        # Count the occurences/bin frequencies for the asked orientations
        dir_class = pd.DataFrame(dir_speed.iloc[:, [0, 1]])
        # Group all orientations ( this is done to combine both Norths)
        df2 = dir_class.groupby('orientation').count()
        reorderlist = quad
        df_direction = df2.reindex(reorderlist)
        # when the freq window is too small its possible there is no data for some orientation
        # to avoid problems in normalizing
        df_direction = df_direction.fillna(0)

        # Count the occurences/bin frequencies for the asked classes
        speed_class = pd.DataFrame(dir_speed.iloc[:, [2, 3]])
        speed_class = speed_class.groupby('class').count()
        df_speed = speed_class
        # Check and add missing speed classes as 0
        df_speed = df_speed.reset_index()
        class_s = (df_speed['class']).tolist()
        list = spd
        missing_class = []  # preallocate
        for i in list:  # range extends from 0 to 11 on the beaufort scale
            # Check if the classes are in the dataframe
            if i in class_s:
                pass  # if yes then pass over it
            else:
                # if no then make a note of the missing one
                missing_class.append(i)

        if len(missing_class) != 0:  # check notes to find the missing one if any
            # if classes are missing make a list with the empty rows
            lists = []
            for j in missing_class:
                new_pair = [j, 0]
                lists.append(new_pair)

            missing_vals = pd.DataFrame(lists)  # convert the list to a df
            missing_vals.columns = ['class', 'speed']
            # Combine the missing dataframe with the original
            df = pd.concat([df_speed, missing_vals])
            df = df.sort_values(by=['class'])
            df = df.reset_index(drop=True)
            df_speed = df.set_index('class')

        else:  # if nothing is missing
            df_speed = df_speed.set_index('class')

        # Count the occurences in the combined dataframe
        dir_speed = dir_speed.groupby(['orientation', 'class']).count()
        dir_speed = dir_speed.reset_index()

        # Normalise/ weightage by occurence for direction
        dir_array = np.asarray(df_direction['dir'])
        df_direction['norm'] = np.transpose(
            preprocessing.normalize([dir_array], norm='l2'))
        df_direction['weightage'] = (
            df_direction['dir'] / df_direction['dir'].sum()) * 100
        df_direction = (df_direction.iloc[:, [1, 2]])

        # Normalise/ weightage by occurence for speed
        spd_array = np.asarray(df_speed['speed'])
        df_speed['norm'] = np.transpose(
            preprocessing.normalize([spd_array], norm='l2'))
        df_speed['weightage'] = (
            df_speed['speed'] / df_speed['speed'].sum()) * 100
        df_speed = (df_speed.iloc[:, [1, 2]])

        return dir_speed, df_direction, df_speed

    def speed_class_of_direction(input_df, directional_sectors):
        """
        This function takes in the output dataframe from the function classify_wind_data as input
        This function needs a list of directional sectors thata are of interest
        example : ['SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
        This function outputs a dataframe which is classified
        (weighted/normalized) for occurences in each given orientation for each speed class(0-11)
        It fills the classes that have no instances with 0
        therefore there are always 12 classes
        """
        input_df = input_df
        list = directional_sectors

        df_list = []  # to append all df later
        # extract the information for the requested orientations
        for q in list:
            # iterate over each listed orientation
            df = input_df[input_df['orientation'] == q]
            df = df.reset_index(drop=True)
            # Conduct a check for missing speed classes
            class_d = (df['class']).tolist()  # isolate the class column
            missing_class = []  # preallocate
            for i in range(0, 12):  # range extends from 0 to 11 on the beaufort scale
                # Check if the classes are in the dataframe
                if i in class_d:
                    pass  # if yes then pass over it
                else:
                    # if no then make a note of the missing one
                    missing_class.append(i)

            if len(missing_class) != 0:  # check notes to find the missing one if any
                # if classes are missing make a list with the empty rows
                lists = []
                for j in missing_class:
                    new_pair = [q, j, 0, 0]
                    lists.append(new_pair)

                missing_vals = pd.DataFrame(lists)  # convert the list to a df
                missing_vals.columns = ['orientation', 'class', 'dir', 'speed']
                # Combine the missing dataframe with the original
                df = pd.concat([df, missing_vals])
                df = df.sort_values(by=['class'])
                df = df.reset_index(drop=True)

                # Proceed to calculate the weightage/norm
                df['weightage'] = (df['dir'] /
                                   df['dir'].sum()) * 100

                float_array = np.asarray(df['dir'])
                # using the l2 normalization
                normalized = np.transpose(
                    preprocessing.normalize([float_array], norm='l2'))

                class_d = normalized
                class_d = pd.DataFrame(normalized, columns=['norm'])
                class_d['weight'] = df['weightage']
                # adding orientation to help indexing later
                class_d['orientation'] = df['orientation']
                df_list.append(class_d)

            else:  # if nothing is missing
                df['weightage'] = (df['dir'] /
                                   df['dir'].sum()) * 100

                float_array = np.asarray(df['dir'])
                normalized = np.transpose(
                    preprocessing.normalize([float_array], norm='l2'))

                class_d = normalized
                class_d = pd.DataFrame(normalized, columns=['norm'])
                class_d['weight'] = df['weightage']
                class_d['orientation'] = df['orientation']
                df_list.append(class_d)

            df_merged = pd.concat(df_list)  # combine the df
        return df_merged

    def direction_sector_of_speed(input_df, speed_class, directional_sectors):
        """
        This function takes in the output dataframe from the function classify_wind_data as input
        This function needs a list of speed classes of interest (0-11)
        example = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        This function needs a list of directional sectors thata are of interest
        example : ['SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
        This function outputs a dataframe which is classified
        (weighted/normalized) for occurences in each given orientation for each speed class(0-11)
        It fills the directions that have no instances with 0
        Therefore there will always be all directional sectors represented
        """
        input_df = input_df
        list = speed_class

        df_list = []
        for s in list:
            df = input_df[input_df['class'] == s]
            reorderlist = directional_sectors
            df = df.set_index('orientation')
            df = df.reindex(reorderlist)  # order according to input
            # replace the nan values in the directions with no values to 0
            df['dir'] = df['dir'].fillna(0)
            # replace the nan values in the classes with the class number
            df['class'] = df['class'].fillna(s)

            df['weightage'] = (df['dir'] /
                               df['dir'].sum()) * 100
            float_array = np.asarray(df['dir'])
            # normalised according to l2
            normalized = np.transpose(
                preprocessing.normalize([float_array], norm='l2'))
            df['norm'] = normalized
            class_s = df['norm']
            class_s = class_s.to_frame()
            class_s['weight'] = df['weightage']
            class_s['class'] = df['class']
            df_list.append(class_s)

        df_merged = pd.concat(df_list)
        return df_merged

    def corelate(input_df, compare_df, param_list):
        """
        This function takes the output df from the functions
        (speed_class_of_direction / direction_sector_of_speed) as input_df and compare df
        This function also requires one of the parameter lists, (directional sectors/speed classes)
        This function then corelates the df to give a metric of representation for each given parameter
        example:
        quad = ['SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
        df_speed_corelate = corelate(dir_class_df, dir_class_df_compare, quad)

        """
        actual_in = input_df
        compare_in = compare_df

        list = param_list
        df_list = []
        for i in list:
            in_df = actual_in[actual_in.iloc[:, 2] == i]
            com_df = compare_in[compare_in.iloc[:, 2] == i]
            in_data = in_df.iloc[:, 0]
            com_data = com_df.iloc[:, 0]
            in_data_weight = in_df.iloc[:, 1]
            in_data_weight = in_data_weight.fillna(0)
            com_data_weight = com_df.iloc[:, 1]
            com_data_weight = com_data_weight.fillna(0)

            # conduct a check for no data
            check = com_data.sum()
            if check == 0:
                nan = float('nan')
                df_list.append([i, nan])

            elif check != 0:
                # compute the squarred differences
                sq_diff = (in_data-com_data)**2
                # compute the weighted average
                wg_avg = (np.average(
                    sq_diff, axis=0, weights=in_data_weight))
                # compute the euclidean distance between the weight distributions
                euc_dist = np.sqrt(
                    np.sum(np.square(in_data_weight-com_data_weight)))
                # Total metric of representation
                rep_metric = wg_avg * euc_dist
                df_list.append([i, rep_metric])

        if type(list[0]) == int:
            df_corelated = pd.DataFrame(
                df_list, columns=['class', 'rep_metric'])
            df_corelated_max = (df_corelated.iloc[:, 1].max()) + 1
            df_corelated = df_corelated.fillna(df_corelated_max)
        elif type(list[0]) == str:
            df_corelated = pd.DataFrame(
                df_list, columns=['orientation', 'rep_metric'])
            df_corelated_max = (df_corelated.iloc[:, 1].max()) + 1
            df_corelated = df_corelated.fillna(df_corelated_max)

        return df_corelated

    def time_window_list(start_time, end_time, time_freq):
        """
        This function needs a start time , end time and a string time frequency to loop over
        example of time freq = '2MS', '6MS', '8MS'
        It then outputs two lists one with the start date and one with the end date of each window

        """
        # create first list of dates
        first_date = pd.date_range(start=start_time, end=end_time, freq='1d')
        first_date = pd.DataFrame(first_date, columns=['date'])
        period = len(first_date)

        # identify the number of rows
        start_second = first_date.iloc[0, 0]
        find_date = pd.date_range(
            start=start_second, end=end_time, freq=time_freq)
        find_val = find_date[1]

        # start the second list
        second_date = pd.date_range(start=find_val, periods=period, freq='1d')
        second_date = pd.DataFrame(second_date, columns=['date'])

        # extract the two lists
        first_date = (first_date.iloc[:, 0]).tolist()
        second_date = (second_date.iloc[:, 0]).to_list()

        return first_date, second_date

    def percent_sim(full_df, compare_df):
        """
        This function needs the total input df where the weights is the second column
        This function needs the comparing df where the weights is the second column
        This function calculates the percentage of similarity between the two weights
        percentage of similarity in distribution of the given param
        """
        # calc the absolute difference (error) betweent the weights (occurences)
        abs_diff = abs(full_df.iloc[:, 1]-compare_df.iloc[:, 1])
        # calc the percentage of absolute error
        err_percent = (abs_diff * 100) / full_df.iloc[:, 1]
        # calc the percentage of similarity
        sim_percent = (100-err_percent)
        sim_percent = np.nan_to_num(sim_percent)  # fill NaNs with 0
        # weighted mean of the similarity percentage
        simp_wavg_1 = np.average(sim_percent, weights=full_df.iloc[:, 1])
        # euclidean distance for calculation of distribution error
        euc_dist = np.sqrt(
            np.sum(np.square(full_df.iloc[:, 1]-compare_df.iloc[:, 1])))
        deg_sim = simp_wavg_1 - euc_dist

        return deg_sim

    # %% test
    # path = 'D:/Clayton_Data/Model_Boundary/Wind/dwd_helgoland'
    # os.chdir(path)

    # file_input = 'helgoland_wind.txt'
    # quad = quad = ['N', 'SSE', 'S']
    # spd =[3, 4, 5]
    # start_time_total= "2015-01-01 00:00:00"
    # end_time_total = "2019-12-31 00:00:00"
    # frequency = ['5MS']
    # start_time = "2016-01-01 00:00:00"
    # end_time= "2018-01-01 00:00:00"

    # %% code start

    wind = pd.read_csv(file_input, delimiter=(','), skiprows=1,
                       names=['date', 'speed', 'dir'])

    # wind = pd.read_csv(file_input, delimiter=(';'), skiprows=1,
    #                    names=['station', 'date', 'qn3', 'speed', 'dir', 'extra', ])

    wind_2 = wind[wind['dir'] <= 360]
    wind_2 = wind_2[wind_2['dir'] >= 0]
    wind_2 = wind_2[wind_2['speed'] >= 0]
    wind_2 = wind_2[wind_2['speed'] <= 100]

    date = pd.to_datetime(wind_2['date'].astype(str), format='%Y%m%d%H')

    data = [date, wind_2['speed'], wind_2['dir']]

    headers = ["datetime", "speed", "dir"]

    obs_data = pd.concat(data, axis=1, keys=headers)

    obs_data_all = obs_data.set_index(['datetime'])

    # %% total

    dir_speed_total, df_dir, df_speed = classify_wind_data(obs_data_all, start_time_total,
                                                           end_time_total, quad, spd)

    dir_class_df = speed_class_of_direction(dir_speed_total, quad)

    speed_class_df = direction_sector_of_speed(dir_speed_total, spd, quad)

    # %% for naming the file
    name_span_out = f'{start_time[0:4]}-{int(end_time[0:4])+1}'
    quad_range = f'{quad[0]}-{quad[-1]}'
    spd_range = f'{spd[0]}-{spd[-1]}'
    freq_name = f'{frequency[0]}-{frequency[-1]}'

    # %% start scan
    rows = []
    rows_2 = []

    list = frequency  # Window of search

    for ff in tqdm(list, desc='Finding rep period per frequency',
                   total=len(list), leave=True, mininterval=0.1):
        t_in = time.time()
        time_freq = ff

        # get the value into int
        val_freq = re.split(r"\D", time_freq)
        val_freq = int(val_freq[0])

        first_date, second_date = time_window_list(
            start_time, end_time, time_freq)

        # %% Corelating parameters

        for f, s in zip(first_date, second_date):

            dir_speed_total_compare, df_dir_compare, df_speed_compare = classify_wind_data(
                obs_data_all, f,
                s, quad, spd)

            dir_class_df_compare = speed_class_of_direction(
                dir_speed_total_compare, quad)

            speed_class_df_compare = direction_sector_of_speed(
                dir_speed_total_compare, spd, quad)

            # speed paramatrized -  Method 1
            # Method- first solve for each directional sector then corelate rep metric of
            # each direction to the frequency of the total (weighted avg)
            # rows = speed. columns = dir
            df_speed_corelate = corelate(
                dir_class_df, dir_class_df_compare, quad)

            weight_total_d = df_dir.iloc[:, 1]      # extract weight from total
            # extract weight for one period
            weight_compare_d = df_dir_compare.iloc[:, 1]

            directional_weighted_avg = np.average(
                df_speed_corelate.iloc[:, 1], weights=weight_total_d)

            euc_dist_class = np.sqrt(
                np.sum(np.square(weight_total_d-weight_compare_d)))

            speed_para_dir_wg = directional_weighted_avg * euc_dist_class

            # direction paramatrized - Method 2
            # Method- first solve for each speed class then corelate rep metric of
            # each speed class to the frequency of the total (weighted avg)
            # rows = dir. columns = speed
            df_dir_corelate = corelate(
                speed_class_df, speed_class_df_compare, spd)

            weight_total_s = df_speed.iloc[:, 1]
            weight_compare_s = df_speed_compare.iloc[:, 1]

            speed_weighted_avg = np.average(
                df_dir_corelate.iloc[:, 1], weights=weight_total_s)
            euc_dist_class = np.sqrt(
                np.sum(np.square(weight_total_s-weight_compare_s)))
            dir_para_speed_wg = speed_weighted_avg * euc_dist_class

            # %% Append all

            rows.append([f, s, val_freq, dir_para_speed_wg, speed_para_dir_wg])

        # %% Quality Check parameters

        start_year = []
        end_year = []

        # for all years
        for i in range(int(start_time_total[0:4]), int(end_time_total[0:4]), 1):
            start_year.append(i)

        for j in range(int(start_time_total[0:4]) + 1, int(end_time_total[0:4]) + 1, 1):
            end_year.append(j)

        dir_speed_total_qc, qc_dir, qc_speed = classify_wind_data_all_params(obs_data_all,
                                                                             start_time_total,
                                                                             end_time_total)

        for f, s in zip(first_date, second_date):

            dir_speed_total_qc, qc_dir_compare, qc_speed_compare = classify_wind_data_all_params(
                obs_data_all, f, s)

            # QUALITY CHECK
            #  percentage of similarity in overall distribution for a given period
            speed_percent = percent_sim(qc_speed, qc_speed_compare)
            dir_percent = percent_sim(qc_dir, qc_dir_compare)

            # statistical qc
            s_qc = qc_speed.iloc[:, 0]
            s_c = qc_speed_compare.iloc[:, 0]
            r2_s = r2_score(s_qc, s_c)  # r2 of speed distribution
            p_s = pearsonr(s_qc, s_c)
            c_s = p_s[0]  # corelation coeff of speed
            p_val_s = p_s[1]  # p-value

            d = qc_dir.iloc[:, 0]
            d_c = qc_dir_compare.iloc[:, 0]
            r2_d = r2_score(d, d_c)  # r2 of dir distribution
            p_d = pearsonr(d, d_c)
            c_d = p_d[0]  # corelation coeff of directions
            p_val_d = p_d[1]  # p-value

            # MAE
            mae_err_dir = round(mae(d_c, d), 3)
            mae_err_speed = round(mae(s_c, s_qc), 3)

            # shape analysis
            speed_dat = obs_data_all[start_time_total:end_time_total]
            speed_dat_compare = obs_data_all[f: s]
            month_s = f.strftime("%m")
            date_s = f.strftime("%d")

            # Identify the period for making the list of dates
            period_num = val_freq
            period = period_num * 30
            smoothing = period * 23

            if month_s == '02' and date_s == '29':
                date_s = '28'

            smooth_total = []
            for s_y, e_y in zip(start_year, end_year):

                in_date = f'{s_y}-{month_s}-{date_s}'
                list_date = pd.date_range(start=in_date, periods=period)
                in_d = list_date[0]
                out_d = list_date[-1]
                speed_profile = speed_dat[in_d:out_d]
                speed_profile = speed_profile.reset_index()
                y = speed_profile.iloc[:, 1]
                # smoothing over the entire period
                smooth = y.ewm(span=smoothing).mean()
                smooth_total.append(smooth)

            speed_mean = pd.DataFrame(smooth_total)
            speed_mean = speed_mean.T
            speed_mean = speed_mean.mean(axis=1)

            # speed_dat compare
            speed_profile_compare = speed_dat_compare
            speed_profile_compare = speed_profile_compare.reset_index()
            y_compare = speed_profile_compare.iloc[:, 1]
            smooth_compare = y_compare.ewm(span=smoothing).mean()
            speed_compare = pd.DataFrame(smooth_compare)
            speed_compare['mean'] = speed_mean

            # r2 corelation
            df = speed_compare
            df = df.dropna()
            df = df.iloc[5:, :]  # to remove the kinks at the start
            df = df.iloc[:-5, :]  # to remove the kinks at the end

            # euclidean distance
            a = np.asarray(df['mean'])
            b = np.asarray(df['speed'])
            euc_dist = np.sqrt(np.sum(np.square(a-b)))

            # p-value pearsons corelation
            p = pearsonr(a, b)
            p_val = p[1]
            c = p[0]

            # %% Append all

            rows_2.append([f, dir_percent, speed_percent, r2_d, c_d,
                          p_val_d, r2_s, c_s, p_val_s, euc_dist, c, p_val,
                          mae_err_dir, mae_err_speed])

        elapsed_time_freq = (time.time() - t_in) / 60
        print(f'Scan completed for {time_freq} in {elapsed_time_freq} mins')

    # %% combine parameters
    year_comparison = pd.DataFrame(
        rows, columns=['start_year', 'end_year', 'period_freq', 'dir_para', 'speed_para'])
    year_comparison = year_comparison.set_index('start_year')

    year_comparison['sum'] = year_comparison['dir_para'] + \
        year_comparison['speed_para']

    year_comp_qc = pd.DataFrame(
        rows_2, columns=['start_year', 'dir_qc', 'speed_qc',
                         'dir_r2', 'dir_corr', 'p-val_dir',
                         'speed_r2', 'speed_corr', 'p-val_speed',
                         's_a_euc_dist', 's_a_corr', 'p_val_s_a', 'mae_dir',
                         'mae_speed'])

    year_comp_qc = year_comp_qc.set_index('start_year')

    # %% combine dataframes

    rep_period = pd.concat([year_comparison, year_comp_qc], axis=1)

    # %% sort by choice

    rep_period = rep_period.sort_values(by=['sum', 'dir_r2',
                                        'dir_qc', 'speed_r2',
                                            'speed_qc', 's_a_euc_dist',
                                            's_a_corr'])

    # rep_period_freq = rep_period[rep_period['period_freq'] == 12]

    # %% copy to csv
    rep_period.to_csv(
        f'rep_period_{file_input[0:-9]}_{name_span_out}_{quad_range}_{spd_range}_{freq_name}.txt')
