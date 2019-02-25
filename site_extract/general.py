#!/usr/bin/env python
# -*- coding: utf-8 -*-


from typing import Optional

import requests

from core.abstract import Extract
from core.result import Result


class General(Extract):
    Host = "*"

    def extract(self, response: requests.Response, img_num, soup=None) -> Optional[Result]:
        return super(General, self).extract(response=response, img_num=img_num)
