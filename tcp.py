# -*-coding:UTF-8-*-
# ////////////////////////////////////////////////////////////////////
# //                          _ooOoo_                               //
# //                         o8888888o                              //
# //                         88" . "88                              //
# //                         (| ^_^ |)                              //
# //                         O\  =  /O                              //
# //                      ____/`---'\____                           //
# //                    .'  \\|     |//  `.                         //
# //                   /  \\|||  :  |||//  \                        //
# //                  /  _||||| -:- |||||-  \                       //
# //                  |   | \\\  -  /// |   |                       //
# //                  | \_|  ''\---/''  |   |                       //
# //                  \  .-\__  `-`  ___/-. /                       //
# //                ___`. .'  /--.--\  `. . ___                     //
# //              ."" '<  `.___\_<|>_/___.'  >'"".                  //
# //            | | :  `- \`.;`\ _ /`;.`/ - ` : | |                 //
# //            \  \ `-.   \_ __\ /__ _/   .-` /  /                 //
# //      ========`-.____`-.___\_____/___.-`____.-'========         //
# //                           `=---='                              //
# //      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        //
# //         佛祖保佑       永无BUG     永不修改                  //
# ////////////////////////////////////////////////////////////////////
import socket
import sys
import chardet
import fileread
import binascii
import threading
import time
import datetime
# ---------------------------------------------------------------------------------------------------------------------------------
default_encoding = 'utf-8'  # 全局 UTF-8
# -----------------------socket配置------------------------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket (AF_INET:IPv4, AF_INET6:IPv6) (SOCK_STREAM:面向流的TCP协议)
name = socket.gethostname()  # 获取ip
port = 8081  # 端口号
s.bind((name, port))  # 绑定本机IP和任意端口(>1024)
s.listen(5)  # 监听，等待连接的最大数目为5
# ----------------------------defaul--------------------------------------------
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
# ----------------------------start---------------------------------------------
print('Server is running...')


def TCP(sock, addr):  # TCP服务器端处理逻辑
    print('Accept new connection from %s:%s.' % addr)  # 接受新的连接请求
    while True:
        InitializeData = sock.recv(1024)  # 接受其数据
        resultone = chardet.detect(InitializeData)  # 识别数据类型
        if resultone['encoding'] == 'ISO-8859-1':  # 判断数据是否是16进制
            print "16进制"
        else:
            if InitializeData == '':  # tcp通信断开会发送空字符 ,接受退出
                break
            print "非16进制"
            continue
        RequestData = str(binascii.b2a_hex(InitializeData))  # 16转ASCII
        if RequestData[0:2] == '5a':  # 判断帧头1
            if RequestData[len(RequestData) - 2:len(RequestData)] == 'ee':  # 判断帧尾
                print "数据完整"
            else:
                print "缺包"
                continue
        else:
            print "非协议内容"
# ------------------------------------------------获取版本号----------------------------------------------------------
        if RequestData[0:4] == '5aa5' and RequestData[6:8] == '10':  # 判断获取版本号命令
            listdata = list(RequestData)  # 字符串数据转列表方便增添删改
            listdata[4] = '0'  # 修改命令
            listdata[5] = '9'
            listdata[6] = '9'
            listdata[7] = '0'
            listdata.insert(len(listdata) - 4, fileread.getver())  # 插入版本号
            checkdata = ''.join(listdata)  # 转字符串
            checkdata = fileread.getcheck(checkdata[6:20])  # 转效验码
            listdata[len(listdata) - 4] = checkdata[0]  # 添加效验码
            listdata[len(listdata) - 3] = checkdata[1]
            Verdata = ''.join(listdata)  # 最终整条完整命令转字符串发送
            print "发送版本号"
            sock.send(binascii.a2b_hex(Verdata))  # ASCII转byte流 hex格式发送
# ------------------------------------------------获取固件----------------------------------------------------------
        if RequestData[0:4] == '5aa5' and RequestData[6:8] == '20':  # 判断请求固件
            try:  # try防止丢包,如果未发送成功则中断,记录日志失败原因
                listdata = list(RequestData)
                listdata[4] = '0'
                listdata[5] = 'd'
                listdata[6] = 'a'
                listdata[7] = '0'
                listdata.insert(len(listdata) - 4, '01')  # 插入确定下载命令,注意数据大小为一个整体插入
                listdata.insert(len(listdata) - 4, fileread.getfilesize())  # 获取数据大小
                checkdata = ''.join(listdata)
                checkdata = fileread.getcheck(checkdata[6:28])
                listdata[len(listdata) - 4] = checkdata[0]  # 效验码两位
                listdata[len(listdata) - 3] = checkdata[1]
                Firdata = ''.join(listdata)
                print "固件下载"
                sock.send(binascii.a2b_hex(Firdata))  # 发送下载命令
                time.sleep(4)
                sock.sendall(fileread.postfile())  # 发送固件
                time.sleep(7)
                Idnum = RequestData[0:18]  # 发送固件后记录版本号
            except:
                print "下载失败"
# ------------------------------------------------返回固件升级成功命令----------------------------------------------------------
        if RequestData[0:4] == '5aa5' and RequestData[6:8] == '30':  # 判断固件升级情况
            id = fileread.getshowid(RequestData)
            type = Idnum[16:18]
            datatime = datetime.datetime.now().strftime('%Y/%m/%d    %H:%M:%S')
            version = fileread.getver()
            try:
                fileread.writeinfo(id, type, version, datatime)  # 固件升级成功后记录信息 设备号 设备ID 升级版本 升级时间
            except:
                print "错误"
            try:
                listdata = list(Idnum)  # 固件升级成功后记录设备的信息用于确定固件升级成功
                listdata[4] = '0'
                listdata[5] = '9'
                listdata[6] = 'b'
                listdata[7] = '0'
                listdata.append('1')  # 添加升级成功命令
                listdata.append('1')
                checkdata = ''.join(listdata)
                checkdata = fileread.getcheck(checkdata[6:20])  # 获取效验码
                listdata.append(checkdata[0])
                listdata.append(checkdata[1])
                listdata.append('ee')
                print listdata
                Firdata = ''.join(listdata)
                print "固件升级成功"
                sock.send(binascii.a2b_hex(Firdata))
            except:
                print '未下载固件'
                continue

        print "已返回设备"
    print '关闭连接'
    sock.close()  # 关闭连接
    print('Connection from %s:%s closed.' % addr)
# --------------------------------------多线程---------------------------------------------------
def jonnyS(client, address):  # 线程处理
    try:
        # 设置超时时间
        client.settimeout(500)
        TCP(sock, addr)  # 处理连接
    except socket.timeout:
        print 'time out'
    client.close()
# --------------------------------------程序入口---------------------------------------------------
while True:
    sock, addr = s.accept()  # 接收一个新连接
    thread = threading.Thread(target=jonnyS, args=(sock, addr))
    thread.start()
