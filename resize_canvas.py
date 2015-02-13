#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
from PIL import ImageTk, Image
import ttk
import io
from wand.image import Image as Image2 # Image затеняет класс в библиотеке tkinter
import intervaltree
from algo2 import veiw_smart_range
from page_range_coord import page_coords
from configuration import app_conf as ac

class ScrolledCanvas(Canvas):
    '''
    Контейнер с канвой. В него автоматически добвляется правый скролбар
    '''
    def __init__(self, container, approot='', **kwargs):
        Canvas.__init__(self, container)
        self.update_idletasks()
        self.config(borderwidth=0)
        self.config(**kwargs)
        # --------
        self.ranges_tree = intervaltree.IntervalTree()
        self.view_port_height = 0
        self.koef = 0
        self.page_counts = 0    # магаважная структура данных
        self.work_pdf_file = '' # содержит строку с полным именем файла
        self.page_range_coord = page_coords()  # словарь вида {0 : {'y_offset': 0, 'orient' : 'a', 'render' : False}, }
        self.first_render = True    # Логический флаг первого рендеринга, после события он инвертируется
        self.width = ac.min_height_a4
        self.height = ac.min_height_a4
        self.ico_dict = {}
        self.ico_objs = {}
        self.pdf_big_blob = {}
        self.dict_lines = {}
        self.set_select_pages = set()
        self.ig_pdf_split_range = ''
        self.status_bar_text = ''
        # картинка должна быть квадратной
        self.active_ico_button = ImageTk.PhotoImage(file=approot + '\\ico\\active.gif')
        self.normal_ico_button = ImageTk.PhotoImage(file=approot + '\\ico\\normal.gif')
        # --------
        self.vbar = ttk.Scrollbar(container)

        self.vbar.pack(side=RIGHT,  fill=Y)                 # pack canvas after bars
        self.pack(side=TOP, fill=BOTH, expand=YES)

        self.vbar.config(command=self.yview)                # call on scroll move
        self.config(yscrollcommand=self.vbar.set)           # call on canvas move

        self.vbar.bind('<ButtonRelease-1>', self.callback)

    def callback(self, event):
        '''

        '''
        procent = self.vbar.get()[1]
        sy = self.view_port_height * procent
        sy-=17
        #print('compute y =', sy)
        #print('event y =', event.y)
        real_y = self.canvasy(sy)
        set1 = self.ranges_tree.search(real_y, real_y + 1)  # искусственно увеличим второй параметр на 1 пиксель
        try:
            page = sorted(set1)[0].data
        except IndexError:
            return
        #print('page = ', page,' ', self.vbar.get()[1])

        if (page - 1) < 0:              # скролл находится на первой странице
            tmp_list = [page, page + 1]
        elif page == self.page_counts-1:  # скролл на последней странице
            tmp_list = [page, page - 1, ]
        else:                           # во всех остальных случаях
            tmp_list = [page, page - 1, page + 1]

        self.render_pages(tmp_list)

    def y_coord_to_page(self, y_coord):
        '''
        Метод реализует перещёт Y координаты в номер страницы.
        '''
        pass

    def render_pages(self, list_pages=[]):
        '''
        Производит рендеринг перечисленных в списке list_pages страниц
        '''
        if self.first_render:
            # производим отрисовку всех кнопок "ножниц" и номеров страниц на канве
            # данный блок выполняется только один раз
            for np in range(self.page_counts):
                orient_page = self.page_range_coord[np].orient
                y_offset = self.page_range_coord[np].y_offset
                if orient_page == 'b':
                    y_offset = y_offset + ac.min_height_a4
                elif orient_page == 'a':
                    y_offset = y_offset + ac.min_width_a4
                else:
                    y_offset = y_offset + ac.min_height_a4

                # в text_label пишем номер странички
                # рисуем номер странички
                x_coord_text = int(self.width/2)
                y_coord_text = y_offset+int(ac.text_label/2)
                self.create_text(x_coord_text, y_coord_text, text=int(np + 1), fill='black')
                # рисуем иконку с зелёными ножницами
                # пропускаем отрисовку последней кнопки ножниц
                if (np + 1) == self.page_counts:
                    break
                # расчитываем координаты x и y на холсте для иконки ножниц
                x_coord_ico = ac.min_width_a4
                y_coord_ico = y_offset + ac.text_label

                # помещаем иконку зеленых ножниц на канву
                self.ico_dict[np] = self.normal_ico_button
                x_coord_ico += int(ac.ico_size/2)
                y_coord_ico += int(ac.ico_size/2)
                ico_obj = self.create_image(x_coord_ico, y_coord_ico, image=self.normal_ico_button)
                self.itemconfig(ico_obj, tags=np)
                self.ico_objs[np] = {'img': ico_obj, 'state': 'normal', 'x': x_coord_ico, 'y': y_coord_ico}

                # связвываем с картинкой код обработчика
                self.tag_bind(self.ico_objs[np]['img'], '<ButtonPress-1>', self.ico_click)

                self.page_range_coord[np].render = False
            # инвертируем флаг self.first_render, и больше в эту веточку не заходим
            self.first_render = False



        for num_img in list_pages:
            # повторно не рендерим то, что уже отрендерено
            if self.page_range_coord[num_img].render :
                continue

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

            # выполняем отрисовку картинок на master_canvas'е

            x_offset = int(self.width/2)
            y_offset = int(self.height/2)

            # отрисовываем картинку на канве
            self.create_image(x_offset, y_offset + self.page_range_coord[num_img].y_offset,
                              image=self.pdf_big_blob[num_img])
            # устанавливаем флажок, что данная страничка отрендеренна
            self.page_range_coord[num_img].render = True
            self.update_idletasks()


    def ico_click(self, event):
        canvas = event.widget
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        item = event.widget.find_closest(x, y)  # в переменной содержится id элемента канвы
        dict_index = self.gettags(item)[0]
        dict_index = int(dict_index)
        if self.ico_objs[dict_index]['state'] == 'normal':
            self.ico_objs[dict_index]['state'] = 'active'
            ico_obj = self.create_image(self.ico_objs[dict_index]['x'], self.ico_objs[dict_index]['y'],\
                                          image=self.active_ico_button)
            self.ico_dict[dict_index] = ico_obj
            self.print_dotted_line(dict_index)
            self.set_select_pages.add(dict_index+1)
            self.change_elem_string()
        else:
            self.ico_objs[dict_index]['state'] = 'normal'
            ico_obj = self.create_image(self.ico_objs[dict_index]['x'], self.ico_objs[dict_index]['y'],\
                                          image=self.normal_ico_button)
            self.ico_dict[dict_index] = ico_obj
            self.delete_dotted_line(dict_index)
            self.set_select_pages.remove(dict_index+1)
            self.change_elem_string()

        # восстанавливаем свойства объекта
        self.itemconfig(ico_obj, tags=dict_index)
        self.ico_objs[dict_index]['img'] = ico_obj
        self.tag_bind(self.ico_objs[dict_index]['img'], '<ButtonPress-1>', self.ico_click)

    def print_dotted_line(self, dict_index):
        # печатаем пунктирную линию, координаты извлекаем из словаря self.ico_objs на основе индекса
        y_ico = self.ico_objs[dict_index]['y']
        start_y = y_ico
        end_x = self.width
        end_y = y_ico
        line_obj = self.create_line(0, start_y, end_x, end_y, width=3, dash=(4, 4))
        self.dict_lines[dict_index] = line_obj

    def delete_dotted_line(self, dict_index):
        self.delete(self.dict_lines[dict_index])

    def change_elem_string(self):
        self.tmp_list = list(self.set_select_pages)
        #print(self.tmp_list)
        mod_tmp_list = veiw_smart_range(self.tmp_list, self.page_counts)
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