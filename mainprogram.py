#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# encoding=utf-8
"""
Created on Sun May 13 14:53:50 2018

@author: dororo
"""

import os
import shutil
import time

import pymysql

import summary

delaytime = 84600
_PATH = os.path.dirname(os.path.abspath(__file__))+"/"
# 1997-08-23_00-00-00 = 872265600


class QueryQueue(object):
    def __init__(self):
        self.namelist = []
        for result in query(sql="select * from `query` where `issearch`=1 order by `file`, `date`"):
            # print(result)
            if time.mktime(time.strptime(result[1], '%Y-%m-%d_%H-%M-%S'))+delaytime < time.time():
                self.namelist.append(result[0])

    def __str__(self):
        string = "["
        for i, n in enumerate(self.namelist):
            if i:
                string += ", "
            string += n
        return string+"]"

    def insert(self, name, timestamp="1997-08-23_00-00-00", file="", issearch=0):
        try:
            query(sql="insert into `query` values ('{}', '{}', '{}', {})".format(
                name, timestamp, file, issearch))
        except:
            return

    def update(self, name, timestamp, file=""):
        for r in query(sql="select * from `query` where `file`='{}'".format(file)):
            # print(r)
            query(sql="update `query` set `date`='{}' where `file`='{}'".format(
                timestamp, r[0]))
        else:
            query(sql="update `query` set `date`='{}', `file`='{}' where `title`='{}'".format(
                timestamp, file, name))
        r = query(
            sql="select `issearch` from `query` where `title`='{}'".format(name))
        if r[0][0] == 1:
            self.namelist.append(name)

    def push(self, name, timestamp="1997-08-23_00-00-00", file="", issearch=0):
        if name not in self.namelist:
            self.insert(name=name, timestamp=timestamp,
                        file=file, issearch=issearch)
            self.namelist.append(name)

    def addword(self):
        for r in query(sql="select `title` from `query` where `issearch`=1 order by `date`")[:10]:
            if r[0] in self.namelist:
                self.namelist.remove(r[0])
            self.namelist.insert(0, r[0])

    def empty(self):
        if self.namelist:
            return False
        return True

    def pop(self):
        if self.empty():
            raise "Queue is empty."
        return_index = -1
        for i in range(len(self.namelist)):
            result = query(
                sql="select `date`, `issearch` from `query` where title='{}'".format(self.namelist[i]))
            if time.mktime(time.strptime(result[0][0], '%Y-%m-%d_%H-%M-%S'))+delaytime < time.time() or result[0][1] == 0:
                return_index = i
                break
        else:
            print("no title need to search.")
            return None
        name = self.namelist[return_index]
        self.namelist.pop(return_index)
        return name

    def __len__(self):
        return len(self.namelist)


def query(sql=""):
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    if "select" in sql:
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            return results
        except:
            print(sql)
            raise "fetch error"
    elif "update" in sql or "insert" in sql:
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
        except:
            # 发生错误时回滚
            db.rollback()
            print(sql)
            raise "commit error"


def requery():
    print("Wait 5min to requery. Now is ", time.strftime(
        "%Y-%m-%d_%H-%M-%S", time.localtime()))
    time.sleep(delaytime)


def dumpdir(path):
    try:
        shutil.rmtree(path)
    except:
        pass
    os.mkdir(path)


if __name__ == "__main__":
    # dumpdir(_PATH+"savetext/")
    # dumpdir(_PATH+"html/")
    # dumpdir(_PATH+"temp/")
    # dumpdir(_PATH+"reference/")
    # dumpdir(_PATH+"summary/")
    # dumpdir(_PATH+"word2vec/")

    # 打开数据库连接
    db = pymysql.connect("localhost", "dororo", "dororo914", "summary")

    qq = QueryQueue()
    qq.push("人工智慧", issearch=1)

    while True:
        if not qq.empty():
            print(qq)
            sname = qq.pop()
            if sname == None:
                for r in query(sql="select `title` from `query` where `issearch`=0 order by `date`")[:20]:
                    qq.push(r[0])
            else:
                filename, RelatedWord = summary.getsummary(
                    search_name=sname, istrainning=True)
                tstamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
                qq.update(sname, tstamp, file=filename)
                for r in RelatedWord:
                    qq.insert(r, tstamp)
            qq.addword()
        else:
            print("queue empty.")
            # requery()
            # qq = QueryQueue()
            break

    # 关闭数据库连接
    db.close()
