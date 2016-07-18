#coding:utf-8
from __future__ import print_function
import multiprocessing
from bs4 import BeautifulSoup
import os, time, random, urllib

def getHtmlSoup(url):
	page = urllib.urlopen(url)
	html = page.read()
	Soup = BeautifulSoup(html, 'lxml')
	return Soup

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
			print("正在下载图片%s" % target)

		countQueue.put(photocount)

	print("--------------------------------------------------\n"
		  "这里是第%s页的进程 ID:%s\n"
		  "--------------------------------------------------\n" % (pagenumber + 1, os.getpid()))
	print(time.strftime("%Y-%m-%d %A %X %Z", time.localtime()))

	# return photocount


def DownloadPhotos(url, foldername):
	Allpreviewpagelist = getAllPreviewpage(url)
	pagenumber = len(Allpreviewpagelist)
	photocount = 0

	global countQueue
	countQueue = multiprocessing.Queue()

	# for i in range(pagenumber):
	# 	photocount += getCurrrntpageImageUrl(Allpreviewpagelist[i], i, foldername)
	#

	downloadphoto = multiProcess(getCurrrntpageImageUrl, Allpreviewpagelist, pagenumber)
	downloadphoto.downloadworks(foldername)

	# 从查找页面的所有进程中通过进程通信queue获得每一页的图片
	for i in range(pagenumber):
		photocount += countQueue.get(True)

	print("这个相册有 %s 张图片" % photocount)

class multiProcess(multiprocessing.Process):
	"""docstring for multiProcess"""
	def __init__(self, func, arg, worknum):
		super(multiProcess, self).__init__()
		self.func = func
		self.arg = arg
		self.worknum = worknum

	def downloadworks(self, foldername):
		proc_record = []

		for i in range(self.worknum):
			page_url = self.arg[i]
			p = multiprocessing.Process(target = self.func, args = (page_url,i,foldername,))
			p.daemon = True
			p.start()
			proc_record.append(p)
		for p in proc_record:
			p.join()

if __name__ == '__main__':
	# url = "https://www.douban.com/photos/album/1632492290/"
	# url = "https://www.douban.com/photos/album/82367742/"
	# url = "https://www.douban.com/photos/album/117047793/"
	url = "https://www.douban.com/photos/album/1621384085/"
	t0 = time.time()

	DownloadPhotos(url, 'test')
	print(time.time()-t0)