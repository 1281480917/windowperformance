#! /usr/bin/env python
# -*- coding:utf-8 -*-


import logging
import time
import csv
import datetime
from selenium import webdriver
from conversions import conversions
from collections import OrderedDict
date = datetime.datetime.now().strftime('%Y%m%d%H%M')

# 生成文件名
filename = 'result/timing_{}.csv'.format(date)


def logging_config():
    # 配置Logging
    logging.getLogger('dicttoxml').setLevel(logging.WARNING)
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='log/get_timing_{}.log'.format(date),
        filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


class windowperformance():
    def __init__(self):
        self.base_url = 'https://192.168.19.250:1443/'
        driver = webdriver.Chrome(r'Tools/chromedriver.exe')
        driver.get(self.base_url)
        driver.find_element_by_id("txtUserID").send_keys('')
        driver.find_element_by_id('txtPwd').send_keys('')
        driver.find_element_by_id('btnLogin').click()
        time.sleep(5)
        logging.info("登录成功！")
        self.driver = driver

    def get_performance_timing(self, url):
        """UI 获取 Windows.performance.timing 时间戳

        :param url: 待处理的url地址
        """
        url = self.base_url + url
        # 进入指定页面, 获取 performance.timing 时间字典
        self.driver.get(url)
        timing = self.driver.execute_script(
            'return window.performance.timing;')
        getEntries = self.driver.execute_script(
            'return window.performance.getEntries();')
        browser = self.driver.get_log('browser')

        # 日志输出 timing 详细信息
        logging.info("页面性能指标详细信息: \n{}".format(timing))
        logging.info("页面资源加载详细信息: \n{}".format(getEntries))
        logging.info("页面控制台日志详细信息: \n{}".format(browser))
        return timing, getEntries

    def handle_data(self, name, timing, getEntries):
        """计算相关耗时参数"""
        timing_dict = OrderedDict()
        timing_dict[''] = name
        duration = 0
        for Entries in getEntries:
            if Entries['duration'] > duration:
                duration = Entries['duration']
        # 白屏时间
        # 白屏时间 = 页面开始展示的时间 - 开始请求时间
        timing_dict['白屏时间'] = (timing['domLoading'] -
                               timing['navigationStart']) / 1000
        # # 首屏时间=首屏内容渲染结束时间点-开始请求时间点
        timing_dict['首屏时间'] = duration / 1000
        # 可交互时间=用户可以正常进行事件输入时间点-开始请求时间点
        timing_dict['可交互时间'] = (timing['domInteractive'] -
                                timing['navigationStart']) / 1000
        # 【重要】页面加载完成的时间
        # 【原因】这几乎代表了用户等待页面可用的时间
        timing_dict['页面加载完成的时间'] = (
            timing['loadEventEnd'] - timing['navigationStart']) / 1000
        # 【重要】解析 DOM 树结构的时间
        # 【原因】反省下你的 DOM 树嵌套是不是太多了！
        timing_dict['解析 DOM 树结构的时间'] = (
            timing['domComplete'] - timing['responseEnd']) / 1000
        # 【重要】重定向的时间
        # 【原因】拒绝重定向！比如，http://example.com/ 就不该写成 http://example.com
        timing_dict['重定向的时间'] = (timing['redirectEnd'] -
                                 timing['redirectStart']) / 1000
        # DNS 缓存时间
        timing_dict['DNS 缓存时间'] = (
            timing['domainLookupStart'] - timing['fetchStart']) / 1000
        # 【重要】DNS 查询时间
        # 【原因】DNS 预加载做了么？页面内是不是使用了太多不同的域名导致域名查询的时间太长？
        # 可使用 HTML5 Prefetch 预查询 DNS
        timing_dict['DNS 查询时间'] = (
            timing['domainLookupEnd'] - timing['domainLookupStart']) / 1000
        # TCP 建立连接完成握手的时间
        timing_dict['TCP 建立连接完成握手的时间'] = (
            timing['connectEnd'] - timing['connectStart']) / 1000
        # 【重要】内容加载完成的时间
        # 【原因】页面内容经过 gzip 压缩了么，静态资源 css/js 等压缩了么？
        timing_dict['内容加载完成的时间'] = (
            timing['responseEnd'] - timing['requestStart']) / 1000
        # 响应时间
        timing_dict['响应时间'] = (timing['responseEnd'] -
                               timing['responseStart']) / 1000
        # 【重要】读取页面第一个字节的时间
        # 【原因】这可以理解为用户拿到你的资源占用的时间，加异地机房了么，加CDN 处理了么？加带宽了么？加 CPU 运算速度了么？
        # TTFB 即 Time To First Byte 的意思
        timing_dict['读取页面第一个字节的时间'] = (
            timing['responseStart'] - timing['navigationStart']) / 1000
        # 【重要】执行 onload 回调函数的时间
        # 【原因】是否太多不必要的操作都放到 onload 回调函数里执行了，考虑过延迟加载、按需加载的策略么？
        timing_dict['执行 onload 回调函数的时间'] = (
            timing['loadEventEnd'] - timing['loadEventStart']) / 1000
        # 卸载页面的时间
        timing_dict['卸载页面的时间'] = (
            timing['unloadEventEnd'] - timing['unloadEventStart']) / 1000
        return timing_dict

    def main(self, urls: dict):
        """主函数

        :param urls: {模块名：url}
        """

        logging.info("UI 获取 Windows.performance.timing 时间戳")

        with open(filename, 'a+', newline='') as csvfile:
            csv_write = csv.writer(csvfile)
            timing, getEntries = self.get_performance_timing('/Index')
            handletime = self.handle_data('', timing, getEntries)
            csv_write.writerow(handletime.keys())

            # 处理 url
            for name, url in urls.items():
                logging.info(" {} ".format(name).center(50, "*"))
                logging.info("解析url: {}".format(url))
                # 获取Windows.performance.timing 时间戳
                timing, getEntries = self.get_performance_timing(url)
                handletime = self.handle_data(
                    name, timing, getEntries)        # 处理timing时间
                csv_write.writerow(handletime.values())      # 写入 csv文件

    def __del__(self):
        # 关闭浏览器
        self.driver.quit()
        logging.info("关闭浏览器！")


if __name__ == "__main__":
    logging_config()
    url = conversions().conversions_to_dict()
   
    windowperformance().main(url)
