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


class Music163Crawler:
    music_config = dict()
    music_crawler = None
    song_url_list = list()

    def __init__(self):
       self.music_crawler = crawler.Crawler()
       cur_path = os.path.split(os.path.realpath(__file__))[0]
       config_path = cur_path + os.path.sep + "config.json"
       json_file = open(config_path)
       self.music_config = json.load(json_file)['music']

    def get_song_url_dict(self, category_url):
        self.music_crawler.open_url(category_url)
        self.music_crawler.switch_frame(frame="contentFrame")
        time.sleep(2)
        title_elements = self.music_crawler.get_elements_by_xpath('//div[@class="ttc"]/span/a')
        # print title_elements
        # exit()
        song_url_info_dict = dict()
        print len(title_elements)
        for title_element in title_elements:
            url = title_element.get_attribute('href')
            original_title = title_element.find_element_by_tag_name('b').text
            title_list = original_title.split('\n')
            if len(title_list) < 3:  # 可能歌名只有一个字
                title = title_list[0]
            else:
                title = title_list[0] + title_list[2]
            print url
            print title
            if url.startswith('https://music.163.com') and not song_url_info_dict.has_key(url):
                song_url_info_dict[url] = title

        return song_url_info_dict

    def get_song_info(self, song_url, page=10):
        song_info = dict()
        print song_url
        self.music_crawler.open_url(song_url)
        self.music_crawler.switch_frame(frame="contentFrame")
        current_url = self.music_crawler.get_current_url()
        if not current_url.startswith('https://music.163.com'):
            return song_info

        # 获取歌名
        title_element = self.music_crawler.get_elements_by_xpath('//em[@class="f-ff2"]')
        title = title_element[0].text
        if not title_element:
            title = "notitle"
        song_info["title"] = title
        print title

        # 获取评论内容
        comments_text = ''
        next_page_button = self.music_crawler.get_element_by_text('下一页')
        for i in range(page-1):
            comments_elements = self.music_crawler.get_elements_by_xpath('//div[@class="cnt f-brk"]')
            # 如果该歌曲没有评论，直接返回
            if not comments_elements:
                song_info["comments"] = comments_text
                return song_info
            for comments_element in comments_elements:
                comment = comments_element.text.split("：")[1]
                # print comment
                comments_text += comment
            self.music_crawler.js_click_element(next_page_button)
        song_info["comments"] = comments_text
        return song_info

    def run_crawler(self):
        corpus_dir = 'data/music'
        mkdir(corpus_dir)

        category_list = self.music_config['category_list']
        for category in category_list:
            category_song_dir = os.path.join(corpus_dir, category['name'])
            mkdir(category_song_dir)
            song_url_info_path = os.path.join(category_song_dir, 'song_url_info.json')
            category_song_url_dict = dict()
            if os.path.exists(song_url_info_path):
                json_file = open(song_url_info_path)
                category_song_url_dict = json.load(json_file)

            if not category_song_url_dict:
                category_song_url_dict = self.get_song_url_dict(category['url'])

            song_url_info_file = open(song_url_info_path, 'w')
            json.dump(category_song_url_dict, song_url_info_file, ensure_ascii=False, indent=0)
            song_url_info_file.close()

            error_song_url_list = list()
            for song_url in category_song_url_dict:
                category_song_json_name = song_url.split('?')[1] + '.json'
                category_song_json_path = os.path.join(category_song_dir, category_song_json_name)
                if os.path.exists(category_song_json_path):
                    continue
                # 每首爬取10页评论
                song_info = self.get_song_info(song_url, page=10)
                if song_info:
                    song_info['url'] = song_url
                    song_info['title'] = category_song_url_dict[song_url]
                    category_song_json_file = open(category_song_json_path, 'w')
                    json.dump(song_info, category_song_json_file, ensure_ascii=False, indent=0)
                    category_song_json_file.close()

                else:
                    error_song_url_list.append(song_url)

            for error_song_url in error_song_url_list:
                category_song_url_dict.pop(error_song_url)

            song_url_info_file = open(song_url_info_path, 'w')
            json.dump(category_song_url_dict, song_url_info_file, ensure_ascii=False, indent=0)
            song_url_info_file.close()


if __name__ == "__main__":
    music_163_crawler = Music163Crawler()
    music_163_crawler.run_crawler()

