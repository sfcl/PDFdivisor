#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import warnings
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
from PyPDF2 import PdfFileReader
from wand.image import Image as Image2 # Image затеняет класс в библиотеке tkinter
from algo2 import veiw_smart_range
from configuration import app_conf as ac
from resize_canvas import ScrolledCanvas

class ImageGallary(object):
    def __init__(self, parent, text_label, pdf_split_range, approot, root_height):
        # parent - родительский фрейм
        # text_label - объект скорллируемого статусбара
        # pdf_split_range - список картежей с разбивкой страниц
        # approot - строка, содержащая полный путь до данного исполняемого файла
        # root_height - высота глобального экрана Windows
        self.ig_pdf_split_range = pdf_split_range
        self.work_pdf_file = ''
        self.status_bar_text = text_label
        self.mydict = {}
        self.ico_dict = {}
        self.ico_objs = {}
        self.dict_lines = {}
        self.tmp_list = []
        self.text_label = ac.text_label
        self.text_box_height = ac.toolbox_height
        self.parent_height = root_height
        self.width = ac.min_height_a4
        self.height = ac.min_height_a4
        self.pdf_big_blob = {}
        self.set_select_pages = set()
        self.pages_count = 0
        self.ico_size = ac.ico_size
        # картинка должна быть квадратной
        self.active_ico_button = ImageTk.PhotoImage(file=approot + '\\ico\\active.gif')
        self.normal_ico_button = ImageTk.PhotoImage(file=approot + '\\ico\\normal.gif')

        self.frame_for_canvas = Frame(parent, relief="flat")
        self.frame_for_canvas.pack(fill=BOTH, expand=YES)


    def show_void_canvas(self,):
        self.c = ScrolledCanvas(self.frame_for_canvas, )
        self.c.config(bg='white',)

    def show_selected_pdf(self, name_pdf_file):
        self.work_pdf_file = name_pdf_file
        self.status_bar_text.push_text('')  # сбрасываем диапазоны выбранных страниц при новом открытии документа
        self.c.delete(ALL)  # очищаем от предыдущего контента
        self.c.config(width=self.width + self.ico_size,)
        self.c.config(height=self.parent_height - ac.status_bar_height - ac.title_bar_height - 2*ac.ico_size,)
        self.c.config(bg='white')
        self.c.config(scrollregion=(0, 0, self.width+self.ico_size, self.calculate_height()))
        self.show_gallery()

    def calculate_height(self):
        '''
        Метод выполняет заполнение словаря self.pdf_big_blob бинарными строками с содержимым.
        Также вычисляет результирующую высоту скроллируемой канвы.
        '''
        result_height = 0
        book_orient = 'book'    # переменная принимает значения из списка: book, alb, quad. Определяет ореинтацию.
        warnings.filterwarnings('ignore')   # отключаем все нунужные сообщения ;-)
        with open(self.work_pdf_file, 'rb') as pdf_descr:
            pypdf2obj = PdfFileReader(pdf_descr)
            self.pages_count = pypdf2obj.numPages
            #self.status_bar_text = str(1) + '-' + str(self.pages_count) + ','
            for pg in range(self.pages_count):
                tmp_pg = pypdf2obj.getPage(pg)

                w_px = tmp_pg['/MediaBox'][2]
                h_px = tmp_pg['/MediaBox'][3]

                if w_px < h_px:
                    book_orient = 'book'
                    result_height += ac.min_height_a4 + ac.text_label + ac.ico_size

                elif w_px > h_px:
                    book_orient = 'alb'
                    result_height += ac.min_width_a4 + ac.text_label + ac.ico_size
                    #result_height += ac.min_height_a4 + ac.text_label + ac.ico_size

                else:
                    book_orient = 'quad'
                    result_height += ac.min_height_a4 + ac.text_label + ac.ico_size # нужно пересмотреть

        #print(result_height)
        return result_height - ac.ico_size  # после последней страницы дабавлять кнопку ножниц смысла нет


    def show_gallery(self):
        for num_img in range(self.pages_count):
            full_file_name = self.work_pdf_file + '[' + str(num_img) + ']'
            # производим построничную конвертацию Pdf файла в jpeg формат
            with Image2(filename=full_file_name, resolution=ac.rez) as img:
                img.format = 'jpeg'
                ib1 = img.make_blob()

            # ресайзим jpeg до нужного (настраиваемого) размера для последующего отображения
            file_like = io.BytesIO(ib1)
            im = Image.open(file_like)
            im.thumbnail((ac.min_width_a4, ac.min_height_a4,), Image.ANTIALIAS)
            # для этого конвертируем blob в ImageTk.PhotoImage
            # сохраняем объекты ImageTk.PhotoImage ресайзенных картинок в хэше
            self.pdf_big_blob[num_img] = ImageTk.PhotoImage(im)
            im.close()

        scroll_height = 0
        # выполняем отрисовку картинок на master_canvas'е
        for num_img in range(self.pages_count):
            x_offset = int(self.width/2)
            y_offset = int(self.height/2)

            # отрисовываем картинку на канве
            self.c.create_image(x_offset, y_offset+scroll_height, image=self.pdf_big_blob[num_img])

            scroll_height = scroll_height + self.height
            # формируем номер странички
            x_coord_text = int(self.width/2)
            y_coord_text = scroll_height+int(self.text_label/2)
            self.c.create_text(x_coord_text, y_coord_text, text=int(num_img + 1), fill='black')

            scroll_height += self.text_label

            # пропускаем отрисовку последней кнопки ножниц
            if (num_img + 1) == self.pages_count:
                break
            # расчитываем координаты x и y на холсте для иконки ножниц
            x_coord_ico = self.width
            y_coord_ico = scroll_height + self.text_label
            ico_button = self.normal_ico_button

            # помещаем иконку зеленых ножниц на канву
            self.ico_dict[num_img] = ico_button
            x_coord_ico += int(self.ico_size/2)
            y_coord_ico += int(self.ico_size/2)
            ico_obj = self.c.create_image(x_coord_ico, y_coord_ico, image=ico_button)
            self.c.itemconfig(ico_obj, tags=num_img)
            self.ico_objs[num_img] = {'img': ico_obj, 'state': 'normal', 'x': x_coord_ico, 'y': y_coord_ico}

            # связвываем с картинкой колюэк обработчика
            self.c.tag_bind(self.ico_objs[num_img]['img'], '<ButtonPress-1>', self.ico_click)

            scroll_height = scroll_height + self.ico_size


    def ico_click(self, event):
        canvas = event.widget
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        item = event.widget.find_closest(x, y)  # в переменной содержится id элемента канвы
        dict_index = self.c.gettags(item)[0]
        dict_index = int(dict_index)
        if self.ico_objs[dict_index]['state'] == 'normal':
            self.ico_objs[dict_index]['state'] = 'active'
            ico_obj = self.c.create_image(self.ico_objs[dict_index]['x'], self.ico_objs[dict_index]['y'],\
                                          image=self.active_ico_button)
            self.ico_dict[dict_index] = ico_obj
            self.print_dotted_line(dict_index)
            self.set_select_pages.add(dict_index+1)
            self.change_elem_string()
        else:
            self.ico_objs[dict_index]['state'] = 'normal'
            ico_obj = self.c.create_image(self.ico_objs[dict_index]['x'], self.ico_objs[dict_index]['y'],\
                                          image=self.normal_ico_button)
            self.ico_dict[dict_index] = ico_obj
            self.delete_dotted_line(dict_index)
            self.set_select_pages.remove(dict_index+1)
            self.change_elem_string()

        # восстанавливаем свойства объекта
        self.c.itemconfig(ico_obj, tags=dict_index)
        self.ico_objs[dict_index]['img'] = ico_obj
        self.c.tag_bind(self.ico_objs[dict_index]['img'], '<ButtonPress-1>', self.ico_click)

    def print_dotted_line(self, dict_index):
        # печатаем пунктирную линию, координаты извлекаем из словаря self.ico_objs на основе индекса
        y_ico = self.ico_objs[dict_index]['y']
        start_y = y_ico
        end_x = self.width
        end_y = y_ico
        line_obj = self.c.create_line(0, start_y, end_x, end_y, width=3, dash=(4, 4))
        self.dict_lines[dict_index] = line_obj

    def delete_dotted_line(self, dict_index):
        self.c.delete(self.dict_lines[dict_index])

    def change_elem_string(self):
        self.tmp_list = list(self.set_select_pages)
        #print(self.tmp_list)
        mod_tmp_list = veiw_smart_range(self.tmp_list, self.pages_count)
        self.ig_pdf_split_range.set(mod_tmp_list)
        #print(mod_tmp_list)
        tmp_str = ''
        for typle_elem in range(len(mod_tmp_list)):
            if mod_tmp_list[typle_elem][0] == mod_tmp_list[typle_elem][1]:
                tmp_str = tmp_str + str(mod_tmp_list[typle_elem][0]) + ', '
            else:
                tmp_str = tmp_str + str(mod_tmp_list[typle_elem][0]) + '-' + str(mod_tmp_list[typle_elem][1]) + ', '
        #self.status_bar_text.set(tmp_str)
        self.status_bar_text.push_text(tmp_str)


