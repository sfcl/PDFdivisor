#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class stuff(object):
    def __init__(self):
        self.page = 0
        self.y_offset = 0
        self.orient = 'b'
        self.render = False


class page_coords(object):
    '''
    Хранилище будующих параметров рендеринга страницы
    '''
    def __init__(self):
        self.prepare_pages = {}

    def set_params(self, page_number=0, y_offset=0, orient='b', render=False ):
        stuff_obj = stuff()
        stuff_obj.page = page_number
        stuff_obj.y_offset = y_offset
        stuff_obj.orient = orient
        stuff_obj.render = render
        self.prepare_pages[page_number] = stuff_obj

    def get_render(self, page_number):
        return self.prepare_pages[page_number].render

    def set_render(self, page_number):
        self.prepare_pages[page_number].render = True

    def __getitem__(self, key):
       return self.prepare_pages[key]

    def __str__(self):
        str_obj = ''
        for elem in self.prepare_pages:
            if self.prepare_pages[elem].render:
                str_obj += str(elem) + ' '
            #str_obj += 'index=' + str(elem) + ' render=' + str(self.prepare_pages[elem].render) + '\n'
            #print('index=', elem,' render=' ,self.prepare_pages[elem].render)
        str_obj += '\n'
        return str_obj