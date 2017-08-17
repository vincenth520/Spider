#/usr/bin/env python
# -*- coding:utf-8 -*-


from urllib import request,parse
from bs4 import BeautifulSoup
import http.cookiejar 
import json
import random
import time
import configparser

'''
构建公共请求头
'''
def build_opener():
	cookie = http.cookiejar.CookieJar()
	cookie_processor = request.HTTPCookieProcessor(cookie)
	opener = request.build_opener(cookie_processor)	
	opener.addheaders = [("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"),
	("Referer", "https://www.zhihu.com/"),
	("Origin", "https://www.zhihu.com/"),
	("Host", "www.zhihu.com")]
	request.install_opener(opener)


def login(code=0):
	login_data = configparser.ConfigParser()
	login_data.read("user.ini") #将用户名密码放在user.ini配置文件

	username = login_data.get("LoginInfo", "email")
	password = login_data.get("LoginInfo", "password")
	url = 'https://www.zhihu.com/signin'
	login_url = 'https://www.zhihu.com/login/email'
	captcha_url = 'https://www.zhihu.com/captcha.gif'
	req = request.Request(url)
	res = request.urlopen(req)

	html = res.read().decode('utf-8')
	soup = BeautifulSoup(html)
	inputs = soup.find_all('input')

	_xsrf = inputs[0]['value']


	# 构造登录参数
	params = {
		'email': username,
		'password': password,
		'_xsrf': _xsrf
	}

	#如果code是1,说明需要验证码，读取验证码并写入到本地,然后手动输入验证码
	if code == 1:
		cap_parms = parse.urlencode({"r": time.time(), "type": "login"}).encode('utf-8')
		captcha_req = request.Request(captcha_url,cap_parms,method="GET")
		captcha_res = request.urlopen(captcha_req)
		fo = open('captcha.jpg','wb+')
		fo.write(captcha_res.read())
		fo.close()
		captcha = input("请输入验证码:\n")
		params['captcha'] = captcha

	params = parse.urlencode(params).encode('utf-8')

	req = request.Request(login_url,params,method="POST")
	res = request.urlopen(req)
	
	result = res.read().decode('utf-8')
	login_result = json.loads(result)


	if login_result['r'] == 0:
		print('登陆成功')
	else:
		if login_result['errcode'] == 1991829: 
			login(1)
		else:
			print(login_result['msg'])
			login()

if __name__ == '__main__':
	build_opener()
	login()