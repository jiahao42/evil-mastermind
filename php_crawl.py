#! /usr/bin/env python3
# -*- coding: utf-8
#
# @File:      php_crawl
# @Brief:     Enter brief here
# @Created:   Sep/20/2019
# @Author:    Jiahao Cai
#


dom_counter = 0
def gen_php_crawl_funcs(attacks):
  php_input = f"""
ini_set('user_agent','Mozilla/4.0 (compatible; MSIE 6.0)');
function fetch_element($url, $element) {{
  $page = new \DomDocument();
  libxml_use_internal_errors(true);
  $page->loadHTMLFile($url);
  libxml_clear_errors();
  $finder = new \DomXPath($page);
  $target = $finder->query($element)[0];
  if ($target)
    return strtolower(trim(preg_replace("/\s+/", " ", (preg_replace( "/\\r|\\n|\s/", " ", $target->nodeValue)))));
  return null;
}}
"""
  php_input += gen_nest_attack_func(attacks)
  return php_input

def gen_nest_attack_func(attacks):
  function = """function nested_attack() {"""
  stmt = """$res = attack%s(); if ($res != null) return implode(" ", $res);"""
  for attack in attacks:
    function += stmt % attack.id
  function += "}"
  for attack in attacks:
    function += gen_crawl_attack_func(attack)
  return function

def gen_crawl_attack_func(attack):
  function = f"""
  function attack{attack.id}() {{
  $input = [];"""
  stmt = """
  $temp = fetch_element("%s", "%s");
  if ($temp == null) return null;
  else $input = array_merge($input, array_slice(explode(" ", $temp), %s, %s));
  """
  for dom in attack.doms:
    keyword_num = len(dom.keyword.split(' '))
    if dom.cond == 0: start = 0
    elif dom.cond == 2:
      start = dom.index
    else: start = -keyword_num
    dom_stmt = stmt % (dom.url, dom.selector, start, keyword_num)
    function += dom_stmt
  function += """return $input;}"""
  return function



