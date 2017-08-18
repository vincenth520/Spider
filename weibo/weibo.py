#/usr/bin/env python
# -*- coding:utf-8 -*-


from urllib import request,parse
from bs4 import BeautifulSoup
import http.cookiejar 
import json
import random
import time
import configparser
import re
import math

'''
构建公共请求头
'''
def build_opener():
	cookie = http.cookiejar.CookieJar()
	cookie_processor = request.HTTPCookieProcessor(cookie)
	opener = request.build_opener(cookie_processor)	
	opener.addheaders = [("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"),
	("Referer", "https://passport.weibo.cn"),
	("Origin", "https://passport.weibo.cn"),
	("Host", "passport.weibo.cn")]
	request.install_opener(opener)


#登录
def login(code=0):
	login_data = configparser.ConfigParser()
	login_data.read("user.ini") #将用户名密码放在user.ini配置文件

	username = login_data.get("LoginInfo", "email")
	password = login_data.get("LoginInfo", "password")
	login_url = 'https://passport.weibo.cn/sso/login'



	# 构造登录参数
	params = {
		'username':username,
		'password':password,
		'savestate':'1',
		'r':'',
		'ec':'0',
		'pagerefer':'',
		'entry':'mweibo',
		'wentry':'',
		'loginfrom':'',
		'client_id':'',
		'code':'',
		'qq':'',
		'mainpageflag':'1',
		'hff':'',
		'hfp':''
	}

	params = parse.urlencode(params).encode('utf-8')

	req = request.Request(login_url,params,method="POST")
	res = request.urlopen(req)
	
	result = res.read().decode('utf-8')
	login_result = json.loads(result)
	if login_result['msg'] == '':
		print('登陆成功')
		return True
	else:
		print(login_result['msg'])
		return False

#获取发微博需要的st参数
def get_st():
	url = 'https://m.weibo.cn/compose'
	req =request.Request(url)
	res = request.urlopen(req)
	html = res.read().decode('utf-8')

	return re.search("st: '(.*)'", html).group(1)

#发微博
def weibo(content):
	st = get_st()
	add_weibo_url = 'https://m.weibo.cn/api/statuses/update'

	# 构造登录参数
	params = {
		'content':content,
		'st':st
	}

	params = parse.urlencode(params).encode('utf-8')
	req =request.Request(add_weibo_url,params,method="POST")
	res = request.urlopen(req)
	html = res.read().decode('utf-8')
	print(html)

#获取当前时间的微博内容
def get_content():
	time_data = ['子时','丑时','寅时','卯时','辰时','巳时','午时','未时','申时','酉时','戌时','亥时']
	now = int(time.strftime('%H',time.localtime(time.time())))
	now_tm = now%12

	res_str = ''
	for x in range(now_tm):
		res_str += '铛～'
	res_str = '【'+time_data[math.floor(now/2)] + '】' + res_str
	return res_str



if __name__ == '__main__':
	build_opener()
	if login():		
		weibo(get_content())
	
