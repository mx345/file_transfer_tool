#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket,json
import sys
import os
import hashlib
import time

conn=json.load(open(r"C:\Users\Administrator\Desktop\kucun\recv_tool\client_conn.json"))
sock = socket.socket()
sock.connect((conn["app_server_ip"],conn["app_server_port"]))

dat=conn["passwd"]
sht=0  
def get_file_md5():
    '''
    函数功能：给密码加密
    返回值：返回一个加密后的MD5值
    '''
    global dat
    m = hashlib.md5()          
    m.update(dat.encode())
    return m.hexdigest().upper()

def get_file_md5n(file_path1):
    m = hashlib.md5()
    '''
    函数功能：给文件夹加密
    返回值：返回一个加密后的MD5值
    '''
    with open(file_path1, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break    
            m.update(data)
    
    return m.hexdigest().upper()

def reg_request():
    '''
    函数功能：给服务器发出注册请求
    返回值：为0 
    表示注册成功，否则注册失败
    '''
   
    file_name={
	"op": 2,
	"args": 
		{
			"uname": "maxun45",
			"passwd": "",  
			"phone": "17371290606", 
			"email": "xg@itmaxub.cn" 
		}
    }

    file_name["args"]["passwd"]=get_file_md5()
    
    head = json.dumps(file_name).encode()
    print(head)
    file_len = "{:<15}".format(len(head)).encode()
    print(file_len)
    sock.send(file_len)
    sock.send(head)

    data_len = sock.recv(15).decode().rstrip()
    print(data_len)
    if len(data_len) > 0:
        data_len = int(data_len)
        recv_size = 0
        json_data = b""
        while recv_size < data_len:
            tmp = sock.recv(data_len - recv_size)
            if len(tmp) == 0:
                break
            json_data += tmp
            recv_size += len(tmp)
        json_data = json_data.decode()
        print(json_data)
        req = json.loads(json_data)
        if req["error_code"] == 1:
            print("注册失败")
            return 1
        else:
            print("注册成功")
            return 0
        
def login_request():
    '''
    函数功能：给服务器发出登录请求
    返回值：为0 
    表示登录成功，否则登录失败
    '''
    # global conn
    # sock = socket.socket()
    # sock.connect((conn["app_server_ip"],conn["app_server_port"]))
    file_name={
	"op": 1,
	"args": 
		{
			"uname": "maxun45",
			"passwd": "",  
		}
    }
    file_name["args"]["passwd"]=get_file_md5()
    haed = json.dumps(file_name).encode()
    file_len = "{:<15}".format(len(haed)).encode()
    sock.send(file_len)
    sock.send(haed)
    data_len = sock.recv(15).decode().rstrip()
    if len(data_len) > 0:
        data_len = int(data_len)
        recv_size = 0
        json_data = b""
        while recv_size < data_len:
            tmp = sock.recv(data_len - recv_size)
            if len(tmp) == 0:
                break
            json_data += tmp
            recv_size += len(tmp)
        json_data = json_data.decode()
        req = json.loads(json_data)
        if req["error_code"] == 1:
            print("登录失败")
            return 1
        else:
            print("登录成功")
            return 0
           
def verify_request():
    '''
    函数功能：给服务器发出校验用户请求
    返回值：为0 
    表示校验用户已存在，否则就不存在
    '''
    file_name={ 
	"op": 3,
	"args": 
		{
			"uname": "maxun45"
		}

    }

    head=json.dumps(file_name).encode()
    print(head)
    file_len = "{:<15}".format(len(head)).encode()
    sock.send(file_len)
    sock.send(head)
    data_len = sock.recv(15).decode().rstrip()
    if len(data_len) > 0:
        data_len = int(data_len)
        recv_size = 0
        json_data = b""
        while recv_size < data_len:
            tmp = sock.recv(data_len - recv_size)
            if len(tmp) == 0:
                break
            json_data += tmp
            recv_size += len(tmp)
        json_data = json_data.decode()
        req = dict(eval(json_data))
        if req["error_code"] == 1:
            print("用户已存在")
            return 0
        else:
            print("用户不存在")
            return 1
def save_file(recv_fiile1,file_size):
    '''
    函数功能：将接受到的数据写入文件中
    计算出拷贝大小、进度和剩余大小
    '''
    v=506000
    try:

        os.makedirs(os.path.dirname(recv_fiile1),exist_ok=True)
        print("\n正在接收文件 %s，请稍候......" % recv_fiile1)
    except:
        print("新文件创建成功")
    f = open(recv_fiile1, "wb")
    recv_size = 0
    while recv_size < file_size:
        file_data = sock.recv(file_size - recv_size)
        if len(file_data) == 0:
            
            break
        f.write(file_data)
        recv_size += len(file_data)
       
        print("\r拷贝进度为:{}%，总大小为{}Bytes,还剩余大小{}Bytes,剩余时间{}分钟" .format(int(recv_size * 100 / file_size),file_size,\
            (file_size - recv_size),((file_size - recv_size)/v/60)),end="")
        # k=md5_a(file_path,file_md5)
    f.close()
    # return recv_fiile1

def md5_a(file_path,file_md5):
    '''
    函数功能：校验服务器端发过来的MD5值我自己接收的文件的
    MD5值是否相同 不相同就返回1（接收失败）
    '''
    recv_file_md5 = get_file_md5n(file_path)

    if recv_file_md5 == file_md5:
        print("\n成功接收文件 %s" % file_path)
    else:
        print("\n接收文件 %s 失败（MD5校验不通过）" % file_path)
        return 1


def main():
    
        print("1.注册信息")
        print("2.登录信息")
        print("3.校验用户")
        req1=input(">>>")
        if req1=="1":
            re=reg_request()
            if re==0:
                print("注册成功")
                print("开始登陆了.....")
                long3=login_request()
            
                if long3==0:
                    recv_file()
                print("传输完毕")
                   
            else:
                print("注册失败")
        elif req1=="2" :
            long1=login_request()
            print("开始传输了.....")
            if long1==0:
                recv_file()
            else:
                print("登录失败")
             
        else:
            ve=verify_request()
            if ve==0:
                print("用户已存在,请进行登录")  
            else:
                print("用户不存在,请注册")
              
def recv_file():
    '''
    函数功能：接受服务器发来的数据，进行处理下载到本地
    '''
    path=r"E:\xu"
    start=time.time()
    while True:
        file_path = sock.recv(300).decode().rstrip()
        print(file_path)
        if len(file_path) == 0:
            break
        file_size = sock.recv(15).decode().rstrip()
        if len(file_size) == 0:
            break
        file_size1 = int(file_size)
        file_md5 = sock.recv(32).decode()
        # print(file_md5)
        if len(file_md5) == 0:
            break
            # 如果为空文件夹
        if file_size == -1:
            print("\n成功接收空文件夹 %s" % file_path)
            os.makedirs(file_path, exist_ok=True)
            continue
        start1=time.time()
        path_recv=os.path.join(path,file_path)
        save_file(path_recv,file_size1)
        k=md5_a(path_recv,file_md5)
        
        if k ==1:
            break
    try:
        end_t=time.time()
        t=end_t-start
        print("本次下载时间为%s s"%t)
        sceep=int(file_size1/(t))
        print("速度为%sBytes"%sceep)
    except ZeroDivisionError as e:
        print(e)
    except TypeError as e:
        print(e)
    finally:
        sock.close()

if __name__ == "__main__":
    main()

