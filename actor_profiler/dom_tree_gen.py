#! /usr/bin/env python3
# -*- coding: utf-8
#
# @File:      dom_tree_gen
# @Brief:     generate a dom tree with frequency of word in elements
# @Created:   Aug/24/2019
# @Author:    Jiahao Cai
#

from bs4 import BeautifulSoup
import re
import os
import sys
import pydot
import hashlib
from utils import *
import subprocess

img_dir = 'static/imgs'
base_dir = 'crawled_dataset'

node_counter = 0
class Node:
  def __init__(self, bs_node, tag, tag_index, path):
    global node_counter
    self.bs_node = bs_node
    self.tag = tag
    self.tag_index = tag_index
    self.name = f'{tag}[{tag_index}]'
    self.kw = [] # [word, freq]
    self.path = path
    self.children = []
    # self.dot_node = pydot.Node(self.name)
    self.dot_node = pydot.Node(node_counter, label=self.name, shape='rectangle')
    self.appear_count = 0
    self.total_appear_num = 0
    node_counter += 1
  @property
  def path_str(self):
    return f'{" > ".join(self.path + [self.name])}'
  @property
  def css_selector(self):
    ret = ['body'] 
    for item in self.path + [self.name]:
      if item == 'body': continue # no need to make it body[0]
      content = item.split('[')[0]
      index = int(item.split('[')[1][:-1])
      extra = f':nth-of-type({index + 1})'
      ret.append(f'{content}{extra}')
    return ' > '.join(ret)
  @property
  def is_leaf(self):
    # print(self.name + f' is leaf? {self.children == []}')
    return self.children == []
  @property
  def stability(self):
    return self.appear_count / self.total_appear_num
  def set_label(self):
    if self.is_leaf: 
      # border_width = self.get_border_width()
      kw_pair = []
      for k, v in self.kw:
        kw_pair.append(f'({k}:{round(v * 100, 1)}%)')
      stability = round(self.stability * 100, 1)
      label = f'<<table cellpadding="1.5" cellborder="0" cellspacing="0">'
      label += f'<tr><td bgcolor="{self.get_color()}">{self.name}: {stability}%</td></tr>'
      if len(self.kw) > 0:
        label += f'<tr><td bgcolor="{self.get_color()}">{",".join(kw_pair)}</td></tr>'
      label += """</table>>"""
      print(label)
      self.dot_node.set_shape('none')
      self.dot_node.set_label(label)
  @property
  def top_freq(self):
    return self.kw[0][1]
  def get_border_width(self):
    if self.stability >= 0.99 and self.top_freq >= 0.1 and self.top_freq <= 0.2:
      return 5
    else:
      return 2
  def set_color(self):
      self.dot_node.set_style('filled')
      self.dot_node.set_fillcolor(self.get_color())
  def get_color(self):
    if self.is_leaf and len(self.kw) > 0:
      color_list = [
        '#CCFFCC', 
        '#88FF88', 
        '#22FF22', 
        '#00DD00', 
        '#00BB00', 
      ]
      freq = 0.2
      color_picker = 0
      while freq < self.top_freq:
        color_picker += 1
        freq += 0.2
      return color_list[color_picker]

ignored_tags = [
  'script', 
  'noscript',
  'img',
  'input',
  'footer',
  'nav',
  'icon',
  'use',
  'svg',
  'defs',
  'mask',
  'g',
  'rect',
  'style',
  'symbol',
  'path',
  'sup',
  'form',
  'button',
]

cur_path = ['body']
def extract_all(node):
  global cur_path
  global total_crawled_num
  ele_dict = {}
  for ele in node.bs_node.find_all(recursive = False):
    tag_name = ele.name
    if tag_name in ignored_tags: continue
    ele_dict[tag_name] = ele_dict.get(tag_name, -1) + 1
    try: # temp hack to fix a potential bug in Beautifulsoup
      if ele.text != None:
        text = rm_linebreak(ele.text)
        if text == '': continue
    except AttributeError:
      pass
    tag_index = ele_dict[tag_name]
    ele_name = f'{tag_name}[{tag_index}]'
    n_node = Node(ele, tag_name, tag_index, cur_path.copy())
    n_node.total_appear_num = total_crawled_num
    cur_path.append(ele_name)
    node.children.append(n_node)
    extract_all(n_node)
    cur_path.pop()

def dump_tree_dfs(root):
  for node in root.children:
    if node.is_leaf:
      print(node.path_str)
    # print(node.selector)
    dump_tree_dfs(node)

def dump_tree_bfs(root):
  queue = [root]
  while len(queue) > 0:
    node = queue[0]
    queue.pop(0)
    for n in node.children:
      if n.is_leaf:
        print(n.path_str)
        # print(n.bs_node.text)
      queue.append(n)

edge_db = {}
def draw(root):
  queue = [root]
  while len(queue) > 0:
    node = queue[0]
    queue.pop(0)
    for n in node.children:
      edge = pydot.Edge(node.dot_node, n.dot_node)
      if edge not in edge_db:
        graph.add_edge(edge)
        edge_db[edge] = 1
      queue.append(n)

depth = 0
def add_hierarchy(root):
  global depth
  global subgraphs
  for node in root.children:
    depth += 1
    if depth not in subgraphs:
      sub = pydot.Subgraph(rank='same')
      subgraphs[depth] = sub
    subgraphs[depth].add_node(node.dot_node)
    add_hierarchy(node)
    depth -= 1

def set_labels(root):
  for node in root.children:
    if node in node_kw_db:
      node.kw = node_kw_db[node]
      print(node.kw)
      node.set_label()
    set_labels(node)
    
def set_colors(root):
  for node in root.children:
    node.set_color()
    set_colors(node)

def simplify_tree(root):
  print(root.children)
  if len(root.children) == 1 and not root.children[0].is_leaf:
    root.children = root.children[0].children
  if len(root.children) > 3:
    root.children = root.children[:3]
  for node in root.children:
    if len(node.children) == 1 and not node.children[0].is_leaf: # omit nodes with only 1 child
      node.children = node.children[0].children
    if len(node.children) > 3:
      node.children = node.children[:3]
    simplify_tree(node)

node_text_db = {}
node_kw_db = {}
not_interesting_words = ['up', 'these', 'gets', 'just', 'need', 'after', 'trump', 'with', 'u', 'have', 'has', 'how', 'what', 'why', 't', 's', 'but', 'of', 'a', 'mr', 'on', 'from', 'u', 'as' ,'to', 'in', 't', 'at', 'into', 'is', 'it', 'here', 'be', 'were', 'are', 'its', 'say', 'of', 'that', 'my', 'he', 'she', 'they', 'our', 're', 'we', 'some', 'more', 'the', 'will', 'i', 'for', 'none', 'no', 'does', 'do', 'and', 'can', 'this', 'was', 'your', 'my', 'want', 'know', 'could', 'over', 'not', 'off', 'case','five', 'by', 'out', 'about', 'inside', 'n', 'said', 'his', 'again', 'who', 'then', 'you', 'when', 'should', 'like', 'an', 'if', 'c', 'get', 'all', 'so', 'one', 'p', 'jr', 'would', 'ii', 'two', 'most', 'op', 'let', 'dx', 'ssw', 'sw', 'had', 'or', 'me', 'been', 'during', 'com', 'ol']
def extract_leaf_nodes(page, root):
  global node_text_db
  global node_kw_db
  for node in root.children:
    if node.is_leaf: # only check leaf
      ele_arr = page.select(node.css_selector)
      # assert len(ele_arr) != 0, f'the css selector [{node.css_selector}] should identify at least one element'
      if len(ele_arr) == 0: 
        # print(node.css_selector)
        continue
      else:
        node.appear_count += 1
      assert len(ele_arr) == 1, f'the css selector [{node.css_selector}] should identify the unique element'
      ele = ele_arr[0]
      text = rm_punctuation(rm_linebreak(ele.text).lower())
      if text != '':
        if node not in node_text_db:
          node_text_db[node] = {}
        word_set = set(text.split(' '))
        for word in word_set:
          if word in not_interesting_words: continue
          node_text_db[node][word] = node_text_db[node].get(word, 0) + 1
    extract_leaf_nodes(page, node)

global_kw_db = []
def get_dir_data(my_dir, root):
  global node_text_db
  global node_kw_db
  filenames = os.listdir(my_dir)
  filenames = sorted(list(filter(lambda x: x[-4:] == 'html', filenames)))
  total_count = len(filenames)
  for filename in filenames:
    print(f'working on {filename}...')
    with open(f'{my_dir}/{filename}', 'r') as f:
      page = BeautifulSoup(f, "html5lib")
      extract_leaf_nodes(page, root)
  for node, db in node_text_db.items():
    node_kw_db[node] = []
    counter = 0
    for word, freq in sorted(db.items(), key=lambda x: x[1], reverse=True):
      if counter >= 1: break # top 2 words
      if word in global_kw_db: continue
      global_kw_db.append(word)
      node_kw_db[node].append((word, round(freq / total_count, 3)))
      counter += 1

legend_large = """
      {   rank="max";
    rankdir="LR";
      Legend [shape=none, margin_bottom=10, fontsize=25, fontname="bold", label=<
      <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="30">
      <TR>
        <TD>Freq. = 0~20%</TD>
        <TD COLSPAN="2" BGCOLOR="#CCFFCC"></TD>
      </TR>
      <TR>
        <TD>Freq. = 20~40%</TD>
        <TD COLSPAN="2" BGCOLOR="#88FF88"></TD>
      </TR>
      <TR>
        <TD>Freq. = 40~60%</TD>
        <TD COLSPAN="2" BGCOLOR="#22FF22"></TD>
      </TR>
      <TR>
        <TD>Freq. = 60~80%</TD>
        <TD COLSPAN="2" BGCOLOR="#00DD00"></TD>
      </TR>
      <TR>
        <TD>Freq. = 80~100%</TD>
        <TD COLSPAN="2" BGCOLOR="#00BB00"></TD>
      </TR>
      <TR>
        <TD>Stability = % of color </TD>
        <TD BGCOLOR="#00BB00">    80%     </TD>
        <TD BGCOLOR="white">20%</TD>
      </TR>
      </TABLE>
    >];
    Legend_text [shape=none, margin=0, label=Legend, fontsize=40, fontname="times bold"];
  }
  """

# For simplified version
legend_small = """
  {   
    rank="max";
    rankdir="LR";
    Legend [shape=none, margin_bottom=10, fontsize=18, fontname="bold", label=<
      <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="10">
      <TR>
        <TD>Freq. = 0~20%</TD>
        <TD WIDTH="120%" BGCOLOR="#CCFFCC"></TD>
      </TR>
      <TR>
        <TD>Freq. = 20~40%</TD>
        <TD COLSPAN="4" BGCOLOR="#88FF88"></TD>
      </TR>
      <TR>
        <TD>Freq. = 40~60%</TD>
        <TD COLSPAN="4" BGCOLOR="#22FF22"></TD>
      </TR>
      <TR>
        <TD>Freq. = 60~80%</TD>
        <TD COLSPAN="4" BGCOLOR="#00DD00"></TD>
      </TR>
      <TR>
        <TD>Freq. = 80~100%</TD>
        <TD COLSPAN="4" BGCOLOR="#00BB00"></TD>
      </TR>
      </TABLE>
    >];
    Legend_text [shape=none, margin=0, label=Legend, fontsize=30, fontname="times bold"];
  }
  """
total_crawled_num = 0
subgraphs = None
graph = pydot.Dot(graph_type='digraph', rankdir="LR", ranksep = "0.005", dpi=200)
def gen_dom_tree(name, simplify = False):
  global depth
  global total_crawled_num
  global subgraphs
  global graph
  data_dir = f'{base_dir}/{name}'
  filenames = os.listdir(data_dir)
  filenames = sorted(list(filter(lambda x: x[-4:] == 'html', filenames)))

  dot_file = f'{img_dir}/dom_{name}.dot'
  png_file = f'{img_dir}/dom_{name}.png'
  if os.path.exists(png_file): return

  total_crawled_num = len(filenames)
  with open(f'{data_dir}/{filenames[0]}', 'r') as f:
    page = BeautifulSoup(f, "html5lib")
  body = page.find('body')
  root = Node(body, 'body', 0, ['body'])
  extract_all(root)
  get_dir_data(data_dir, root)
  legend = legend_large
  if simplify:
    simplify_tree(root)
    legend = legend_small
  set_labels(root)

  top_subgraph = pydot.Subgraph(rank='same')
  top_subgraph.add_node(root.dot_node)
  subgraphs = {depth: top_subgraph}
  add_hierarchy(root)
  for depth, sub in subgraphs.items():
    graph.add_subgraph(sub)

  draw(root)
  graph.write_dot(dot_file)
  with open(dot_file, 'r') as f:
    lines = f.read().split('\n')
    new_files = lines[:-2] + [legend] + lines[-2:]
  with open(dot_file, 'w') as f:
    f.write('\n'.join(new_files))

  subprocess.run(['dot', dot_file, '-v', '-Tpng', '-Gdpi=150', '-o', png_file])

if __name__ == '__main__':
  gen_dom_tree(sys.argv[1].split('/')[-1])
