# -*-   coding: utf-8 -*-
'''
抓取soutv网站的电视节目单
抓取荔枝网的广东本地电视台节目单
'''
import os
import sys
import re
import random
reload(sys)
sys.setdefaultencoding("utf-8")
import datetime
import time
from argparse import ArgumentParser
import mysql
try:
    import xml.etree.CElementTree as ET
except:
    import xml.etree.ElementTree as ET

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from connect import get, post, json_load
from log import LOG

INPUT_DATE = None

def get_tomorrow_date(fmt='%Y-%m-%d'):
    date = datetime.datetime.now() + datetime.timedelta(days=1)
    if INPUT_DATE:
        date = datetime.datetime.strptime(INPUT_DATE, '%Y-%m-%d')
    return date.strftime(fmt)

def timestamp_to_time(timestamp):
    '''
    把时间戳转换成yyyy-mm-dd HH24:MM:SS
    '''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))

def sleep():
    num = random.randint(2, 5)
    time.sleep(num)

def get_tvsou_channels():
    data = mysql.getAllLiveEpg()
    channels = [{'gid': epg['gid'], 'cid': epg['channel_id']} for epg in data if epg['origin'] == 'tvsou']
    return channels


def get_gdtv_channels():
    data = mysql.getAllLiveEpg()
    channels = [{'gid': epg['gid'], 'cid': epg['channel_id']} for epg in data if epg['origin'] == 'gdtv']
    return channels


def process_tvsou(cid, date, retry=3):
    import api
    api, ts = api.GET_API()
    api = api[0].encode("utf-8")
    ts = ts[0].encode("utf-8")
    url = 'https://www.tvsou.com' + api
    sub_data = {'date': date, 'channelid': cid, 't':ts}
    print url, sub_data
    data = None
    while retry > 0:
        data = post(url, sub_data, ctype='json')
        if not data:
            LOG.error('[%s]No data, try again.' % cid)
            retry -= 1
        else:
            break
    if not data:
        return None
    datas = list()
    print data
    data = json_load(data)
    for obj in data.get('list'):
        datas.append({'time': timestamp_to_time(
            obj.get('playtimes')), 'program_name': obj.get('title')})
    return datas


def process_gdtv(cid, date, retry=3):
    url = 'http://epg.gdtv.cn/f/%s/%s.xml' % (cid, date)
    data = None
    while retry > 0:
        data = get(url, ctype='xml')
        if not data:
            LOG.error('[%s]No data, try again.' % cid)
            retry -= 1
        else:
            break
    if not data:
        return None
    root = ET.fromstring(data.encode('utf8'))
    datas = list()
    for obj in root[1].findall('content'):
        datas.append({'time': timestamp_to_time(
            obj.attrib['time1']), 'program_name': obj.text})
    return datas


def run_tvsou(channels=None):
    '''
    获取搜视网的非广东电视频道的节目
    '''
    if not channels:
        channels = get_tvsou_channels()
    date = get_tomorrow_date('%Y%m%d')
    result = dict()
    for channel in channels:
        data = process_tvsou(channel['cid'], date)
        if data:
            result[channel['gid']] = data
        sleep()
    return result


def run_gdtv(channels=None):
    '''
    获取广东本地的电视节目
    '''
    if not channels:
        channels = get_gdtv_channels()
    date = get_tomorrow_date()
    result = dict()
    url = 'http://epg.gdtv.cn/f/%s/%s.xml'
    for channel in channels:
        data = process_gdtv(channel['cid'], date)
        result[channel['gid']] = data
        sleep()
    return result


def save_program(gid, data):
    for program in data:
        mysql.UpdateEPG(gid, program['program_name'], program['time'], "/data/" + gid)


def main():
    data1 = run_gdtv()
    data2 = run_tvsou()
    result = dict(data1.items() + data2.items())
    for key, val in result.items():
        if not val:
            LOG.error('[%s]channel clawl failed.' % key)
            continue
        save_program(key, val)
    sys.exit(0)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-date', type=str, help='crawl date, eg. 2018-01-01')
    args = parser.parse_args()
    regex = r'^\d{4}-\d{2}-\d{2}'
    if args.date:
        if re.match(regex, args.date):
            INPUT_DATE = args.date
        else:
            LOG.error('Date format is incorrect.')
            sys.exit(1)
    main()
