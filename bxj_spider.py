# coding:utf-8

from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
from threading import Thread
import re
import requests
import os

class bxj:
    def __init__(self):
        self.indexUrl = 'https://bbs.hupu.com'
        self.baseUrl = self.indexUrl + '/bxj'
        self.index = 1
        #self.all_posts = []
    
    def connectDB(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client.bxj
        self.posts = self.db.posts

    def updateDB(self, post):
        self.posts.update({'_id': post['_id']}, {'$set': post}, True)


    def build_soup(self, url, index):
        if index == 1:
            url = url
        else:
            url = url + '-' + str(index)
            #url = 'https://bbs.hupu.com/bxj-2'
        html = requests.get(url)
        content = html.content
        return BeautifulSoup(content, 'html.parser')

    def page(self, url, index):
        soup = self.build_soup(url, index)
        #print(soup)
        tbody = soup.find('tr', mid=re.compile('[\d]{8}')).parent
        rows = tbody.findAll('tr')
        
        for row in rows:
            post = {}
            tds = row.findAll('td')
            title_link = tds[1]
            author_date = tds[2]
            view_reply = tds[3]
            post['_id'] = row['mid']
            post['title'] = title_link.find('a').get_text()
            post['link'] = title_link.find('a')['href']
            post['author'] = author_date.find('a').get_text()
            post['createDate'] = datetime.strptime(author_date.get_text().strip('\t\n\r')[-10:], "%Y-%m-%d")
            post['views'] = int(view_reply.get_text().split('/')[0])
            post['replies'] = int(view_reply.get_text().split('/')[1])
            #self.posts.update({'_id': post['_id']}, {'$set': post}, True)
            self.updateDB(post)

    def loadPage(self, url, index):
        for index in range(1,11):
            self.page(url, index)
            self.index += 1
        #print(self.all_posts)


    def start(self):
        self.connectDB();
        self.loadPage(self.baseUrl, self.index)

inst = bxj()
inst.start()
        