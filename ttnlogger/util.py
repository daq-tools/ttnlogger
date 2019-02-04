# -*- coding: utf-8 -*-
# (c) 2016 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import math
import datetime


def convert_floats(data, integers=None):
    """
    Convert all numeric values in dictionary to float type.
    """
    integers = integers or []
    delete_keys = []
    for key, value in data.iteritems():
        try:
            if isinstance(value, datetime.datetime):
                continue
            if is_number(value):
                if key in integers:
                    data[key] = int(value)
                else:
                    data[key] = float(value)
            if math.isnan(data[key]):
                delete_keys.append(key)
        except:
            pass

    for key in delete_keys:
        del data[key]

    return data


def is_number(s):
    """
    Check string for being a numeric value.
    http://pythoncentral.io/how-to-check-if-a-string-is-a-number-in-python-including-unicode/
    """
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False
