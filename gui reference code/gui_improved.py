import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style
import sys
import time
import threading
import queue
import output_methods
import extract_from_d3d_files
import bct_generator
import bct_year_overlap_file_generator
import bcw_generator
import bcw_year_overlap_file_generator
import mdw_writer
import sea_level_change
import rep_period
import cosmo_wind_file_generator
import ast
import os
from datetime import datetime, timedelta


def resource_path(self, relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def show_splash(app, resource_path):
    splash = tk.Toplevel()
    splash.overrideredirect(True)

    # Load splash screen image
    splash_image = tk.PhotoImage(file=resource_path('easyd3d_logo.png'))
    splash_label = tk.Label(splash, image=splash_image)
    splash_label.pack()

    # Center splash screen
    window_width = 60
    window_height = 40
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    splash.geometry(
        f'{window_width}x{window_height}+{position_right}+{position_top}')

    def close_splash():
        splash.destroy()
        app.deiconify()  # Show the main window

    # Close splash screen after 3 seconds
    splash.after(3000, close_splash)
    splash.mainloop()


class Application(tk.Tk):
    def toggle_fullscreen(event=None):
        app.attributes("-fullscreen", True)

    def end_fullscreen(event=None):
        app.attributes("-fullscreen", False)

    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide the main window initially
        self.title("Delft3d-EasyGSH companion (EasyD3D)")
        self.geometry('700x800')
        self.resizable(0, 0)

        style = Style(theme="darkly")

        self.task_queue = queue.Queue()

        # Load logo
        self.img = tk.PhotoImage(
            file=self.resource_path('easyd3d_logo_large.png'))
        self.iconphoto(True, self.img)

        self.setup_ui()
        self.after(0, lambda: show_splash(
            self, self.resource_path))  # Show splash screen

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def setup_ui(self):
        # First Frame for browsing directory
        frame1 = tk.Frame(self)
        frame1.pack(padx=10, pady=10, fill=tk.X)

        path_label = tk.Label(frame1, text="Select the input/output path:")
        path_label.pack(side=tk.LEFT, padx=10)

        self.path_entry = tk.Entry(frame1, width=30)
        self.path_entry.pack(side=tk.LEFT, padx=10)

        browse_button = tk.Button(
            frame1, text="Browse", command=self.browse_path)
        browse_button.pack(side=tk.LEFT, pady=10)

        # Second Frame for choosing file type using radio buttons
        frame2 = tk.Frame(self, borderwidth=1, relief='solid')
        frame2.pack(padx=10, pady=10)

        file_types = [
            "All files",
            "Bct file (water-level time series)",
            "Bct file overlapping over two years",
            "Bcw file (wave data time series)",
            "Bcw file overlapping over two years",
            "Boundary location CSV file",
            "Boundary location and mdw file",
            "Add sea level change to .bct files",
            "Identify representative period",
            "Generate ST-varying wind field files- COSMO"
        ]

        self.choice_var = tk.IntVar()

        for idx, file_type in enumerate(file_types, start=1):
            radio_button = tk.Radiobutton(frame2, text=file_type,
                                          variable=self.choice_var, value=idx, font=('Times', 14))
            radio_button.pack(anchor=tk.W, pady=5)

        # Submit button
        submit_button = tk.Button(
            self, text="Submit", command=self.submit_choice, width=20)
        submit_button.pack(pady=10)

        # Information frame
        frame3 = tk.Frame(self)
        frame3.pack()

        text = """Source for EasyGSH data: https://mdi-de.baw.de/easygsh/Easy_Viewer_syn.html#home\n\nCitations for using EasyGSH data: Hagen, R., Plüß, A., Schrage, N., Dreier, N. (2020): EasyGSH-DB: Themengebiet - synoptische Hydrodynamik. Bundesanstalt für Wasserbau. https://doi.org/10.48437/02.2020.K2.7000.0004\n\nDocumentation and source code can be found at https://github.com/capt-clay10/bct-bcw-mdw-grd_to_CSV_file_generator-for-EasyGSH-Delft3D.git
        """

        permanent_text_label = tk.Label(
            frame3, text=text, justify=tk.LEFT, wraplength=400, font=('Arial', 10))
        permanent_text_label.pack()

        frame4 = tk.Frame(self, borderwidth=0.2, relief='solid')
        frame4.pack(padx=10, pady=10, side='left')

        text = "GUI created by : Clayton Soares\ncontact: clayton.soares@ifg.uni-kiel.de"
        permanent_text_label = tk.Label(
            frame4, text=text, font=('Helvetic', 10), justify=tk.LEFT, wraplength=400)
        permanent_text_label.pack(anchor='sw')

        # Start the queue processing
        self.after(100, self.process_queue)

    def browse_path(self):
        folder_selected = filedialog.askdirectory()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, folder_selected)

    def run_task_in_thread(self, task, *args):
        def wrapper():
            result = task(*args)
            self.task_queue.put((task.__name__, result))
        thread = threading.Thread(target=wrapper)
        thread.start()

    def process_queue(self):
        try:
            while True:
                task_name, result = self.task_queue.get_nowait()
                if task_name == "long_running_task":
                    messagebox.showinfo("Info", result)
                elif task_name == "submit_choice":
                    self.handle_task_result(result)
        except queue.Empty:
            pass
        self.after(100, self.process_queue)

    def handle_task_result(self, result):
        # Process the result of the task here
        pass

    def submit_choice(self):
        selected_choice = self.choice_var.get()
        if not self.path_entry.get():
            messagebox.showwarning(
                "Warning", "Please browse for a directory before submitting.")
        elif selected_choice == 0:
            messagebox.showwarning(
                "Warning", "Please select a file type before submitting.")
        elif selected_choice in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            t = time.time()  # start the time counter

            new_window = tk.Toplevel(self)
            new_window.title("Processing Window")
            # new_window.geometry('1000x1000')
            new_window.grab_set()
            new_window.resizable(1, 0)
            # Bind the F11 key to toggle full screen for the internal window
            new_window.bind("<F11>", self.toggle_fullscreen)
            # Bind the Escape key to exit full screen for the internal window
            new_window.bind("<Escape>", self.end_fullscreen)

            # Function to browse for files
            def browse_file(entry_widget):
                file_path = filedialog.askopenfilename()
                entry_widget.delete(0, "end")
                entry_widget.insert(0, file_path)

            main_frame = tk.Frame(new_window)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Console frame
            frame_console = tk.Frame(
                new_window, width=100, height=10, borderwidth=1, relief='solid')
            frame_console.pack(side='bottom', fill='both', padx=10, pady=10)

            # Create a Text widget to display console output
            console_output = tk.Text(
                frame_console, wrap=tk.WORD, width=80, height=10)
            console_output.pack(padx=10, pady=10)

            # Redirect sys.stdout to the Text widget
            class ConsoleRedirector:
                def __init__(self, text_widget):
                    self.text_space = text_widget
                    self._stdout = sys.stdout
                    self._stderr = sys.stderr

                def write(self, message):
                    if not message.endswith('\n'):
                        message += '\n'
                    self.text_space.insert(tk.END, message)
                    # Automatically scroll to the end
                    self.text_space.see(tk.END)
                    self.text_space.update_idletasks()  # Update the widget

                def flush(self):
                    self.text_space.update_idletasks()  # Ensure the widget updates

            # console_redirector = ConsoleRedirector(console_output)
            # Redirect stdout to the Text widget
            sys.stdout = ConsoleRedirector(console_output)
            sys.stderr = ConsoleRedirector(console_output)

            def process_choice():
                if selected_choice == 1:
                    self.process_all_files(main_frame)
                elif selected_choice == 2:
                    self.process_bct_files(main_frame)
                elif selected_choice == 3:
                    self.process_bct_overlap_files(main_frame)
                elif selected_choice == 4:
                    self.process_bcw_files(main_frame)
                elif selected_choice == 5:
                    self.process_bcw_overlap_files(main_frame)
                elif selected_choice == 6:
                    self.generate_boundary_csv(main_frame)
                elif selected_choice == 7:
                    self.generate_boundary_mdw(main_frame)
                elif selected_choice == 8:
                    self.add_sea_level(main_frame)
                elif selected_choice == 9:
                    self.identify_representative_period(main_frame)
                elif selected_choice == 10:
                    self.generate_wind_files(main_frame)

            # Run the processing function in a separate thread to avoid blocking the GUI
            threading.Thread(target=process_choice).start()

    def process_all_files(self, main_frame):

        # Frame for Flow Module
        frameup = tk.Frame(main_frame, width=250, borderwidth=1, relief='solid')
        frameup.pack(side='left', fill='both', expand=True, padx=10)
        left_label = tk.Label(frameup, text="Flow Module", font=("Times", 16))
        left_label.pack(side='top', padx=10, pady=10)

        # Frame for Wave Module
        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='right', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Wave Module", font=("Times", 16))
        right_label.pack(side='top', padx=10, pady=10)
        t = time.time()
        # Function to browse for files

        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        # Input buttons for Flow Module
        mdf_label = tk.Label(frameup, text="MDF file:",
                             font='Times').pack(pady=5)
        mdf_entry = tk.Entry(frameup, width=50)
        mdf_entry.pack()
        mdf_button = tk.Button(frameup, text="Browse",
                               command=lambda: browse_file(mdf_entry)).pack(pady=20)

        grd_label = tk.Label(frameup, text=".grd file (flow):",
                             font='Times').pack(pady=5)
        grd_entry = tk.Entry(frameup, width=50)
        grd_entry.pack()
        grd_button = tk.Button(frameup, text="Browse",
                               command=lambda: browse_file(grd_entry)).pack(pady=20)

        bnd_label = tk.Label(frameup, text=".bnd file (flow):",
                             font='Times').pack(pady=5)
        bnd_entry = tk.Entry(frameup, width=50)
        bnd_entry.pack()
        bnd_button = tk.Button(frameup, text="Browse",
                               command=lambda: browse_file(bnd_entry)).pack(pady=20)

        nc_label = tk.Label(
            frameup, text=".nc waterlevel file (EasyGSH):", font='Times').pack(pady=5)
        nc_entry = tk.Entry(frameup, width=50)
        nc_entry.pack()
        nc_button = tk.Button(frameup, text="Browse",
                              command=lambda: browse_file(nc_entry)).pack(pady=20)

        step_types = ["20 mins", "40 mins", "60 mins", "80 mins"]

        stepf_label = tk.Label(
            frameup, text="Time step for waterlevel extraction:", font='Times').pack(pady=5)
        selected_step_f = tk.IntVar()

        for idx, step_type in enumerate(step_types, start=1):
            radio_button_f = tk.Radiobutton(
                frameup, text=step_type, variable=selected_step_f, value=idx)
            radio_button_f.pack(anchor='c')

        # Input buttons for Wave Module
        mdw_label = tk.Label(framedown, text="MDW file:",
                             font='Times').pack(pady=5)
        mdw_entry = tk.Entry(framedown, width=50)
        mdw_entry.pack()
        mdw_button = tk.Button(framedown, text="Browse",
                               command=lambda: browse_file(mdw_entry)).pack(pady=20)

        grdw_label = tk.Label(
            framedown, text=".grd file (wave):", font='Times').pack(pady=5)
        grdw_entry = tk.Entry(framedown, width=50)
        grdw_entry.pack()
        grdw_button = tk.Button(framedown, text="Browse",
                                command=lambda: browse_file(grdw_entry)).pack(pady=20)

        bndw_label = tk.Label(
            framedown, text=".bnd file (wave):", font='Times').pack(pady=5)
        bndw_entry = tk.Entry(framedown, width=50)
        bndw_entry.pack()
        bndw_button = tk.Button(framedown, text="Browse",
                                command=lambda: browse_file(bndw_entry)).pack(pady=20)

        ncw_label = tk.Label(
            framedown, text=".nc wave file (EasyGSH):", font='Times').pack(pady=5)
        ncw_entry = tk.Entry(framedown, width=50)
        ncw_entry.pack()
        ncw_button = tk.Button(framedown, text="Browse",
                               command=lambda: browse_file(ncw_entry)).pack(pady=20)

        stepw_label = tk.Label(
            framedown, text="Time step for wave extraction:", font='Times').pack(pady=5)
        step_types_w = ["20 mins", "40 mins", "60 mins", "80 mins", "120 mins"]
        selected_step_w = tk.IntVar()

        for idx_w, step_type_w in enumerate(step_types_w, start=1):
            radio_button_w = tk.Radiobutton(
                framedown, variable=selected_step_w, text=step_type_w, value=idx_w)
            radio_button_w.pack(anchor='c')

        def check_submit():
            t = time.time()
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
                # Input files from browsed
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
                        if '=' in line:
                            if string_name in line:
                                val = line.split('=')
                                string_val = val[1].strip()
                                break
                    file1.close()
                    return string_val

                # Files
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
                time_start = ref_time+" 00:00:00"  # Assuming it always starts at 00
                date_format_str = "%Y-%m-%d %H:%M:%S"
                start_time_steps = int(start/60)  # to convert minutes to hours
                end_time_steps = int(stop/60)
                extracted_time = datetime.strptime(time_start, date_format_str)
                start_time = extracted_time + timedelta(hours=start_time_steps)
                start_time = start_time .strftime("%Y-%m-%d %H:%M:%S")
                end_time = extracted_time + timedelta(hours=end_time_steps)
                end_time = end_time .strftime("%Y-%m-%d %H:%M:%S")

                # Output files
                name_with_dot = mdf_file.partition('.')
                name_until_dot = name_with_dot[0]
                bct_file_name = '{}.bct'.format(name_until_dot)
                path_out_file = '{}.csv'.format(name_until_dot)
                wave_name_with_dot = mdw_file.partition('.')
                wave_name_until_dot = wave_name_with_dot[0]
                bcw_file = '{}.bcw'.format(wave_name_until_dot)
                wave_path_out_file = '{}.csv'.format(wave_name_until_dot)

                # Create the csv file for flow boundaries
                bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_input)
                coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_input, request_list=bnd_grd_indices_output)
                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)

                # Create the csv file for wave boundaries
                bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_wave_input)
                coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_wave_input, request_list=bnd_wave_grd_indices_output)
                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)

                # Create the bct file
                boundaries = path_out_file  # the csv file generated from process one
                bct = bct_generator.bct_file_generator(
                    boundaries=boundaries, nc_file=nc_file, mdf_file=mdf_file, step=step,
                    bct_file_name=bct_file_name)

                # Create the bcw file
                boundaries_wave = wave_path_out_file
                bcw = bcw_generator.bcw_file_generator(
                    boundaries_wave=boundaries_wave, nc_file_wave=nc_file_wave, mdw_file=mdw_file, start_time=start_time,
                    end_time=end_time, step_wave=step_wave, bcw_file_name=bcw_file)

                # Write the new mdw file
                mdw_writer.write_mdw_file(
                    mdw_file=mdw_file, boundaries_wave=boundaries_wave)

                elapsed_final = time.time() - t
                print(
                    f'Total time taken for both files is {elapsed_final/60} mins')

        # Submit code for execution
        frame_submit = tk.Frame(main_frame, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(side='bottom', fill='both', padx=10, pady=10)

        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit, width=30)
        submit_button.pack(pady=10, anchor='s')

    def process_bct_files(self, main_frame):

        # Frame for Flow Module
        frameup = tk.Frame(main_frame, width=250, borderwidth=1, relief='solid')
        frameup.pack(fill='both', expand=True, padx=10)
        left_label = tk.Label(frameup, text="Flow Module", font=("Times", 16))
        left_label.pack(side='top', padx=10, pady=10)

        # Function to browse for files
        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        # Input buttons for Flow Module
        mdf_label = tk.Label(frameup, text="MDF file:",
                             font='Times').pack(pady=5)
        mdf_entry = tk.Entry(frameup, width=50)
        mdf_entry.pack()
        mdf_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(mdf_entry)).pack(pady=20)

        grd_label = tk.Label(
            frameup, text=".grd file (flow):", font='Times').pack(pady=5)
        grd_entry = tk.Entry(frameup, width=50)
        grd_entry.pack()
        grd_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(grd_entry)).pack(pady=20)

        bnd_label = tk.Label(
            frameup, text=".bnd file (flow):", font='Times').pack(pady=5)
        bnd_entry = tk.Entry(frameup, width=50)
        bnd_entry.pack()
        bnd_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(bnd_entry)).pack(pady=20)

        nc_label = tk.Label(
            frameup, text=".nc waterlevel file (EasyGSH):", font='Times').pack(pady=5)
        nc_entry = tk.Entry(frameup, width=50)
        nc_entry.pack()
        nc_button = tk.Button(frameup, text="Browse",
                              command=lambda: browse_file(nc_entry)).pack(pady=20)

        step_types = ["20 mins", "40 mins", "60 mins", "80 mins"]

        stepf_label = tk.Label(
            frameup, text="Time step for waterlevel extraction:", font='Times').pack(pady=5)
        selected_step_f = tk.IntVar()

        for idx, step_type in enumerate(step_types, start=1):
            radio_button_f = tk.Radiobutton(
                frameup, text=step_type, variable=selected_step_f, value=idx)
            radio_button_f.pack(anchor='c')

        def check_submit():
            t = time.time()
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
                # Input files from browsed
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
                        if '=' in line:
                            if string_name in line:
                                val = line.split('=')
                                string_val = val[1].strip()
                                break
                    file1.close()
                    return string_val

                # Files
                mdf_file = mdf_entry.get()
                grid_input = grd_entry.get()
                bnd_input = bnd_entry.get()
                nc_file = nc_entry.get()

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
                time_start = ref_time+" 00:00:00"  # Assuming it always starts at 00
                date_format_str = "%Y-%m-%d %H:%M:%S"
                start_time_steps = int(start/60)  # to convert minutes to hours
                end_time_steps = int(stop/60)
                extracted_time = datetime.strptime(time_start, date_format_str)
                start_time = extracted_time + timedelta(hours=start_time_steps)
                start_time = start_time .strftime("%Y-%m-%d %H:%M:%S")
                end_time = extracted_time + timedelta(hours=end_time_steps)
                end_time = end_time .strftime("%Y-%m-%d %H:%M:%S")

                # Output files
                name_with_dot = mdf_file.partition('.')
                name_until_dot = name_with_dot[0]
                bct_file_name = '{}.bct'.format(name_until_dot)
                path_out_file = '{}.csv'.format(name_until_dot)

                # Create the csv file for flow boundaries
                bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_input)
                coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_input, request_list=bnd_grd_indices_output)
                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)

                # Create the bct file
                boundaries = path_out_file  # the csv file generated from process one
                bct = bct_generator.bct_file_generator(
                    boundaries=boundaries, nc_file=nc_file, mdf_file=mdf_file, step=step,
                    bct_file_name=bct_file_name)

                elapsed_final = time.time() - t
                print(
                    f'Total time taken for bct file is {elapsed_final/60} mins')

        # Submit code for execution
        frame_submit = tk.Frame(main_frame, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit, width=30)
        submit_button.pack(pady=10, anchor='s')

    def process_bct_overlap_files(self, main_frame):
        # Frame for Flow Module
        frameup = tk.Frame(main_frame, width=250, borderwidth=1, relief='solid')
        frameup.pack(side='left', fill='both', expand=True, padx=10)
        left_label = tk.Label(frameup, text="Flow Module", font=("Times", 16))
        left_label.pack(side='top', padx=10, pady=10)
        t = time.time()
        # Function to browse for files

        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        # Input buttons for Flow Module
        mdf_label = tk.Label(frameup, text="MDF file:",
                             font='Times').pack(pady=5)
        mdf_entry = tk.Entry(frameup, width=50)
        mdf_entry.pack()
        mdf_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(mdf_entry)).pack(pady=20)

        grd_label = tk.Label(
            frameup, text=".grd file (flow):", font='Times').pack(pady=5)
        grd_entry = tk.Entry(frameup, width=50)
        grd_entry.pack()
        grd_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(grd_entry)).pack(pady=20)

        bnd_label = tk.Label(
            frameup, text=".bnd file (flow):", font='Times').pack(pady=5)
        bnd_entry = tk.Entry(frameup, width=50)
        bnd_entry.pack()
        bnd_button = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(bnd_entry)).pack(pady=20)

        nc_label = tk.Label(
            frameup, text=".nc waterlevel file (EasyGSH):", font='Times').pack(pady=5)
        nc_entry = tk.Entry(frameup, width=50)
        nc_entry.pack()
        nc_button = tk.Button(frameup, text="Browse",
                              command=lambda: browse_file(nc_entry)).pack(pady=20)

        nc_label_2 = tk.Label(
            frameup, text=".nc waterlevel file- part 2 (EasyGSH):", font='Times').pack(pady=5)
        nc_entry_2 = tk.Entry(frameup, width=50)
        nc_entry_2.pack()
        nc_button_2 = tk.Button(
            frameup, text="Browse", command=lambda: browse_file(nc_entry_2)).pack(pady=20)

        step_types = ["20 mins", "40 mins", "60 mins", "80 mins"]

        stepf_label = tk.Label(
            frameup, text="Time step for waterlevel extraction:", font='Times').pack(pady=5)
        selected_step_f = tk.IntVar()

        for idx, step_type in enumerate(step_types, start=1):
            radio_button_f = tk.Radiobutton(
                frameup, text=step_type, variable=selected_step_f, value=idx)
            radio_button_f.pack(anchor='c')

        def check_submit():
            t = time.time()
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
                # Input files from browsed
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
                        if '=' in line:
                            if string_name in line:
                                val = line.split('=')
                                string_val = val[1].strip()
                                break
                    file1.close()
                    return string_val

                # Files
                mdf_file = mdf_entry.get()
                grid_input = grd_entry.get()
                bnd_input = bnd_entry.get()
                nc_file = nc_entry.get()
                nc_file_2 = nc_entry_2.get()

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
                time_start = ref_time+" 00:00:00"  # Assuming it always starts at 00
                date_format_str = "%Y-%m-%d %H:%M:%S"
                start_time_steps = int(start/60)  # to convert minutes to hours
                end_time_steps = int(stop/60)
                extracted_time = datetime.strptime(time_start, date_format_str)
                start_time = extracted_time + timedelta(hours=start_time_steps)
                start_time = start_time .strftime("%Y-%m-%d %H:%M:%S")
                end_time = extracted_time + timedelta(hours=end_time_steps)
                end_time = end_time .strftime("%Y-%m-%d %H:%M:%S")

                # Output files
                name_with_dot = mdf_file.partition('.')
                name_until_dot = name_with_dot[0]
                bct_file_name = '{}.bct'.format(name_until_dot)
                path_out_file = '{}.csv'.format(name_until_dot)

                # Create the csv file for flow boundaries
                bnd_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_input)
                coord_from_d3d_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_input, request_list=bnd_grd_indices_output)
                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_grd_output, out_path=path_out_file)

                # Create the bct file
                boundaries = path_out_file  # the csv file generated from process one
                bct = bct_year_overlap_file_generator.bct_year_overlap_file_generator(
                    boundaries=boundaries, nc_file_year1=nc_file, nc_file_year2=nc_file_2,
                    mdf_file=mdf_file, step=step, bct_file_name=bct_file_name)

                elapsed_final = time.time() - t
                print(
                    f'Total time taken for the bct overlap file is {elapsed_final/60} mins')

        # Submit button for execution
        frame_submit = tk.Frame(main_frame, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit, width=30)
        submit_button.pack(pady=10, anchor='s')

    def process_bcw_files(self, main_frame):
        # Frame for Wave Module
        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Wave Module", font=("Times", 16))
        right_label.pack(side='top', padx=10, pady=10)
        t = time.time()
        # Function to browse for files

        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        # Input buttons for Wave Module
        mdw_label = tk.Label(framedown, text="MDW file:",
                             font='Times').pack(pady=5)
        mdw_entry = tk.Entry(framedown, width=50)
        mdw_entry.pack()
        mdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(mdw_entry)).pack(pady=20)

        grdw_label = tk.Label(
            framedown, text=".grd file (wave):", font='Times').pack(pady=5)
        grdw_entry = tk.Entry(framedown, width=50)
        grdw_entry.pack()
        grdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(grdw_entry)).pack(pady=20)

        bndw_label = tk.Label(
            framedown, text=".bnd file (wave):", font='Times').pack(pady=5)
        bndw_entry = tk.Entry(framedown, width=50)
        bndw_entry.pack()
        bndw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bndw_entry)).pack(pady=20)

        ncw_label = tk.Label(
            framedown, text=".nc wave file (EasyGSH):", font='Times').pack(pady=5)
        ncw_entry = tk.Entry(framedown, width=50)
        ncw_entry.pack()
        ncw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(ncw_entry)).pack(pady=20)

        stepw_label = tk.Label(
            framedown, text="Time step for wave extraction:", font='Times').pack(pady=5)
        step_types_w = ["20 mins", "40 mins", "60 mins", "80 mins", "120 mins"]
        selected_step_w = tk.IntVar()

        for idx_w, step_type_w in enumerate(step_types_w, start=1):
            radio_button_w = tk.Radiobutton(
                framedown, variable=selected_step_w, text=step_type_w, value=idx_w)
            radio_button_w.pack(anchor='c')

        # Date selection for wave extraction
        framedate = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedate.pack(anchor='s', fill='both', expand=True, padx=10)

        frame_date_label = tk.Label(
            framedate, text="Start date", font=("Times", 16))
        frame_date_label.pack(side='top', padx=10, pady=10)

        framedate_end = tk.Frame(main_frame, width=250,
                                 borderwidth=1, relief='solid')
        framedate_end.pack(anchor='s', fill='both', expand=True, padx=10)

        frame_date_end_label = tk.Label(
            framedate_end, text="End date", font=("Times", 16))
        frame_date_end_label.pack(side='top', padx=10, pady=10)

        # Start date
        s_date_label = tk.Label(
            framedate, text="start date of simulation (YYYY-mm-dd HH:MM:SS):", font='Times').pack(pady=5)
        s_date_entry = tk.Entry(framedate, width=50)
        s_date_entry.pack(pady=5)

        # End date
        e_date_label = tk.Label(
            framedate_end, text="end date of simulation (YYYY-mm-dd HH:MM:SS):", font='Times').pack(pady=5)
        e_date_entry = tk.Entry(framedate_end, width=50)
        e_date_entry.pack(pady=5)

        def check_submit():
            t = time.time()
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
                # Input files from browsed
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
                        if '=' in line:
                            if string_name in line:
                                val = line.split('=')
                                string_val = val[1].strip()
                                break
                    file1.close()
                    return string_val

                # Files
                mdw_file = mdw_entry.get()
                grid_wave_input = grdw_entry.get()
                bnd_wave_input = bndw_entry.get()
                nc_file_wave = ncw_entry.get()
                start_time = s_date_entry.get()
                end_time = e_date_entry.get()

                # Output file
                wave_name_with_dot = mdw_file.partition('.')
                wave_name_until_dot = wave_name_with_dot[0]
                bcw_file = '{}.bcw'.format(wave_name_until_dot)
                wave_path_out_file = '{}.csv'.format(wave_name_until_dot)

                # Create the csv file for wave boundaries
                bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_wave_input)
                coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_wave_input, request_list=bnd_wave_grd_indices_output)
                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)

                # Create the bcw file
                boundaries_wave = wave_path_out_file
                bcw = bcw_generator.bcw_file_generator(
                    boundaries_wave=boundaries_wave, nc_file_wave=nc_file_wave, mdw_file=mdw_file,
                    start_time=start_time, end_time=end_time, step_wave=step_wave, bcw_file_name=bcw_file)

                print(
                    'The process of extracting wave boundary conditions has now completed.')
                elapsed = time.time() - t
                print(f'Total time taken: {elapsed/60} mins')

                # Write the new mdw file
                mdw_writer.write_mdw_file(
                    mdw_file=mdw_file, boundaries_wave=boundaries_wave)
                print('New mdw file created')

        # Submit button for execution
        frame_submit = tk.Frame(main_frame, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit, width=30)
        submit_button.pack(pady=10, anchor='s')

    def process_bcw_overlap_files(self, main_frame):
        # Frame for Wave Module
        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Wave Module", font=("Times", 16))
        right_label.pack(side='top', padx=10, pady=10)
        t = time.time()
        # Function to browse for files

        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        # Input buttons for Wave Module
        mdw_label = tk.Label(framedown, text="MDW file:",
                             font='Times').pack(pady=5)
        mdw_entry = tk.Entry(framedown, width=50)
        mdw_entry.pack()
        mdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(mdw_entry)).pack(pady=20)

        grdw_label = tk.Label(
            framedown, text=".grd file (wave):", font='Times').pack(pady=5)
        grdw_entry = tk.Entry(framedown, width=50)
        grdw_entry.pack()
        grdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(grdw_entry)).pack(pady=20)

        bndw_label = tk.Label(
            framedown, text=".bnd file (wave):", font='Times').pack(pady=5)
        bndw_entry = tk.Entry(framedown, width=50)
        bndw_entry.pack()
        bndw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bndw_entry)).pack(pady=20)

        ncw_label = tk.Label(
            framedown, text=".nc wave file (EasyGSH):", font='Times').pack(pady=5)
        ncw_entry = tk.Entry(framedown, width=50)
        ncw_entry.pack()
        ncw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(ncw_entry)).pack(pady=20)

        ncw2_label = tk.Label(
            framedown, text=".nc wave file part 2 (EasyGSH):", font='Times').pack(pady=5)
        ncw2_entry = tk.Entry(framedown, width=50)
        ncw2_entry.pack()
        ncw2_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(ncw2_entry)).pack(pady=20)

        stepw_label = tk.Label(
            framedown, text="Time step for wave extraction:", font='Times').pack(pady=5)
        step_types_w = ["20 mins", "40 mins", "60 mins", "80 mins", "120 mins"]
        selected_step_w = tk.IntVar()

        for idx_w, step_type_w in enumerate(step_types_w, start=1):
            radio_button_w = tk.Radiobutton(
                framedown, variable=selected_step_w, text=step_type_w, value=idx_w)
            radio_button_w.pack(anchor='c')

        # Date selection for wave extraction
        framedate = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedate.pack(anchor='s', fill='both', expand=True, padx=10)

        frame_date_label = tk.Label(
            framedate, text="Start date", font=("Times", 16))
        frame_date_label.pack(side='top', padx=10, pady=10)

        framedate_end = tk.Frame(main_frame, width=250,
                                 borderwidth=1, relief='solid')
        framedate_end.pack(anchor='s', fill='both', expand=True, padx=10)

        frame_date_end_label = tk.Label(
            framedate_end, text="End date", font=("Times", 16))
        frame_date_end_label.pack(side='top', padx=10, pady=10)

        # Start date
        s_date_label = tk.Label(
            framedate, text="start date of simulation (YYYY-mm-dd HH:MM:SS):", font='Times').pack(pady=5)
        s_date_entry = tk.Entry(framedate, width=50)
        s_date_entry.pack(pady=5)

        # End date
        e_date_label = tk.Label(
            framedate_end, text="end date of simulation (YYYY-mm-dd HH:MM:SS):", font='Times').pack(pady=5)
        e_date_entry = tk.Entry(framedate_end, width=50)
        e_date_entry.pack(pady=5)

        def check_submit():
            t = time.time()
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
                # Input files from browsed
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
                        if '=' in line:
                            if string_name in line:
                                val = line.split('=')
                                string_val = val[1].strip()
                                break
                    file1.close()
                    return string_val

                # Files
                mdw_file = mdw_entry.get()
                grid_wave_input = grdw_entry.get()
                bnd_wave_input = bndw_entry.get()
                nc_file_wave = ncw_entry.get()
                nc_file_wave_2 = ncw2_entry.get()
                start_time = s_date_entry.get()
                end_time = e_date_entry.get()

                # Output file
                wave_name_with_dot = mdw_file.partition('.')
                wave_name_until_dot = wave_name_with_dot[0]
                bcw_file = '{}.bcw'.format(wave_name_until_dot)
                wave_path_out_file = '{}.csv'.format(wave_name_until_dot)

                # Create the csv file for wave boundaries
                bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_wave_input)
                coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_wave_input, request_list=bnd_wave_grd_indices_output)
                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)

                # Create the bcw file
                boundaries_wave = wave_path_out_file
                bcw = bcw_year_overlap_file_generator.bcw_year_overlap_file_generator(
                    boundaries_wave=boundaries_wave, nc_file_wave_year1=nc_file_wave,
                    nc_file_wave_year2=nc_file_wave_2, mdw_file=mdw_file, start_time=start_time,
                    end_time=end_time, step_wave=step_wave, bcw_file_name=bcw_file)

                print(
                    'The process of extracting wave boundary conditions has now completed.')
                elapsed = time.time() - t
                print(f'Total time taken: {elapsed/60} mins')

                # Write the new mdw file
                mdw_writer.write_mdw_file(
                    mdw_file=mdw_file, boundaries_wave=boundaries_wave)
                print('New mdw file created')

        # Submit button for execution
        frame_submit = tk.Frame(main_frame, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit, width=30)
        submit_button.pack(pady=10, anchor='s')

    def generate_boundary_csv(self, main_frame):
        # Frame for Wave/Flow Module
        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Wave/Flow Module", font=("Times", 16))
        right_label.pack(side='top', padx=10, pady=10)
        t = time.time()
        # Function to browse for files

        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        # Input buttons for .grd and .bnd files
        grdw_label = tk.Label(framedown, text=".grd file:",
                              font='Times').pack(pady=5)
        grdw_entry = tk.Entry(framedown, width=50)
        grdw_entry.pack()
        grdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(grdw_entry)).pack(pady=20)

        bndw_label = tk.Label(framedown, text=".bnd file:",
                              font='Times').pack(pady=5)
        bndw_entry = tk.Entry(framedown, width=50)
        bndw_entry.pack()
        bndw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bndw_entry)).pack(pady=20)

        def check_submit():
            t = time.time()
            if not grdw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .grd file.")
            elif not bndw_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .bnd file.")
            else:
                # Input files
                grid_input = grdw_entry.get()
                bnd_input = bndw_entry.get()

                # Use grid file to extract bct file and output file
                wave_name_with_dot = grid_input.partition('.')
                wave_name_until_dot = wave_name_with_dot[0]
                wave_path_out_file = '{}.csv'.format(wave_name_until_dot)

                # Create the csv file for wave boundaries
                bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_input)
                coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_input, request_list=bnd_wave_grd_indices_output)
                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)

                print(
                    'The process of creating the boundary location csv file is completed.')

        # Submit button for execution
        frame_submit = tk.Frame(main_frame, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit, width=30)
        submit_button.pack(pady=10, anchor='s')

    def generate_boundary_mdw(self, main_frame):
        # Frame for Wave Module
        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Wave Module", font=("Times", 16))
        right_label.pack(side='top', padx=10, pady=10)
        t = time.time()
        # Function to browse for files

        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        # Input buttons for .grd, .bnd, and .mdw files
        grdw_label = tk.Label(framedown, text=".grd file:",
                              font='Times').pack(pady=5)
        grdw_entry = tk.Entry(framedown, width=50)
        grdw_entry.pack()
        grdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(grdw_entry)).pack(pady=20)

        bndw_label = tk.Label(framedown, text=".bnd file:",
                              font='Times').pack(pady=5)
        bndw_entry = tk.Entry(framedown, width=50)
        bndw_entry.pack()
        bndw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bndw_entry)).pack(pady=20)

        mdw_label = tk.Label(framedown, text="MDW file:",
                             font='Times').pack(pady=5)
        mdw_entry = tk.Entry(framedown, width=50)
        mdw_entry.pack()
        mdw_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(mdw_entry)).pack(pady=20)

        def check_submit():
            t = time.time()
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
                # Input files
                grid_input = grdw_entry.get()
                bnd_input = bndw_entry.get()
                mdw_file = mdw_entry.get()

                # Use grid file to extract bct file and output file
                wave_name_with_dot = grid_input.partition('.')
                wave_name_until_dot = wave_name_with_dot[0]
                wave_path_out_file = '{}.csv'.format(wave_name_until_dot)

                # Create the csv file for wave boundaries
                bnd_wave_grd_indices_output = extract_from_d3d_files.extract_bnd_grd_indices(
                    path_bnd=bnd_input)
                coord_from_d3d_wave_grd_output = extract_from_d3d_files.extract_coord_from_d3d_grd(
                    path_grd=grid_input, request_list=bnd_wave_grd_indices_output)
                output_methods.write_bnd_coord_ascii(
                    bnd_data_list=coord_from_d3d_wave_grd_output, out_path=wave_path_out_file)

                # Create the new mdw file
                mdw_writer.write_mdw_file(
                    mdw_file=mdw_file, boundaries_wave=wave_path_out_file)
                print('New mdw file created.')

        # Submit button for execution
        frame_submit = tk.Frame(main_frame, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        submit_button = tk.Button(
            frame_submit, text="Extract Boundary conditions", command=check_submit, width=30)
        submit_button.pack(pady=10, anchor='s')

    def add_sea_level(self, main_frame):
        # Frame for Flow Module
        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="Flow Module", font=("Times", 16))
        right_label.pack(side='top', padx=10, pady=10)
        t = time.time()
        # Function to browse for files

        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        # Input buttons for .bct file
        bct_label = tk.Label(framedown, text=".bct file:",
                             font='Times').pack(pady=5)
        bct_entry = tk.Entry(framedown, width=50)
        bct_entry.pack()
        bct_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(bct_entry)).pack(pady=20)

        # Radio buttons for type of sea level change
        type_choice = ["Gradual", "Constant"]
        selected_step_c = tk.IntVar()

        for idx_c, step_type_c in enumerate(type_choice, start=1):
            radio_button_c = tk.Radiobutton(
                framedown, variable=selected_step_c, text=step_type_c, value=idx_c)
            radio_button_c.pack(anchor='c')

        # Entry for amount of change
        change_label = tk.Label(
            framedown, text="Amount of sea level rise (m):", font='Times').pack(pady=5)
        change_entry = tk.Entry(framedown, width=50)
        change_entry.pack(pady=5)

        def check_submit_bct():
            if not bct_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the .bct file.")
            elif selected_step_c.get() == 0:
                messagebox.showwarning(
                    "Warning", "Please select type of sea level change.")
            else:
                bct_file_name = bct_entry.get()
                change_amount = float(change_entry.get())
                type_inc = selected_step_c.get() == 2  # True if constant, False if gradual
                sea_level_change.add_wl(
                    bct_file_name, sea_level_change=change_amount, constant=type_inc)
                type_add = "constant" if type_inc else "gradual"
                print(
                    f'Sea level change added to water levels, type {type_add}')

        # Submit button for execution
        frame_submit = tk.Frame(main_frame, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        submit_button = tk.Button(
            frame_submit, text="Add sea level", command=check_submit_bct, width=20)
        submit_button.pack(pady=10, anchor='s')

    def identify_representative_period(self, main_frame):
        # Frame for Representative Period
        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='left', fill='both', expand=True, padx=10)
        left_label = tk.Label(
            framedown, text="Representative period", font=("Times", 16))
        left_label.pack(side='top', padx=10, pady=10)

        frameup = tk.Frame(main_frame, width=250, borderwidth=1, relief='solid')
        frameup.pack(side='right', fill='both', expand=True, padx=10)
        t = time.time()
        # Function to browse for files

        def browse_file(entry_widget):
            file_path = filedialog.askopenfilename()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

        # Input button for WIND file
        wind_label = tk.Label(framedown, text="WIND file: \n\nThe file should have only 3 columns, in the following order date, speed, dir \nThe file should be comma separated (,)\n Please remove nans and inconsistencies before hand",
                              font='Times').pack(pady=5)
        wind_entry = tk.Entry(framedown, width=50)
        wind_entry.pack()
        wind_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(wind_entry)).pack(pady=20)

        # Output name
        output_label = tk.Label(
            framedown, text="Output filename:", font=('Times', 14)).pack(pady=5)
        output_entry = tk.Entry(framedown, width=50)
        output_entry.pack(pady=5)

        text = "\nInsert values as a list\n\nDirectional orientations:\n['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE','SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']\n\nSpeed classes:\n[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]\n\nPeriod frequency:\n['2MS', '3MS', '4MS', '5MS', '6MS']\n\n"

        permanent_text_label = tk.Label(
            framedown, text=text, justify=tk.LEFT, wraplength=400, font=('Times', 14))
        permanent_text_label.pack()

        # Quad selection
        quad_label = tk.Label(
            framedown, text="Directional orientations (minimum 2):", font=('Times', 14)).pack(pady=5)
        quad_entry = tk.Entry(framedown, width=50)
        quad_entry.pack(pady=5)

        # Speed selection
        spd_label = tk.Label(framedown, text="Speed classes:",
                             font=('Times', 14)).pack(pady=5)
        spd_entry = tk.Entry(framedown, width=50)
        spd_entry.pack(pady=5)

        # Frequency selection
        frq_label = tk.Label(framedown, text="Period frequency:",
                             font=('Times', 14)).pack(pady=5)
        frq_entry = tk.Entry(framedown, width=50)
        frq_entry.pack(pady=5)

        # Total reference period
        t_start_label = tk.Label(
            frameup, text="Start time of total period:\n eg  : 1975-01-01 00:00:00 ", font=('Times', 14)).pack()
        t_start_entry = tk.Entry(frameup, width=50)
        t_start_entry.pack(pady=5)

        t_end_label = tk.Label(
            frameup, text="End time of total period:", font=('Times', 14)).pack()
        t_end_entry = tk.Entry(frameup, width=50)
        t_end_entry.pack(pady=5)

        # Compare periods
        start_label = tk.Label(
            frameup, text=" Start time of scanning window period", font=('Times', 14)).pack()
        start_entry = tk.Entry(frameup, width=50)
        start_entry.pack(pady=5)

        end_label = tk.Label(
            frameup, text=" End time of scanning window period must be at most\n(Total period end time - largest period frequency) ", font=('Times', 14)).pack()
        end_entry = tk.Entry(frameup, width=50)
        end_entry.pack(pady=5)

        def parse_list_input(input_str):
            # Parse the input string as a Python expression (list)
            converted_list = ast.literal_eval(input_str)
            if isinstance(converted_list, list):
                return converted_list

        def check_submit_rr():
            if not wind_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the wind file.")
            else:
                file_input = wind_entry.get()
                output_name = output_entry.get()
                quad = parse_list_input(quad_entry.get())
                spd = parse_list_input(spd_entry.get())
                frequency = parse_list_input(frq_entry.get())
                start_time_total = t_start_entry.get()
                end_time_total = t_end_entry.get()
                start_time = start_entry.get()
                end_time = end_entry.get()

                rep_period.identify_rep_period(
                    file_input, output_name, quad, spd, start_time_total, end_time_total, frequency, start_time, end_time)
                print('Representative period file has been generated')

        # Submit button for execution
        submit_button = tk.Button(
            frameup, text="Identify Rep period", command=check_submit_rr, width=20)
        submit_button.pack(pady=15, anchor='s')

    def generate_wind_files(self, main_frame):
        # Frame for Wave Module
        framedown = tk.Frame(main_frame, width=250,
                             borderwidth=1, relief='solid')
        framedown.pack(side='top', fill='both', expand=True, padx=10)
        right_label = tk.Label(
            framedown, text="COSMO- Wind files", font=("Times", 16))
        right_label.pack(side='top', padx=10, pady=10)
        t = time.time()

        # Function to browse for files

        def browse_file(entry_widget):
            file_path = filedialog.askdirectory()
            entry_widget.config(state='normal')
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)
            entry_widget.config(state='disabled')

        # Input buttons for .grd, .bnd, and .mdw files
        cosmo_file_path_label = tk.Label(framedown, text="File path with COSMO (U,V,P) data:",
                                         font='Times').pack(pady=5)
        cosmo_file_path_entry = tk.Entry(framedown, width=50, state='readonly')
        cosmo_file_path_entry.pack()
        cosmo_file_path_button = tk.Button(
            framedown, text="Browse", command=lambda: browse_file(cosmo_file_path_entry))
        cosmo_file_path_button.pack(pady=20)

        ref_time_label = tk.Label(framedown, text="Reference time from model simulation:\n    eg: 2011-01-01 00:00:00     ",
                                  font='Times').pack(pady=5)
        ref_time_entry = tk.Entry(framedown, width=50)
        ref_time_entry.pack()

        output_filename_label = tk.Label(framedown, text="Output file name:\n        eg: cosmo_2011",
                                         font='Times').pack(pady=5)
        output_filename_entry = tk.Entry(framedown, width=50)
        output_filename_entry.pack()

        text = "\nThe folder containing the COSMO files should be structured as such\n\nTWO folders in the main path\nFolder 1 called UV and should have all the U and V monthly cosmo files you wish to extract from.\n\nFolder 2 called PS and should have all the PS monthly files.\nThe files can be found at\n\nhttps://opendata.dwd.de/climate_environment/REA/COSMO_REA6/hourly/2D/  \n\n here look for PS, U_10M and V_10M and download all monthly files necesssary\n "

        permanent_text_label = tk.Label(
            framedown, text=text, justify=tk.LEFT, wraplength=400, font=('Times', 14))
        permanent_text_label.pack()

        def check_submit():
            t = time.time()
            if not cosmo_file_path_entry.get():
                messagebox.showwarning(
                    "Warning", "Please browse for the path with the U,V,PS files")
            elif not output_filename_entry.get():
                messagebox.showwarning(
                    "Warning", "Please provide the output file name.")
            elif not ref_time_entry.get():
                messagebox.showwarning(
                    "Warning", "Please provide the reference time.")
            else:
                # Input files
                script_dir = os.path.dirname(os.path.abspath(__file__))
                grid_ed_path = os.path.join(script_dir, 'DB_6km.mat')
                cosmo_db_utm_path = os.path.join(script_dir, 'COSMO_DB_UTM.mat')

                cosmo_files_path = cosmo_file_path_entry.get()
                file_name = output_filename_entry.get()
                ref_time = ref_time_entry.get()

                # Delete .idx files before starting the process
                for root, dirs, files in os.walk(cosmo_files_path):
                    for file in files:
                        if file.endswith('.idx'):
                            os.remove(os.path.join(root, file))

                cosmo_wind_file_generator.create_wind_fields_cosmo(grid_ed_path,
                                                                   cosmo_db_utm_path,
                                                                   cosmo_files_path,
                                                                   file_name,
                                                                   ref_time)

        # Submit button for execution
        frame_submit = tk.Frame(main_frame, width=200,
                                height=20, borderwidth=1, relief='solid')
        frame_submit.pack(fill='both', padx=10, pady=10)

        submit_button = tk.Button(
            frame_submit, text="Generate wind files", command=check_submit, width=30)
        submit_button.pack(pady=10, anchor='s')


if __name__ == "__main__":

    app = Application()
    app.mainloop()
