#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import threading
from threading import current_thread
import os
import os.path
import queue
from tkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
import intervaltree
from algo2 import veiw_smart_range
from page_range_coord import page_coords
from configuration import app_conf as ac
from thread_class import thread_render_one_page

class ScrolledCanvas(Canvas):
    '''
    Контейнер с канвой. В него автоматически добвляется правый скролбар
    '''
    def __init__(self, container, approot='', **kwargs):
        Canvas.__init__(self, container)
        self.update_idletasks()
        self.queue = queue.Queue()
        self.config(borderwidth=0)
        self.config(**kwargs)
        self.config(highlightthickness=0,) # убираем бордер в 2 пикселя вокруг канвы
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
        self.image_name = ''
        self.fp = 0
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
        #self.vbar.config(command=self.yview)                # call on scroll move
        self.vbar.config(command=self.click_arrow)                # call on scroll move
        self.config(yscrollcommand=self.vbar.set)           # call on canvas move
        self.vbar.bind('<ButtonRelease-1>', self.callback)
        self.vbar.bind("<MouseWheel>", self.mouse_wheel)
        self.bind("<MouseWheel>", self.mouse_wheel)

    def click_arrow(self, *argv):
        self.yview(*argv)
        self.callback()

    def mouse_wheel(self, event):
        '''
        Прокручиваем канву при скроллировании ролика мыши
        '''
        self.yview("scroll", int((-1)*event.delta / 120), "units")
        self.callback()


    def callback(self, event=None):
        '''
        Метод-обработчик, срабатывающий после отпускания левой клавиши мыши
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

        if page == 0:              # скролл находится на первой странице
            tmp_list = [page, ]
        elif page == self.page_counts-1:  # скролл на последней странице
            tmp_list = [page, page - 1]
        else:                           # во всех остальных случаях
            #tmp_list = [page - 1, page, page + 1]
            tmp_list = [page - 1, page + 1 , page]

        print('list_for_render=',tmp_list)
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

        # производим отрисовку кнопок "ножниц" и номеров страниц на канве
        # если страница отрендерина, то не рисуем картинку
        for np in list_pages:

            if self.page_range_coord[np].render:
                continue

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
            if self.page_range_coord[np].orient == 'b':
                x_coord_text = int(ac.min_width_a4 / 2)
            elif self.page_range_coord[np].orient == 'a':
                x_coord_text = int(ac.min_height_a4 / 2)
            else:
                x_coord_text = int(ac.min_height_a4 / 2)

            y_coord_text = y_offset+int(ac.text_label/2)
            self.create_text(x_coord_text, y_coord_text, text=int(np + 1), fill='black')
            # рисуем иконку с зелёными ножницами
            # пропускаем отрисовку последней кнопки ножниц
            if (np + 1) == self.page_counts:
                break
            # расчитываем координаты x и y на холсте для иконки ножниц
            x_coord_ico = ac.min_height_a4
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


        # через жопу очищаем содержимое очереди
        while not self.queue.empty():
            try:
                self.queue.get(False)
            except Empty:
                continue
            self.queue.task_done()

        for num_img in list_pages:
            # повторно не рендерим то, что уже отрендерено
            if self.page_range_coord[num_img].render:
                print('page_num=',num_img, ' render!')
                continue
            else:
                self.queue.put(num_img)
            #t1 = threading.Thread(target=self.render_one_page, args=(num_img,))
            #t1.start()
            #print('page= ', num_img)


        self.queue.put(None)
        thread_render_one_page(
            queue_pages=self.queue,
            work_pdf_file=self.work_pdf_file,
            page_range_coord=self.page_range_coord,
            canvas=self,
            pdf_big_blob=self.pdf_big_blob,
        ).start()

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