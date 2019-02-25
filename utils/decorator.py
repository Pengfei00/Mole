#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time


def time_print(fun):
    def fn(*args, **kwargs):
        star = time.time()
        res = fun(*args, **kwargs)
        print(fun, time.time() - star)
        return res

    return fn

