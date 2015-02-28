#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
from os import environ

from tkinter import *
from tkinter import filedialog, messagebox
from flow import ImageGallary
from PyPDF2 import PdfFileWriter, PdfFileReader
from configuration import app_conf as ac
from share_var import share_list_diap
from my_status_bar import my_status_bar
from about_window import about_box

# цель сделать доступными dll библиотеки imagemagic и gs из каталога программы
# когда данные библиотеки не устаовлены
try:
    approot = os.path.dirname(os.path.abspath(__file__))
except NameError:
    approot = os.path.dirname(os.path.abspath(sys.argv[0]))

old_path = environ['PATH']
environ['PATH'] = old_path + ';' + approot
#print(environ['PATH'])
file_name = os.path.abspath(sys.argv[0]).split(os.sep)[-1]
ext = file_name.split('.')[-1]

if ext == 'exe':
    environ['MAGICK_CODER_MODULE_PATH'] = approot + '/modules/coders'
    environ['MAGICK_HOME'] = approot
    environ['GS_DLL'] = approot
    environ['GS_LIB'] = approot



class App():
    def __init__(self, master, main_screen_height):
        self.main_screen_height = main_screen_height
        self.pdf_file_name = ''
        self.output_directory = ''
        self.pdf_split_range = share_list_diap()
        self.frame = Frame(master, relief=FLAT, width=win_width, height=11)
        self.frame.config(bg=ac.bg)

        self.button_pannel = Frame(self.frame, relief="flat")
        self.button_pannel.pack(side=TOP, fill=BOTH, expand=YES)
        self.button_pannel.config(bg=ac.bg)

        add_gif = PhotoImage(file=approot + '/ico/add.gif')
        self.b1 = Button(self.button_pannel, command=self.open_file, image=add_gif)
        self.b1.image = add_gif
        self.b1.pack(padx=2, pady=2, side=LEFT)

        openfolder = PhotoImage(file=approot + '/ico/openfolder.gif')
        self.b2 = Button(self.button_pannel, image=openfolder, command=self.open_folder)
        self.b2.image = openfolder
        self.b2.pack(padx=2, pady=2, side=LEFT)

        runico = PhotoImage(file=approot + '/ico/run.gif')
        self.b3 = Button(self.button_pannel, image=runico, command=self.run_split)
        self.b3.image = runico
        self.b3.pack(padx=2, pady=2, side=LEFT)

        aboutico = PhotoImage(file=approot + '/ico/about.gif')
        self.b4 = Button(self.button_pannel, image=aboutico, command=self.about)
        self.b4.image = aboutico
        self.b4.pack(padx=2, pady=2, side=LEFT)

        exitico = PhotoImage(file=approot + '/ico/exit.gif')
        self.b5 = Button(self.button_pannel, image=exitico, command=lambda: self.quit(master))
        self.b5.image = exitico
        self.b5.pack(padx=2, pady=2, side=LEFT)


        self.context_line = my_status_bar(self.frame)
        self.context_line.pack(side=BOTTOM, fill=X)
        # отрисовываем пустую канву при запуске программы

        self.flow = ImageGallary(self.frame, approot, self.main_screen_height)
        self.flow.show_void_canvas(pdf_split_range=self.pdf_split_range, text_label=self.context_line)
        self.frame.pack()

    def open_file(self):
        self.pdf_file_name = filedialog.askopenfilename(filetypes=[('PDF документ', '*.pdf',)],
                                                        title='Выберите PDF файл',
                                                        initialdir='E:\\work\\darsy\\projects\\prepare_pdf')
        self.flow.show_selected_pdf(self.pdf_file_name)

    def open_folder(self):
        self.output_directory = filedialog.askdirectory(title='Выберите каталог сохранения файлов', parent=self.frame)

    def about(self):
        title = 'О программе'
        message = "Автор программы: Хозяинов Максим \nВерсия: %s \n "
        message = (message % (version,))
        ab = about_box(self.frame, title, message, r'http://darsytools.org/divisor/')

    def run_split(self):
        '''
            Производит работу по разбиению PDF файла на диапазоны.
            Предварительно проверив на отсутствие значений некоторых переменных.
        '''
        if self.output_directory == '' and self.pdf_file_name == '':
            pass
            return

        if self.output_directory == '':
            title = 'Ошибка'
            message = 'Необходиомо выбрать каталог для сохранения PDF файлов'
            messagebox.showinfo(title, message)
            return

        if self.pdf_file_name == '':
            title = 'Ошибка'
            message = 'Необходимо выбрать PDF файл'
            messagebox.showinfo(title, message)
            return

        if len(self.pdf_split_range.get_all()) == 0 or len(self.pdf_split_range.get_all()) == 1:
            return

        base_file_name = os.path.basename(self.pdf_file_name).split('.')[-2]
        tmp_list = self.pdf_split_range.get_all()

        # выполняем основную работу по разбивке PDF документа
        for diap in range(len(tmp_list)):

            if tmp_list[diap][0] == tmp_list[diap][1]:
                cunstruct_pdf_file_name = self.output_directory + '/' + base_file_name + '_' + str(tmp_list[diap][0])+ \
                    '-' + str(tmp_list[diap][0]) + '.pdf'
                infile = PdfFileReader(open(self.pdf_file_name, 'rb'))
                p = infile.getPage(tmp_list[diap][0]-1)
                outfile = PdfFileWriter()
                outfile.addPage(p)
                with open(cunstruct_pdf_file_name, 'wb') as f:
                    outfile.write(f)

                #print(cunstruct_pdf_file_name)


            if tmp_list[diap][0] < tmp_list[diap][1]:
                cunstruct_pdf_file_name = self.output_directory + '/' + base_file_name + '_' + str(tmp_list[diap][0])+ \
                    '-' + str(tmp_list[diap][1]) + '.pdf'
                infile = PdfFileReader(open(self.pdf_file_name, 'rb'))
                range_length = tmp_list[diap][1] - tmp_list[diap][0] + 1
                outfile = PdfFileWriter()
                for pgs in range(range_length):
                    p = infile.getPage(tmp_list[diap][0] + pgs - 1)
                    outfile.addPage(p)

                    # сохраняем диапазон в отдельном файле
                with open(cunstruct_pdf_file_name, 'wb') as f:
                    outfile.write(f)

    def quit(self, master):
        master.destroy()

version = '0.2.1'


root = Tk()
root.title(ac.title)
root.config(bg=ac.bg)

# данные значения подобраны опытным путём для PDF в формате А4.
min_width_a4 = ac.min_width_a4
min_height_a4 = ac.min_height_a4

# выполняем центрирование окна
w = root.winfo_vrootwidth()
h = root.winfo_vrootheight()

# в данном случае предусмотрена возможнасть открытия PDF с альбомной ориентацией
win_width = min_height_a4 + ac.ico_size
#win_height = min_height_a4 + ac.toolbox_height + ac.status_bar_height

x = (w // 2) - (win_width // 2)
y = 0
root.geometry("+%d+%d" % (x, y,))
#root.resizable(0, 0)    # запрет на изменение размеров родительского фрейма

app = App(root, h)
root.mainloop()
