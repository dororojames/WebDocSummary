#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 00:18:06 2018

@author: dororo
"""

from bs4 import BeautifulSoup


def findsubdiv(soup, depth=0):
    global savelist
    if str(soup.name) in ["h1", "h2", "h3", "h4", "h5", "h6", "th", "td"]:
        savelist.append("\n"+soup.get_text(strip=True)+"\n")
        return
    if str(soup.name) in ["p"]:
        savelist.append(soup.get_text(strip=True))
        return
    subdiv = soup.find_all(recursive=False)
    for sd in subdiv:
        findsubdiv(sd, depth+1)
    if str(soup.name) in ["div", "img"]:
        savelist.append("\n")


def savetext(soup):
    global savelist
    if soup == None:
        print("error")
    try:
        body = soup.find("html").find("body")
    except:
        try:
            body = soup.find("body")
        except:
            body = soup.find(id="mw-content-text")
    if body == None:
        raise "body error"
    savelist = []
    findsubdiv(body)
    return savelist


if __name__ == "__main__":
    soup = BeautifulSoup(open("/Users/dororo/Documents/資訊專題/html/人工智慧/pansci.asia.html",
                              "r", encoding="utf-8").read(), "html.parser")
    text = savetext(soup)
