#!/usr/bin/env python
#-*- coding: utf-8 -*- 

import MySQLdb
import time
import string
from DBUtils.PooledDB import PooledDB
import dbconfig
import datetime


ERROR = {0:"OK", 1:"Parameter Error", 2:"Database Error", 3:u"您已赞", 4:u"你无权开通直播"}
Default_Snapshot = "http://7xvsyw.com2.z0.glb.qiniucdn.com/n.jpg"

DBConfig = dbconfig.Parser()

class DbManager():
    def __init__(self):
        kwargs = {}
        kwargs['host'] =  DBConfig.getConfig('database', 'dbhost')
        kwargs['port'] =  int(DBConfig.getConfig('database', 'dbport'))
        kwargs['user'] =  DBConfig.getConfig('database', 'dbuser')
        kwargs['passwd'] =  DBConfig.getConfig('database', 'dbpassword')
        kwargs['db'] =  DBConfig.getConfig('database', 'dbname')
        kwargs['charset'] =  DBConfig.getConfig('database', 'dbcharset')
        self._pool = PooledDB(MySQLdb, mincached=1, maxcached=15, maxshared=10, maxusage=10000, **kwargs)

    def getConn(self):
        return self._pool.connection()

_dbManager = DbManager()

def getConn():
    return _dbManager.getConn()

def UpdateEPG(gid, program_name, time, store_path):
    con = getConn()
    cur =  con.cursor()

    sql = """delete from vod where gid = "{0}" and time = "{1}" """.format(gid, time) 
    cur.execute(sql)
    con.commit()

    sql = "insert into vod (gid, program_name, time, store_path, class,subclass)values('{0}','{1}','{2}','{3}',1,1)".format(
                           gid, program_name, time, store_path) 
    cur.execute(sql)
    con.commit()

    cur.close()
    con.close()

def deleteEPG(gid, time):
    con = getConn()
    cur =  con.cursor()

    sql = """delete from vod where gid = "{0}" and time = "{1}" """.format(gid, time) 
    cur.execute(sql)
    con.commit()

    cur.close()
    con.close()

def updatePlayNum(which):
    con = getConn()
    cur =  con.cursor()

    sql = """update vod set num = num +1 where url like "%%%s" """%(which) 
    cur.execute(sql)
    con.commit()

    cur.close()
    con.close()

def getAllLiveEpg():
    con = getConn()
    cur = con.cursor()
    sql = 'select gid, channel_id,origin from live_epg;'
    cur.execute(sql)
    con.commit()
    data = cur.fetchall()
    cur.close()
    con.close()
    result = [{'gid':epg[0],'channel_id':epg[1],'origin':epg[2]} for epg in data]
    return result

def getLiveEpg(gid):
    con = getConn()
    cur = con.cursor()
    sql = 'select  gid, channel_id,origin from live_epg where gid="{gid}"'.format(gid=gid)
    cur.execute(sql)
    con.commit()
    data = cur.fetchone()
    cur.close()
    con.close()
    if not data:
        return None
    return {'gid':data[0],'channel_id':data[1],'origin':data[2]}

if __name__ ==  '__main__':
    pass
    #print getAllLiveEpg()
    #print getLiveEpg('cctv2')
    #print UpdateEPG("cctv9", "电视剧", "2020-12-20 11:00:00", "/data/cctv9")
    #deleteEPG("cctv9", "2020-12-20 11:00")
