#!/usr/bin/env python
# -*- coding:utf-8 -*-

from urllib import request,parse
from bs4 import BeautifulSoup
import http.cookiejar 
import re
import configparser
'''
构建公共请求头
'''
def build_opener():
	cookie = http.cookiejar.CookieJar()
	cookie_processor = request.HTTPCookieProcessor(cookie)
	opener = request.build_opener(cookie_processor)	
	opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0"),
	("Referer", "http://cn.v2ex.com/signin"),
	("Origin", "http://cn.v2ex.com"),
	("Host", "cn.v2ex.com")]
	request.install_opener(opener)


def login():
	login_data = configparser.ConfigParser()
	login_data.read("user.ini") #将用户名密码放在user.ini配置文件

	username = login_data.get("LoginInfo", "email")
	password = login_data.get("LoginInfo", "password")
	url = 'https://www.v2ex.com/signin'
	req = request.Request(url)
	res = request.urlopen(req)
	html = res.read().decode('gbk','ignore')  #获取到登录页的源代码并分析
	soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
	inputs = soup.find_all('input')

	# 构造登录参数
	params = {
		inputs[1]["name"]: username,
		inputs[2]["name"]: password,
		inputs[3]["name"]: inputs[3]["value"],
		inputs[5]["name"]: inputs[5]["value"]
	}
	params = parse.urlencode(params).encode('utf-8')

	req = request.Request(url,params,method="POST") #将构造好的登录参数发送到登录地址
	res = request.urlopen(req)

def daily():
	url = 'https://www.v2ex.com/mission/daily' #领取奖励地址
	req = request.Request(url)
	res = request.urlopen(req)
	html = res.read().decode("utf-8")
	soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8') #获取领取奖励页面的代码
	inputs = soup.find_all('input')

	try:
		daily_link = 'https://www.v2ex.com' + re.search("location.href = '(.*)';", inputs[1]['onclick']).group(1) #查找点击领取的地址
		if daily_link == 'https://www.v2ex.com/balance':
			print('您今天已经领取了！')
			return False

		req = request.Request(daily_link)
		res = request.urlopen(req)

		html = res.read().decode("utf-8")

		soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
		
		print(soup.find('div',class_="message").text)
	except Exception as e:
		print('账号密码错误')
	
	



if __name__ == '__main__':
	build_opener()
	login()
	daily()