#coding:utf-8
from __future__ import print_function
from bs4 import BeautifulSoup
import multiprocessing
import urllib
import re
import os
import time

def Filter_input(inputlist):
	charlist =  set(inputlist.split())
	numlist = []

	def is_number(char):
		try:
			int(char)
			return True
		except ValueError:
			return False

	for i in charlist:
		if is_number(i):
			num = int(i)
			numlist.append(num)
	count = len(numlist)
	return numlist

def getHtml(url):
	page = urllib.urlopen(url)
	html = page.read()
	return html

def EnterPhotos(url):
	people_reg = r'https://www.douban.com/people/.+?/$'
	people_url = re.compile(people_reg)
	photo_reg = r'https://www.douban.com/people/.+?/.+?'
	photo_url = re.compile(photo_reg)

	if re.match(people_reg,url):
		URL = url + 'photos'
		print("正在寻找相册并打开...")
		return URL
	elif re.match(photo_url,url):
		print("正在寻找专辑...")
		return url
	else:
		print("你输入的链接不符合规则,请重新输入!")
		return False


def getAllAlbumPagesUrl(url):
	html = getHtml(url)
	Soup = BeautifulSoup(html, 'lxml')
	pageNumber = len(AllAlbumPageUrlList)

	nextpagetags = Soup.select('#content > div.grid-16-8.clearfix > div.article > div.paginator > span.next > a')
	# print(nextpagetags)
	if nextpagetags:
		if not AllAlbumPageUrlList:
			AllAlbumPageUrlList.append(url)

		nextpageurl = nextpagetags[0].get('href')
		AllAlbumPageUrlList.append(nextpageurl)
		getAllAlbumPagesUrl(nextpageurl)

	else:
		if AllAlbumPageUrlList:

			print("一共%d页" % pageNumber)

		else:
			albumtags = Soup.select('#content > div.grid-16-8.clearfix > div.article > div > div > a')
			if albumtags:
				AllAlbumPageUrlList.append(url)
				# print("一共1页",AllAlbumPageUrlList)
			else:
				print("这里没有上传过任何照片")



class GetAlbum(object):
	"""docstring for GetAlbum"""
	
	def __init__(self, url, pagenumber):
		super(GetAlbum, self).__init__()
		self.url = url
		self.html = getHtml(url)
		self.pagenumber = pagenumber
		
	def getAlbum(self):
		Soup = BeautifulSoup(self.html, 'lxml')

		data = {}
		count = 0
		# print Soup
		imagetags = Soup.select('#content > div.grid-16-8.clearfix > div.article > div.wr > div > div > div.pl2 > a')
		picnumbertags = Soup.select('#content > div.grid-16-8.clearfix > div.article > div.wr > div > div > span')

		for albumhref, albumname, picnumber in zip(imagetags,imagetags,picnumbertags):
			count += 1
			number = self.pagenumber * 16 + count
			data = {
				'albumnumb':number,
				'albumhref':albumhref.get('href'),
				'albumname':albumname.get_text(),
				'picnumber':picnumber.get_text()
			}
			print("------------------------------------------------",
				  "相册%d" % data['albumnumb'],data['albumname'],data['picnumber'],data['albumhref'],sep='\n')
			AllAlbumInfoList.append(data)


def SelectAlbum(select_album_number, album_number):
	if select_album_number in range(1,album_number+1):
		for i in AllAlbumInfoList:
			if i['albumnumb'] == select_album_number:
				select_album_url = i['albumhref']
				select_album_name = i['albumname']
				# print(select_album_number,select_album_name,select_album_url)
		return select_album_number,select_album_name,select_album_url
	else:
		return False


class multiProcess(multiprocessing.Process):
	"""docstring for multiProcess"""
	def __init__(self, func, arg, worknum):
		super(multiProcess, self).__init__()
		self.func = func
		self.arg = arg
		self.worknum = worknum

	def works(self):
		proc_record = []

		for i in range(self.worknum):
			p = multiprocessing.Process(target = self.func, args = (i,))
			p.daemon = True
			p.start()
			proc_record.append(p)
		for p in proc_record:
			p.join()



if __name__ == '__main__':
	t0 = time.time()
	url = "https://www.douban.com/people/63226581/photos"
	# url = "https://www.douban.com/people/58175165/"
	# url = "https://www.douban.com/people/148026269/"

	URL = EnterPhotos(url)
	print(URL)

	global AllAlbumPageUrlList
	AllAlbumPageUrlList = []
	global AllAlbumInfoList
	AllAlbumInfoList = []

	getAllAlbumPagesUrl(URL)
	AlbumPageNumber = len(AllAlbumPageUrlList)

	for i in range(AlbumPageNumber):
		page_url = AllAlbumPageUrlList[i]
		getAlbum = GetAlbum(page_url, i)
		getAlbum.getAlbum()

	AlbumNumber = len(AllAlbumInfoList)

	chose_quit = 'Y'
	while not chose_quit == 'N':

		correctFlag = False # 用来标记有正确的相册序号出现
		while (not correctFlag) and (not AlbumNumber == 0):
			print("\n下载所有相册请直接输入数字'0'")
			inputlist = raw_input("请输入你要下载的相册序号:")
			Numlist = Filter_input(inputlist)

			if Numlist and Numlist[0] == 0:
				# 下载所有相册
				print("正在下载所有相册,请耐心等待...")

				for i in range(1,AlbumNumber+1):
					select_album_number = i
					AlbumInfo = SelectAlbum(select_album_number, AlbumNumber)
					SelectAlbum_name = AlbumInfo[1]
					SelectAlbum_url = AlbumInfo[2]

					print(select_album_number, SelectAlbum_name, SelectAlbum_url)

				correctFlag = True

				# 下载所有相册
			else:
				# 选择相册序号下载
				for i in Numlist:
					select_album_number = i
					AlbumInfo = SelectAlbum(select_album_number, AlbumNumber)

					if AlbumInfo:
						SelectAlbum_name = AlbumInfo[1]
						SelectAlbum_url = AlbumInfo[2]

						print(select_album_number,SelectAlbum_name,SelectAlbum_url)
						correctFlag = True

				# 选择相册序号下载
			chose_quit = raw_input('\n继续选择下载请按键[Y],退出请按键[N]:')

	print(time.time()- t0)



