#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class share_list_diap(object):
    """
    Класс для создания интерфейсного объекта, используемого для взаимодействия объектов класса
    ImageGallary и App.
    """
    def __int__(self):
        self.inner_list = []

    def set(self, some_list):
        self.inner_list = some_list

    def get_all(self):
        return self.inner_list
