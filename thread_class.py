#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import threading
import tempfile
from PIL import Image, ImageTk
from pdf2img import convert
from configuration import app_conf as ac


class thread_render_one_page(threading.Thread):
    def __init__(self,
                 queue_pages=None,
                 work_pdf_file=None,
                 page_range_coord=None,
                 canvas=None,
                 pdf_big_blob=None,
    ):
        threading.Thread.__init__(self)
        self.queue_pages = queue_pages
        self.im = ''
        self.worker = ''
        self.canvas = canvas
        self.page_range_coord = page_range_coord
        self.pdf_big_blob = pdf_big_blob
        self.work_pdf_file = work_pdf_file
        self.f_name = ''
        self.fp = None
        self.num_img = 0

    def run(self):
        while 1:
            self.num_img = self.queue_pages.get()
            if self.num_img is None:
                break   # достигнут конец очереди
            #print('in thread', self.num_img)
            self.fp = tempfile.TemporaryFile()
            self.f_name = self.fp.name
            self.fp.close()

            self.worker = convert(filename=self.work_pdf_file,
                                  rez=ac.rez,
                                  page_number=self.num_img + 1,
                                  cache_img=self.f_name)
            #print(self.f_name, 'Файл существует', os.path.isfile(self.f_name))
            if not(os.path.isfile(self.f_name)):
                return
            #sys.exit(0)
            self.im = Image.open(self.f_name)
            if self.page_range_coord[self.num_img].orient == 'b':     # если ориентация страницы книжная, то
                self.im.thumbnail((ac.min_width_a4, ac.min_height_a4,), Image.ANTIALIAS)
            elif self.page_range_coord[self.num_img].orient == 'a':   # если ориентация страницы альюомная, то
                self.im.thumbnail((ac.min_height_a4, ac.min_width_a4, ), Image.ANTIALIAS)
            else:                                       # во всех остальных случаях
                self.im.thumbnail((ac.min_height_a4, ac.min_height_a4, ), Image.ANTIALIAS)

            # для этого конвертируем blob в ImageTk.PhotoImage
            # сохраняем объекты ImageTk.PhotoImage ресайзенных картинок в хэше
            self.pdf_big_blob[self.num_img] = ImageTk.PhotoImage(self.im)
            #print('pdf_blob=', self.pdf_big_blob[self.num_img], 'num_img=', num_img)
            self.im.close()

            # выполняем отрисовку картинок на master_canvas'е
            if self.page_range_coord[self.num_img].orient == 'b':
                x_offset = int(ac.min_width_a4 / 2)
            elif self.page_range_coord[self.num_img].orient == 'a':
                x_offset = int(ac.min_height_a4 / 2)
            else:
                x_offset = int(ac.min_height_a4 / 2)

            if self.page_range_coord[self.num_img].orient == 'b':
                y_offset = int(ac.min_height_a4 / 2)
            elif self.page_range_coord[self.num_img].orient == 'a':
                y_offset = int(ac.min_width_a4 / 2)
            else:
                y_offset = int(ac.min_height_a4 / 2)

            # отрисовываем картинку на канве
            self.canvas.create_image(x_offset, y_offset + self.page_range_coord[self.num_img].y_offset,
                              image=self.pdf_big_blob[self.num_img])
            # устанавливаем флажок, что данная страничка отрендеренна
            self.page_range_coord[self.num_img].render = True
            self.canvas.update_idletasks()

            #очищаем за собой больше ненужные файлы
            os.remove(self.f_name)

    def __del__(self):
        '''
        Подчищаем за собой файловую систему
        '''
        return
        os.remove(self.f_name)