#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class app_conf(object):
    """
    Данный класс создан исключительно для хранения настроек
    приложения.
    """
    title = 'divpdf'
    min_width_a4 = 446
    min_height_a4 = 631
    #min_height_a4 = 650
    bg = "#D4D0C8"
    toolbox_height = 11
    #status_bar_height = 14
    #vertical_line_ico_box = 25   #
    text_label = 25 # высота блока отводимого для отображения номеров страниц
    ico_size = 25 # размеры иконки

    rez = 120 # DPI для геперируемой странички
    title_bar_height = 30 # возьмём с запасом высоту заголовка окна, данный параметр зависит от текущей темы Windows
    status_bar_height = 65

    magic_constant = 3 # максимальное кол-во страниц, рендеринг которых происходит сразу при загрузке файла

    def __int__(self):
        pass

    def __str__(self):
        pass