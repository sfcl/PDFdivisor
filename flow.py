#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from tkinter import *
from tkinter import filedialog

import warnings
from PyPDF2 import PdfFileReader
from configuration import app_conf as ac
from resize_canvas import ScrolledCanvas

class ImageGallary(object):
    def __init__(self, parent, approot, root_height):
        # parent - родительский фрейм
        # text_label - объект скорллируемого статусбара
        # pdf_split_range - список картежей с разбивкой страниц
        # approot - строка, содержащая полный путь до данного исполняемого файла
        # root_height - высота глобального экрана Windows

        self.mydict = {}
        self.approot = approot
        self.tmp_list = []
        self.text_label = ac.text_label
        self.text_box_height = ac.toolbox_height
        self.parent_height = root_height
        self.c = ''
        self.width = ac.min_width_a4
        self.pages_count = 0
        self.ico_size = ac.ico_size
        self.frame_for_canvas = Frame(parent, relief="flat")
        self.frame_for_canvas.pack(fill=BOTH, expand=YES)
        self.full_canvas_height = 0

    def show_void_canvas(self, pdf_split_range=None, text_label=None):
        self.c = ScrolledCanvas(self.frame_for_canvas, approot=self.approot)
        self.c.config(bg='white',)
        self.c.ig_pdf_split_range = pdf_split_range
        self.c.status_bar_text = text_label

    def show_selected_pdf(self, name_pdf_file):
        self.c.first_render = True
        self.c.work_pdf_file = name_pdf_file
        self.c.status_bar_text.push_text('')  # сбрасываем диапазоны выбранных страниц при новом открытии документа
        self.c.delete(ALL)  # очищаем от предыдущего контента
        self.c.config(width=ac.min_height_a4 + self.ico_size,)
        self.c.view_port_height = self.parent_height - ac.status_bar_height - ac.title_bar_height - 2*ac.ico_size
        self.c.config(height=self.c.view_port_height,)
        self.c.config(bg='white')
        self.full_canvas_height = self.calculate_height
        #self.c.koef = self.full_canvas_height / view_port_height
        self.c.config(scrollregion=(0, 0, self.width+self.ico_size, self.full_canvas_height))
        self.c.set_select_pages = set() # очищаем множество выбранных диапазонов

        if self.c.page_counts <= ac.magic_constant:
            # рендеринг всех страниц, какие есть в документе

            self.c.render_pages([le for le in range(self.c.page_counts)])
        else:
            # рендерим только первые ac.magic_constant страниц, остальные бужем рендерить по ходу скроллирования
            self.c.render_pages([le for le in range(ac.magic_constant)])

    @property
    def calculate_height(self):
        '''
        Метод выполняет заполнение словаря self.pdf_big_blob бинарными строками с содержимым.
        Также вычисляет результирующую высоту скроллируемой канвы.
        Также производим инициализацию словаря self.c.page_range_coord по которому потом будем итерироваться
        '''

        warnings.filterwarnings('ignore')   # отключаем все нунужные сообщения ;-)

        # иногда случается, что пользователь открыл окно выбора файла, ничего не выбрал, и закрыл.
        # данный хак позволяет обйти этот юскейс
        if not self.c.work_pdf_file:
            return 0

        with open(self.c.work_pdf_file, 'rb') as pdf_descr:
            pypdf2obj = PdfFileReader(pdf_descr)
            self.c.page_counts = pypdf2obj.numPages
            result_height = 0
            y_offset = 0

            for pg in range(self.c.page_counts):
                tmp_pg = pypdf2obj.getPage(pg)

                w_px = tmp_pg['/MediaBox'][2]
                h_px = tmp_pg['/MediaBox'][3]

                if w_px < h_px:
                    book_orient = 'b' # book
                    result_height += ac.min_height_a4 + ac.text_label + ac.ico_size
                    page_height = ac.min_height_a4

                elif w_px > h_px:
                    book_orient = 'a' # album
                    result_height += ac.min_width_a4 + ac.text_label + ac.ico_size
                    page_height = ac.min_width_a4

                else:
                    book_orient = 'q' # quadrat
                    result_height += ac.min_height_a4 + ac.text_label + ac.ico_size # нужно пересмотреть
                    page_height = ac.min_height_a4

                self.c.page_range_coord.set_params(page_number=pg, y_offset=y_offset, orient=book_orient, render=False)
                long_y_offset = y_offset + page_height + ac.ico_size + ac.text_label
                self.c.ranges_tree.addi(y_offset, long_y_offset-1, pg)

                # смещение по оси Y следующей странички
                if book_orient == 'b':
                    y_offset = y_offset + ac.min_height_a4 + ac.text_label + ac.ico_size
                elif book_orient == 'a':
                    y_offset = y_offset + ac.min_width_a4 + ac.text_label + ac.ico_size
                elif book_orient == 'q':
                    y_offset = y_offset + ac.min_height_a4 + ac.text_label + ac.ico_size
                else:
                    print('Error. C\'nt get page orient!')



        return result_height - ac.ico_size  # после последней страницы дабавлять кнопку ножниц смысла нет
