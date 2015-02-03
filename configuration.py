#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class app_conf(object):
    """
    Данный класс создан исключительно для хранения настроек
    приложения.
    """
    title = 'PDF Divisor'
    min_width_a4 = 446
    min_height_a4 = 631
    #min_height_a4 = 650

    toolbox_height = 11
    status_bar_height = 14
    #vertical_line_ico_box = 25   #
    text_label = 25 # высота блока отводимого для отображения номеров страниц
    ico_size = 25 # размеры иконки

    rez = 120 # DPI для геперируемой странички

    def __int__(self):
        pass

    def __str__(self):
        pass