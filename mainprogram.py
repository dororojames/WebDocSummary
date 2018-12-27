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


class QueryQueue(object):
    def __init__(self):
        self.namelist = []
        for result in query(sql="select title from query where date < {}".format(time.time()-10)):
            print(result)
            self.namelist.append(result[0])

    def push(self, name, timestamp, file=""):
        if name in self.namelist:
            return
        self.namelist.append(name)
        for r in query(sql="select * from query where file={}".format(file)):
            print(r)
            query(sql="update from query set date={} where file={}".format(
                timestamp, r[0]))
        else:
            query(sql="insert into query values({},{},{})".format(
                name, timestamp, file))

    def empty(self):
        if self.namelist:
            return False
        return True

    def pop(self):
        if self.empty():
            raise "Queue is empty."
        return_index = 0
        for i in range(len(self.namelist)):
            result = query(
                sql="select date from query where title={}".format(self.namelist[i]))
            if int(result[0])+10 < time.time():
                return_index = i
                break
        n = self.namelist[return_index]
        self.namelist.pop(return_index)
        return n


def query(sql=""):
    if "select" in sql:
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            return results
        except:
            print("Error: unable to fetch data")
    elif "update" in sql or "insert" in sql:
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
        except:
            # 发生错误时回滚
            db.rollback()


if __name__ == "__main__":
    # 打开数据库连接
    db = pymysql.connect("localhost", "testuser", "test123", "TESTDB")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    qq = QueryQueue()
    qq.push("人工智慧", time.time())
    while True:
        if not qq.empty():
            sname = qq.pop()
            summary.getsummary(search_name=sname)
            qq.push(sname, time.time())
        else:
            time.sleep(10)
            qq = QueryQueue()

    # 关闭数据库连接
    db.close()
