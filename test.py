#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 21:50:31 2017

@author: Marco
"""

from person import API_KEY
from person import API_SECRET
import misc

client = misc.ApiClient(API_KEY, API_SECRET)

kline = client.get('/market/detail/merged',symbol='ltcbtc')
print(kline)
