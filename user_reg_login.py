﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import re
import urllib.parse
import urllib.request
import random, json
import sys
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import socket
#获取本机电脑名
myname = socket.getfqdn(socket.gethostname(  ))
#获取本机ip
myaddr = socket.gethostbyname(myname)
print( myname)
print (myaddr,type(myaddr))


def check_user_name(user_name):
    '''
    函数功能：校验用户名是否合法
    函数参数：
    user_name 待校验的用户名
    返回值：校验通过返回0，校验失败返回非零（格式错误返回1，用户名已存在返回2）
    '''
    # [a-zA-Z0-9_]{6, 15}
    if not re.match("^[a-zA-Z0-9_]{6,15}$", user_name):
        return 1

    # 连接数据库，conn为Connection对象
    conn = pymysql.connect("localhost", "mx12", "123456", "mydb")

    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            cur.execute("select uname from test where uname=%s", (user_name, ))
            # 通过游标获取执行结果
            rows = cur.fetchone()
    finally:
        # 关闭数据库连接
        conn.close()  

    if rows:
        return 2

    return 0


def check_uname_pwd(user_name, password):
    '''
    函数功能：校验用户名和密码是否合法
    函数参数：
    user_name 待校验的用户名
    password 待校验的密码
    返回值：校验通过返回0，校验失败返回1
    '''
    # 连接数据库，conn为Connection对象
    conn = pymysql.connect("localhost", "mx12", "123456", "mydb")

    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            cur.execute("select uname from test where uname=%s and passwd=password(%s)", (user_name, password))
            # 通过游标获取执行结果
            rows = cur.fetchone()
    finally:
        # 关闭数据库连接
        conn.close()  

    if rows:
        return 0

    return 1    


def check_password(password):
    '''
    函数功能：校验用户密码是否合法
    函数参数：
    password 待校验的密码
    返回值：校验通过返回0，校验错误返回非零（密码太长或太短返回1，密码安全强度太低返回2）
    '''
    if re.match("^[0-9]{1}([a-zA-Z0-9]|[._]){6,15}$", password):
        return 0
    elif re.match("^[0-9]|[a-zA-Z]{6,15}$", password):
        return 2
    else:
        return 1


def check_phone(phone):
    '''
    函数功能：校验手机号格式是否合法
    函数参数：
    phone 待校验的手机号
    返回值：校验通过返回0，校验错误返回1
    '''

    if re.match("^1\d{10}$", phone):
        return 0

    return 1


def send_sms_code(phone):
    '''
    函数功能：发送短信验证码（6位随机数字）
    函数参数：
    phone 接收短信验证码的手机号
    返回值：发送成功返回验证码，失败返回False
    '''
    verify_code = str(random.randint(100000, 999999))

    try:
        url = "http://v.juhe.cn/sms/send"
        params = {
            "mobile": phone,  # 接受短信的用户手机号码
            "tpl_id": "181072",  # 您申请的短信模板ID，根据实际情况修改
            "tpl_value": "#code#=%s" % verify_code,  # 您设置的模板变量，根据实际情况修改
            "key": "4573a1de4d447819432ad57487e27b80",  # 应用APPKEY(应用详细页查询)
        }
        params = urllib.parse.urlencode(params).encode()

        f = urllib.request.urlopen(url, params)
        content = f.read()
        res = json.loads(content)

        if res and res['error_code'] == 0:
            return verify_code
        else:
            return False
    except:
        return False


def send_email_code():
    '''
    函数功能：发送邮箱验证码（6位随机数字）
    函数参数：
    email 接收验证码的邮箱
    返回值：发送成功返回验证码，失败返回False
    '''
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "xg@itmaxub.cn"  # 用户名
    mail_pass = "igfixexvdnxpdhia"  # 口令
    sender = 'xg@itmaxub.cn'
    receivers = ['xmg@itmaxub.cn']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    verify_code = str(random.randint(100000, 999999))
    message = MIMEText(verify_code, 'plain', 'utf-8')
    subject = "验证码"
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        print("邮件发送成功")
        k=1
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")
        k=0

    if k==1:
        return verify_code
    else:
        return False

def user_reg(uname, password, phone, email):
    '''
    函数功能：将用户注册信息写入数据库
    函数描述：
    uname 用户名
    password 密码
    phone 手机号
    email 邮箱
    返回值：成功返回True，失败返回False
    '''
    # 连接数据库，conn为Connection对象
    conn = pymysql.connect("localhost", "mx12", "123456", "mydb")

    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            cur.execute("insert into test (uname, passwd, phone, email) values (%s, password(%s), %s, %s)", (uname, password, phone, email))
            r = cur.rowcount
            conn.commit()
    finally:
        # 关闭数据库连接
        conn.close()      

    return bool(r)

def reg_main():
    while True:
        user_name = input("请输入用户名（只能包含英文字母、数字或下划线，最短6位，最长15位）：")

        ret = check_user_name(user_name)

        if ret == 0:
            break
        elif ret == 1:
            print("用户名格式错误，请重新输入！")
        elif ret == 2:
            print("用户名已存在，请重新输入！")

    while True:
        while True:
            password = input("请输入密码（只能包含英文字母、数字或下划线或点号等，最短6位，最长15位）：")

            ret = check_password(password)

            if ret == 0:
                break
            elif ret == 1:
                print("密码不符合长度要求，请重新输入！")
            elif ret == 2:
                print("密码太简单，请重新输入！")

        confirm_pass = input("请再次输入密码：")

        if password == confirm_pass:
            break
        else:
            print("两次输入的密码不一致，请重新输入！")


    while True:
        phone = input("请输入手机号：")

        if check_phone(phone):
            print("手机号输入错误，请重新输入！")
        else:
            break

    # verify_code = send_sms_code(phone)

    # if verify_code:
    #     print("短信验证码已发送！")
    # else:
    #     print("短信验证码发送失败，请检查网络连接或联系软件开发商！")
    #     sys.exit(1)

    # while True:
    #     verify_code2 = input("请输入短信验证码：")

    #     if verify_code2 != verify_code:
    #         print("短信验证码输入错误，请重新输入！")
    #     else:
    #         break
    while True:
        email = input("请输入邮箱：")
        if re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$',email):  
            #if re.match(r'[0-9a-zA-Z_]{0,19}@163.com',text):  
            print('你的邮箱输入正确') 
            break 
        else:  
            print('请重新输入的你的邮箱')
    email_code1=send_email_code()
    if email_code1:
        print("邮箱验证码已发送！")
    else:
        print("邮箱验证码发送失败，请检查网络连接！")
        sys.exit(1)
    while True:
        email1=input("请输入你收到的邮箱验证码：")
        if email_code1!=email1:
            print('验证码输入错误')
        else:
            break

   
    if user_reg(user_name, password, phone, email):
        print("注册成功！")
    else:
        print("注册失败！")


def login_main():
    '''
    函数功能：用户登录验证
    函数参数：无
    返回值：登录验证成功返回用户名，失败返回False
    '''
    while True:
        user_name = input("\n用户名：")
        ret = check_user_name(user_name)
        if ret == 0:
            print("用户名不存在，请重新输入！")
        elif ret == 1:
            print("用户名格式错误，请重新输入！")
        else:
            break
        
    while True:
        password = input("\n密码：")
        ret = check_password(password)
        if ret == 0:
            break
        else:
            print("密码格式错误，请重新输入！")
    
    if check_uname_pwd(user_name, password):
        return False
    return user_name



def user_center(user_name):
    print("%s，欢迎你使用本系统！" % user_name)

    while True:
        print("\n操作提示：")
        print("1：商品入库存")
        print("2：盘点库存")
        print("3：查看销售额")
    # print("4：修改个人密码")
        print("0：退出")
        op = input("\n>：")

        if op == "0":
            print("感谢你的使用，下次再见！")
            sys.exit(2)
        elif op == "1":
            insert_db()
           
        elif op == "2":
            select_knc()
           
        elif op == "3":
            update_xiaosh()
           
        
        else:
            print("输入错误，请重新输入！")


    










