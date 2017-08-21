#/usr/bin/env python
# -*- coding:utf-8 -*-


from urllib import request,parse
from bs4 import BeautifulSoup
import http.cookiejar 
import time
import re
import pyqrcode
import io
import math
import os
import random
import json
import subprocess
import sys

'''
构建公共请求头
'''

global globalData
QRImagePath = os.path.join(os.getcwd(), 'qrcode.jpg')

def build_opener():
	cookie = http.cookiejar.CookieJar()
	cookie_processor = request.HTTPCookieProcessor(cookie)
	opener = request.build_opener(cookie_processor)	
	opener.addheaders = [("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36"),
	("Referer", "https://wx.qq.com/"),
	("Origin", "https://wx.qq.com/"),
	("Host", "wx.qq.com")]
	request.install_opener(opener)

#获取uuid
def get_uuid():
	url = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_='+str(time.time())
	req = request.Request(url)
	res = request.urlopen(req)
	html = res.read().decode('utf-8')
	return re.search("QRLogin.uuid = \"(.*)\"", html).group(1)

#获取二维码
def getQrcode(uuid):
	print('Please scan the QR code.')

	url = 'https://login.weixin.qq.com/qrcode/' + uuid

	req = request.Request(url)
	res = request.urlopen(req)

	f = open(QRImagePath, 'wb')
	f.write(res.read())
	f.close()
	time.sleep(1)

	if sys.platform.find('darwin') >= 0:
	    subprocess.call(['open', QRImagePath])
	elif sys.platform.find('linux') >= 0:
	    subprocess.call(['xdg-open', QRImagePath])
	else:
	    os.startfile(QRImagePath)


def is_login():
	uuid = get_uuid()
	getQrcode(uuid)
	while True:
		url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid='+ uuid +'&tip=0&r=' + str(time.time()) + '&_=' + str(time.time())
		req = request.Request(url)
		res = request.urlopen(req)
		html = res.read().decode('utf-8')
		status = re.search("window.code=(.*);",html).group(1)
		if str(status) == '200':
			print('login success.')
			index_url = re.search("window.redirect_uri=\"(.*)\"",html).group(1)

			# closeQRImage
			if sys.platform.find('darwin') >= 0:  # for OSX with Preview
				os.system("osascript -e 'quit app \"Preview\"'")

			return index_url
			break
		elif str(status) == '201':
			print('confirm the login on the phone.')

#获取当前用户数据
def getSKey(url):
	global globalData
	req = request.Request(url+'&fun=new&version=v2&lang=zh_CN')
	res = request.urlopen(req)
	html = res.read().decode('utf-8')
	globalData = {}

	globalData['wxuin'] = re.search("<wxuin>(.*)</wxuin>",html).group(1)
	globalData['skey'] = re.search("<skey>(.*)</skey>",html).group(1)
	globalData['wxsid'] = re.search("<wxsid>(.*)</wxsid>",html).group(1)
	globalData['pass_ticket'] = re.search("<pass_ticket>(.*)</pass_ticket>",html).group(1)

	webwxinit() #登陆成功,初始化设备
	return globalData


#登录成功初始化设备
def webwxinit():
	global globalData
	globalData['DeviceID'] = repr(random.random())[2:17]
	init_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=%s&lang=zh_CN&pass_ticket=%s' %(math.floor(time.time()*1000),globalData['pass_ticket'])
	globalData['BaseRequest'] = {
			"Uin":globalData['wxuin'],
			"Sid":globalData['wxsid'],
			"Skey":globalData['skey'],
			"DeviceID":globalData['DeviceID']
		}
	params = {
		'BaseRequest':globalData['BaseRequest']
	}
	params = json.dumps(params)
	params = bytes(params,'utf8')
	headers = {'Content-Type': 'application/json;charset=UTF-8'}
	req = request.Request(init_url,params,method="POST",headers=headers)
	res = request.urlopen(req)
	result = json.loads(res.read().decode('utf-8'))
	if result['BaseResponse']['Ret'] == 0:
		globalData['UserName'] = result['User']['UserName']
		SyncKey = ''
		for v in result['SyncKey']['List']:
			SyncKey += str(v['Key']) + '_' + str(v['Val']) + '|'
		SyncKey = SyncKey[0:-1]
		globalData['SyncKey'] = SyncKey
		print('init success')
		webwxstatusnotify()

#开启微信状态通知
def webwxstatusnotify():
	global globalData
	url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' %(globalData['pass_ticket'])
	params = {
		'BaseRequest':globalData['BaseRequest'],
		"Code":3,
		"FromUserName":globalData['UserName'],
		"ToUserName":globalData['UserName'],
		"ClientMsgId":math.floor(time.time()*1000)
	}
	params = json.dumps(params)
	params = bytes(params,'utf8')
	headers = {'Content-Type': 'application/json;charset=UTF-8'}
	req = request.Request(url,params,method="POST",headers=headers)
	res = request.urlopen(req)
	result = json.loads(res.read().decode('utf-8'))
	if result['BaseResponse']['Ret'] == 0:
		print('MsgID:%s' %(result['MsgID']))


#获取所有好友
def getMembers():
	global globalData
	url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact'
	
	req = request.Request(url)
	res = request.urlopen(req)
	result = json.loads(res.read().decode('utf-8'))
	print(result)

def webwxbatchgetcontact():
	global globalData
	url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxbatchgetcontact?type=ex&r=%s&lang=zh_CN&pass_ticket=%s' %(int(time.time()),globalData['pass_ticket'])
	params = {
		'BaseRequest':globalData['BaseRequest'],
	"Count":1,
	"List":[
			{
				"UserName":"@@a900dd2fe01da33c7d6b5db0b18eaeea678fa542570cd7dc2a9f7182605561de",
				"EncryChatRoomId":""
			}
		]
	}
	params = json.dumps(params)
	params = bytes(params,'utf8')
	headers = {'Content-Type': 'application/json;charset=UTF-8'}
	req = request.Request(url,params,method="POST",headers=headers)
	res = request.urlopen(req)
	result = json.loads(res.read().decode('utf-8'))
	print(result)

#发送消息
def sendMsg(content):
	global globalData
	url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket=%s' %(globalData['pass_ticket'])
	ClientMsgId = math.floor(time.time()*1000)
	params = {
		'BaseRequest':globalData['BaseRequest'],
		"Msg":{
			'ClientMsgId':ClientMsgId,
			'Content':content,
			'FromUserName':globalData['UserName'],
			'LocalID':ClientMsgId,
			'ToUserName':"filehelper",
			'Type':1
		},
		'Scene':0
	}
	params = json.dumps(params)
	params = bytes(params,'utf8')
	headers = {'Content-Type': 'application/json;charset=UTF-8'}
	req = request.Request(url,params,method="POST",headers=headers)
	res = request.urlopen(req)
	result = json.loads(res.read().decode('utf-8'))
	print(result)

#检测消息
def synccheck():
	global globalData
	url = 'https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck?r=%s&skey=%s&sid=%s&uin=%s&deviceid=%s&synckey=%s&_=%s' %(int(time.time()),globalData['skey'],globalData['wxsid'],globalData['wxuin'],globalData['DeviceID'],globalData['SyncKey'],int(time.time()))


def test():
	global globalData
	url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?lang=zh_CN&pass_ticket=uFmjJCtZA1NsHRvMIHquw%2BpGUYWPn53QgKYKKv85AdHClaMHTGk8o%2BpTleP1Ku30&r=1503047436369&seq=0&skey=@crypt_a8d285f8_852ff0a66cc244be8f4ed15050717a1a'
	print(parse.quote(url))

if __name__ == '__main__':
	getSKey(is_login())
	getMembers()
	sendMsg('dsadada')
	# test()