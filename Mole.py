#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.parse import urlparse
from core.abstract import Empty
from site_extract import *


def fetch(url, img_num=1):
    if url[:4] != "http":
        return None
    host = urlparse(url=url).netloc
    fn = General.function_map.get(host, General.function_map.get("*"))
    result = fn.new(url=url, img_num=img_num)
    if result == Empty:
        return None
    return result
