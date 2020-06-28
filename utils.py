# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 13:10:49 2020

@author: Mert Ketenci
"""

def remove_html_tags(text):

    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)