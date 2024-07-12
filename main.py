#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jerry'

import datetime
from tkinter import *
from seckill.seckill_taobao import ChromeDrive


def run_killer(txt, txt2, option, link=None):
    seckill_time = txt.get()
    password = str(txt2.get())
    option_value = option.get()
    link_value = link.get() if link else ''
    print(seckill_time, password, option_value, link_value)
    # Adjust this part to handle the link if necessary
    if option_value == '1':
        ChromeDrive(seckill_time=seckill_time, password=password).sec_kill()
    elif option_value == '2':
        ChromeDrive(seckill_time=seckill_time, password=password, link=link_value).AllKill()


def on_option_change(option, lbl_link, link_entry):
    if option.get() == '2':
        lbl_link.grid(column=0, row=3, padx=10, pady=10, sticky=E)
        link_entry.grid(column=1, row=3, padx=10, pady=10)
    else:
        lbl_link.grid_forget()
        link_entry.grid_forget()


def main():
    win = Tk()
    win.title('小熊秒杀助手')

    lbl = Label(win, text="开抢时间：", width=10, height=2, bg='#f0f0f0', font=('Arial', 12))
    lbl.grid(column=0, row=0, padx=10, pady=10, sticky=E)
    start_time = StringVar()
    txt = Entry(win, textvariable=start_time, width=25, font=('Arial', 12))
    txt.grid(column=1, row=0, padx=10, pady=10)
    start_time.set(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    lbl2 = Label(win, text="支付密码：", width=10, height=2, bg='#f0f0f0', font=('Arial', 12))
    lbl2.grid(column=0, row=1, padx=10, pady=10, sticky=E)
    txt2 = Entry(win, width=25, show='*', font=('Arial', 12))
    txt2.grid(column=1, row=1, padx=10, pady=10)

    option = StringVar()
    option.set('1')

    lbl3 = Label(win, text="选项：", width=10, height=2, bg='#f0f0f0', font=('Arial', 12))
    lbl3.grid(column=0, row=2, padx=10, pady=10, sticky=E)

    lbl_link = Label(win, text="抢购链接：", width=10, height=2, bg='#f0f0f0', font=('Arial', 12))
    link_entry = Entry(win, width=25, font=('Arial', 12))
    # Initially hidden, will be shown when option 2 is selected

    r1 = Radiobutton(win, text='选项1', variable=option, value='1', bg='#f0f0f0', font=('Arial', 12),
                     command=lambda: on_option_change(option, lbl_link, link_entry))
    r1.grid(column=1, row=2, sticky=W, padx=10, pady=5)
    r2 = Radiobutton(win, text='选项2', variable=option, value='2', bg='#f0f0f0', font=('Arial', 12),
                     command=lambda: on_option_change(option, lbl_link, link_entry))
    r2.grid(column=1, row=2, sticky=W, padx=100, pady=5)

    b1 = Button(win, text='开始',
                command=lambda: run_killer(txt, txt2, option, link_entry if option.get() == '2' else None))
    b1.config(font='Helvetica -12 bold', bg='#ff5c5c', fg='white', relief='raised', width=10, height=2)
    b1.grid(column=0, row=4, columnspan=2, pady=20)
    win.resizable(width=False, height=False)

    instructions = [
        '使用说明:',
        '1、安装chrome浏览器以及chromeDriver',
        '2、如果选择SecKill，则抢购前要清空购物车，然后把要抢的东西加入购物车，如果选择AnyKill, 则需要填写想要购买的商品的链接',
        '3、开抢时间必须是 %Y-%m-%d %H:%M:%S 形式，如2020-12-29 12:10:15',
        '4、输入开抢时间和支付密码后点开始，程序会控制浏览器打开淘宝登陆页',
        '5、扫码登陆后，程序会自动刷新购物车页面，到点会完成抢购动作',
        '6、本项目仅供交流学习使用，请勿用于其它任何商业用途',
        '7、如果想手动付款，输入开抢时间后不用输入支付密码，直接点开始就可以了'
    ]

    txt0 = Label(win, text=instructions[0], width=10, height=2, bg='#f0f0f0', font=('Arial', 12, 'bold'))
    txt0.grid(column=0, row=5, padx=10, pady=5, columnspan=2, sticky=W)

    for i, instruction in enumerate(instructions[1:], start=6):
        lbl_instruction = Label(win, text=instruction, bg='#f0f0f0', font=('Arial', 10), wraplength=450, justify=LEFT)
        lbl_instruction.grid(column=0, row=i, padx=10, pady=2, columnspan=2, sticky=W)

    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    screenwidth = win.winfo_screenwidth()
    screenheight = win.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    win.geometry(alignstr)

    win.mainloop()


if __name__ == '__main__':
    main()
