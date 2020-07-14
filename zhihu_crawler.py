#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import crawler
import json
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class ZhiHuCrawler:
    zhihu_config = dict()
    zhihu_crawler = None
    article_url_list = list()

    def __init__(self):
       self.zhihu_crawler = crawler.Crawler()
       cur_path = os.path.split(os.path.realpath(__file__))[0]
       config_path = cur_path + os.path.sep + "config.json"
       json_file = open(config_path)
       self.zhihu_config = json.load(json_file)['zhihu']

    # 获取问题和问题网址
    def get_article_url_dict(self, category_url, question_number):
        self.zhihu_crawler.open_url(category_url)
        title_elements = self.zhihu_crawler.get_elements_by_xpath('//div[@itemprop="zhihu:question"]/a', question_number)
        article_url_info_dict = dict()
        for title_element in title_elements:
            url = title_element.get_attribute('href').split("/")
            new_url = url[0] + '//' + url[2] + '/' + url[3] + '/' + url[4]  # 这里直接获取问题下所有回答的网址，不需要再点击全部回答按钮了
            title = title_element.text
            if new_url.startswith('https://www.zhihu.com') and not article_url_info_dict.has_key(new_url):
                article_url_info_dict[new_url] = title

        return article_url_info_dict

    # 获取问题下面的回答
    def get_article_info(self, article_url):
        print article_url
        # 打开问题网址
        article_info = dict()
        self.zhihu_crawler.open_url(article_url)
        current_url = self.zhihu_crawler.get_current_url()
        if not current_url.startswith('https://www.zhihu.com'):
            return article_info
        # # 展开全部回答
        # try:
        #     self.zhihu_crawler.get_elements_by_xpath(
        #         '//div/a[@class="QuestionMainAction ViewAll-QuestionMainAction"]')[0].click()
        #     sleep(1)  # 防止一下拉到最下面导致页面没有继续加载
        # except Exception as e:
        #     print e
        # 获取回答数量
        answer_number_str = self.zhihu_crawler.get_elements_by_xpath('//h4[@class="List-headerText"]')
        answer_number_str = answer_number_str[0].text.split(' ')[0]
        print("该问题下的全部回答数量：%s" % answer_number_str)
        answer_number = int(answer_number_str.replace(",", ""))  # 将数字中的逗号剔除
        answer_number = min(int(answer_number), 10)  # 可以调整最多获取的问题数量
        # 获取回答内容，将所有文字汇总成一个字符串
        article_elements = self.zhihu_crawler.get_elements_by_xpath(
            '//span[@class="RichText ztext CopyrightRichText-richText"]', num_limit=answer_number)
        all_article_text = ''
        if len(article_elements) > 0:
            list_length = len(article_elements)
            print("爬取的回答数：%d" % list_length)
            for article_element in article_elements:
                try:
                    all_article_text += article_element.text
                except Exception as e:
                    print e
        # 将回答内容写入该问题的json文件
        article_info['all_article_text'] = all_article_text
        return article_info

    # 启动爬虫
    def run_crawler(self):
        # 创建文件夹zhihu
        corpus_dir = 'data/zhihu'
        os.mkdir(corpus_dir)
        # 获取爬取知乎的类别
        category_list = self.zhihu_config['category_list']
        for category in category_list:
            category_article_dir = os.path.join(corpus_dir, category['name'])
            os.mkdir(category_article_dir)  # 创建类别的文件夹
            article_url_info_path = os.path.join(category_article_dir, 'article_url_info.json')
            category_article_url_dict = dict()
            if os.path.exists(article_url_info_path):
                json_file = open(article_url_info_path)
                category_article_url_dict = json.load(json_file)
            if not category_article_url_dict:
                category_article_url_dict = self.get_article_url_dict(category['url'], int(category['question_number']))
            # 创建问题名和问题网址的文件 article_url_info.json
            article_url_info_file = open(article_url_info_path, 'w')
            json.dump(category_article_url_dict, article_url_info_file, ensure_ascii=False, indent=0)
            article_url_info_file.close()

            error_article_url_list = list()
            # 写各个问题回答的json文件
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
                # article_info为空的错误回答
                else:
                    error_article_url_list.append(article_url)

            for error_article_url in error_article_url_list:
                category_article_url_dict.pop(error_article_url)

            article_url_info_file = open(article_url_info_path, 'w')
            json.dump(category_article_url_dict, article_url_info_file, ensure_ascii=False, indent=0)
            article_url_info_file.close()


if __name__ == "__main__":
    zhihu_crawler = ZhiHuCrawler()
    zhihu_crawler.run_crawler()

