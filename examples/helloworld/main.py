#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
execute(["scrapy", "crawl", "ycombinator"])