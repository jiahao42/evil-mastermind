#! /usr/bin/env python3
# -*- coding: utf-8
#
# @File:      calc_stats
# @Brief:     generate frequency and stability
# @Created:   Sep/19/2019
# @Author:    Jiahao Cai
#


from bs4 import BeautifulSoup
import re
import datetime
import os
import sys
from datetime import datetime
from collections import OrderedDict
from utils import *
from hashlib import md5

class CalcStats:
  def __init__(self, name, selector, target, cond, regex = ""):
    self.name = name
    self.cache_path = f'cache/{name}_{md5(selector.encode("utf-8")).hexdigest()}.txt'
    self.path = f'crawled_dataset/{name}'
    self.selector = selector
    self.target = target
    self.cond = int(cond)
    self.regex = regex
    self.found_counter = 0
    self.found_db = []
    self.satisfied_counter = 0
    self.satisfied_db = []
    self.total_counter = 0
    self.total_db = []
    self.freq = 0
    self.stab = 0
    self.word_db = []
  def load_cache(self):
    if os.path.exists(self.cache_path):
      lines = read_file_as_list(self.cache_path)
      return lines
    else:
      return None
  def _calc_stats_with_cache(self, lines):
    for line in lines:
      ts, text = line.split(',', 1)
      self.word_db += text.split(' ')
      res = self.satisfied(text)
      self.found_counter += 1
      self.found_db.append(ts)
      if res:
        self.satisfied_counter += 1
        self.satisfied_db.append(ts)

  def _calc_stats(self):
    filenames = sorted(os.listdir(self.path))
    filenames = list(filter(lambda x: x[-4:] == 'html', filenames))
    self.total_counter = len(filenames)
    lines = self.load_cache()
    if lines != None:
      return self._calc_stats_with_cache(lines)
    for filename in filenames:
      if 'html' not in filename: continue
      print(f'working on {filename}...')
      ts = re.search(r'.*(2019.*)\.html', filename).group(1)
      ts = cvt_timestamp(ts)
      with open(f'{self.path}/{filename}', 'r') as f:
        try:
          page = BeautifulSoup(f, "html5lib")
          ele_arr = page.select(self.selector)
          if len(ele_arr) == 0:
            print(f'not found! selector: {self.selector}')
            continue
          else:
            self.found_counter += 1
            self.found_db.append(ts)
            ele = ele_arr[0]
          text = rm_linebreak(ele.text).lower()
          self.word_db += text.split(' ')
          # print(text)
          self.total_db.append((ts, text))
          if text == None: continue
          res = self.satisfied(text)
          if res:
            self.satisfied_counter += 1
            self.satisfied_db.append(ts)
        except Exception as e:
          print(e) 
          pass
    with open(self.cache_path, 'w') as f:
      for ts, text in self.total_db:
        f.write(ts + ',' + text + '\n')
  def calc_stats(self):
    self._calc_stats()
    freq = round(self.satisfied_counter / self.total_counter, 4)
    stab = round(self.found_counter / self.total_counter, 4)
    self.freq = freq
    self.stab = stab
    return freq, stab

  def satisfied(self, text):
    text = rm_linebreak(text).lower()
    def starts_with(text):
      if text.startswith(self.target):
        return True
      return False
    def ends_with(text):
      if text.endswith(self.target):
        return True
      return False
    def contains(text):
      if self.target in text:
        return True
      return False
    def matches_to(text):
      res = re.search(self.regex, text)
      if res != None and res.group(1) == self.target:
        return True
      return False
    table = {
      0: starts_with,
      1: ends_with,
      2: contains,
      3: matches_to,
    }
    return table[self.cond](text)
  
  def get_word_db(self):
    if len(self.word_db) == 0:
      self.calc_stats()
    return list(set(self.word_db))


