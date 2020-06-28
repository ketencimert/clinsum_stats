# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 13:10:49 2020

@author: Mert Ketenci
"""
import re

def remove_html_tags(text):

    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)