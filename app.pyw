#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import locale
import os.path
from os import environ
import gettext
import warnings
from tkinter import *
from tkinter import filedialog, messagebox
from flow import ImageGallary
import PyPDF2
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
        
        # создаем временный файл, для рендеринга PDF
        # послу закрытия программы этот файл удаляется


        # отрисовываем пустую канву при запуске программы
        self.flow = ImageGallary(self.frame, approot, self.main_screen_height)
        self.flow.show_void_canvas(pdf_split_range=self.pdf_split_range, text_label=self.context_line)
        self.frame.pack()

    def open_file(self):
        self.pdf_file_name = filedialog.askopenfilename(filetypes=[(_('PDF document'), '*.pdf',)],
                                                        title=_('Select PDF file'),
                                                        initialdir='')
        # перехватываем возможные проблемы с битыми PDF никами
        warnings.filterwarnings('ignore')

        # если ничего не выбрано,то выходим из метода
        if not self.pdf_file_name:
            return
        fp = open(self.pdf_file_name, 'rb')
        try:
            yap = PdfFileReader(fp)
            tmp = str(yap.documentInfo)
        except PyPDF2.utils.PdfReadError as ex:
            tmp = str(ex)
            messagebox.showinfo('Ошибка', tmp)
            # messagebox(_('Error'), _('Not do') + tmp)

        except PyPDF2.utils.PdfStreamError as ex:
            tmp = str(ex)
            messagebox.showinfo('Ошибка', tmp)
            # messagebox(_('Error'), _('Not do') + tmp)

        except PyPDF2.utils.PyPdfError as ex:
            tmp = str(ex)
            messagebox.showinfo('Ошибка', tmp)
            # messagebox(_('Error'), _('Not do') + tmp)
        else:
            # данный блок выполняется если исключения не сработали
            fp.close()
            self.flow.show_selected_pdf(self.pdf_file_name)
        finally:
            fp.close()

    def open_folder(self):
        self.output_directory = filedialog.askdirectory(title=_('Select directoy to save PDF files'), parent=self.frame)

    def about(self):
        title = _('About program')
        message = _('Author program:') + ' ' + _("Hozyainov Maxim") + '\n' + _("Version:") + " %s \n "
        message = (message % (version,))
        message = message + _('license') + ': GPL v3\n'
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
            title = _('Error')
            message = _('Need to select folder to save PDF files')
            messagebox.showinfo(title, message)
            return

        if self.pdf_file_name == '':
            title = _('Error')
            message = _('Need to select PDF file')
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


# производим настройку i18n
# >>> locale.getdefaultlocale()
# ('ru_RU', 'cp1251')
if locale.getdefaultlocale()[0].split('_')[0].upper() == 'RU':
    ru = gettext.translation('ru', localedir='translations', languages=['ru'])
    ru.install()
else:
    # для всех остальных локализаций будем показывать сообщения на английском
    en = gettext.translation('en', localedir='translations', languages=['en'])
    en.install()

version = '0.2.5'


root = Tk()
root.title(ac.title + ' ' + version)
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
