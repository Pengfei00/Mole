#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from core.abstract import Extract
from core.result import Img


class Musci163(Extract):
    Host = "music.163.com"

    def get_img(self, soup, response, img_num, **kwargs):
        if img_num < 1:
            return

        img_url = soup.find("meta", attrs={"property": "og:image"})['content']
        img_width, img_height = re.search("thumbnail=(\d+)y(\d+)&", img_url).groups()
        yield Img(url=img_url, width=img_width, height=img_height)
