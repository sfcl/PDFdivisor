#!/usr/bin/env python
# -*- coding: utf-8 -*-

def veiw_smart_range(list_buttons, max_num_page):
    diap = []
    sbuttons = list_buttons[:]
    sbuttons.append(1)
    sbuttons.append(max_num_page)

    sbuttons.sort()
    max = len(sbuttons)

    for i in range(max-1):
        if len(sbuttons) == 0:
            break

        elif sbuttons[0] == sbuttons[1]:
            diap.append((sbuttons[0], sbuttons[0],))
            tmp = sbuttons[0]
            del sbuttons[0:2:1]
            sbuttons.append(tmp+1)
            sbuttons.sort()

        elif sbuttons[0] == sbuttons[1] - 1:
            diap.append((sbuttons[0], sbuttons[1],))
            tmp = sbuttons[1]
            del sbuttons[0:2:1]
            sbuttons.append(tmp+1)
            sbuttons.sort()

        elif sbuttons[0] < (sbuttons[1] - 1):
            diap.append((sbuttons[0], sbuttons[1],))
            tmp = sbuttons[1]
            del sbuttons[0:2:1]
            sbuttons.append(tmp+1)
            sbuttons.sort()


    return diap

if __name__ == '__main__':
    buttons = [1,2,4,5,]
    mp = 30
    print(veiw_smart_range(buttons, mp))