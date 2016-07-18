#coding:utf-8  
import requests  
from bs4 import BeautifulSoup  
import urllib  
import re

def doubanLogin(url):
    print '''
    ---------------------------------------
                欢迎使用豆瓣登录器
    ---------------------------------------  
    '''
    user = raw_input("请输入你的用户名：")
    password = raw_input("请输入你的密码  ：")

    loginUrl = 'http://accounts.douban.com/login' 
    
    formData={   
        'source': 'main',
        'redir': url,
        'form_email':user,  
        'form_password':password, 
        'remember': 'on' ,
        'login':u'登录'  
    }   
    headers = { 
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'accounts.douban.com',
        'Origin':'https://www.douban.com',
        'Referer':'https://www.douban.com/accounts/login?source=main',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        }
    respost = requests.post(loginUrl, data =formData, headers = headers) 
    # print '%r' % respost.cookies 
    resget = requests.get(url, cookies = respost.cookies, headers = headers )
    return resget
 
def captcha(resget):
    res = resget
    page = resget.text
    #获取验证码图片

    #利用bs4获取captcha地址  
    Soup = BeautifulSoup(page,"html.parser")  
    captchatag = Soup.select('#captcha_image') 
    print Soup, captchatag
    captchaSrc = captchatag[0].get('src')   
     
    #保存到本地  
    urllib.urlretrieve(captchaSrc,"captcha_image.jpg")  
    captcha = raw_input('请到本程序目录下找到验证码图片\n输入验证码:')  
      
    formData['captcha-solution'] = captcha  
    formData['captcha-id'] = captchaID  
  
    respost = requests.post(loginUrl, data =formData, headers = headers)  
    resget = requests.get(url, cookies = respost.cookies, headers = headers )
    page = resget.text
    return resget,page 

def doubanMovieCollect(resget):
    Resget = resget
    page = resget.text
    if Resget.url=='https://movie.douban.com/mine?status=collect':  
        print 'Login successfully!!!'  
        print '我看过的电影','-'*60  
        #获取看过的电影  
        Soup = BeautifulSoup(page,"lxml")  
        tags = Soup.select('#content > div.grid-16-8.clearfix > div.article > div.grid-view > div > div.pic > a')  
        # print Soup,tags
         
    else:  
        print "failed!" 

def main():
    url =  'https://movie.douban.com/mine?status=collect'
    doubanMovieCollect(doubanLogin(url))

    
if __name__ == '__main__':
    main()


