#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import crawler
import json
import os
import sys
import time

reload(sys)
sys.setdefaultencoding('utf8')

class TaobaoCrawler:
    taobao_config = dict()
    taobao_crawler = None
    goods_url_list = list()

    def __init__(self):
        self.taobao_crawler = crawler.Crawler()
        cur_path = os.path.split(os.path.realpath(__file__))[0]
        config_path = cur_path + os.path.sep + "config.json"
        json_file = open(config_path)
        self.taobao_config = json.load(json_file)['taobao']
        # 登录淘宝，这里用微博用户名登录，需要首先在淘宝网页上进行绑定，使用之后请将自己的用户名密码删除
        weibo_username = ""  # 默认: username
        weibo_password = ""  # 默认：password
        self.taobao_crawler.login_taobao(weibo_username, weibo_password)

    # 获取商品网址
    def get_goods_url_dict(self, category_url):
        self.taobao_crawler.open_url(category_url)
        # 获取首页所有商品的url
        goods_elements = self.taobao_crawler.get_elements_by_xpath('//div[@class="row row-2 title"]/a')
        goods_url_list = []
        for goods_element in goods_elements:
            try:
                url = goods_element.get_attribute('href')
                if url not in goods_url_list:
                    goods_url_list.append(url)
            except Exception as e:
                print("fail getting this url", e)
        return goods_url_list

    # 获取问题下面的回答
    def get_goods_info(self, goods_url):
        print goods_url
        # 打开问题网址
        goods_info = dict()
        goods_info["comments"] = ''
        self.taobao_crawler.open_url(goods_url)
        comment_elements = []
        # 如果是天猫的商店：
        if goods_url.startswith("https://detail.tmall.com"):
            # 获取商品名称
            title = self.taobao_crawler.get_elements_by_xpath('//div[@class="tb-detail-hd"]/h1')[0]
            goods_info["title"] = title.text
            # 获取商品评论，只取首屏评论即可
            try:
                comments_item = self.taobao_crawler.get_elements_by_xpath('//div/ul/li/a[@data-index="1"]')[0]
                if comments_item.text == "规格参数":
                    comments_item = self.taobao_crawler.get_elements_by_xpath(
                        '//div/ul/li/a[@data-index="2"]')[0]
                self.taobao_crawler.js_click_element(comments_item)
                comment_elements = self.taobao_crawler.get_elements_by_xpath(
                    '//div[@class="tm-rate-content"]/div[@class="tm-rate-fulltxt"]')
            except Exception as e:
                print e
        # 如果是淘宝的商店
        elif goods_url.startswith("https://item.taobao.com"):
            title = self.taobao_crawler.get_elements_by_xpath('//div[@class="tb-title"]/h3')[0].text
            print title
            goods_info["title"] = title
            comments_item = self.taobao_crawler.get_elements_by_xpath('//div/ul/li/a[@data-index="1"]')[0]
            # print comments_item
            # self.taobao_crawler.click_element(comments_item)
            self.taobao_crawler.js_click_element(comments_item)
            # 获取商品评论，只取首屏评论即可
            comment_elements = self.taobao_crawler.get_elements_by_xpath(
                '//div[@class="J_KgRate_ReviewContent tb-tbcr-content "]')
        comments_number = len(comment_elements)
        print("共获取评论数量 %d 条" % comments_number)
        comments = ''
        # 如果没有获取到评论，则直接返回
        if comments_number == 0:
            goods_info["comments"] = comments
            return goods_info
        try:
            for comment_element in comment_elements:
                    comments += comment_element.text
            goods_info["comments"] = comments
        except Exception as e:
                print("fail getting the comment text", e)

        return goods_info

    # 启动爬虫
    def run_crawler(self):
        # 创建文件夹taobao
        corpus_dir = 'data/taobao'
        os.mkdir(corpus_dir)
        # 获取爬取taobao的类别
        category_list = self.taobao_config['category_list']
        for category in category_list:
            category_goods_dir = os.path.join(corpus_dir, category['name'])
            os.mkdir(category_goods_dir)  # 创建类别的文件夹
            goods_url_path = os.path.join(category_goods_dir, 'goods_url.json')
            category_goods_url_dict = dict()
            if os.path.exists(goods_url_path):
                json_file = open(goods_url_path)
                category_goods_url_dict = json.load(json_file)
            if not category_goods_url_dict:
                category_goods_url_dict["category"] = category["name"]
                category_goods_url_dict["url_list"] = self.get_goods_url_dict(category['url'])
            # 创建首页商品url的文件 goods_url.json
            goods_url_file = open(goods_url_path, 'w')
            json.dump(category_goods_url_dict, goods_url_file, ensure_ascii=False, indent=0)
            goods_url_file.close()

            error_goods_url_list = list()
            # 写各个商品的json文件，包含商品名称和评论
            for goods_url in category_goods_url_dict["url_list"]:
                category_goods_json_name = goods_url.split("?")[1].split('&')[0] + '.json'
                category_goods_json_path = os.path.join(category_goods_dir, category_goods_json_name)
                if os.path.exists(category_goods_json_path):
                    continue
                goods_info = self.get_goods_info(goods_url)
                if goods_info:
                    goods_info['url'] = goods_url
                    goods_json_file = open(category_goods_json_path, 'w')
                    json.dump(goods_info, goods_json_file, ensure_ascii=False, indent=0)
                    goods_json_file.close()
                    time.sleep(3)
                # goods_info为空的错误回答
                else:
                    error_goods_url_list.append(goods_url)

            for error_goods_url in error_goods_url_list:
                category_goods_url_dict["url_list"].pop(error_goods_url)

            goods_url_file = open(goods_url_path, 'w')
            json.dump(category_goods_url_dict, goods_url_file, ensure_ascii=False, indent=0)
            goods_url_file.close()


if __name__ == "__main__":
    taobao_crawler = TaobaoCrawler()
    taobao_crawler.run_crawler()

