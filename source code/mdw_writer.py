
def write_mdw_file(mdw_file, boundaries_wave):
    import pandas as pd
    import os
    import numpy as np

    # %% input files

    # mdw_file = 'wave.mdw'
    # boundaries_wave = 'wave.csv'

    name_with_dot = mdw_file.partition('.')
    name_until_dot = name_with_dot[0]
    file_name = '{}_new.mdw'.format(name_until_dot)  # Create name for new mdw file

    string_name = '[Boundary]'  # To find line from mdw file
    print(".")
    # %% functions

    def convert_flt_to_sci_not(fltt, prec, exp_digits):
        s = "%.*e" % (prec, fltt)
        # print(f's: {s}')
        if s == 'nan':
            s = "%.*e" % (prec, 0)  # TODO: is it a good idea to replace nan with 0?
        mantissa, exp = s.split('e')
        # add 1 to digits as 1 is taken by sign +/-
        return "%se%+0*d" % (mantissa, exp_digits + 1, int(exp))

    def convert_list_to_sci_not(input_list, prec, exp_digits):
        converted = []
        for flt in input_list:
            sci = convert_flt_to_sci_not(fltt=flt, prec=prec, exp_digits=exp_digits)
            converted.append(sci)

        return converted
    print(".")
    # %% import boundaries and convert to sci notation

    bnd_loc = pd.read_csv(boundaries_wave, names=['boundary', 'easting', 'northing'], )

    bnd_a = bnd_loc.iloc[::2]
    bnd_a = bnd_a.reset_index()

    bnd_a_boundary = bnd_a.iloc[:, 1].to_list()
    bnd_a_easting = bnd_a.iloc[:, 2].to_list()
    bnd_a_northing = bnd_a.iloc[:, 3].to_list()
    bnd_a_easting = convert_list_to_sci_not(input_list=bnd_a_easting, prec=7, exp_digits=3)
    bnd_a_northing = convert_list_to_sci_not(input_list=bnd_a_northing, prec=7, exp_digits=3)

    bnd_a = (pd.DataFrame([bnd_a_boundary, bnd_a_easting, bnd_a_northing])).T

    bnd_b = bnd_loc.iloc[1::2]
    bnd_b = bnd_b.reset_index()
    bnd_b_boundary = bnd_b.iloc[:, 1].to_list()
    bnd_b_easting = bnd_b.iloc[:, 2].to_list()
    bnd_b_northing = bnd_b.iloc[:, 3].to_list()
    bnd_b_easting = convert_list_to_sci_not(input_list=bnd_b_easting, prec=7, exp_digits=3)
    bnd_b_northing = convert_list_to_sci_not(input_list=bnd_b_northing, prec=7, exp_digits=3)

    bnd_b = (pd.DataFrame([bnd_b_boundary, bnd_b_easting, bnd_b_northing])).T
    print(".")
    # %% To look for an remove if the new file already exists
    try:
        os.remove(file_name)
    except FileNotFoundError:
        pass
    print(".")
    # %% Write first half of the mdw file
    line_number = []
    with open(mdw_file, 'r') as m:
        for number, lines in enumerate(m):
            if string_name in lines:
                line_number.append(number)
                break

    if np.count_nonzero(line_number) == 0:
        print("Please add atleast one Boundary in mdw file, it doesnt need to have the exact coordinates")

    with open(mdw_file, 'r') as m:
        with open(file_name, 'a') as f:
            for i in range(line_number[0]):
                line = m.readline()
                for element in line:
                    f.write(element)

    print(".")
    # %% Write second half of the mdw file

    for index in range(len(bnd_a)):
        bnd_header = ['[Boundary]',
                      f'   Name                 = {bnd_a.iloc[index,0][: -2]}                       ',
                      '   Definition           = xy-coordinates               ',
                      f'   StartCoordX          =  {bnd_a.iloc[index,1]}              ',
                      f'   EndCoordX            =  {bnd_b.iloc[index,1]}              ',
                      f'   StartCoordY          =  {bnd_a.iloc[index,2]}              ',
                      f'   EndCoordY            =  {bnd_b.iloc[index,2]}              ',
                      '   SpectrumSpec         = parametric                   ',
                      '   SpShapeType          = jonswap                      ',
                      '   PeriodType           = peak                         ',
                      '   DirSpreadType        = degrees                        ',
                      '   PeakEnhanceFac       =  3.3000000e+000              ',
                      '   GaussSpread          =  9.9999998e-003              ']

        with open(file_name, 'a') as mm:
            for one_line in bnd_header:
                mm.write(one_line)
                # f.write('\r\n')
                mm.write('\n')
    print(".")
