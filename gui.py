# -*- coding: utf-8 -*-
import Tkinter as TK
# from Tkinter import Tk, Button, Entry, END, IntVar
import Tkinter as tk
import ttk
import tkFileDialog, tkMessageBox
import os


class classUI:
    def __init__(self, master):
        frame = tk.Frame(master)
        frame.pack()
        # ************* ТЕЧЕНИЯ ************

        self.modellabel = tk.Label(frame, text='Выберите папку с данными течений и вид данных')

        self.dirButton_text = tk.StringVar()
        self.dirButton_text.set('Течения...')
        self.dirButton = tk.Button(frame,
                                   textvariable=self.dirButton_text,
                                   command=self.opencurrentsdir)

        self.mode = 'model'
        self.mode_option = tk.StringVar(None, 'LADCP')
        self.r1 = tk.Radiobutton(frame,
                                 text='Модель',
                                 variable=self.mode_option,
                                 value='model',
                                 command = lambda v = self.mode_option:self.enable_model(v))
                                 #command=self.setModel)
        self.r2 = tk.Radiobutton(frame,
                                 text='LADCP',
                                 variable=self.mode_option,
                                 value='LADCP',
                                 command = lambda v = self.mode_option:self.enable_model(v))

        self.set_time_var = tk.StringVar(value=1)
        self.set_time = tk.Spinbox(frame,
                                   from_=1,
                                   to=10,
                                   textvariable = self.set_time_var,
                                   state = 'disabled')

        # ************* РЕЛЬЕФ ***********
        self.refLabel= tk.Label(frame, text='Выберите файл рельефа')
        self.relfButton_text = tk.StringVar()
        self.relfButton_text.set('Рельеф...')
        self.relfButton = tk.Button(frame,
                                    textvariable=self.relfButton_text,
                                    command=self.openrelieffile)

        self.echo_val = tk.StringVar(value=0)
        self.echoCbox = tk.Checkbutton(frame,
                                       text='Эхолот',
                                       variable=self.echo_val,
                                       onvalue=1,
                                       offvalue=0)

        # ************* характеристики разреза ***********

        self.startlatbox = tk.Entry(frame)
        self.endlatbox = tk.Entry(frame)
        self.startlonbox = tk.Entry(frame)
        self.endlonbox = tk.Entry(frame)

        self.useboundsCbox_val = tk.IntVar(value=0)
        self.useboundsCbox = tk.Checkbutton(frame,
                                            text = 'Использовать границы данных',
                                            variable=self.useboundsCbox_val,
                                            onvalue=1,
                                            offvalue=0,
                                            command = lambda v = self.useboundsCbox_val:
                                            self.disable_entry(v))

        self.z_val_var = tk.StringVar(value=0)
        self.z_val = tk.Spinbox(frame,
                                from_=0,
                                to=5000,
                                increment = 200,
                                textvariable = self.z_val_var)


        # ************* when ready ***********
        self.printButton = tk.Button(frame,
                                     text='Готово!',
                                     command=self.reg_state)


        # ************* GEOMETRY ***********
        self.modellabel.grid(row=1, column=1, columnspan=3)
        self.dirButton.grid(row=2, column=1)
        self.r1.grid(row=2, column=2)
        self.r2.grid(row=2, column=3)
        tk.Label(frame, text='Модельное время').grid(row=3, column=1)
        self.set_time.grid(row=3, column=2)
        self.refLabel.grid(row=4, column=0, columnspan=3)
        self.relfButton.grid(row=6, column=1)
        self.echoCbox.grid(row=6, column=2)

        tk.Label(frame, text='Начало').grid(row=7, column=2)
        tk.Label(frame, text='Конец').grid(row=7, column=3)
        tk.Label(frame, text='Широта').grid(row=8, column=1)
        tk.Label(frame, text='Долгота').grid(row=9, column=1)

        self.startlatbox.grid(row=8, column=2)
        self.endlatbox.grid(row=8, column=3)
        self.startlonbox.grid(row=9, column=2)
        self.endlonbox.grid(row=9, column=3)

        self.useboundsCbox.grid(row=10, column=2)
        self.z_val.grid(row=11, column=2)
        tk.Label(frame, text='Граница по\nглубине').grid(row=11, column=1)

        self.printButton.grid(row=12, column=2)

    def opencurrentsdir(self):
        self.currents_dir = tkFileDialog.askdirectory(initialdir=os.path.dirname(os.path.abspath(__file__)))
        #tkMessageBox.showinfo("Выберите папку с данными", self.currents_dir)
        if self.currents_dir:
            self.dirButton_text.set('Папка выбрана')

    def openrelieffile(self):
        self.relief_file = tkFileDialog.askopenfilename(initialdir=os.path.dirname(os.path.abspath(__file__)))
        #tkMessageBox.showinfo("Выберите файл рельефа", self.relief_file)
        if self.relief_file:
            self.relfButton_text.set('Файл выбран')

    def disable_entry(self, var):
        if var.get() == 1:
            self.startlatbox.configure(state='disabled')
            self.endlatbox.configure(state='disabled')
            self.startlonbox.configure(state='disabled')
            self.endlonbox.configure(state='disabled')
        else:
            self.startlatbox.configure(state='normal')
            self.endlatbox.configure(state='normal')
            self.startlonbox.configure(state='normal')
            self.endlonbox.configure(state='normal')

    def enable_model(self, var):
        if var.get() == 'model':
            self.set_time.configure(state = 'normal')
            self.mode = 'model'
        if var.get() == 'LADCP':
            self.set_time.configure(state = 'disabled')
            self.mode = 'LADCP'


    def get_box_val(self):
        if self.usebounds == 0:
            try:
                self.startlat = float(self.startlatbox.get())
                self.endlat = float(self.endlatbox.get())
                self.startlon = float(self.startlonbox.get())
                self.endlon = float(self.endlonbox.get())
            except ValueError:
                tkMessageBox.showinfo("Ошибка","Ошибка ввода значений границ")

    def reg_state(self):
        self.mode = self.mode
        self.echo = self.echo_val.get()
        self.usebounds = self.useboundsCbox_val.get()
        self.get_box_val()
        print self.z_val_var.get()
        try:
            print(self.relief_file)
        except:
            tkMessageBox.showinfo("Ошибка", 'Не выбран файл рельефа')
        try:
            print self.currents_dir
        except:
            tkMessageBox.showinfo("Ошибка", 'Не выбрана папка с данными течений')

        print(self.mode)
        print(self.echo)


root = tk.Tk()
classUI(root)
# root.geometry("200x300")
root.title("Discharge in channel")
root.mainloop()
