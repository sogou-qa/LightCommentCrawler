# LightCommentCrawler
一个轻量级的评论爬虫程序

**声明**
本项目仅供感兴趣的小伙伴们一起交流学习使用，请勿应用于商业用途
头条、知乎爬虫因网站做了反爬虫限制，暂时无法使用，后续会进行优化

### 配置爬虫
- 电脑端安装Chrome浏览器
- 下载对应自己chrome版本的chromedriver,下载完毕后放到当前目录下，下载网址http://npm.taobao.org/mirrors/chromedriver/
- 创建data文件夹，用于存放爬取的数据

### 爬取数据
- 对于微博、微博热门、B站、网易云音乐的数据，执行对应脚本即可爬取数据
- 对于获取淘宝数据 需要配置账号密码，目前我们支持的方式是使用微博账号登陆淘宝，需要事先将自己的微博账号与淘宝账号绑定，然后将微博账号密码添加到taobao_crawler.py的以下位置：

’‘’
weibo_username = ""  # 默认: username
weibo_password = ""  # 默认：password
‘’‘

使用后请及时删除

爬取数据示例：

<img src="https://github.com/zuoshigang/LightCommentCrawler/blob/br/2.x/images/data_get.gif" alt="show" />
