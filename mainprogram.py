#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# encoding=utf-8
"""
Created on Sun May 13 14:53:50 2018

@author: dororo
"""

import time

import pymysql

import summary

delaytime = 300


class QueryQueue(object):
    def __init__(self):
        self.namelist = []
        for result in query(sql="select * from query"):
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

    def push(self, name, timestamp, file=""):
        if name in self.namelist:
            return
        self.namelist.append(name)
        for r in query(sql="select * from query where file='{}'".format(file)):
            # print(r)
            query(sql="update `query` set date='{}' where file='{}'".format(
                timestamp, r[0]))
        else:
            query(sql="update `query` set date='{}',file='{}' where title='{}'".format(
                timestamp, file, name))

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
                sql="select date from `query` where title='{}'".format(self.namelist[i]))
            if time.mktime(time.strptime(result[0][0], '%Y-%m-%d_%H-%M-%S'))+delaytime < time.time():
                return_index = i
                break
        else:
            print("no title need to search.")
            return None
        n = self.namelist[return_index]
        self.namelist.pop(return_index)
        return n


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
    return QueryQueue()


if __name__ == "__main__":
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "root", "summary")

    qq = QueryQueue()
    qq.push("人工智慧", time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))
    while True:
        if not qq.empty():
            print(qq)
            sname = qq.pop()
            if sname == None:
                qq = requery()
            else:
                filename = summary.getsummary(
                    search_name=sname, istrainning=False)
                qq.push(sname, time.strftime("%Y-%m-%d_%H-%M-%S",
                                             time.localtime()), file=filename)
        else:
            print("queue empty.")
            break

    # 关闭数据库连接
    db.close()
