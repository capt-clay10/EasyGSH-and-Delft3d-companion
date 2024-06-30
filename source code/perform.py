# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 12:37:12 2022

@author: sungw765
"""

import requests
import re
import time
import bct_generator
import os

# path = 'F:/test'
# os.chdir(path)

# boundaries = 'midres.csv'
# nc_file = '2015_1000m_waterlevel_2D.nc'
# mdf_file = 'midres.mdf'
# start_time = '2015-02-01 00:00:00'
# end_time = '2015-02-28 00:00:00'
# step = 20
# bct_file_name = 'midres.bct'


# bct_generator.bct_file_generator(
#     boundaries=boundaries, nc_file=nc_file, mdf_file=mdf_file, start_time=start_time, end_time=end_time, step=step,
#     bct_file_name=bct_file_name)


def main():
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        bct_generator.bct_file_generator(
            boundaries=boundaries, nc_file=nc_file, mdf_file=mdf_file, start_time=start_time, end_time=end_time, step=step,
            bct_file_name=bct_file_name)

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats(10)


if __name__ == '__main__':
    main()
