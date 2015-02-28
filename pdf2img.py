#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ghostscript import _gsprint as gs

def convert(filename='', rez=300, page_number=1,cache_img=''):

    args = [
    #"pdf2jpeg",	# данное значение не обязательно
    "-dBATCH",
    "-dSAFER",
    "-dFirstPage=" + str(page_number),
    "-dLastPage=" + str(page_number),
    "-sDEVICE=jpeg",
    "-r" + str(rez),
    "-sOutputFile=" + cache_img,
    #"-c",
    #".setpdfwrite",
    #"-f",
    "-dNOPAUSE",
    "-dQUIET",   # отключаем вывод тектовых сообщений
    "" + str(filename)
    ]

    instance = gs.new_instance()
    code = gs.init_with_args(instance, args)
    code1 = gs.exit(instance)
    gs.delete_instance(instance)
