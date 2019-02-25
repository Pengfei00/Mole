#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from typing import Optional

import requests

from core.abstract import Extract, Empty
from core.result import Result, Img


class MpWeiXin(Extract):
    Host = "mp.weixin.qq.com"

    def extract(self, response: requests.Response, img_num, soup=None) -> Optional[Result]:
        data = response.text
        start_end = re.search(pattern="var msg_title = .*?    var msg_link = ", string=data, flags=re.S)
        if not start_end:
            return Empty
        title = ""
        description = ""
        img = []
        for i in start_end.group().split("\n"):
            text = i.strip()
            if text.startswith("var msg_title"):
                title = text.split(" = ", maxsplit=1)[-1][1:-2]
            elif text.startswith("var msg_desc"):
                description = text.split(" = ", maxsplit=1)[-1][1:-2]
            elif len(img) < img_num and text.startswith("var msg_cdn_url"):
                img.append(Img(url=text.split(" = ", maxsplit=1)[-1][1:-2]))
            elif len(img) < img_num and text.startswith("var cdn_url_1_1"):
                img.append(Img(url=text.split(" = ", maxsplit=1)[-1][1:-2]))
            elif len(img) < img_num and text.startswith("var cdn_url_235_1"):
                img.append(Img(url=text.split(" = ", maxsplit=1)[-1][1:-2]))
            else:
                pass
        if img_num > 0 and len(img) < 1:
            img.append(Img(url="https://res.wx.qq.com/a/wx_fed/assets/res/OTE0YTAw.png", width=180, height=180))
        return Result(title=title, keywords=None, description=description, img=img, limit_img_num=img_num)
