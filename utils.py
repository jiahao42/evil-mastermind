#! /usr/bin/env python3
# -*- coding: utf-8
#
# @File:      utils
# @Brief:     utility functions for MindGen
# @Created:   Sep/16/2019
# @Author:    Jiahao Cai
#

import re
import random
import pickle

def read_file_raw(filename):
  with open(filename, 'r', encoding='utf8', errors='ignore') as f:
    ret = f.read()
  return ret

def read_file_as_one_line(filename):
  with open(filename, 'r', encoding='utf8', errors='ignore') as f:
    ret = f.read().split('\n')
  return ' '.join(ret)

def merge_space(text):
  return re.sub(r'\s+', ' ', text).strip()

input_token_counter = 1
output_token_counter = 1

def substr_tokenize(tokens, token_set, max_len):
  res = []
  my_len = 0
  ordered_token_set = sorted(list(token_set))
  for token in tokens:
    if my_len > max_len: break
    can_be_split = False
    if len(token) > 6:
      for tk in ordered_token_set:
        if len(tk) <= 1: continue
        if token[:len(tk)] == tk:
          rest = token[len(tk):]
          if len(rest) > 1 and rest in ordered_token_set:
            res.append(tk)
            res.append(rest)
            can_be_split = True
            my_len += 2
            break
    if not can_be_split:
      res.append(token)
      my_len += 1
  return res


ESCAPE_MAP = {
  r'\\': r'\\\\',
  r'"': '\\"',
  r'\n': '\\\\n',
  r'\t': '\\\\t',
  r'\$': '\\$',
  r'\'': '\\\'',
}

def my_escape(text, escape_map = ESCAPE_MAP):
  for k, v in escape_map.items():
    # print(text, k, v)
    text = re.sub(k, v, text)
    # print(text)
  return text
