#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import crawler
import json
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class WeiboHotCrawler:
    weibo_config = dict()
    weibo_crawler = None
    # blogger_url_list = list()

    def __init__(self):
       self.weibo_crawler = crawler.Crawler()
       cur_path = os.path.split(os.path.realpath(__file__))[0]
       config_path = cur_path + os.path.sep + "config.json"
       json_file = open(config_path)
       self.weibo_config = json.load(json_file)['weibo_hot']

    # 获取微博网址，不止一页内容
    def get_blogger_url_dict(self, category_url, blog_number):
        # 清除网页缓存，防止浏览器崩溃
        self.weibo_crawler.delete_cookies()
        blogger_url_info_dict = dict()
        self.weibo_crawler.open_url(category_url)
        blogger_elements = self.weibo_crawler.get_elements_by_xpath('//div[@action-type="feed_list_item"]', num_limit=blog_number)
        for blogger_element in blogger_elements:
            url = blogger_element.get_attribute("href")
            if url is not None and url.startswith('//weibo.com'):
                real_url = "https:" + url
                blogger_url_info_dict[real_url] = "title"
            else:
                continue
        print('共获取 %d 个blog url' % len(blogger_url_info_dict))
        # for url in blogger_url_info_dict:
        #     print url
        return blogger_url_info_dict

    # 获取各个微博内容的网址
    def get_blogs_info(self, blog_url):
        print blog_url
        self.weibo_crawler.open_url(blog_url)
        # 获取微博内容
        blog_info = dict()
        # 微博内容
        content_element = self.weibo_crawler.get_elements_by_xpath('//div[@class="WB_text W_f14"]')
        if len(content_element) == 1:
            content = content_element[0].text
        else:
            content = ''
        # 获取评论内容
        comments = ''
        comments_elements = self.weibo_crawler.get_elements_by_xpath('//div[@class="WB_text"]')
        for comments_element in comments_elements:
            comment_list = comments_element.text.split("：")
            if len(comment_list) > 1:  # 只抓取评论内容
                comment = comment_list[1]
                comments += comment
        # 写入json文件
        blog_info["weibo"] = content
        blog_info["comments"] = comments
        blog_info["url"] = blog_url

        return blog_info

    # 启动爬虫
    def run_crawler(self):
        # 创建文件夹weibo_hot
        corpus_dir = 'data/weibo_hot'
        os.mkdir(corpus_dir)
        # 获取weibo的爬取类别
        category_list = self.weibo_config['category_list']
        for category in category_list:
            category_blog_dir = os.path.join(corpus_dir, category['name'])
            os.mkdir(category_blog_dir)  # 创建类别的文件夹
            blogger_url_info_path = os.path.join(category_blog_dir, 'blogger_url_info.json')
            category_blogger_url_dict = dict()
            if os.path.exists(blogger_url_info_path):
                json_file = open(blogger_url_info_path)
                category_blogger_url_dict = json.load(json_file)
            if not category_blogger_url_dict:
                category_blogger_url_dict = self.get_blogger_url_dict(category['url'], int(category['weibo_number']))
            # 创建问题名和问题网址的文件 blogger_url_info.json
            blogger_url_info_file = open(blogger_url_info_path, 'w')
            json.dump(category_blogger_url_dict, blogger_url_info_file, ensure_ascii=False, indent=0)
            blogger_url_info_file.close()

            error_blog_url_list = list()
            # 写各个问题回答的json文件
            for blogger_url in category_blogger_url_dict:
                name = blogger_url.split("/")[3]
                category_blogger_json_name = name + '.json'
                category_blogger_json_path = os.path.join(category_blog_dir, category_blogger_json_name)
                if os.path.exists(category_blogger_json_path):
                    continue
                blogs_info = self.get_blogs_info(blogger_url)
                # time.sleep(1)
                if blogs_info:
                    # blog_info['url'] = blog_url
                    # blog_info['title'] = category_blog_url_dict[blog_url]
                    category_blogs_json_file = open(category_blogger_json_path, 'w')
                    json.dump(blogs_info, category_blogs_json_file, ensure_ascii=False, indent=0)
                    category_blogs_json_file.close()
                # blog_info为空的错误回答
                else:
                    error_blog_url_list.append(blogger_url)

            for error_blog_url in error_blog_url_list:
                category_blogger_url_dict.pop(error_blog_url)

            blogger_url_info_file = open(blogger_url_info_path, 'w')
            json.dump(category_blogger_url_dict, blogger_url_info_file, ensure_ascii=False, indent=0)
            blogger_url_info_file.close()


if __name__ == "__main__":
    weibo_crawler = WeiboHotCrawler()
    weibo_crawler.run_crawler()

