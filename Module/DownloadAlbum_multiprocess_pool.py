#coding:utf-8
from __future__ import print_function
from multiprocessing import Pool
import multiprocessing
from bs4 import BeautifulSoup
import os, time, random, urllib
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def getHtmlSoup(url):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
		'Cookie' : 'bid="nSrT7p8EE2w"; gr_user_id=32bfb902-ff98-4ae9-9e0c-140b33b338d7; _ga=GA1.2.1806406022.1440759784; ll="108090"; ps=y; ct=y; cn_d6168da03fa1ahcc4e86_dplus=%7B%22distinct_id%22%3A%20%221539c2fda9c1c4-00d07e40331b6e-123b6e5f-fa000-1539c2fda9d707%22%2C%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201468247199%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201468247199%2C%22%24id%22%3A%20%2258175165%22%2C%22%24initial_time%22%3A%20%221460882242%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fmovie.douban.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22movie.douban.com%22%2C%22initial_view_time%22%3A%20%221468242437%22%2C%22initial_referrer%22%3A%20%22https%3A%2F%2Fmovie.douban.com%2Fsubject%2F20505982%2F%3Ffrom%3Dshowing%22%2C%22initial_referrer_domain%22%3A%20%22movie.douban.com%22%7D; ue="bill.zxb@qq.com"; as="https://movie.douban.com/"; ck=gMs4; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1468807193%2C%22https%3A%2F%2Fmovie.douban.com%2F%22%5D; __utmt=1; dbcl2="148473388:v4QizcqOlaE"; _vwo_uuid_v2=E6A49BB6DF236D4F60261E4F121C7BED|cba1af9a5fa12a42f4ac05fe149679bd; ap=1; push_noty_num=0; push_doumail_num=0; _pk_id.100001.8cb4=d0c4f6d094349915.1466324420.80.1468807314.1468768546.; _pk_ses.100001.8cb4=*; __utma=30149280.1806406022.1440759784.1468766439.1468806370.113; __utmb=30149280.3.10.1468806370; __utmc=30149280; __utmz=30149280.1468293177.90.25.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=30149280.14847',
		'Connection' : 'keep-alive'
	}
	webdata = requests.get(url, headers = headers)
	html = webdata.text
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

			time.sleep(1)

		print("--------------------------------------------------\n"
			  "第%s页下载完成,进程ID:%s\n"
			  "--------------------------------------------------\n" % (pagenumber + 1, os.getpid()))

	countQueue.put(photocount)


def DownloadPhotos(url, foldername):

	print("正在读取相册片信息...")
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

class multiProcess(multiprocessing.Process):
	"""docstring for multiProcess"""
	def __init__(self, func, arg, worknum):
		super(multiProcess, self).__init__()
		self.func = func
		self.arg = arg
		self.worknum = worknum

	def downloadworks(self, foldername):
		p = multiprocessing.Pool()
		for i in range(self.worknum):
			page_url = self.arg[i]
			p.apply_async( self.func, args = (page_url,i,foldername,))

		p.close()
		p.join()


if __name__ == '__main__':
	# url = "https://www.douban.com/photos/album/117047793/"
	# url = "https://www.douban.com/photos/album/155037365/"
	url = "https://www.douban.com/photos/album/107197270/"
	# url = "https://www.douban.com/photos/album/107197270/"
	t0 = time.time()

	DownloadPhotos(url, 'test')
	# print(getHtmlSoup(url))
	print(time.time()-t0)