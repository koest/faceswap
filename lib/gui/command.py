#!/usr/bin python3
""" The command frame for Faceswap GUI """

import tkinter as tk
from tkinter import TclError, ttk

from lib.cli import FileFullPaths

from .tooltip import Tooltip
from .utils import Config, Images, FileHandler
from .wrapper import ProcessWrapper


class CommandNotebook(ttk.Notebook):
    """ Frame to hold each individual tab of the command notebook """

    def __init__(self, parent, opts):
        ttk.Notebook.__init__(self, parent, width=420, height=500)
        parent.add(self)

        self.build_tabs(opts)

    def build_tabs(self, opts):
        """ Build the tabs for the relevant command """
        for category in sorted(key for key in opts.keys()):
            if category == 'faceswap':
                cmdlist = ("extract", "train", "convert")
            else:
                cmdlist = sorted(key for key in opts['tools'].keys())

            for command in cmdlist:
                title = command.title()
                commandtab = CommandTab(self, category, opts[category], command)
                self.add(commandtab, text=title)

class CommandTab(ttk.Frame):
    """ Frame to hold each individual tab of the command notebook """

    def __init__(self, parent, category, opts, command):
        ttk.Frame.__init__(self, parent)

        self.category = category
        self.opts = opts
        self.command = command

        self.build_tab()

    def build_tab(self):
        """ Build the tab """
        OptionsFrame(self, self.opts, self.command)

        self.add_frame_separator()

        ActionFrame(self, self.category, self.opts, self.command)

    def add_frame_separator(self):
        """ Add a separator between top and bottom frames """
        sep = ttk.Frame(self, height=2, relief=tk.RIDGE)
        sep.pack(fill=tk.X, pady=(5, 0), side=tk.TOP)

class OptionsFrame(ttk.Frame):
    """ Options Frame - Holds the Options for each command """

    def __init__(self, parent, opts, command):
        ttk.Frame.__init__(self, parent)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.opts = opts
        self.command = command

        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.optsframe = ttk.Frame(self.canvas)
        self.optscanvas = self.canvas.create_window((0, 0), window=self.optsframe, anchor=tk.NW)
        self.chkbtns = self.checkbuttons_frame()

        self.build_frame()

    def checkbuttons_frame(self):
        """ Build and format frame for holding the check buttons """
        container = ttk.Frame(self.optsframe)

        lbl = ttk.Label(container, text="Options", width=16, anchor=tk.W)
        lbl.pack(padx=5, pady=5, side=tk.LEFT, anchor=tk.N)

        chkframe = ttk.Frame(container)
        chkframe.pack(side=tk.BOTTOM, expand=True)

        chkleft = ttk.Frame(chkframe, name="leftFrame")
        chkleft.pack(side=tk.LEFT, anchor=tk.N, expand=True)

        chkright = ttk.Frame(chkframe, name="rightFrame")
        chkright.pack(side=tk.RIGHT, anchor=tk.N, expand=True)

        return container, chkframe

    def build_frame(self):
        """ Build the options frame for this command """
        self.add_scrollbar()
        self.canvas.bind('<Configure>', self.resize_frame)

        for option in self.opts[self.command]:
            optioncontrol = OptionControl(option, self.opts, self.optsframe, self.chkbtns[1])
            optioncontrol.build_full_control()

        if self.chkbtns[1].winfo_children():
            self.chkbtns[0].pack(side=tk.BOTTOM, fill=tk.X, expand=True)

    def add_scrollbar(self):
        """ Add a scrollbar to the options frame """
        scrollbar = ttk.Scrollbar(self, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=scrollbar.set)
        self.optsframe.bind("<Configure>", self.update_scrollbar)

    def update_scrollbar(self, event):
        """ Update the options frame scrollbar """
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def resize_frame(self, event):
        """ Resize the options frame to fit the canvas """
        canvas_width = event.width
        self.canvas.itemconfig(self.optscanvas, width=canvas_width)

class OptionControl(object):
    """ Build the correct control for the option parsed and place it on the
    frame """

    def __init__(self, option, opts, option_frame, checkbuttons_frame):
        self.option = option
        self.option_frame = option_frame
        self.chkbtns = checkbuttons_frame
        self.opts = opts

    def build_full_control(self):
        """ Build the correct control type for the option passed through """
        ctl = self.option['control']
        ctltitle = self.option['control_title']
        sysbrowser = self.option['filesystem_browser']
        ctlhelp = ' '.join(self.option.get('help', '').split())
        ctlhelp = '. '.join(i.capitalize() for i in ctlhelp.split('. '))
        ctlhelp = ctltitle + ' - ' + ctlhelp
        dflt = self.option.get('default', '')
        dflt = self.option.get('default', False) if ctl == ttk.Checkbutton else dflt
        choices = self.option['choices'] if ctl == ttk.Combobox else None

        ctlframe = self.build_one_control_frame()

        if ctl != ttk.Checkbutton:
            self.build_one_control_label(ctlframe, ctltitle)

        ctlvars = (ctl, ctltitle, dflt, ctlhelp)
        self.option['value'] = self.build_one_control(ctlframe,
                                                      ctlvars,
                                                      choices,
                                                      sysbrowser)

    def build_one_control_frame(self):
        """ Build the frame to hold the control """
        frame = ttk.Frame(self.option_frame)
        frame.pack(fill=tk.X, expand=True)
        return frame

    @staticmethod
    def build_one_control_label(frame, control_title):
        """ Build and place the control label """
        lbl = ttk.Label(frame, text=control_title, width=16, anchor=tk.W)
        lbl.pack(padx=5, pady=5, side=tk.LEFT, anchor=tk.N)

    def build_one_control(self, frame, controlvars, choices, sysbrowser):
        """ Build and place the option controls """
        control, control_title, default, helptext = controlvars
        default = default if default is not None else ''

        var = tk.BooleanVar(
            frame) if control == ttk.Checkbutton else tk.StringVar(frame)
        var.set(default)

        if sysbrowser is not None:
            self.add_browser_buttons(frame, sysbrowser, var)

        if control == ttk.Checkbutton:
            self.checkbutton_to_checkframe(control, control_title, var, helptext)
        else:
            self.control_to_optionsframe(control, frame, var, choices, helptext)
        return var

    def checkbutton_to_checkframe(self, control, control_title, var, helptext):
        """ Add checkbuttons to the checkbutton frame """
        leftframe = self.chkbtns.children['leftFrame']
        rightframe = self.chkbtns.children['rightFrame']
        chkbtn_count = len({**leftframe.children, **rightframe.children})

        frame = leftframe if chkbtn_count % 2 == 0 else rightframe

        ctl = control(frame, variable=var, text=control_title)
        ctl.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.W)

        Tooltip(ctl, text=helptext, wraplength=200)

    @staticmethod
    def control_to_optionsframe(control, frame, var, choices, helptext):
        """ Standard non-check buttons sit in the main options frame """
        ctl = control(frame, textvariable=var)
        ctl.pack(padx=5, pady=5, fill=tk.X, expand=True)

        if control == ttk.Combobox:
            ctl['values'] = [choice for choice in choices]

        Tooltip(ctl, text=helptext, wraplength=200)
    #TODO: Review all of the file handling changes brought in by merge Master
    def add_browser_buttons(self, frame, sysbrowser, filepath):
        """ Add correct file browser button for control """
        if sysbrowser == "combo":
            img = Images().icons['load']
        else:
            img = Images().icons[sysbrowser]
        action = getattr(self, 'ask_' + sysbrowser)
        filetypes = self.option['filetypes']
        fileopn = ttk.Button(frame, image=img,
                             command=lambda cmd=action: cmd(filepath,
                                                            filetypes))
        fileopn.pack(padx=(0, 5), side=tk.RIGHT)

    @staticmethod
    def ask_folder(filepath, filetypes=None):
        """ Pop-up to get path to a directory
            :param filepath: tkinter StringVar object
            that will store the path to a directory.
            :param filetypes: Unused argument to allow
            filetypes to be given in ask_load(). """
        dirname = FileHandler('dir').retfile
        if dirname:
            filepath.set(dirname)

    @staticmethod
    def ask_load(filepath, filetypes=None):
        """ Pop-up to get path to a file """
        if filetypes is None:
            filename = FileHandler('filename').retfile
        else:
            # In case filetypes were not configured properly in the
            # arguments_list
            try:
                filename = FileHandler('filename', filetype=filetypes).retfile
            except TclError as te1:
                filetypes = FileFullPaths.prep_filetypes(filetypes)
                filename = FileHandler('filename', filetype=filetypes).retfile
            except TclError as te2:
                filename = FileHandler('filename').retfile
        if filename:
            filepath.set(filename)

    #TODO CHECK THIS WORKS. AB ORIGINALLY HAD IN AS ASKSAVEASFILENAME
    @staticmethod
    def ask_save(filepath, filetypes=None):
        """ Pop-up to get path to save a new file """
        if filetypes is None:
            filename = FileHandler('save').retfile
        else:
            # In case filetypes were not configured properly in the
            # arguments_list
            try:
                filename = FileHandler('save', filetype=filetypes).retfile
            except TclError as te1:
                filetypes = FileFullPaths.prep_filetypes(filetypes)
                filename = FileHandler('save', filetype=filetypes).retfile
            except TclError as te2:
                filename = FileHandler('save').retfile
        if filename:
            filepath.set(filename)

    @staticmethod
    def ask_nothing(filepath, filetypes=None):
        """ Method that does nothing, used for disabling open/save pop up """
        return

    def ask_combo(self, filepath, filetypes):
        """ Method to pop the correct dialog depending on context """
        actions_open_type = self.option['actions_open_type']
        task_name = actions_open_type['task_name']
        chosen_action = self.opts[task_name][0]['value'].get()
        action = getattr(self, "ask_" + actions_open_type[chosen_action])
        filetypes = filetypes[chosen_action]
        action(filepath, filetypes)

class ActionFrame(ttk.Frame):
    """Action Frame - Displays action controls for the command tab """

    def __init__(self, parent, category, opts, command):
        ttk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH, padx=5, pady=5, side=tk.BOTTOM, anchor=tk.N)

        self.config = Config(opts)
        self.command = command
        self.title = command.title()

        self.add_action_button(category, opts)
        self.add_util_buttons()

    def add_action_button(self, category, opts):
        """ Add the action buttons for page """
        actframe = ttk.Frame(self)
        actframe.pack(fill=tk.X, side=tk.LEFT)

        btnact = ttk.Button(actframe,
                            text=self.title,
                            width=10,
                            command=lambda: ProcessWrapper().action_command(
                                category, self.command, opts))
        btnact.pack(side=tk.LEFT)
        Tooltip(btnact, text='Run the {} script'.format(self.title), wraplength=200)
        ProcessWrapper().actionbtns[self.command] = btnact

        btngen = ttk.Button(actframe,
                            text="Generate",
                            width=10,
                            command=lambda: ProcessWrapper().generate_command(
                                category, self.command, opts))
        btngen.pack(side=tk.RIGHT, padx=5)
        Tooltip(btngen, text='Output command line options to the console', wraplength=200)

    def add_util_buttons(self):
        """ Add the section utility buttons """
        utlframe = ttk.Frame(self)
        utlframe.pack(side=tk.RIGHT)

        for utl in ('load', 'save', 'clear', 'reset'):
            img = Images().icons[utl]
            action = getattr(self.config, utl)
            btnutl = ttk.Button(utlframe,
                                image=img,
                                command=lambda cmd=action: cmd(self.command))
            btnutl.pack(padx=2, side=tk.LEFT)
            Tooltip(btnutl, text=utl.capitalize() + ' ' + self.title + ' config', wraplength=200)
