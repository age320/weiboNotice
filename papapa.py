#!/usr/bin/python
#coding=utf8
"""
# Author: zhang
# Created Time : 2016-11-28 11:07:36

# File Name: papapa.py
# Description: Notification of weibo release time

"""
import urllib2
import smtplib
import time
import sys
import json
import requests
import base64
import re
from lxml import etree
from email.mime.text import MIMEText

mailto_list =["XXX@XXX.com"]  #收件人邮箱地址
mail_host = "smtp.XXX.com"    #SMTP服务器地址
mail_user = "XXX"             #用户名
mail_pwd = "XXX"              #密码
mail_postfix = "XXX.com"      #邮箱前缀

base_url = "http://weibo.cn/微博用户数字标示/profile?filter=0"
old_weibo = []
headers = {
        'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6,1;\
                en-US;rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
        }
myWeiBo = [   #登陆的用户帐号密码
        {'no':'XXXXXX', 'psw':'XXXXXX'},
        ]

def send_mail(to_list,subject,content):
    me = "Scrapy"+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_subtype='plain',_charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP(mail_host,25)
        server.login(mail_user,mail_pwd)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print "SendMail Error:" + str(e)
        return False

def getCookies(weibo):
    """ 获取Cookies """
    cookies = []
    loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
    for elem in weibo:
        account = elem['no']
        password = elem['psw']
        username = base64.b64encode(account.encode('utf-8')).decode('utf-8')
        postData = {
            "entry": "sso",
            "gateway": "1",
            "from": "null",
            "savestate": "30",
            "useticket": "0",
            "pagerefer": "",
            "vsnf": "1",
            "su": username,
            "service": "sso",
            "sp": password,
            "sr": "1440*900",
            "encoding": "UTF-8",
            "cdult": "3",
            "domain": "sina.com.cn",
            "prelt": "0",
            "returntype": "TEXT",
        }
        session = requests.Session()
        r = session.post(loginURL, data=postData)
        jsonStr = r.content.decode('gbk')
        info = json.loads(jsonStr)
        if info["retcode"] == "0":
            print "Get Cookie Success!( Account:%s )" % account
            cookie = session.cookies.get_dict()
            cookies.append(cookie)
        else:
            print "Failed!( Reason:%s )" % info['reason']
    return cookies

def isOldWeibo(url):
    return (True if url in old_weibo else False)

def getPage(myCookie):
    try:
        page = requests.get(base_url,headers=headers,cookies=myCookie).content
    except requests.exceptions.HTTPError as e:
        print "Urlopen Error:"+str(e)
        return -1
    selector = etree.HTML(page)
    items = selector.xpath('//div/span[@class="ctt"]/text()')
    hrefs = re.findall('>转发\[.*?<a href="(.*?)" class="cc">评论',page,re.S)
    return items,hrefs

def getOldWeibo(myCookie):
    '''获取已发布微博列表'''
    temp_data=[]
    old_items,hrefs = getPage(myCookie)
    for item in old_items:
        #print item.encode('utf-8')
        temp_data.append(item)
    old_weibo.extend(temp_data)

def getNewWeibo(myCookie):
    '''判断是否发布新微博'''
    while(True):
        time.sleep(5)
        new_items,hrefs = getPage(myCookie)
        if new_items[1] not in old_weibo and hrefs is not None:
            send_mail(mailto_list, "Your Dream Girl's New Weibo", hrefs[0])
            old_weibo.append(new_items[1])
            print "Send the link of the new weibo to your email!"
        if new_items[2] not in old_weibo and hrefs is not None:
            send_mail(mailto_list, "Your Dream Girl's New Weibo", hrefs[0])
            old_weibo.append(new_items[2])
            print "Send the link of the new weibo to your email!"

def main():
    cookie = getCookies(myWeiBo)
    getOldWeibo(cookie[0])
    getNewWeibo(cookie[0])


if __name__ == '__main__':
    main()

