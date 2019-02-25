#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional, Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from core.result import Empty, Result, Img


class ExtractMetaClass(abc.ABCMeta):
    function_map = {}

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        cls.function_map = ExtractMetaClass.function_map
        if cls.Host:
            ExtractMetaClass.function_map[cls.Host] = cls()
        return cls


class Extract(metaclass=ExtractMetaClass):
    UA = "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Mobile Safari/537.36"
    Host = ""

    def __init__(self):
        self.__session = requests.session()
        self.__session.headers['User-Agent'] = self.UA

    def new(self, url, img_num):
        try:
            response = self.session.get(url=url)
            response.encoding = response.apparent_encoding if response.encoding == "ISO-8859-1" else response.encoding
        except requests.exceptions.ConnectionError:
            return Empty
        return self.extract(response=response, img_num=img_num)

    @property
    def session(self):
        return self.__session

    def extract(self, response: requests.Response, img_num: int, soup: Any = None) -> Optional[Result]:
        soup = soup and soup or self.get_soup(response=response, img_num=img_num)
        if soup is None:
            return Empty

        function_kw = {
            "response": response,
            "img_num": img_num,
            "soup": soup
        }

        title = self.get_title(**function_kw)
        keywords = self.get_keywords(**function_kw)
        description = self.get_description(**function_kw)
        img = [i for i in self.get_img(**function_kw)]

        return Result(title=title, keywords=keywords, description=description, img=img, limit_img_num=img_num)

    def get_soup(self, response: requests.Response, img_num, **kwargs):
        return BeautifulSoup(response.text, features="html.parser")

    def get_img(self, soup, response, img_num, **kwargs):
        has_img = False
        for i in [*soup.find_all("meta"), *soup.find_all("link")]:
            res = i.get("content", i.get("href", None))
            if res and res.split(".")[-1].split("?", 1)[0].lower() in {"svg", "png", "ico", "jpg", "jpeg"}:
                has_img = True
                yield Img(url=self.fix_url(response=response, url=res))

        if has_img is False:
            yield Img(url=self.fix_url(response=response, url="/favicon.ico"))

    def get_description(self, soup, response, img_num, **kwargs):
        description_attr = soup.find("meta", attrs={"name": "description"})
        description = description_attr and description_attr['content'] or None
        return description

    def get_keywords(self, soup, response, img_num, **kwargs):
        keywords_attr = soup.find("meta", attrs={"name": "keywords"})
        keywords = keywords_attr and keywords_attr['content'] or None
        return keywords

    def get_title(self, soup, response, **kwargs):
        title = soup.title.text
        return title

    def fix_url(self, response, url: str) -> str:
        if url.startswith("http"):
            return url
        url_parse = urlparse(url=response.url)
        if url.startswith("//"):
            return f"{url_parse.scheme}:{url}"
        elif url.startswith("/"):
            return f"{url_parse.scheme}://{url_parse.netloc}{url}"
        elif url.startswith("./"):
            return f"{response.url}{url}"
