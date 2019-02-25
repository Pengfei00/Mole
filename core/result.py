#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from enum import Enum
from typing import Optional, Union, Dict, List

import requests
from PIL import ImageFile


class MediaType(str, Enum):
    JPEG = "image/jpeg"
    GIF = "image/gif"
    PNG = "image/png"
    SVG = "image/svg+xml"
    TIFF = "image/tiff"
    ICO = "image/x-icon"


class Img:
    def __init__(self, url: str, width: Optional[Union[int, str]] = None, height: Optional[Union[int, str]] = None,
                 media_type: str = None):

        self.url = url

        self.media_type = media_type
        if self.media_type == MediaType.SVG:
            self.width = "*"
            self.height = "*"
        else:
            self.width = width
            self.height = height

    def infer_size_and_media_type(self):
        ImPar = ImageFile.Parser()
        with requests.get(self.url, stream=True) as r:
            media_type = r.headers['Content-Type']
            self.media_type = media_type
            if not (self.width is None or self.height is None):
                return
            if media_type == MediaType.ICO:
                count = 10240
            elif media_type == MediaType.SVG:
                self.width, self.height = "*", "*"
                return
            else:
                count = 128
            for chunk in r.iter_content(chunk_size=count):
                try:
                    ImPar.feed(chunk)
                except ValueError as e:
                    pass
                if ImPar.image:
                    break
        self.width, self.height = ImPar.image.size

    def json(self) -> str:
        return json.dumps(self.dict(), ensure_ascii=False)

    def dict(self) -> Optional[Dict[str, str]]:
        response = None
        if self.width is None or self.height is None or self.media_type is None:
            self.infer_size_and_media_type()

        return {
            "url": self.url if response is None else response.url,
            "wedith": self.width,
            "height": self.height,
            "media_type": self.media_type,
        }


class Result:
    def __init__(self, limit_img_num: int, title: str, keywords: Optional[str], description: Optional[str],
                 img: List[Optional[Img]]):
        self.title = title
        self.keywords = keywords
        self.description = description
        self.__img = img or []
        self.__limit_img_num = limit_img_num

    def json(self) -> str:
        return json.dumps(self.dict(), ensure_ascii=False)

    @property
    def img(self) -> List[Dict[str, str]]:
        if self.__limit_img_num == 0:
            return []
        result = []
        n = 0
        for i in self.__img:
            r = i.dict()
            if r is None:
                continue
            result.append(r)
            n = n + 1
            if n >= self.__limit_img_num:
                return result
        return result

    def dict(self):
        return {
            "title": self.title,
            "keywords": self.keywords,
            "description": self.description,
            "img": self.img
        }

    def __str__(self):
        return self.json()


class Empty(Result):

    def __init__(self, *args, **kwargs):
        super(Empty, self).__init__(limit_img_num=0, title="", description="", img=[])

    def json(self):
        return ""