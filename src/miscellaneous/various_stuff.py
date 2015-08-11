# -*- coding: utf-8 -*-
from __future__ import division
import os
import shutil

"""
Created on Mon Oct 13 12:10:55 2014

@author: mark
"""


def create_dir(directory):
    if directory[-1] == "/":
        directory = directory[:-1]

    if not os.path.exists(directory):
        os.makedirs(directory)


def dict_to_string(d, sort_key=None):
    if len(d) == 0:
        return "empty dict"

    keys = sorted(d.keys(), key=sort_key)
    m_key = max(len(x.__repr__()) for x in keys) + 1
    str_format = "{:<%s}" % (m_key, ) + "{}"
    str_rows = []
    for each_key in keys:
        str_rows.append(str_format.format(each_key, d[each_key]))
    return "\n".join(str_rows) + "\n"


def doubledict_to_string(d, title="-", str_default=".", sort_key=None):
    if len(d) == 0:
        return "empty doubledict"

    col_title = "<" + title + ">"
    rows = sorted(d.keys(), key=sort_key)
    cols = sorted(list(reduce(lambda x, y: x | y, [set(d[r].keys()) for r in rows])), key=sort_key)

    m_row = max(max(len(x.__repr__()) for x in rows), len(col_title))
    m_col = max(len(x.__repr__()) for x in set(cols) | {cell for sub_dict in d.values() for cell in sub_dict.values()})
    m_row += 1
    m_col += 1

    header_format = "{:^%s}" % (m_row, ) + "".join(["{:>%s}" % (m_col, )] * len(cols))
    cells = [col_title] + [x.__repr__() for x in cols]
    str_rows = [header_format.format(*cells)]

    str_format = "{:<%s}" % (m_row, ) + "".join(["{:>%s}" % (m_col, )] * len(cols))
    for row_name in rows:
        each_row = d[row_name]
        cells = [row_name.__repr__()]
        for col_name in cols:
            if col_name in each_row:
                cells.append(each_row[col_name].__repr__())
            else:
                cells.append(str_default)
        str_rows.append(str_format.format(*cells))

    return "\n".join(str_rows) + "\n"


def multi_max(iterable, key=lambda x: x):
    if len(iterable) == 0:
        raise ValueError("iterable is empty")
    max_value = 0
    max_elements = []
    for each_element in iterable:
        this_val = key(each_element)
        if max_value < this_val or len(max_elements) == 0:
            max_value = this_val
            max_elements = [each_element]
        elif this_val == max_value:
            max_elements.append(each_element)
    return max_elements, max_value