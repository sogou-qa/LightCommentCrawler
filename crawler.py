#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time


class Crawler(object):
    crawler_brower = None

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # 不加载图片,加快访问速度
        options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大
        self.crawler_brower = webdriver.Chrome(executable_path='./chromedriver', options=options)
        # self.crawler_brower = webdriver.Chrome(options=options)
        self.crawler_brower.implicitly_wait(3)
        self.crawler_brower.maximize_window()  # 最大化窗口
        self.wait = WebDriverWait(self.crawler_brower, 10) #超时时长为10s

    def open_url(self, url):
        self.crawler_brower.get(url)
        self.crawler_brower.implicitly_wait(6)

    # Chrome长时间运行会内存溢出而崩溃，需要定时清理缓存
    def delete_cookies(self):
        self.crawler_brower.delete_all_cookies()

    # 网易云音乐网站使用动态网页技术，需要使用该方法才能爬取网页内容
    def switch_frame(self, frame='contentFrame'):
        self.crawler_brower.switch_to.frame(frame)

    def wait(self, wait_time):
        self.crawler_brower.implicitly_wait(wait_time)

    # 模拟向下滑动
    def swipe_down(self):
        self.crawler_brower.execute_script("window.scrollTo(0,0.7*document.body.clientHeight);")

    def get_elements_by_xpath(self, xpath, num_limit=0):
        element_set = set(self.crawler_brower.find_elements_by_xpath(xpath))
        while len(element_set) < num_limit:
            original_set_length = len(element_set)
            # 这里滑动两次，防止直接滑到最底部没有加载新的内容
            self.crawler_brower.execute_script("window.scrollTo(0,0.45*document.body.clientHeight);")
            time.sleep(0.5)
            self.crawler_brower.execute_script("window.scrollTo(0,document.body.clientHeight);")
            # self.swipe_down(1)
            time.sleep(1.5)
            element_set = element_set | set(self.crawler_brower.find_elements_by_xpath(xpath))
            current_set_length = len(element_set)
            # 判断下拉之后是否网页有新的内容加载，如果没有加载则取消下拉
            if original_set_length == current_set_length:
                break

        return list(element_set)

    def get_element_by_text(self, text):
        element = None
        try:
            element = self.crawler_brower.find_element_by_link_text(text)
        except NoSuchElementException as msg:
            print u"查找元素异常%s" % msg
        return element

    # 寻找父元素的子元素
    def get_child_element_by_xpath(self, father_element, xpath):
        return father_element.find_element_by_xpath(xpath)

    def click_element(self, element):
        if element:
            element.click()
            self.crawler_brower.implicitly_wait(10)

    def js_click_element(self, element):
        if element:
            self.crawler_brower.execute_script("arguments[0].click();", element)  # 运用js代码点击按钮
            self.crawler_brower.implicitly_wait(5)

    def get_current_url(self):
        return self.crawler_brower.current_url

    #登录淘宝，采用微博用户名，使用之前应该绑定
    def login_taobao(self, weibo_username, weibo_password):
        # 打开网页
        url = 'https://login.taobao.com/member/login.jhtml'
        self.crawler_brower.get(url)
        # 自适应等待，点击密码登录选项
        self.crawler_brower.implicitly_wait(30) #智能等待，直到网页加载完毕，最长等待时间为30s
        self.crawler_brower.find_element_by_xpath('//*[@class="forget-pwd J_Quick2Static"]').click()
        # 自适应等待，点击微博登录
        self.crawler_brower.implicitly_wait(30)
        self.crawler_brower.find_element_by_xpath('//*[@class="weibo-login"]').click()
        # 自适应等待，输入微博账号
        self.crawler_brower.implicitly_wait(30)
        self.crawler_brower.find_element_by_name('username').send_keys(weibo_username)
        # 自适应等待，输入微博密码
        self.crawler_brower.implicitly_wait(30)
        self.crawler_brower.find_element_by_name('password').send_keys(weibo_password)
        # 自适应等待，点击确认登录按钮
        self.crawler_brower.implicitly_wait(30)
        self.crawler_brower.find_element_by_xpath('//*[@class="btn_tip"]/a/span').click()
        # 直到获取到淘宝会员昵称才能确定是登录成功
        taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
        # 输出淘宝昵称
        print(taobao_name.text)

    # 登录微博
    def login_weibo(self, weibo_username, weibo_password):
        url = 'https://weibo.com'
        # 登录网页
        self.crawler_brower.get(url)
        self.crawler_brower.implicitly_wait(10)
        # 输入用户名
        self.crawler_brower.find_elements_by_xpath('//input[@id="loginname"]')[0].send_keys(weibo_username)
        self.crawler_brower.implicitly_wait(10)
        # 输入密码
        self.crawler_brower.find_elements_by_xpath('//input[@type="password"]')[0].send_keys(weibo_password)
        self.crawler_brower.implicitly_wait(10)
        # 点击登录
        self.crawler_brower.find_elements_by_xpath('//div[@class="info_list login_btn"]/a[@tabindex="6"]')[0].click()
        self.crawler_brower.implicitly_wait(10)

