#! /usr/bin/env python3
# -*- coding: utf-8
#
# @File:      utils
# @Brief:     utility functions
# @Created:   Sep/19/2019
# @Author:    Jiahao Cai
#

import re
from cssselect import GenericTranslator
from lxml.etree import XPath

def css_selector2xpath(css_selector):
  return XPath(GenericTranslator().css_to_xpath(css_selector))
  
def cvt_timestamp(ts):
  # e.g. 2019-05-07_01-30-01 to 2019-05-07 01:30
  date, time = ts.split('_')
  time = time.replace('-', ':')
  return date + ' ' + time[:-3] # ignore second

def rm_linebreak(text):
  text = re.sub(r'\n', ' ', text)
  return reduce_space(text)

def read_file_as_list(filename):
  with open(filename, 'r', encoding='utf8', errors='ignore') as f:
    ret = f.read().split('\n')
    ret = list(filter(lambda x: x != '', ret))
  return ret

def reduce_space(text):
  return re.sub(r'\s+', ' ', text).strip()

from string import punctuation
def rm_punctuation(string):
  for s in punctuation:
    string = string.replace(s, ' ')
  return reduce_space(string)