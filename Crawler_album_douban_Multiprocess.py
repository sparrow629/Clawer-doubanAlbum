#coding:utf-8
from __future__ import print_function
from bs4 import BeautifulSoup
from multiprocessing import Pool
import requests
import multiprocessing
import urllib
import re
import os
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

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

def getHtmlSoup(url):
	cookie = '这里是cookie'
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
		'Cookie' : cookie,
		'Connection' : 'keep-alive'
	}
	webdata = requests.get(url, headers = headers)
	html = webdata.text
	Soup = BeautifulSoup(html, 'lxml')
	return Soup

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

	Soup = getHtmlSoup(url)
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

		
def getAlbum(url,pagenumber):

	Soup = getHtmlSoup(url)

	data = {}
	count = 0
	# print Soup
	imagetags = Soup.select('#content > div.grid-16-8.clearfix > div.article > div.wr > div > div > div.pl2 > a')
	picnumbertags = Soup.select('#content > div.grid-16-8.clearfix > div.article > div.wr > div > div > span')

	for albumhref, albumname, picnumber in zip(imagetags,imagetags,picnumbertags):
		count += 1
		number = pagenumber * 16 + count
		data = {
			'albumnumb':number,
			'albumhref':albumhref.get('href'),
			'albumname':albumname.get_text(),
			'picnumber':picnumber.get_text()
		}
		# print("------------------------------------------------",
		# 	  "相册%d" % data['albumnumb'],data['albumname'],data['picnumber'],data['albumhref'],sep='\n')

		AllAlbumInfoDict[pagenumber].append(data)

	#与主进程通信,通过放入queue传递每一页得到的相册信息
	transQueue.put(AllAlbumInfoDict[pagenumber])

	print("--------------------------------------------------\n"
		  "这里是第%s页的进程 ID:%s\n"
		  "--------------------------------------------------\n" % (pagenumber+1,os.getpid()))
	print(time.strftime("%Y-%m-%d %A %X %Z", time.localtime()))



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


def getAllPreviewhref(url):

	Soup = getHtmlSoup(url)

	previewtags = Soup.select('#content > div > div.article > div.photolst.clearfix > div > a')
	if previewtags:
		AllPreviewhref = previewtags.get('href')
		print(AllPreviewhref)


class multiProcess(multiprocessing.Process):
	"""docstring for multiProcess"""
	def __init__(self, func, arg, worknum):
		super(multiProcess, self).__init__()
		self.func = func
		self.arg = arg
		self.worknum = worknum

	def works(self):
		p = multiprocessing.Pool(5)

		for i in range(self.worknum):
			page_url = self.arg[i]
			p.apply_async(self.func, args = (page_url,i,))

		p.close()
		p.join()

	def downloadworks(self, foldername):
		p = multiprocessing.Pool(5)
		for i in range(self.worknum):
			page_url = self.arg[i]
			p.apply_async(self.func, args=(page_url,i,foldername,))

		p.close()
		p.join()

#下载相册照片函数组
def getNextpageurl(url):

	Soup = getHtmlSoup(url)

	nextpagetag = Soup.select('#content > div > div.article > div.paginator > span.next > a')
	if nextpagetag:
		nextpageurl = nextpagetag[0].get('href')
		# print(nextpageurl)
		return nextpageurl
	else:
		return False

def getAllPreviewpage(url):
	allPageUrl = [url]

	nexturl = url
	while nexturl:
		nexturl = getNextpageurl(nexturl)
		if nexturl:
			allPageUrl.append(nexturl)

	return allPageUrl


def getCurrrntpageImageUrl(url, pagenumber, foldername):

	Soup = getHtmlSoup(url)
	photocount = 0



	previewtags = Soup.select('#content > div.grid-16-8.clearfix > div.article > div.photolst.clearfix > div > a')
	if previewtags:
		for i in previewtags:
			largeimghref = i.get('href')
			Soup = getHtmlSoup(largeimghref)

			imgsrctag = Soup.select('#link-report > div.image-show > div > a > img')
			imgsrc = imgsrctag[0].get('src')
			# print(imgsrc)
			# time.sleep(2)
			photocount += 1
			filename = photocount + pagenumber * 18
			path = 'doubanPhotos/%s/' % foldername

			if not os.path.exists(path):
				os.makedirs(path)
			target = path + '%s.jpg' % filename

			urllib.urlretrieve(imgsrc, target)
			print("正在下载图片...\n%s" % target)

			time.sleep(1)

	print("--------------------------------------------------\n"
		  "第%s页下载完成,进程ID:%s\n"
		  "--------------------------------------------------\n" % (pagenumber + 1, os.getpid()))

	countQueue.put(photocount)


def DownloadPhotos(url, foldername):

	print("正在读取相册图片信息...")
	Allpreviewpagelist = getAllPreviewpage(url)
	pagenumber = len(Allpreviewpagelist)
	photocount = 0

	global countQueue
	manager = multiprocessing.Manager()
	countQueue = manager.Queue()

	# for i in range(pagenumber):
	# 	photocount += getCurrrntpageImageUrl(Allpreviewpagelist[i], i, foldername)
	#

	downloadphoto = multiProcess(getCurrrntpageImageUrl, Allpreviewpagelist, pagenumber)
	downloadphoto.downloadworks(foldername)

	# 从查找页面的所有进程中通过进程通信queue获得每一页的图片
	for i in range(pagenumber):
		photocount += countQueue.get(True)

	print("这个相册有 %s 张图片" % photocount)


if __name__ == '__main__':

	# url = "https://www.douban.com/people/63226581/photos"
	# getAllPreviewhref(url)

	print('''
		---------------------------------
			  欢迎使用豆瓣相册批量下载器
		---------------------------------
		Author:  Sparrow
  		Created: 2016-7.17
  		Email: sparrow629@163.com
	''')
	print('请输入豆瓣个人主页的URL地址或者相册首页的URL地址')
	url = raw_input('地址:')


	manager = multiprocessing.Manager()
	transQueue = manager.Queue()

	URL = EnterPhotos(url)
	print(URL)

	global AllAlbumPageUrlList
	AllAlbumPageUrlList = []
	global AllAlbumInfoDict
	AllAlbumInfoDict = {}

	AllAlbumInfoList = []


	getAllAlbumPagesUrl(URL)
	AlbumPageNumber = len(AllAlbumPageUrlList)

	for i in range(AlbumPageNumber):
		AllAlbumInfoDict[i] = []

	#按相册的页数分配进程数
	GetAlbum = multiProcess(getAlbum, AllAlbumPageUrlList, AlbumPageNumber)
	GetAlbum.works()

	#从查找页面的所有进程中通过进程通信queue获得每一页的相册
	for i in range(AlbumPageNumber):
		AllAlbumInfoDict[i] = transQueue.get(True)

	print("--------------------------------------------------\n"
		  "这里是主进程 ID:%s\n"
		  "--------------------------------------------------\n" % os.getpid())
	print("\t\t\t\t\t相册列表")

	if AllAlbumInfoDict:
		for i in range(AlbumPageNumber):
			for j in range(AlbumPageNumber):
				if AllAlbumInfoDict[j][0]['albumnumb'] == i * 16 + 1:
					AllAlbumInfoList = AllAlbumInfoList + AllAlbumInfoDict[j]

		AlbumNumber = len(AllAlbumInfoList)
		for i in range(AlbumNumber):
			print("------------------------------------------------",
			  "相册%d" % AllAlbumInfoList[i]['albumnumb'], AllAlbumInfoList[i]['albumname'], AllAlbumInfoList[i]['picnumber'],
			  AllAlbumInfoList[i]['albumhref'], sep='\n')

		print(AlbumNumber)

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
					t0 = time.time()

					for i in range(1,AlbumNumber+1):
						select_album_number = i
						AlbumInfo = SelectAlbum(select_album_number, AlbumNumber)
						SelectAlbum_name = AlbumInfo[1]
						SelectAlbum_url = AlbumInfo[2]
						print(select_album_number, SelectAlbum_name, SelectAlbum_url)

						DownloadPhotos(SelectAlbum_url, SelectAlbum_name)

					correctFlag = True
					print(time.time() - t0)

					# 下载所有相册
				else:
					# 选择相册序号下载
					t0 = time.time()
					for i in Numlist:
						select_album_number = i
						AlbumInfo = SelectAlbum(select_album_number, AlbumNumber)

						if AlbumInfo:
							SelectAlbum_name = AlbumInfo[1]
							SelectAlbum_url = AlbumInfo[2]


							DownloadPhotos(SelectAlbum_url, SelectAlbum_name)


							print(select_album_number,SelectAlbum_name,SelectAlbum_url)
							correctFlag = True

					print(time.time() - t0)
					# 选择相册序号下载
				chose_quit = raw_input('\n继续选择下载请按键[Y],退出请按键[N]:')





