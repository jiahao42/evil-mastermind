#! /usr/bin/env python3
# -*- coding: utf-8
#
# @File:      server
# @Brief:     Enter brief here
# @Created:   Sep/18/2019
# @Author:    Jiahao Cai
#


from flask import Flask, send_from_directory, render_template, request, jsonify, make_response, render_template_string
import json
import urllib
from calc_stats import CalcStats
import os
import hashlib
from dom_tree_gen import gen_dom_tree
from utils import *
app = Flask(__name__)

nav = """
<nav class="navbar navbar-expand-lg navbar-light bg-light" style="margin-bottom: 10px;">
    <a class="navbar-brand" href="/">EvilMind Actor Profiler</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNavDropdown">
      <ul class="navbar-nav">
        <li class="nav-item active">
          <a class="nav-link" href="/">Homepage</a>
        </li>
        <li class="nav-item active">
          <a class="nav-link" href="#" data-target="#selectedModal" data-toggle="modal">Selected DOM elements</a>
        </li>
      </ul>
    </div>
</nav>
"""

selected_dom_modal = """
<script>
$('#selectedModal').on('show.bs.modal', function (event) {
  $.get("/attack_create", function (data) {
    console.log(data);
    $('#selected_table').html(data);
  });
});
$("#bt_save_attack").click(function() {
  $.get("/attack_save", function (data) {
    $('#selectedModal').modal('hide');
  });
});
</script>
"""


@app.route('/')
def index():
  table = """
    <table class="table table-bordered table-striped table-condensed" style="width: 100%">
      <thead>
        <tr>
          <th scope="col">Category</th>
          <th scope="col">1</th>
          <th scope="col">2</th>
          <th scope="col">3</th>
        </tr>
      </thead>
      <tbody>
  """
  with open('websites.json', 'r') as f:
    data = json.load(f)
  th = """<th scope="row">%s<i class="fa fa-plus icon" id="add_%s" name="%s" data-target="#addModal" data-toggle="modal" category="%s"></i></th>"""
  td = """<td><a href="/website_details?website=%s">%s</a><i class="fa fa-edit icon" id="edit_%s" name="%s" data-target="#editModal" data-toggle="modal" category="%s"></i></td>"""
  for category, websites in data.items():
    table += "<tr>"
    table += th % (category, category, category, category)
    for website in websites:
      table += td % (website['website'], website['website'], website['website'], website['website'], category)
    table += "</tr>"
  table += """</tbody></table>"""
  return render_template('index.html', table=table, nav=nav, selected_dom_modal=selected_dom_modal)

@app.route('/website_add')
def website_add():
  with open('websites.json', 'r') as f:
    data = json.load(f)
    requested_category = request.args.get('category')
    current_website = request.args.get('website')
    url = request.args.get('url')
    for category, websites in data.items():
      if category == requested_category:
        last_index = len(websites)
        data[category].append(dict())
        data[category][last_index]['website'] = current_website
        data[category][last_index]['url'] = url
        break
  with open('websites.json', 'w') as f:
    f.write(json.dumps(data, indent=2))
  return jsonify(success=True)

def get_freq_stab(selector, keyword, cond, regex = ""):
  """calculate the frequency and stability"""
  current_website = request.cookies.get('current_website')
  path = current_website.replace(' ', '_')
  stats = CalcStats(path, selector, keyword, cond, regex)
  print(f'calculating... {selector}, {cond}, {keyword}')
  return stats.calc_stats()

@app.route('/dom_add')
def dom_add():
  with open('websites.json', 'r') as f:
    data = json.load(f)
    current_website = request.cookies.get('current_website')
    selector = urllib.parse.unquote(request.args.get('selector'))
    condition = int(urllib.parse.unquote(request.args.get('condition')))
    keyword = urllib.parse.unquote(request.args.get('keyword'))
    for category, websites in data.items():
      for i, website in enumerate(websites):
        if website['website'] == current_website:
          last_index = len(website['candidates'])
          data[category][i]['candidates'].append(dict())
          data[category][i]['candidates'][last_index]['selector'] = selector
          data[category][i]['candidates'][last_index]['condition'] = condition
          data[category][i]['candidates'][last_index]['keyword'] = keyword
          freq, stab = get_freq_stab(selector, keyword, condition)
          data[category][i]['candidates'][last_index]['frequency'] = freq
          data[category][i]['candidates'][last_index]['stability'] = stab
          break
  with open('websites.json', 'w') as f:
    f.write(json.dumps(data, indent=2))
  return jsonify(success=True)

@app.route('/website_edit')
def website_edit():
  with open('websites.json', 'r') as f:
    data = json.load(f)
    prev_website = request.args.get('prev_website')
    current_website = request.args.get('website')
    url = request.args.get('url')
    for category, websites in data.items():
      for i, website in enumerate(websites):
        if website['website'] == prev_website:
          data[category][i]['website'] = current_website
          data[category][i]['url'] = url
  with open('websites.json', 'w') as f:
    f.write(json.dumps(data, indent=2))
  return jsonify(success=True)

@app.route('/dom_edit')
def dom_edit():
  with open('websites.json', 'r') as f:
    data = json.load(f)
    current_website = request.cookies.get('current_website')
    dom_id = int(urllib.parse.unquote(request.args.get('dom_id')))
    selector = urllib.parse.unquote(request.args.get('selector'))
    condition = urllib.parse.unquote(request.args.get('condition'))
    keyword = urllib.parse.unquote(request.args.get('keyword'))
    for category, websites in data.items():
      for i, website in enumerate(websites):
        if website['website'] == current_website:
          data[category][i]['candidates'][dom_id]['selector'] = selector
          data[category][i]['candidates'][dom_id]['condition'] = condition
          data[category][i]['candidates'][dom_id]['keyword'] = keyword
          freq, stab = get_freq_stab(selector, keyword, condition)
          data[category][i]['candidates'][dom_id]['frequency'] = freq
          data[category][i]['candidates'][dom_id]['stability'] = stab
          break
  with open('websites.json', 'w') as f:
    f.write(json.dumps(data, indent=2))
  return jsonify(success=True)

@app.route('/website_lookup')
def website_lookup():
  with open('websites.json', 'r') as f:
    data = json.load(f)
  requested_website = urllib.parse.unquote(request.args.get('website'))
  for category, websites in data.items():
    for website in websites:
      if website['website'] == requested_website:
        return jsonify(json.dumps(website))
  return jsonify('null')

@app.route('/dom_lookup')
def dom_lookup():
  # current_website = request.cookies.get('current_website')
  current_website = urllib.parse.unquote(request.args.get('website'))
  dom_id = int(urllib.parse.unquote(request.args.get('dom_id')))
  with open('websites.json', 'r') as f:
    data = json.load(f)
  for category, websites in data.items():
    for website in websites:
      if website['website'] == current_website:
        dom = website['candidates'][dom_id]
        return jsonify(json.dumps(dom))
  return jsonify('null')
  
def translate_condition(cond):
  cond_table = {
    0: 'starts with',
    1: 'ends with',
    2: 'contains',
    3: 'matches to',
  }
  return cond_table[int(cond)]

@app.route('/website_details')
def website_details():
  requested_website = urllib.parse.unquote(request.args.get('website'))
  cookie_attack = request.cookies.get('attack')
  dom_id_set = []
  if cookie_attack:
    attack = json.loads(cookie_attack)
    for item in attack['attack']:
      current_website = item.split(':')[0]
      dom_id = int(item.split(':')[1])
      if current_website == requested_website:
        dom_id_set.append(dom_id)
  with open('websites.json', 'r') as f:
    data = json.load(f)
  td_dom = """<th scope="row" rowspan="1" align="center">%s<i class="fa fa-edit icon"  name="%s" data-target="#editModal" data-toggle="modal" id=""></i></th>"""
  td_cond = """<td><input type="checkbox" class="dom_checkbox" value="#" website="%s" dom_id="%s" %s> The content %s "%s"<i class="fa fa-edit icon"  name="%s" data-target="#editModal" data-toggle="modal" id=""></i></td>"""
  progress_bar = """<td><center>%s%%</center><div class="progress"><div class="progress-bar bg-success" role="progressbar" aria-valuenow="%s" aria-valuemin="0" aria-valuemax="100" style="width:%s%%"></div></div></td>"""
  tbody = """<tbody>"""
  for category, websites in data.items():
    for website in websites:
      if website['website'] == requested_website:
        for i, candidate in enumerate(website['candidates']):
          tbody += "<tr>"
          tbody += f'<td style="width: 20px;">{i}</td>'
          tbody += td_dom % (candidate['selector'], str(i))
          checked = ''
          if i in dom_id_set: checked = 'checked'
          tbody += td_cond % (requested_website, str(i), checked, translate_condition(candidate['condition']), candidate['keyword'], str(i))
          freq = str(round(candidate['frequency'] * 100, 2))
          tbody += progress_bar % (freq, freq, freq)
          stab = str(round(candidate['stability'] * 100, 2))
          tbody += progress_bar % (stab, stab, stab)
          tbody += "</tr>"
  tbody += """</tbody>"""
  name = requested_website.replace(' ', '_')
  try:
    gen_dom_tree(name)
  except FileNotFoundError as e:
    print(e)
  dom_tree = f'static/imgs/dom_{name}.png'
  resp = make_response(render_template('details.html', tbody=tbody, subtitle=requested_website, dom_tree=dom_tree, nav=nav, selected_dom_modal=selected_dom_modal))
  resp.set_cookie('current_website', requested_website)
  return resp

attack_word_db = []
@app.route('/attack_create')
def attack_create():
  global attack_word_db
  attack_word_db = []
  cookie_attack = request.cookies.get('attack')
  attack = json.loads(cookie_attack)
  table = """<thead><tr>
  <th scope='col'>Website</th>
  <th scope='col'>DOM elements</th>
  <th scope='col'>Condition</th>
  <th scope='col'>Frequency</th>
  <th scope='col'>Stability</th>
  </tr></thead><tbody>"""
  th = """<th scope='row' rowspan='1' align='center'>%s</th>"""
  td = """<td style="white-space: break;">%s</td>"""
  with open('websites.json', 'r') as f:
    data = json.load(f)
  satisfied_record = {}
  for item in attack['attack']:
    table += '<tr>'
    current_website = item.split(':')[0]
    dom_id = int(item.split(':')[1])
    min_stab = 1.0
    for category, websites in data.items():
      for website in websites:
        if website['website'] == current_website:
          dom = website['candidates'][dom_id]
          table += th % current_website
          selector = dom['selector']
          table += td % selector
          cond = dom['condition']
          keyword = dom['keyword']
          table += td % (translate_condition(cond) + ' ' + '"' + keyword + '"')
          freq = f"{str(round(dom['frequency'] * 100, 2))}%"
          table += td % freq
          stab = f"{str(round(dom['stability'] * 100, 2))}%"
          table += td % stab
          break
    path = current_website.replace(' ', '_')
    stats = CalcStats(path, selector, keyword, cond, "")
    stats.calc_stats()
    attack_word_db += stats.get_word_db()
    # solve stability
    if stats.stab < min_stab:
      min_stab = stats.stab
    # solve freq
    for ts in stats.satisfied_db:
      satisfied_record[ts] = satisfied_record.get(ts, 0) + 1
    table += '</tr>'
  satisfied_counter = 0
  for k, v in satisfied_record.items():
    # print(k, v)
    if v == len(attack['attack']):
      satisfied_counter += 1
  table += '<tr>'
  table += th % "Combined"
  table += td % "N/A"
  table += td % "N/A"
  combined_freq = f"{str(round(satisfied_counter / stats.total_counter * 100, 2))}%"
  table += td % combined_freq
  min_stab = f"{str(round(min_stab * 100, 2))}%"
  table += td % min_stab
  table += '</tr>'
  table += '</tbody>'
  return render_template_string(table)

def query_dom_element(website_name, dom_id):
  with open('websites.json', 'r') as f:
    data = json.load(f)
  for category, websites in data.items():
    for website in websites:
      if website['website'] == website_name:
        dom = website['candidates'][dom_id]
        return dom
  return None

def query_website(website_name):
  with open('websites.json', 'r') as f:
    data = json.load(f)
  for category, websites in data.items():
    for website in websites:
      if website['website'] == website_name:
        return website
  return None

@app.route('/attack_save')
def attack_save():
  global attack_word_db
  cookie_attack = request.cookies.get('attack')
  attack = json.loads(cookie_attack)
  attack_obj = {'attack': []}
  word_db_obj = {}
  for item in attack['attack']:
    website_name = item.split(':')[0]
    dom_id = int(item.split(':')[1])
    website = query_website(website_name)
    dom = website['candidates'][dom_id]
    dom['website'] = website_name
    dom['url'] = website['url']
    dom['selector'] = str(css_selector2xpath(dom['selector']))
    attack_obj['attack'].append(dom)
  attack_hash = hashlib.md5(cookie_attack.encode('utf-8')).hexdigest()
  with open(f'attacks/attack_{attack_hash}.json', 'w') as f:
    json.dump(attack_obj, f, indent=2)
  word_db_obj['dictionary'] = attack_word_db
  with open(f'attacks/dict_{attack_hash}.json', 'w') as f:
    json.dump(word_db_obj, f, indent=2)
  return jsonify(success=True)
