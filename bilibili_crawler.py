#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import crawler
import json
import os
import sys
import time
from sogou_utils.file import mkdir

reload(sys)
sys.setdefaultencoding('utf8')


class BilibiliCrawler:
    bilibili_config = dict()
    bilibili_crawler = None
    vedio_url_list = list()

    def __init__(self):
       self.bilibili_crawler = crawler.Crawler()
       cur_path = os.path.split(os.path.realpath(__file__))[0]
       config_path = cur_path + os.path.sep + "config.json"
       json_file = open(config_path)
       self.bilibili_config = json.load(json_file)['bilibili']

    def get_vedio_url_dict(self, category_url, vedio_number):
        self.bilibili_crawler.open_url(category_url)
        title_elements = self.bilibili_crawler.get_elements_by_xpath('//div[@class="info"]/a[@class="title"]', vedio_number)
        vedio_url_info_dict = dict()
        for title_element in title_elements:
            url = title_element.get_attribute('href')
            title = title_element.text
            if url.startswith('https://www.bilibili.com') and not vedio_url_info_dict.has_key(url):
                vedio_url_info_dict[url] = title

        return vedio_url_info_dict

    def get_vedio_info(self, vedio_url, page=5):
        vedio_info = dict()
        print vedio_url
        self.bilibili_crawler.open_url(vedio_url)
        current_url = self.bilibili_crawler.get_current_url()
        if not current_url.startswith('https://www.bilibili.com'):
            return vedio_info

        # 获取视频标题
        title_element = self.bilibili_crawler.get_elements_by_xpath('//h1[@class="video-title"]/span')
        if not title_element:
            title_element = self.bilibili_crawler.get_elements_by_xpath('//div[@class="header-info"]/h1')
        if not title_element:
            title_element = self.bilibili_crawler.get_elements_by_xpath('//div[@class="media-wrapper"]/h1')
        title = title_element[0].text
        vedio_info["title"] = title 

        # 获取评论的页数
        time.sleep(2)
        self.bilibili_crawler.swipe_down()
        time.sleep(2)
        page_number_elements = self.bilibili_crawler.get_elements_by_xpath('//div[@class="header-page paging-box"]/a[@class="tcd-number"]')
        if page_number_elements:
            page_number_list = []
            for page_number_element in page_number_elements:
                current_page = page_number_element.text
                page_number_list.append(int(current_page))
            max_page = max(page_number_list)
            comment_page = page
            if comment_page > max_page:
                comment_page = max_page
            print("max page is %d" % max_page)
            print("comment page is %d" % comment_page)
            # 获取评论内容
            comments_text = ''
            for i in range(comment_page-1):
                next_page_button = \
                    self.bilibili_crawler.get_elements_by_xpath('//div[@class="header-page paging-box"]/a[@class="next"]')[0]
                comments_elements_con = self.bilibili_crawler.get_elements_by_xpath('//p[@class="text"]')
                comments_elements_re = self.bilibili_crawler.get_elements_by_xpath('//span[@class="text-con"]')
                for comments_element in comments_elements_con:
                    comments_text += comments_element.text
                for comments_element in comments_elements_re:
                    comments_text += comments_element.text
                self.bilibili_crawler.js_click_element(next_page_button)
            vedio_info["comments"] = comments_text
        else:
            comments_text = ''
            comments_elements_con = self.bilibili_crawler.get_elements_by_xpath('//p[@class="text"]')
            comments_elements_re = self.bilibili_crawler.get_elements_by_xpath('//span[@class="text-con"]')
            for comments_element in comments_elements_con:
                comments_text += comments_element.text
            for comments_element in comments_elements_re:
                comments_text += comments_element.text
            vedio_info["comments"] = comments_text
        return vedio_info

    def run_crawler(self):
        corpus_dir = 'data/bilibili'
        mkdir(corpus_dir)

        category_list = self.bilibili_config['category_list']
        for category in category_list:
            category_vedio_dir = os.path.join(corpus_dir, category['name'])
            mkdir(category_vedio_dir)
            vedio_url_info_path = os.path.join(category_vedio_dir, 'vedio_url_info.json')
            category_vedio_url_dict = dict()
            if os.path.exists(vedio_url_info_path):
                json_file = open(vedio_url_info_path)
                category_vedio_url_dict = json.load(json_file)

            if not category_vedio_url_dict:
                category_vedio_url_dict = self.get_vedio_url_dict(category['url'], int(category['vedio_number']))

            vedio_url_info_file = open(vedio_url_info_path, 'w')
            json.dump(category_vedio_url_dict, vedio_url_info_file, ensure_ascii=False, indent=0)
            vedio_url_info_file.close()

            error_vedio_url_list = list()
            for vedio_url in category_vedio_url_dict:
                category_vedio_json_name = vedio_url.split('/')[4] + '.json'
                category_vedio_json_path = os.path.join(category_vedio_dir, category_vedio_json_name)
                if os.path.exists(category_vedio_json_path):
                    continue
                vedio_info = self.get_vedio_info(vedio_url, page=5)  # 每个视频爬取5页评论
                if vedio_info:
                    vedio_info['url'] = vedio_url
                    vedio_info['title'] = category_vedio_url_dict[vedio_url]
                    category_vedio_json_file = open(category_vedio_json_path, 'w')
                    json.dump(vedio_info, category_vedio_json_file, ensure_ascii=False, indent=0)
                    category_vedio_json_file.close()

                else:
                    error_vedio_url_list.append(vedio_url)

            for error_vedio_url in error_vedio_url_list:
                category_vedio_url_dict.pop(error_vedio_url)

            vedio_url_info_file = open(vedio_url_info_path, 'w')
            json.dump(category_vedio_url_dict, vedio_url_info_file, ensure_ascii=False, indent=0)
            vedio_url_info_file.close()


if __name__ == "__main__":
    bilibili_crawler = BilibiliCrawler()
    bilibili_crawler.run_crawler()

