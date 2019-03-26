#!/usr/bin/env python
#coding:utf-8
import requests
import re


url = "https://www.tvsou.com/epg"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
           "Referer":"www.tvmao.com",
           "Accept-Language":"zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,zh-TW;q=0.6",
           "Connection":"Keep-Alive"
           }


r = requests.get(url, headers=headers)
r.close()
ts_pattern = re.compile(r'\w{32}')
api_pattern = re.compile(r'/api/\w+')
ts = ts_pattern.findall(r.text)
api = api_pattern.findall(r.text)
print ts, api
