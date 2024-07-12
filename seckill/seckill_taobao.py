#!/usr/bin/env python3
# encoding=utf-8


import os
import json
import platform
from time import sleep
from random import choice
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

import seckill.settings as utils_settings
from utils.utils import get_useragent_data
from utils.utils import notify_user

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import tkinter as tk
from tkinter import ttk

# 抢购失败最大次数
max_retry_count = 30


def default_chrome_path():
    driver_dir = getattr(utils_settings, "DRIVER_DIR", None)
    if platform.system() == "Windows":
        if driver_dir:
            return os.path.abspath(os.path.join(driver_dir, "chromedriver.exe"))

        raise Exception("The chromedriver drive path attribute is not found.")
    else:
        if driver_dir:
            return os.path.abspath(os.path.join(driver_dir, "chromedriver"))

        raise Exception("The chromedriver drive path attribute is not found.")


def parse_sku_wrap(lines):
    lines = lines.split("\n")
    result = {}
    # 初始化变量
    key = None
    i = 0
    while i < len(lines):
        item = lines[i]
        if item == '数量':
            break
        if item == '：':
            i += 1
            continue
        elif i + 1 < len(lines) and lines[i + 1] == '：':
            # 当前item是key
            key = item
            result[key] = []  # 为key初始化一个空列表
            i += 2  # 跳过下一个冒号
        else:
            # 当前item是value
            if key is not None:
                result[key].append(item)
            i += 1
    return result


class ChromeDrive:

    def __init__(self, chrome_path=default_chrome_path(), seckill_time=None, password=None, link=None):
        self.chrome_path = chrome_path
        self.seckill_time = seckill_time
        self.seckill_time_obj = datetime.strptime(self.seckill_time, '%Y-%m-%d %H:%M:%S')
        self.password = password
        self.link = link
        self.selected_options = None
        #self.driver = webdriver.Chrome(executable_path=self.chrome_path)

    def start_driver(self):
        try:
            driver = self.find_chromedriver()
            if driver is None:
                raise WebDriverException("Unable to find chromedriver.")
        except WebDriverException as e:
            print(f"Unable to find chromedriver: {e}. Please check the drive path.")
            return None
        else:
            return driver

    def find_chromedriver(self):
        try:
            driver = webdriver.Chrome()

        except WebDriverException:
            try:
                driver = webdriver.Chrome(executable_path=self.chrome_path, chrome_options=self.build_chrome_options())

            except WebDriverException:
                raise
        return driver

    def build_chrome_options(self):
        """配置启动项"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.accept_untrusted_certs = True
        chrome_options.assume_untrusted_cert_issuer = True
        arguments = ['--no-sandbox', '--disable-impl-side-painting', '--disable-setuid-sandbox',
                     '--disable-seccomp-filter-sandbox',
                     '--disable-breakpad', '--disable-client-side-phishing-detection', '--disable-cast',
                     '--disable-cast-streaming-hw-encoding', '--disable-cloud-import', '--disable-popup-blocking',
                     '--ignore-certificate-errors', '--disable-session-crashed-bubble', '--disable-ipv6',
                     '--allow-http-screen-capture', '--start-maximized']
        for arg in arguments:
            chrome_options.add_argument(arg)
        chrome_options.add_argument(f'--user-agent={choice(get_useragent_data())}')
        return chrome_options

    def login(self, login_url: str = "https://www.taobao.com"):
        if login_url:
            self.driver = self.start_driver()
        else:
            print("Please input the login url.")
            raise Exception("Please input the login url.")

        while True:
            self.driver.get(login_url)
            try:
                if self.driver.find_element(By.LINK_TEXT, "亲，请登录"):
                    print("没登录，开始点击登录按钮...")
                    self.driver.find_element(By.LINK_TEXT, "亲，请登录").click()
                    print("请在30s内扫码登陆!!")
                    sleep(30)
                    if self.driver.find_element(By.XPATH, '//*[@id="J_SiteNavMytaobao"]/div[1]/a/span'):
                        print("登陆成功")
                        break
                    else:
                        print("登陆失败, 刷新重试, 请尽快登陆!!!")
                        continue
            except Exception as e:
                print(str(e))
                continue

    def keep_wait(self):
        self.login()
        print("等待到点抢购...")
        while True:
            current_time = datetime.now()
            if (self.seckill_time_obj - current_time).seconds > 180:
                self.driver.get("https://cart.taobao.com/cart.htm")
                print("每分钟刷新一次界面，防止登录超时...")
                sleep(60)
            else:
                self.get_cookie()
                print("抢购时间点将近，停止自动刷新，准备进入抢购阶段...")
                break

    def sec_kill(self):
        self.keep_wait()
        self.driver.get("https://cart.taobao.com/cart.htm")
        sleep(1)

        if self.driver.find_element(By.ID, "J_SelectAll1"):
            self.driver.find_element(By.ID, "J_SelectAll1").click()
            print("已经选中全部商品！！！")

        submit_succ = False
        retry_count = 0

        while True:
            now = datetime.now()
            if now >= self.seckill_time_obj:
                print(f"开始抢购, 尝试次数： {str(retry_count)}")
                if submit_succ:
                    print("订单已经提交成功，无需继续抢购...")
                    break
                if retry_count > max_retry_count:
                    print("重试抢购次数达到上限，放弃重试...")
                    break

                retry_count += 1

                try:

                    if self.driver.find_element(By.ID, "J_Go"):
                        self.driver.find_element(By.ID, "J_Go").click()
                        print("已经点击结算按钮...")
                        click_submit_times = 0
                        while True:
                            try:
                                if click_submit_times < 10:
                                    self.driver.find_element(By.LINK_TEXT, '提交订单').click()
                                    print("已经点击提交订单按钮")
                                    submit_succ = True
                                    break
                                else:
                                    print("提交订单失败...")
                            except Exception as e:

                                print("没发现提交按钮, 页面未加载, 重试...")
                                click_submit_times = click_submit_times + 1
                                sleep(0.1)
                except Exception as e:
                    print(e)
                    print("临时写的脚本, 可能出了点问题!!!")

            sleep(0.1)
        if submit_succ:
            if self.password:
                self.pay()

    def AllKill(self):
        self.login()
        self.configure_options()
        print(self.selected_options)
        while not self.monitor_options():
            self.driver.refresh()
            sleep(1)
        self.buy_on_page()

    def buy_on_page(self):
        for option, value in self.selected_options.items():
            if option == '数量':
                try:
                    quantity_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'Operation--countValue--3VF_tPH'))
                    )
                    quantity_input.clear()
                    quantity_input.send_keys(value)
                except Exception as e:
                    print(f"Error setting quantity: {e}")
                continue

            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//span[@title='{value}']"))
                )
                parent_element = element.find_element(By.XPATH, "..")
                if "SkuContent--isSelected" not in parent_element.get_attribute("class"):
                    element.click()
            except Exception as e:
                print(f"Error clicking on option {option} with value {value}: {e}")

        try:
            buy_now_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button/span[text()='立即购买']"))
            )
            buy_now_button.click()
        except Exception as e:
            print(f"Error clicking on the '立即购买' button: {e}")

        click_submit_times = 0
        while True:
            try:
                if click_submit_times < 10:
                    self.driver.find_element(By.LINK_TEXT, '提交订单').click()
                    print("已经点击提交订单按钮")
                    submit_succ = True
                    break
                else:
                    print("提交订单失败...")
            except Exception as e:
                print("没发现提交按钮, 页面未加载, 重试...")
                click_submit_times = click_submit_times + 1
                sleep(0.1)
            sleep(0.1)
        if submit_succ:
            if self.password:
                self.pay()

    def monitor_options(self):
        all_available = True
        for option, value in self.selected_options.items():
            if option == '数量':
                continue

            option_elements = self.driver.find_elements(By.XPATH,
                                                        f"//span[text()='{option}']/../following-sibling::div//span[@title='{value}']")
            if not option_elements:
                print(f"Option {option} with value {value} not found.")
                all_available = False
                break
            option_element = option_elements[0]
            parent_class = option_element.find_element(By.XPATH, "..").get_attribute("class")
            if 'isDisabled' in parent_class:
                print(f"Option {option} with value {value} is disabled.")
                all_available = False
                break
        return all_available

    def configure_options(self):
        def on_submit():
            selected_options = {key: vars[key].get() for key in vars}
            quantity = quantity_var.get()
            print("选择的配置: ", selected_options)
            print(f"填写的数量: {quantity}")
            self.selected_options = selected_options
            self.selected_options['数量'] = quantity
            config_window.destroy()

        self.driver.get(self.link)
        if self.driver.find_element(By.ID, "skuWrap"):
            skuWrap_text = self.driver.find_element(By.ID, "skuWrap").text
            options = parse_sku_wrap(skuWrap_text)

        config_window = tk.Toplevel()
        config_window.title("选择配置")

        vars = {}
        row = 0
        for option, values in options.items():
            if values:
                var = tk.StringVar()
                ttk.Label(config_window, text=f"{option}:").grid(column=0, row=row, padx=10, pady=5)
                combobox = ttk.Combobox(config_window, textvariable=var)
                combobox['values'] = values
                combobox.grid(column=1, row=row, padx=10, pady=5)
                vars[option] = var
                row += 1

        quantity_var = tk.StringVar()
        ttk.Label(config_window, text="数量:").grid(column=0, row=row, padx=10, pady=5)
        quantity_entry = ttk.Entry(config_window, textvariable=quantity_var)
        quantity_entry.grid(column=1, row=row, padx=10, pady=5)

        submit_button = ttk.Button(config_window, text="提交", command=on_submit)
        submit_button.grid(column=1, row=row + 1, padx=10, pady=10)

        config_window.grab_set()
        config_window.wait_window()

        return self.selected_options

    def pay(self):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'sixDigitPassword')))
            element.send_keys(self.password)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'J_authSubmit'))).click()
            notify_user(msg="付款成功")
        except:
            notify_user(msg="付款失败")
        finally:
            sleep(60)
            self.driver.quit()

    def get_cookie(self):
        cookies = self.driver.get_cookies()
        cookie_json = json.dumps(cookies)
        with open('./cookies.txt', 'w', encoding='utf-8') as f:
            f.write(cookie_json)
