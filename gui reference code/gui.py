"""
A standalone gui companion connecting easygsh and delft3d.
Currently only for north sea data
GUI based on the source code:
https://github.com/capt-clay10/bct-bcw-mdw-grd_to_CSV_file_generator-for-EasyGSH-Delft3D.git


@author: Clayton Soares
"""
# %% define functions to run
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from ttkbootstrap import Style
import sys
from datetime import datetime
from datetime import timedelta
import output_methods
import extract_from_d3d_files
import os
import time
import bct_generator
import bct_year_overlap_file_generator
import bcw_generator
import bcw_year_overlap_file_generator
import mdw_writer
import sea_level_change


def browse_path():
    folder_selected = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, folder_selected)

# %% the actual code


def submit_choice():
    selected_choice = choice_var.get()
    if not path_entry.get():
        messagebox.showwarning(
            "Warning", "Please browse for a directory before submitting.")
    elif selected_choice == 0:
        messagebox.showwarning(
            "Warning", "Please select a file type before submitting.")

    elif selected_choice == 1:
        t = time.time()  # start the time counter

        new_window = tk.Toplevel(root)
        new_window.title("Generate all files")
        new_window.geometry('800x1000')
        new_window.grab_set()
        new_window.resizable(0, 0)

        # Function to browse for files
        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        main_frame = tk.Frame(new_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # % frame 1
        frameup = tk.Frame(main_frame, width=250, borderwidth=1, relief='solid')
        frameup.pack(side='left', fill='both', expand=True, padx=10)
        left_label = tk.Label(frameup, text="Flow Module",
                              font=("Helvetica", 16))
        left_label.pack(side='top', padx=10, pady=10)

        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='right', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Wave Module", font=("Helvetica", 16))
        right_label.pack(side='top', padx=10, pady=10)

        # % input buttons mdf
        mdf_label = tk.Label(frameup, text="MDF file:",
                             font='Helvetica').pack(pady=5)
        mdf_entry = tk.Entry(frameup, width=50)
        mdf_entry.pack()
        mdf_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(mdf_entry)).pack(pady=20)

        grd_label = tk.Label(frameup, text=".grd file (flow):",
                             font='Helvetica').pack(pady=5)
        grd_entry = tk.Entry(frameup, width=50)
        grd_entry.pack()
        grd_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(grd_entry)).pack(pady=20)

        bnd_label = tk.Label(frameup, text=".bnd file (flow):",
                             font='Helvetica').pack(pady=5)
        bnd_entry = tk.Entry(frameup, width=50)
        bnd_entry.pack()
        bnd_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(bnd_entry)).pack(pady=20)

        nc_label = tk.Label(
            frameup, text=".nc waterlevel file (EasyGSH):", font='Helvetica').pack(pady=5)
        nc_entry = tk.Entry(frameup, width=50)
        nc_entry.pack()
        nc_button = tk.Button(frameup, text="Browse",
                              command=lambda: browse_file(nc_entry)).pack(pady=20)

        # time step for extraction
        step_types = [
            "20 mins",
            "40 mins",
            "60 mins",
            "80 mins"]

        stepf_label = tk.Label(
            frameup, text="Time step for waterlevel extraction:", font='Helvetica').pack(pady=5)

        selected_step_f = tk.IntVar()

        for idx, step_type in enumerate(step_types, start=1):
            radio_button_f = tk.Radiobutton(frameup, text=step_type, variable=selected_step_f,
                                            value=idx)
            radio_button_f.pack(anchor='c')

        # % input buttons mdw
        mdw_label = tk.Label(framedown, text="MDW file:",
                             font='Helvetica').pack(pady=5)
        mdw_entry = tk.Entry(framedown, width=50)
        mdw_entry.pack()
        mdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(mdw_entry)).pack(pady=20)

        grdw_label = tk.Label(
            framedown, text=".grd file (wave):", font='Helvetica').pack(pady=5)
        grdw_entry = tk.Entry(framedown, width=50)
        grdw_entry.pack()
        grdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(grdw_entry)).pack(pady=20)

        bndw_label = tk.Label(
            framedown, text=".bnd file (wave):", font='Helvetica').pack(pady=5)
        bndw_entry = tk.Entry(framedown, width=50)
        bndw_entry.pack()
        bndw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bndw_entry)).pack(pady=20)

        ncw_label = tk.Label(
            framedown, text=".nc wave file (EasyGSH):", font='Helvetica').pack(pady=5)
        ncw_entry = tk.Entry(framedown, width=50)
        ncw_entry.pack()
        ncw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(ncw_entry)).pack(pady=20)

        stepw_label = tk.Label(
            framedown, text="Time step for wave extraction:", font='Helvetica').pack(pady=5)

        step_types_w = [
            "20 mins",
            "40 mins",
            "60 mins",
            "80 mins",
            "120 mins"]

        selected_step_w = tk.IntVar()

        for idx_w, step_type_w in enumerate(step_types_w, start=1):
            radio_button_w = tk.Radiobutton(framedown, variable=selected_step_w,
                                            text=step_type_w,
                                            value=idx_w)
            radio_button_w.pack(anchor='c')

        # build the console

        frame_console = tk.Frame(new_window, width=100,
                                 height=10, borderwidth=1, relief='solid')
        frame_console.pack(side='bottom', fill='both', padx=10, pady=10)

        # Create a Text widget to display console output
        console_output = tk.Text(
            frame_console, wrap=tk.WORD, width=80, height=10)
        console_output.pack(padx=10, pady=10)

        # Redirect sys.stdout to the Text widget
        class ConsoleRedirector:
            def __init__(self, text_widget):
                self.text_space = text_widget

            def write(self, message):
                self.text_space.insert(tk.END, message)
                self.text_space.see(tk.END)  # Automatically scroll to the end
                self.text_space.update_idletasks()  # Update the widget

        # Create an instance of ConsoleRedirector and redirect sys.stdout
        console_redirector = ConsoleRedirector(console_output)
        sys.stdout = console_redirector

        # submit to start extracting

        def check_submit():
            if not mdf_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .mdf file")
            elif not grd_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .grd (flow) file")
            elif not bnd_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .bnd (flow) file")
            elif not nc_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .nc waterlevel file")
            elif not mdw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .mdw file")
            elif not grdw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .grd (wave) file.")
            elif not bndw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .bnd (wave) file.")
            elif not ncw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .nc wave file.")
            else:

                # input files from browsed
                step_w = selected_step_w.get()
                step_f = selected_step_f.get()

                def step_number(step):
                    if step == 1:
                        step_c = 20
                    elif step == 2:
                        step_c = 40
                    elif step == 3:
                        step_c = 60
                    else:
                        step_c = 80
                    return step_c

                def step_number_w(step):
                    if step == 1:
                        step_c = 20
                    elif step == 2:
                        step_c = 40
                    elif step == 3:
                        step_c = 60
                    elif step == 4:
                        step_c = 80
                    else:
                        step_c = 120
                    return step_c

                step = step_number(step_f)
                step_wave = step_number_w(step_w)

                def value_from_txt_file(file, string_name):
                    file1 = open(file, "r")
                    for line in file1:
                        # checking string is present in line or not
                        if '=' in line:
                            if string_name in line:
                                val = line.split('=')
                                string_val = val[1].strip()
                                break
                                file1.close()  # close file
                            # else:
                                # print('{} is not in the file'.format(string_name))
                    return string_val

                # files

                mdf_file = mdf_entry.get()
                mdw_file = mdw_entry.get()
                grid_input = grd_entry.get()
                bnd_input = bnd_entry.get()
                grid_wave_input = grdw_entry.get()
                bnd_wave_input = bndw_entry.get()
                nc_file = nc_entry.get()
                nc_file_wave = ncw_entry.get()

                # Extract start and end time from mdf file
                string1 = 'Tstart'
                tstart_val = value_from_txt_file(
                    file=mdf_file, string_name=string1)
                string2 = 'Tstop'
                tstop_val = value_from_txt_file(
                    file=mdf_file, string_name=string2)
                string3 = 'Itdate'  # reference time
                ref_time_unedited = value_from_txt_file(
                    file=mdf_file, string_name=string3)
                start = float(tstart_val)  # from mdf file
                stop = float(tstop_val)  # from mdf file
                ref_time = ref_time_unedited[1:11]
                # remove the hyphen for the bct file format
                reference_time = ref_time.replace('-', '')
                # extract start time and end time from mdf
                time_start = ref_time+" 00:00:00"  # Assuming it always starts at 00
                date_format_str = "%Y-%m-%d %H:%M:%S"
                # Calculate number of hours between ref time and sim time
                start_time_steps = int(start/60)  # to convert minutes to hours
                end_time_steps = int(stop/60)
                # create datetime object from timestamp string
                extracted_time = datetime.strptime(time_start, date_format_str)
                start_time = extracted_time + timedelta(hours=start_time_steps)
                # Convert datetime object to string in specific format
                start_time = start_time .strftime("%Y-%m-%d %H:%M:%S")
                end_time = extracted_time + timedelta(hours=end_time_steps)
                end_time = end_time .strftime("%Y-%m-%d %H:%M:%S")
                print('.')
                print('.')
                print('.')
                print('.')
                print("1 of 6")

                # %% output files
                # Use mdf file to extract bct file name and output file
                name_with_dot = mdf_file.partition('.')
                name_until_dot = name_with_dot[0]
                bct_file_name = '{}.bct'.format(name_until_dot)
                path_out_file = '{}.csv'.format(name_until_dot)

                # Use mdw file to extract bcw file name and output file
                wave_name_with_dot = mdw_file.partition('.')
                wave_name_until_dot = wave_name_with_dot[0]
                bcw_file = '{}.bcw'.format(wave_name_until_dot)
                wave_path_out_file = '{}.csv'.format(wave_name_until_dot)
                print('.')
                print("2 of 6")
                print('.')
                print('.')

                # %% Create the csv file for flow boundaries
                bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_input)

                coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_input,
                    request_list=bnd_grd_indices_output)

                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)
                print('.')
                print('.')
                print('.')
                print('The process of creating',
                      'the boundary location csv file for flow is completed - 3 of 6')
                print('.')
                print('.')
                print('.')

                # %% Create the csv file for wave boundaries
                bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_wave_input)

                coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_wave_input,
                    request_list=bnd_wave_grd_indices_output)

                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)
                print('.')
                print('.')
                print('.')
                print('The process of creating',
                      ' the boundary location csv file for Wave is completed - 4 of 6')

                # %% Create the bct file
                boundaries = path_out_file  # the csv file generated from process one
                bct = bct_generator.bct_file_generator(
                    boundaries=boundaries, nc_file=nc_file, mdf_file=mdf_file, step=step,
                    bct_file_name=bct_file_name)

                t_2 = time.time()

                # %% end the time counter
                print('.')
                print('The process of extracting water level has now completed in : ')
                elapsed = time.time() - t
                print(str(elapsed) + " sec - 5 of 6")

                # %% Create the bcw file
                boundaries_wave = wave_path_out_file
                bcw = bcw_generator.bcw_file_generator(
                    boundaries_wave=boundaries_wave, nc_file_wave=nc_file_wave, mdw_file=mdw_file, start_time=start_time,
                    end_time=end_time, step_wave=step_wave, bcw_file_name=bcw_file)

                print('.')
                print(
                    'The process of extracting wave boundary conditions has now completed in : ')
                elapsed = time.time() - t_2
                print(str(elapsed) + " sec - 6 of 6")
                print('.')
                print('.')
                print('.')
                # %% Write the new mdw file
                mdw_writer.write_mdw_file(
                    mdw_file=mdw_file, boundaries_wave=boundaries_wave)
                print('New mdw file created')
                print('.')
                elapsed_final = time.time() - t
                print(
                    f'Total time taken for both files is {elapsed_final/60} mins')

        # %% end of main code for choice 1
        frame_submit = tk.Frame(new_window, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit)
        submit_button.pack(pady=10, anchor='s')

    elif selected_choice == 2:  # bct nly
        t = time.time()  # start the time counter

        new_window = tk.Toplevel(root)
        new_window.title("Bct file generator")
        # new_window.geometry('800x950')
        new_window.grab_set()
        new_window.resizable(0, 0)

        # Function to browse for files
        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        main_frame = tk.Frame(new_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # % frame 1
        frameup = tk.Frame(main_frame, width=250, borderwidth=1, relief='solid')
        frameup.pack(side='left', fill='both', expand=True, padx=10)
        left_label = tk.Label(frameup, text="Flow Module",
                              font=("Helvetica", 16))
        left_label.pack(side='top', padx=10, pady=10)

        # % input buttons mdf
        mdf_label = tk.Label(frameup, text="MDF file:",
                             font='Helvetica').pack(pady=5)
        mdf_entry = tk.Entry(frameup, width=50)
        mdf_entry.pack()
        mdf_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(mdf_entry)).pack(pady=20)

        grd_label = tk.Label(frameup, text=".grd file (flow):",
                             font='Helvetica').pack(pady=5)
        grd_entry = tk.Entry(frameup, width=50)
        grd_entry.pack()
        grd_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(grd_entry)).pack(pady=20)

        bnd_label = tk.Label(frameup, text=".bnd file (flow):",
                             font='Helvetica').pack(pady=5)
        bnd_entry = tk.Entry(frameup, width=50)
        bnd_entry.pack()
        bnd_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(bnd_entry)).pack(pady=20)

        nc_label = tk.Label(
            frameup, text=".nc waterlevel file (EasyGSH):", font='Helvetica').pack(pady=5)
        nc_entry = tk.Entry(frameup, width=50)
        nc_entry.pack()
        nc_button = tk.Button(frameup, text="Browse",
                              command=lambda: browse_file(nc_entry)).pack(pady=20)

        # time step for extraction
        step_types = [
            "20 mins",
            "40 mins",
            "60 mins",
            "80 mins"]

        stepf_label = tk.Label(
            frameup, text="Time step for waterlevel extraction:", font='Helvetica').pack(pady=5)

        selected_step_f = tk.IntVar()

        for idx, step_type in enumerate(step_types, start=1):
            radio_button_f = tk.Radiobutton(frameup, text=step_type, variable=selected_step_f,
                                            value=idx)
            radio_button_f.pack(anchor='c')

        # build the console

        frame_console = tk.Frame(new_window, width=100,
                                 height=10, borderwidth=1, relief='solid')
        frame_console.pack(side='bottom', fill='both', padx=10, pady=10)

        # Create a Text widget to display console output
        console_output = tk.Text(
            frame_console, wrap=tk.WORD, width=80, height=10)
        console_output.pack(padx=10, pady=10)

        # Redirect sys.stdout to the Text widget
        class ConsoleRedirector:
            def __init__(self, text_widget):
                self.text_space = text_widget

            def write(self, message):
                self.text_space.insert(tk.END, message)
                self.text_space.see(tk.END)  # Automatically scroll to the end
                self.text_space.update_idletasks()  # Update the widget

        # Create an instance of ConsoleRedirector and redirect sys.stdout
        console_redirector = ConsoleRedirector(console_output)
        sys.stdout = console_redirector

        # submit to start extracting

        def check_submit():
            if not mdf_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .mdf file")
            elif not grd_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .grd (flow) file")
            elif not bnd_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .bnd (flow) file")
            elif not nc_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .nc waterlevel file")
            else:

                # input files from browsed
                step_f = selected_step_f.get()

                def step_number(step):
                    if step == 1:
                        step_c = 20
                    elif step == 2:
                        step_c = 40
                    elif step == 3:
                        step_c = 60
                    else:
                        step_c = 80
                    return step_c

                step = step_number(step_f)

                def value_from_txt_file(file, string_name):
                    file1 = open(file, "r")
                    for line in file1:
                        # checking string is present in line or not
                        if '=' in line:
                            if string_name in line:
                                val = line.split('=')
                                string_val = val[1].strip()
                                break
                                file1.close()  # close file
                            # else:
                                # print('{} is not in the file'.format(string_name))
                    return string_val

                # files
                mdf_file = mdf_entry.get()
                grid_input = grd_entry.get()
                bnd_input = bnd_entry.get()
                nc_file = nc_entry.get()

                # %% output files
                # Use mdf file to extract bct file and output file
                name_with_dot = mdf_file.partition('.')
                name_until_dot = name_with_dot[0]
                bct_file_name = '{}.bct'.format(name_until_dot)
                path_out_file = '{}.csv'.format(name_until_dot)
                print('.')
                print("1 of 3")

                # %% Create the csv file for flow boundaries
                bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_input)

                coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_input,
                    request_list=bnd_grd_indices_output)

                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)
                print('.')
                print('.')
                print('.')
                print('The process of creating',
                      'the boundary location csv file for flow is completed - 2 of 3')

                # %% Create the bct file
                boundaries = path_out_file  # the csv file generated from process one
                bct = bct_generator.bct_file_generator(
                    boundaries=boundaries, nc_file=nc_file, mdf_file=mdf_file, step=step,
                    bct_file_name=bct_file_name)

                # %% end the time counter
                print('.')
                print('The process of extracting water level has now completed in : ')
                elapsed = time.time() - t
                print(str(elapsed) + " sec - 3 of 3")

        # %% end of main code for choice 1
        frame_submit = tk.Frame(new_window, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit)
        submit_button.pack(pady=10, anchor='s')

    elif selected_choice == 3:  # bct only over two years
        t = time.time()  # start the time counter

        new_window = tk.Toplevel(root)
        new_window.title("Generate Bct file overlapping over two years")
        # new_window.geometry('800x950')
        new_window.grab_set()
        new_window.resizable(0, 0)

        # Function to browse for files
        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        main_frame = tk.Frame(new_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # % frame 1
        frameup = tk.Frame(main_frame, width=250, borderwidth=1, relief='solid')
        frameup.pack(side='left', fill='both', expand=True, padx=10)
        left_label = tk.Label(frameup, text="Flow Module",
                              font=("Helvetica", 16))
        left_label.pack(side='top', padx=10, pady=10)

        # % input buttons mdf
        mdf_label = tk.Label(frameup, text="MDF file:",
                             font='Helvetica').pack(pady=5)
        mdf_entry = tk.Entry(frameup, width=50)
        mdf_entry.pack()
        mdf_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(mdf_entry)).pack(pady=20)

        grd_label = tk.Label(frameup, text=".grd file (flow):",
                             font='Helvetica').pack(pady=5)
        grd_entry = tk.Entry(frameup, width=50)
        grd_entry.pack()
        grd_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(grd_entry)).pack(pady=20)

        bnd_label = tk.Label(frameup, text=".bnd file (flow):",
                             font='Helvetica').pack(pady=5)
        bnd_entry = tk.Entry(frameup, width=50)
        bnd_entry.pack()
        bnd_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(bnd_entry)).pack(pady=20)

        nc_label = tk.Label(
            frameup, text=".nc waterlevel file (EasyGSH):", font='Helvetica').pack(pady=5)
        nc_entry = tk.Entry(frameup, width=50)
        nc_entry.pack()
        nc_button = tk.Button(frameup, text="Browse",
                              command=lambda: browse_file(nc_entry)).pack(pady=20)

        nc_label_2 = tk.Label(
            frameup, text=".nc waterlevel file- part 2 (EasyGSH):", font='Helvetica').pack(pady=5)
        nc_entry_2 = tk.Entry(frameup, width=50)
        nc_entry_2.pack()
        nc_button_2 = tk.Button(frameup, text="Browse",
                                command=lambda: browse_file(nc_entry_2)).pack(pady=20)

        # time step for extraction
        step_types = [
            "20 mins",
            "40 mins",
            "60 mins",
            "80 mins"]

        stepf_label = tk.Label(
            frameup, text="Time step for waterlevel extraction:", font='Helvetica').pack(pady=5)

        selected_step_f = tk.IntVar()

        for idx, step_type in enumerate(step_types, start=1):
            radio_button_f = tk.Radiobutton(frameup, text=step_type, variable=selected_step_f,
                                            value=idx)
            radio_button_f.pack(anchor='c')

        # build the console

        frame_console = tk.Frame(new_window, width=100,
                                 height=10, borderwidth=1, relief='solid')
        frame_console.pack(side='bottom', fill='both', padx=10, pady=10)

        # Create a Text widget to display console output
        console_output = tk.Text(
            frame_console, wrap=tk.WORD, width=80, height=10)
        console_output.pack(padx=10, pady=10)

        # Redirect sys.stdout to the Text widget
        class ConsoleRedirector:
            def __init__(self, text_widget):
                self.text_space = text_widget

            def write(self, message):
                self.text_space.insert(tk.END, message)
                self.text_space.see(tk.END)  # Automatically scroll to the end
                self.text_space.update_idletasks()  # Update the widget

        # Create an instance of ConsoleRedirector and redirect sys.stdout
        console_redirector = ConsoleRedirector(console_output)
        sys.stdout = console_redirector

        # submit to start extracting

        def check_submit():
            if not mdf_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .mdf file")
            elif not grd_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .grd (flow) file")
            elif not bnd_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .bnd (flow) file")
            elif not nc_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .nc waterlevel file")
            elif not nc_entry_2.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the second .nc waterlevel file")
            else:

                # input files from browsed
                step_f = selected_step_f.get()

                def step_number(step):
                    if step == 1:
                        step_c = 20
                    elif step == 2:
                        step_c = 40
                    elif step == 3:
                        step_c = 60
                    else:
                        step_c = 80
                    return step_c

                step = step_number(step_f)

                def value_from_txt_file(file, string_name):
                    file1 = open(file, "r")
                    for line in file1:
                        # checking string is present in line or not
                        if '=' in line:
                            if string_name in line:
                                val = line.split('=')
                                string_val = val[1].strip()
                                break
                                file1.close()  # close file
                            # else:
                                # print('{} is not in the file'.format(string_name))
                    return string_val

                # files
                mdf_file = mdf_entry.get()
                grid_input = grd_entry.get()
                bnd_input = bnd_entry.get()
                nc_file = nc_entry.get()
                nc_file_2 = nc_entry_2.get()

                # %% output files
                # Use mdf file to extract bct file and output file
                name_with_dot = mdf_file.partition('.')
                name_until_dot = name_with_dot[0]
                bct_file_name = '{}.bct'.format(name_until_dot)
                path_out_file = '{}.csv'.format(name_until_dot)
                print('.')
                print("1 of 3")

                # %% Create the csv file for flow boundaries
                bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_input)

                coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_input,
                    request_list=bnd_grd_indices_output)

                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)
                print('.')
                print('.')
                print('.')
                print('The process of creating',
                      'the boundary location csv file for flow is completed - 2 of 3')

                # %% Create the bct file
                boundaries = path_out_file  # the csv file generated from process one
                bct = bct_year_overlap_file_generator.bct_year_overlap_file_generator(
                    boundaries=boundaries, nc_file_year1=nc_file,
                    nc_file_year2=nc_file_2, mdf_file=mdf_file, step=step,
                    bct_file_name=bct_file_name)

                # %% end the time counter
                print('.')
                print('The process of extracting water level has now completed in : ')
                elapsed = time.time() - t
                print(str(elapsed) + " sec - 3 of 3")

        # %% end of main code for choice 1
        frame_submit = tk.Frame(new_window, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit)
        submit_button.pack(pady=10, anchor='s')

    elif selected_choice == 4:  # bcw only
        t = time.time()  # start the time counter

        new_window = tk.Toplevel(root)
        new_window.title("Bcw file generator")
        new_window.geometry('800x1250')
        new_window.grab_set()
        new_window.resizable(0, 0)

        # Function to browse for files
        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        main_frame = tk.Frame(new_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Wave Module", font=("Helvetica", 16))
        right_label.pack(side='top', padx=10, pady=10)

        # % input buttons mdw
        mdw_label = tk.Label(framedown, text="MDW file:",
                             font='Helvetica').pack(pady=5)
        mdw_entry = tk.Entry(framedown, width=50)
        mdw_entry.pack()
        mdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(mdw_entry)).pack(pady=20)

        grdw_label = tk.Label(
            framedown, text=".grd file (wave):", font='Helvetica').pack(pady=5)
        grdw_entry = tk.Entry(framedown, width=50)
        grdw_entry.pack()
        grdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(grdw_entry)).pack(pady=20)

        bndw_label = tk.Label(
            framedown, text=".bnd file (wave):", font='Helvetica').pack(pady=5)
        bndw_entry = tk.Entry(framedown, width=50)
        bndw_entry.pack()
        bndw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bndw_entry)).pack(pady=20)

        ncw_label = tk.Label(
            framedown, text=".nc wave file (EasyGSH):", font='Helvetica').pack(pady=5)
        ncw_entry = tk.Entry(framedown, width=50)
        ncw_entry.pack()
        ncw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(ncw_entry)).pack(pady=20)

        frameright = tk.Frame(main_frame, width=250,
                              borderwidth=1, relief='solid')
        frameright.pack(fill='both', expand=True, padx=10)

        stepw_label = tk.Label(
            frameright, text="Time step for wave extraction:", font='Helvetica').pack(pady=5)

        step_types_w = [
            "20 mins",
            "40 mins",
            "60 mins",
            "80 mins",
            "120 mins"]

        selected_step_w = tk.IntVar()

        for idx_w, step_type_w in enumerate(step_types_w, start=1):
            radio_button_w = tk.Radiobutton(frameright, variable=selected_step_w,
                                            text=step_type_w,
                                            value=idx_w)
            radio_button_w.pack(anchor='c')

        # get the date from a drop down
        # Create a function to handle the selection from the dropdown menus

        framedate = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedate.pack(anchor='s', fill='both', expand=True, padx=10)

        frame_date_label = tk.Label(
            framedate, text="Start date", font=("Helvetica", 16))
        frame_date_label.pack(side='top', padx=10, pady=10)

        framedate_end = tk.Frame(main_frame, width=250,
                                 borderwidth=1, relief='solid')
        framedate_end.pack(anchor='s', fill='both', expand=True, padx=10)

        frame_date_end_label = tk.Label(
            framedate_end, text="End date", font=("Helvetica", 16))
        frame_date_end_label.pack(side='top', padx=10, pady=10)

        # start date
        s_date_label = tk.Label(
            framedate, text="start date of simulation (YYYY-mm-dd HH:MM:SS):", font='Helvetica').pack(pady=5)
        s_date_entry = tk.Entry(framedate, width=50)
        s_date_entry.pack(pady=5)

        # end date
        e_date_label = tk.Label(
            framedate_end, text="end date of simulation (YYYY-mm-dd HH:MM:SS):", font='Helvetica').pack(pady=5)
        e_date_entry = tk.Entry(framedate_end, width=50)
        e_date_entry.pack(pady=5)

        # build the console

        frame_console = tk.Frame(new_window, width=100,
                                 height=10, borderwidth=1, relief='solid')
        frame_console.pack(side='bottom', fill='both', padx=10, pady=10)

        # Create a Text widget to display console output
        console_output = tk.Text(
            frame_console, wrap=tk.WORD, width=80, height=10)
        console_output.pack(padx=10, pady=10)

        # Redirect sys.stdout to the Text widget
        class ConsoleRedirector:
            def __init__(self, text_widget):
                self.text_space = text_widget

            def write(self, message):
                self.text_space.insert(tk.END, message)
                self.text_space.see(tk.END)  # Automatically scroll to the end
                self.text_space.update_idletasks()  # Update the widget

        # Create an instance of ConsoleRedirector and redirect sys.stdout
        console_redirector = ConsoleRedirector(console_output)
        sys.stdout = console_redirector

        # submit to start extracting

        def check_submit():

            if not mdw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .mdw file")
            elif not grdw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .grd (wave) file.")
            elif not bndw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .bnd (wave) file.")
            elif not ncw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .nc wave file.")

            elif not s_date_entry.get():
                messagebox.showwarning(
                    "Warning", "Please write the start date for simulation.")

            elif not e_date_entry.get():
                messagebox.showwarning(
                    "Warning", "Please write the end date for simulation.")

            else:

                # input files from browsed
                step_w = selected_step_w.get()

                def step_number(step):
                    if step == 1:
                        step_c = 20
                    elif step == 2:
                        step_c = 40
                    elif step == 3:
                        step_c = 60
                    elif step == 4:
                        step_c = 80
                    else:
                        step_c = 120
                    return step_c

                step_wave = step_number(step_w)

                def value_from_txt_file(file, string_name):
                    file1 = open(file, "r")
                    for line in file1:
                        # checking string is present in line or not
                        if '=' in line:
                            if string_name in line:
                                val = line.split('=')
                                string_val = val[1].strip()
                                break
                                file1.close()  # close file
                            # else:
                                # print('{} is not in the file'.format(string_name))
                    return string_val

                # files

                mdw_file = mdw_entry.get()
                grid_wave_input = grdw_entry.get()
                bnd_wave_input = bndw_entry.get()
                nc_file_wave = ncw_entry.get()
                start_time = s_date_entry.get()
                end_time = e_date_entry.get()

                # %% bcw output file
                # Use mdw file to extract bcw file and output file
                wave_name_with_dot = mdw_file.partition('.')
                wave_name_until_dot = wave_name_with_dot[0]
                bcw_file = '{}.bcw'.format(wave_name_until_dot)
                wave_path_out_file = '{}.csv'.format(wave_name_until_dot)
                print('.')
                print("1 of 3")

                # %% Create the csv file for wave boundaries
                bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_wave_input)

                coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_wave_input,
                    request_list=bnd_wave_grd_indices_output)

                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)
                print('.')
                print('.')
                print('.')
                print('The process of creating',
                      ' the boundary location csv file for wave is completed - 2 of 3')
                print('.')
                print('.')
                print('.')
                print('Initiating wave parameter extraction')

                # %% Create the bcw file
                boundaries_wave = wave_path_out_file
                bcw = bcw_generator.bcw_file_generator(
                    boundaries_wave=boundaries_wave, nc_file_wave=nc_file_wave,
                    mdw_file=mdw_file, start_time=start_time,
                    end_time=end_time, step_wave=step_wave, bcw_file_name=bcw_file)
                print('.')
                print(
                    'The process of extracting wave boundary conditions has now completed in : ')
                elapsed = time.time() - t
                print(str(elapsed) + " sec - 3 of 3")
                print('.')
                print('.')
                # %% Write the new mdw file
                mdw_writer.write_mdw_file(
                    mdw_file=mdw_file, boundaries_wave=boundaries_wave)
                print('New mdw file created')

        # %% end of main code for choice 1
        frame_submit = tk.Frame(new_window, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit)
        submit_button.pack(pady=10, anchor='s')

    elif selected_choice == 5:  # bcw over two years
        t = time.time()  # start the time counter

        new_window = tk.Toplevel(root)
        new_window.title("Generate Bcw file overlapping over two years")
        new_window.geometry('800x1500')
        new_window.grab_set()
        new_window.resizable(0, 0)

        # Function to browse for files
        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        main_frame = tk.Frame(new_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Wave Module", font=("Helvetica", 16))
        right_label.pack(side='top', padx=10, pady=10)

        # % input buttons mdw
        mdw_label = tk.Label(framedown, text="MDW file:",
                             font='Helvetica').pack(pady=5)
        mdw_entry = tk.Entry(framedown, width=50)
        mdw_entry.pack()
        mdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(mdw_entry)).pack(pady=20)

        grdw_label = tk.Label(
            framedown, text=".grd file (wave):", font='Helvetica').pack(pady=5)
        grdw_entry = tk.Entry(framedown, width=50)
        grdw_entry.pack()
        grdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(grdw_entry)).pack(pady=20)

        bndw_label = tk.Label(
            framedown, text=".bnd file (wave):", font='Helvetica').pack(pady=5)
        bndw_entry = tk.Entry(framedown, width=50)
        bndw_entry.pack()
        bndw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bndw_entry)).pack(pady=20)

        ncw_label = tk.Label(
            framedown, text=".nc wave file (EasyGSH):", font='Helvetica').pack(pady=5)
        ncw_entry = tk.Entry(framedown, width=50)
        ncw_entry.pack()
        ncw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(ncw_entry)).pack(pady=20)

        ncw2_label = tk.Label(
            framedown, text=".nc wave file part 2 (EasyGSH):", font='Helvetica').pack(pady=5)
        ncw2_entry = tk.Entry(framedown, width=50)
        ncw2_entry.pack()
        ncw2_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(ncw2_entry)).pack(pady=20)

        frameright = tk.Frame(main_frame, width=250,
                              borderwidth=1, relief='solid')
        frameright.pack(fill='both', expand=True, padx=10)

        stepw_label = tk.Label(
            frameright, text="Time step for wave extraction:", font='Helvetica').pack(pady=5)

        step_types_w = [
            "20 mins",
            "40 mins",
            "60 mins",
            "80 mins",
            "120 mins"]

        selected_step_w = tk.IntVar()

        for idx_w, step_type_w in enumerate(step_types_w, start=1):
            radio_button_w = tk.Radiobutton(frameright, variable=selected_step_w,
                                            text=step_type_w,
                                            value=idx_w)
            radio_button_w.pack(anchor='c')

        # get the date from a drop down
        # Create a function to handle the selection from the dropdown menus

        framedate = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedate.pack(anchor='s', fill='both', expand=True, padx=10)

        frame_date_label = tk.Label(
            framedate, text="Start date", font=("Helvetica", 16))
        frame_date_label.pack(side='top', padx=10, pady=10)

        framedate_end = tk.Frame(main_frame, width=250,
                                 borderwidth=1, relief='solid')
        framedate_end.pack(anchor='s', fill='both', expand=True, padx=10)

        frame_date_end_label = tk.Label(
            framedate_end, text="End date", font=("Helvetica", 16))
        frame_date_end_label.pack(side='top', padx=10, pady=10)

        # start date
        s_date_label = tk.Label(
            framedate, text="start date of simulation (YYYY-mm-dd HH:MM:SS):", font='Helvetica').pack(pady=5)
        s_date_entry = tk.Entry(framedate, width=50)
        s_date_entry.pack(pady=5)

        # end date
        e_date_label = tk.Label(
            framedate_end, text="end date of simulation (YYYY-mm-dd HH:MM:SS):", font='Helvetica').pack(pady=5)
        e_date_entry = tk.Entry(framedate_end, width=50)
        e_date_entry.pack(pady=5)

        # build the console

        frame_console = tk.Frame(new_window, width=100,
                                 height=10, borderwidth=1, relief='solid')
        frame_console.pack(side='bottom', fill='both', padx=10, pady=10)

        # Create a Text widget to display console output
        console_output = tk.Text(
            frame_console, wrap=tk.WORD, width=80, height=10)
        console_output.pack(padx=10, pady=10)

        # Redirect sys.stdout to the Text widget
        class ConsoleRedirector:
            def __init__(self, text_widget):
                self.text_space = text_widget

            def write(self, message):
                self.text_space.insert(tk.END, message)
                self.text_space.see(tk.END)  # Automatically scroll to the end
                self.text_space.update_idletasks()  # Update the widget

        # Create an instance of ConsoleRedirector and redirect sys.stdout
        console_redirector = ConsoleRedirector(console_output)
        sys.stdout = console_redirector

        # submit to start extracting

        def check_submit():

            if not mdw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .mdw file")
            elif not grdw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .grd (wave) file.")
            elif not bndw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .bnd (wave) file.")
            elif not ncw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .nc wave file.")

            elif not ncw2_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .nc wave file part 2.")

            elif not s_date_entry.get():
                messagebox.showwarning(
                    "Warning", "Please write the start date for simulation.")

            elif not e_date_entry.get():
                messagebox.showwarning(
                    "Warning", "Please write the end date for simulation.")
            else:

                # input files from browsed
                step_w = selected_step_w.get()

                def step_number(step):
                    if step == 1:
                        step_c = 20
                    elif step == 2:
                        step_c = 40
                    elif step == 3:
                        step_c = 60
                    elif step == 4:
                        step_c = 80
                    else:
                        step_c = 120
                    return step_c

                step_wave = step_number(step_w)

                def value_from_txt_file(file, string_name):
                    file1 = open(file, "r")
                    for line in file1:
                        # checking string is present in line or not
                        if '=' in line:
                            if string_name in line:
                                val = line.split('=')
                                string_val = val[1].strip()
                                break
                                file1.close()  # close file
                            # else:
                                # print('{} is not in the file'.format(string_name))
                    return string_val

                # files

                mdw_file = mdw_entry.get()
                grid_wave_input = grdw_entry.get()
                bnd_wave_input = bndw_entry.get()
                nc_file_wave = ncw_entry.get()
                nc_file_wave_2 = ncw2_entry.get()
                start_time = s_date_entry.get()
                end_time = e_date_entry.get()

                # %% bcw output file
                # Use mdw file to extract bcw file and output file
                wave_name_with_dot = mdw_file.partition('.')
                wave_name_until_dot = wave_name_with_dot[0]
                bcw_file = '{}.bcw'.format(wave_name_until_dot)
                wave_path_out_file = '{}.csv'.format(wave_name_until_dot)
                print('.')
                print("1 of 3")

                # %% Create the csv file for wave boundaries
                bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_wave_input)

                coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_wave_input,
                    request_list=bnd_wave_grd_indices_output)

                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)
                print('.')
                print('.')
                print('.')
                print('The process of creating',
                      ' the boundary location csv file for wave is completed - 2 of 3')
                print('.')
                print('.')
                print('.')
                print('Initiating wave parameter extraction')

                # %% Create the bcw file
                boundaries_wave = wave_path_out_file
                bcw = bcw_year_overlap_file_generator.bcw_year_overlap_file_generator(
                    boundaries_wave=boundaries_wave, nc_file_wave_year1=nc_file_wave,
                    nc_file_wave_year2=nc_file_wave_2,     mdw_file=mdw_file, start_time=start_time,
                    end_time=end_time, step_wave=step_wave, bcw_file_name=bcw_file)
                print('.')
                print(
                    'The process of extracting wave boundary conditions has now completed in : ')
                elapsed = time.time() - t
                print(str(elapsed) + " sec - 3 of 3")
                print('.')
                print('.')
                # %% Write the new mdw file
                mdw_writer.write_mdw_file(
                    mdw_file=mdw_file, boundaries_wave=boundaries_wave)
                print('New mdw file created')

        # %% end of main code for choice 1
        frame_submit = tk.Frame(new_window, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit)
        submit_button.pack(pady=10, anchor='s')

    elif selected_choice == 6:  # boundary conditions file
        t = time.time()  # start the time counter

        new_window = tk.Toplevel(root)
        new_window.title("Boundary location file (csv) Generator")
        new_window.geometry('800x600')
        new_window.grab_set()
        new_window.resizable(0, 0)

        # Function to browse for files
        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        main_frame = tk.Frame(new_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Wave/Flow module", font=("Helvetica", 16))
        right_label.pack(side='top', padx=10, pady=10)

        # % input buttons

        grdw_label = tk.Label(
            framedown, text=".grd file:", font='Helvetica').pack(pady=5)
        grdw_entry = tk.Entry(framedown, width=50)
        grdw_entry.pack()
        grdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(grdw_entry)).pack(pady=20)

        bndw_label = tk.Label(
            framedown, text=".bnd file:", font='Helvetica').pack(pady=5)
        bndw_entry = tk.Entry(framedown, width=50)
        bndw_entry.pack()
        bndw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bndw_entry)).pack(pady=20)

        # build the console

        frame_console = tk.Frame(new_window, width=100,
                                 height=10, borderwidth=1, relief='solid')
        frame_console.pack(side='bottom', fill='both', padx=10, pady=10)

        # Create a Text widget to display console output
        console_output = tk.Text(
            frame_console, wrap=tk.WORD, width=80, height=10)
        console_output.pack(padx=10, pady=10)

        # Redirect sys.stdout to the Text widget
        class ConsoleRedirector:
            def __init__(self, text_widget):
                self.text_space = text_widget

            def write(self, message):
                self.text_space.insert(tk.END, message)
                self.text_space.see(tk.END)  # Automatically scroll to the end
                self.text_space.update_idletasks()  # Update the widget

        # Create an instance of ConsoleRedirector and redirect sys.stdout
        console_redirector = ConsoleRedirector(console_output)
        sys.stdout = console_redirector

        # submit to start extracting

        def check_submit():

            if not grdw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .grd file.")
            elif not bndw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .bnd file.")
            else:

                # files

                grid_input = grdw_entry.get()
                bnd_input = bndw_entry.get()

                # Use grid file to extract bct file and output file
                wave_name_with_dot = grid_input.partition('.')
                wave_name_until_dot = wave_name_with_dot[0]
                wave_path_out_file = '{}.csv'.format(wave_name_until_dot)
                print('.')
                print("1 of 2")

                # %% Create the csv file for wave boundaries
                bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_input)

                coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_input,
                    request_list=bnd_wave_grd_indices_output)

                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)
                print('.')
                print('.')
                print('.')
                print('The process of creating',
                      ' the boundary location csv file is completed - 2 of 2')

        # %% end of main code for choice 1
        frame_submit = tk.Frame(new_window, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit)
        submit_button.pack(pady=10, anchor='s')

    elif selected_choice == 7:  # boundary conditions file and mdw file
        t = time.time()  # start the time counter

        new_window = tk.Toplevel(root)
        new_window.title("Boundary location and mdw file generator")
        new_window.geometry('800x600')
        new_window.grab_set()
        new_window.resizable(0, 0)

        # Function to browse for files
        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        main_frame = tk.Frame(new_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Wave Module", font=("Helvetica", 16))
        right_label.pack(side='top', padx=10, pady=10)

        # % input buttons

        grdw_label = tk.Label(
            framedown, text=".grd file:", font='Helvetica').pack(pady=5)
        grdw_entry = tk.Entry(framedown, width=50)
        grdw_entry.pack()
        grdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(grdw_entry)).pack(pady=20)

        bndw_label = tk.Label(
            framedown, text=".bnd file:", font='Helvetica').pack(pady=5)
        bndw_entry = tk.Entry(framedown, width=50)
        bndw_entry.pack()
        bndw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bndw_entry)).pack(pady=20)

        mdw_label = tk.Label(framedown, text="MDW file:",
                             font='Helvetica').pack(pady=5)
        mdw_entry = tk.Entry(framedown, width=50)
        mdw_entry.pack()
        mdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(mdw_entry)).pack(pady=20)

        # build the console

        frame_console = tk.Frame(new_window, width=100,
                                 height=10, borderwidth=1, relief='solid')
        frame_console.pack(side='bottom', fill='both', padx=10, pady=10)

        # Create a Text widget to display console output
        console_output = tk.Text(
            frame_console, wrap=tk.WORD, width=80, height=10)
        console_output.pack(padx=10, pady=10)

        # Redirect sys.stdout to the Text widget
        class ConsoleRedirector:
            def __init__(self, text_widget):
                self.text_space = text_widget

            def write(self, message):
                self.text_space.insert(tk.END, message)
                self.text_space.see(tk.END)  # Automatically scroll to the end
                self.text_space.update_idletasks()  # Update the widget

        # Create an instance of ConsoleRedirector and redirect sys.stdout
        console_redirector = ConsoleRedirector(console_output)
        sys.stdout = console_redirector

        # submit to start extracting

        def check_submit():

            if not grdw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .grd file.")
            elif not bndw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .bnd file.")
            elif not mdw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .mdw file.")
            else:

                # files

                grid_input = grdw_entry.get()
                bnd_input = bndw_entry.get()
                mdw_file = mdw_entry.get()

                # Use grid file to extract bct file and output file
                wave_name_with_dot = grid_input.partition('.')
                wave_name_until_dot = wave_name_with_dot[0]
                wave_path_out_file = '{}.csv'.format(wave_name_until_dot)
                print('.')
                print("1 of 3")

                # %% Create the csv file for wave boundaries
                bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_input)

                coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_input,
                    request_list=bnd_wave_grd_indices_output)

                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)
                print('.')
                print('.')
                print('.')
                print('The process of creating',
                      ' the boundary location csv file is completed - 2 of 3')

                # %% create mdw file
                boundaries_wave = wave_path_out_file
                mdw_writer.write_mdw_file(
                    mdw_file=mdw_file, boundaries_wave=boundaries_wave)
                print('New mdw file created')

        # %% end of main code for choice 1
        frame_submit = tk.Frame(new_window, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit)
        submit_button.pack(pady=10, anchor='s')

    elif selected_choice == 8:  # Add sea level changes to bct file
        t = time.time()  # start the time counter

        new_window = tk.Toplevel(root)
        new_window.title("Add sea level to .bct file")
        new_window.geometry('800x600')
        new_window.grab_set()
        new_window.resizable(0, 0)

        # Function to browse for files
        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        main_frame = tk.Frame(new_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Flow Module", font=("Helvetica", 16))
        right_label.pack(side='top', padx=10, pady=10)

        bct_label = tk.Label(
            framedown, text=".bct file:", font='Helvetica').pack(pady=5)
        bct_entry = tk.Entry(framedown, width=50)
        bct_entry.pack()
        bct_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bct_entry)).pack(pady=20)

        type_choice = [
            "Gradual",
            "Constant"]

        selected_step_c = tk.IntVar()

        for idx_c, step_type_c in enumerate(type_choice, start=1):
            radio_button_c = tk.Radiobutton(framedown, variable=selected_step_c,
                                            text=step_type_c,
                                            value=idx_c)
            radio_button_c.pack(anchor='c')

        # amount of change
        change_label = tk.Label(
            framedown, text="Amount of sea level rise (m):", font='Helvetica').pack(pady=5)
        change_entry = tk.Entry(framedown, width=50)
        change_entry.pack(pady=5)

        # build the console

        frame_console = tk.Frame(new_window, width=100,
                                 height=10, borderwidth=1, relief='solid')
        frame_console.pack(side='bottom', fill='both', padx=10, pady=10)

        # Create a Text widget to display console output
        console_output = tk.Text(
            frame_console, wrap=tk.WORD, width=80, height=10)
        console_output.pack(padx=10, pady=10)

        # Redirect sys.stdout to the Text widget
        class ConsoleRedirector:
            def __init__(self, text_widget):
                self.text_space = text_widget

            def write(self, message):
                self.text_space.insert(tk.END, message)
                self.text_space.see(tk.END)  # Automatically scroll to the end
                self.text_space.update_idletasks()  # Update the widget

        # Create an instance of ConsoleRedirector and redirect sys.stdout
        console_redirector = ConsoleRedirector(console_output)
        sys.stdout = console_redirector

        # submit to start extracting

        def check_submit_bct():

            if not bct_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .grd file.")
            elif selected_step_c.get() == 1:
                bct_file_name = bct_entry.get()
                type_inc = False
                type_add = 'gradual'
                change_amount = float(change_entry.get())

                sea_level_change.add_wl(
                    bct_file_name, sea_level_change=change_amount, constant=type_inc)

                print(
                    f'sea level change added to water levels, type {type_add}')

            elif selected_step_c.get() == 2:
                bct_file_name = bct_entry.get()
                type_inc = True
                type_add = 'constant'
                change_amount = float(change_entry.get())

                sea_level_change.add_wl(
                    bct_file_name, sea_level_change=change_amount, constant=type_inc)

                print(
                    f'sea level change added to water levels, type {type_add}')

            else:
                messagebox.showwarning(
                    "Warning", "Please select type of sea level change.")

        # %% end of main code for choice 1
        frame_submit = tk.Frame(new_window, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        # Submit button
        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit_bct)
        submit_button.pack(pady=10, anchor='s')


root = tk.Tk()
root.title("Delft3d-EasyGSH companion")
root.geometry('800x950')
root.resizable(0, 0)

style = Style(theme="darkly")


# %% Load the logo image

# path = "D:/Clayton_Phd/Script_archive/Gui_bnd_generator/easyd3d_logo.png"
# path_2 = "D:/Clayton_Phd/Script_archive/Gui_bnd_generator/easyd3d_logo_large.ico"

# root.img = tk.PhotoImage(file=path)
# root.iconphoto(True,  root.img)
# #

# %% Load the logo image
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


root.img = tk.PhotoImage(file=resource_path('easyd3d_logo.png'))
root.iconphoto(True,  root.img)


# %%
# First Frame for browsing directory
frame1 = tk.Frame(root)
frame1.pack(padx=10, pady=10, fill=tk.X)

path_label = tk.Label(frame1, text="Select the input/output path:")
path_label.pack(side=tk.LEFT, padx=10)

path_entry = tk.Entry(frame1, width=30)
path_entry.pack(side=tk.LEFT, padx=10)

browse_button = tk.Button(frame1, text="Browse", command=browse_path)
browse_button.pack(side=tk.LEFT, pady=10)

# Second Frame for choosing file type using radio buttons
frame2 = tk.Frame(root, borderwidth=1, relief='solid')
frame2.pack(padx=10, pady=10)

file_types = [
    "All files",
    "Bct file",
    "Bct file overlapping over two years",
    "Bcw file",
    "Bcw file overlapping over two years",
    "Boundary location CSV file",
    "Boundary location and mdw file",
    "Add sea level change to .bct files"
]

choice_var = tk.IntVar()

for idx, file_type in enumerate(file_types, start=1):
    radio_button = tk.Radiobutton(frame2, text=file_type,
                                  variable=choice_var, value=idx,  font=('Times', 10))
    radio_button.pack(anchor=tk.W, pady=5)

# Submit button
submit_button = tk.Button(root, text="Submit", command=submit_choice)
submit_button.pack(pady=10)

# Second Frame for choosing file type using radio buttons
frame3 = tk.Frame(root)
frame3.pack()

text = """Source for EasyGSH data: https://mdi-de.baw.de/easygsh/Easy_Viewer_syn.html#home\n
Citations for using EasyGSH data: Hagen, R., Plüß, A., Schrage, N., Dreier, N. (2020): EasyGSH-DB: Themengebiet - synoptische Hydrodynamik. Bundesanstalt für Wasserbau. https://doi.org/10.48437/02.2020.K2.7000.0004\n
Please read the source document to understand how these datasets are generated. \nHere are some quick points:
The data provided are the results of a numerical simulation gridded over 1km and provided every 20 minutes.\nThe numerical modeling approach used to generate the data utilizes annually updated bathymetry, tidal dynamics simulated by the Untrim2 modeling system using tidal constituents at the open boundaries (corrected for external surge), waves computed using a combination of the model UnK (Schneggenburger et al., 2000) and SWAN for near-shore physical processes.\n\nThis GUI creates files for the Delft3D4 module.\nIt extract time-series water level 2D information for any designed boundaries within the EasyGSH model domain (data found under the synoptic simulation, UnTRIM2, 1000m grid section.)\nIt extracts time series wave/Sea-state data 2D (significant height, peak period, direction, directional spread) for any designed boundaries within the EasyGSH model domain (data found under the synoptic simulation, UnTRIM2, 1000m grid section.)"""

# Create a label with the provided text and place it inside the frame
permanent_text_label = tk.Label(
    frame3, text=text, justify=tk.LEFT, wraplength=400, font=('Arial', 10))
permanent_text_label.pack()


frame4 = tk.Frame(root, borderwidth=0.2, relief='solid')
frame4.pack(padx=10, pady=10, side='left')

text = "The source code can be found at https://github.com/capt-clay10/bct-bcw-mdw-grd_to_CSV_file_generator-for-EasyGSH-Delft3D.git\nGUI created by : Clayton Soares"

# Create a label with the provided text and place it inside the frame
permanent_text_label = tk.Label(
    frame4, text=text, font=('Helvetic', 6), justify=tk.LEFT, wraplength=400)
permanent_text_label.pack(anchor='sw')


root.mainloop()
