#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import crawler
import json
import os
import sys
from sogou_utils.file import mkdir\

reload(sys)
sys.setdefaultencoding('utf8')

class WeiboCrawler:
    weibo_config = dict()
    weibo_crawler = None
    # blogger_url_list = list()

    def __init__(self):
       self.weibo_crawler = crawler.Crawler()
       cur_path = os.path.split(os.path.realpath(__file__))[0]
       config_path = cur_path + os.path.sep + "config.json"
       json_file = open(config_path)
       self.weibo_config = json.load(json_file)['weibo']

    # 获取微博用户和该用户的微博网址，不止一页内容
    def get_blogger_url_dict(self, category_url, page_number):
        # 清除网页缓存，防止浏览器崩溃
        self.weibo_crawler.delete_cookies()
        blogger_url_info_dict = dict()
        for i in range(page_number):
            full_url = category_url + '?page=' + str(i+1)
            self.weibo_crawler.open_url(full_url)
            blogger_elements = self.weibo_crawler.get_elements_by_xpath(
                '//div[@class="info_name W_fb W_f14"]/a[@class="S_txt1"]', 10)  # 每页只有10个博主
            for blogger_element in blogger_elements:
                title = blogger_element.get_attribute("title")
                url = blogger_element.get_attribute("href")
                blogger_url_info_dict[url] = title
        return blogger_url_info_dict

    # 获取博主的各个微博内容的网址
    def get_blogs_info(self, blog_url, blog_number):
        print '----' * 20
        print blog_url
        blogs_info = dict()
        blogs_info["total info"] = []
        self.weibo_crawler.open_url(blog_url)
        real_blogs_number = blog_number
        # 判断首页微博的内容数量是否少于10，则抓取首页那仅有的几个blog
        blogs_number_onpage = len(self.weibo_crawler.get_elements_by_xpath('//div[@class="WB_feed_handle"]'))
        print(u'首页共 %d 条微博' % blogs_number_onpage)
        if blogs_number_onpage <= 14:  # 一般首页会出现15个微博，如果博主有更多微博的话可以往下拉，如果首页少于15个微博，不用下拉
            real_blogs_number = blogs_number_onpage
        # 获取微博内容
        weibo_elements = self.weibo_crawler.get_elements_by_xpath(
            '//div[@class="WB_cardwrap WB_feed_type S_bg2 WB_feed_like "]', num_limit=real_blogs_number)
        if not weibo_elements:
            weibo_elements = self.weibo_crawler.get_elements_by_xpath(
                '//div[@class="WB_cardwrap WB_feed_type S_bg2 WB_feed_vipcover WB_feed_like "]',
                num_limit=real_blogs_number)
        print(u'实际抓取 %d 微博' % len(weibo_elements))
        count = 1
        for weibo_element in weibo_elements:
            print(u'现在爬取第 %d 微博' % count)
            count += 1
            blog_info = dict()
            # 微博内容
            content = weibo_element.find_element_by_css_selector("[class='WB_text W_f14']").text
            # 微博评论按钮
            comment_button = weibo_element.find_element_by_css_selector("[action-type='fl_comment']")
            # 点击微博评论按钮
            self.weibo_crawler.js_click_element(comment_button)
            # 获取评论内容
            comments = ''
            comments_elements = weibo_element.find_elements_by_css_selector("[class='WB_text']")
            for comments_element in comments_elements:
                comment_list = comments_element.text.split("：")
                if len(comment_list) > 1:  # 只抓取评论内容
                    comment = comment_list[1]
                    comments += comment
            # 再次点击评论按钮
            self.weibo_crawler.js_click_element(comment_button)
            # 写入json文件
            blog_info["weibo"] = content
            blog_info["comments"] = comments
            blogs_info["total info"].append(blog_info)
        return blogs_info

    # 启动爬虫
    def run_crawler(self):
        # 创建文件夹weibo
        corpus_dir = 'data/weibo'
        mkdir(corpus_dir)
        # 获取weibo的爬取类别
        category_list = self.weibo_config['category_list']
        for category in category_list:
            category_blog_dir = os.path.join(corpus_dir, category['name'])
            mkdir(category_blog_dir)  # 创建类别的文件夹
            blogger_url_info_path = os.path.join(category_blog_dir, 'blogger_url_info.json')
            category_blogger_url_dict = dict()
            if os.path.exists(blogger_url_info_path):
                json_file = open(blogger_url_info_path)
                category_blogger_url_dict = json.load(json_file)
            if not category_blogger_url_dict:
                category_blogger_url_dict = self.get_blogger_url_dict(category['url'], int(category['page_number']))
            # 创建问题名和问题网址的文件 blogger_url_info.json
            blogger_url_info_file = open(blogger_url_info_path, 'w')
            json.dump(category_blogger_url_dict, blogger_url_info_file, ensure_ascii=False, indent=0)
            blogger_url_info_file.close()

            error_blog_url_list = list()
            # 写各个问题回答的json文件
            for blogger_url in category_blogger_url_dict:
                category_blogger_json_name = category_blogger_url_dict[blogger_url] + '.json'
                category_blogger_json_path = os.path.join(category_blog_dir, category_blogger_json_name)
                if os.path.exists(category_blogger_json_path):
                    continue
                blogs_info = self.get_blogs_info(blogger_url, 25)  # 每个博主下面抓25条微博
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
    weibo_crawler = WeiboCrawler()
    weibo_crawler.run_crawler()

