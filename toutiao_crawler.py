#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import crawler
import json
import os
import sys
from sogou_utils.file import mkdir

reload(sys)
sys.setdefaultencoding('utf8')


class TouTiaoCrawler:
    toutiao_config = dict()
    toutiao_crawler = None
    article_url_list = list()

    def __init__(self):
       self.toutiao_crawler = crawler.Crawler()
       cur_path = os.path.split(os.path.realpath(__file__))[0]
       config_path = cur_path + os.path.sep + "config.json"
       json_file = open(config_path)
       self.toutiao_config = json.load(json_file)['toutiao']

    def get_article_url_dict(self, category_url, article_number):
        self.toutiao_crawler.open_url(category_url)
        title_elements = self.toutiao_crawler.get_elements_by_xpath('//div[@class="title-box"]/a', article_number)
        article_url_info_dict = dict()
        for title_element in title_elements:
            url = title_element.get_attribute('href')
            title = title_element.text
            if url.startswith('https://www.toutiao.com') and not article_url_info_dict.has_key(url):
                article_url_info_dict[url] = title

        return article_url_info_dict

    def get_article_info(self, article_url):
        article_info = dict()
        self.toutiao_crawler.open_url(article_url)
        current_url = self.toutiao_crawler.get_current_url()
        if not current_url.startswith('https://www.toutiao.com'):
            return article_info

        article_elements = self.toutiao_crawler.get_elements_by_xpath('//div[@class="article-content"]')
        all_article_text = ''
        if len(article_elements) > 0:
            all_article_text = article_elements[0].text
        if len(all_article_text) < 10:
            return article_info

        article_info['all_article_text'] = all_article_text
        more_comment_btn = self.toutiao_crawler.get_element_by_text('查看更多评论')
        self.toutiao_crawler.click_element(more_comment_btn)
        comments_list = list()
        comments_elements = self.toutiao_crawler.get_elements_by_xpath('//div[@class="c-content"]/p')

        for comments_element in comments_elements:
            comments_list.append(comments_element.text)
        article_info['comments_list'] = comments_list
        return article_info

    def run_crawler(self):
        corpus_dir = 'data/toutiao'
        mkdir(corpus_dir)

        category_list = self.toutiao_config['category_list']
        for category in category_list:
            category_article_dir = os.path.join(corpus_dir, category['name'])
            mkdir(category_article_dir)
            article_url_info_path = os.path.join(category_article_dir, 'article_url_info.json')
            category_article_url_dict = dict()
            if os.path.exists(article_url_info_path):
                json_file = open(article_url_info_path)
                category_article_url_dict = json.load(json_file)

            if not category_article_url_dict:
                category_article_url_dict = self.get_article_url_dict(category['url'], int(category['article_number']))

            article_url_info_file = open(article_url_info_path, 'w')
            json.dump(category_article_url_dict, article_url_info_file, ensure_ascii=False, indent=0)
            article_url_info_file.close()

            error_article_url_list = list()
            for article_url in category_article_url_dict:
                category_article_json_name = article_url.split('/')[4] + '.json'
                category_article_json_path = os.path.join(category_article_dir, category_article_json_name)
                if os.path.exists(category_article_json_path):
                    continue
                article_info = self.get_article_info(article_url)
                if article_info:
                    article_info['url'] = article_url
                    article_info['title'] = category_article_url_dict[article_url]
                    category_article_json_file = open(category_article_json_path, 'w')
                    json.dump(article_info, category_article_json_file, ensure_ascii=False, indent=0)
                    category_article_json_file.close()

                else:
                    error_article_url_list.append(article_url)

            for error_article_url in error_article_url_list:
                category_article_url_dict.pop(error_article_url)

            article_url_info_file = open(article_url_info_path, 'w')
            json.dump(category_article_url_dict, article_url_info_file, ensure_ascii=False, indent=0)
            article_url_info_file.close()


if __name__ == "__main__":
    toutiao_crawler = TouTiaoCrawler()
    toutiao_crawler.run_crawler()

