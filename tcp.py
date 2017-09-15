#-*-coding:UTF-8-*-
import socket
import sys
import chardet,fileread,binascii
import threading,time


sjdx=fileread.getfilesize()
changenum=''
default_encoding = 'utf-8'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket (AF_INET:IPv4, AF_INET6:IPv6) (SOCK_STREAM:面向流的TCP协议)
name = socket.gethostname()
port = 8081
s.bind((name, port))  # 绑定本机IP和任意端口(>1024)
s.listen(5) # 监听，等待连接的最大数目为5
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

print('Server is running...')

def TCP(sock, addr):                                          # TCP服务器端处理逻辑

    print('Accept new connection from %s:%s.' % addr)         # 接受新的连接请求


    while True:

        InitializeData = sock.recv(1024)                       # 接受其数据
        resultone = chardet.detect(InitializeData)             #识别数据类型
        if resultone['encoding']== 'ISO-8859-1':               #判断数据是否是16进制
             print "16进制"
        else:
             if InitializeData=='':
                 break
             print "非16进制"
             continue
        RequestData = str(binascii.b2a_hex(InitializeData))    #16转ASCII
        if RequestData[0:2]=='5a':#判断帧头1
            if RequestData[len(RequestData)-2:len(RequestData)]=='ee':#判断帧尾
                print "数据完整"
            else:
                print "缺包"
                continue
        else:
            print "非协议内容"
        if RequestData[0:4]=='5aa5'and RequestData[6:8]=='10':                       #判断获取版本号命令

           listdata = list(RequestData)
           listdata[4] = '0'                                   #应答
           listdata[5] = '9'
           listdata[6] = '9'
           listdata[7] = '0'
           listdata.insert(len(listdata) - 4, fileread.getver())
           checkdata=''.join(listdata)
           checkdata=fileread.getcheck(checkdata[6:18])
           listdata[len(listdata)-4]=checkdata[0]
           listdata[len(listdata)-3] = checkdata[1]
           Verdata = ''.join(listdata)
           print "发送版本号"
           sock.send(binascii.a2b_hex(Verdata))
        if  RequestData[0:4]=='5aa5'and RequestData[6:8]=='20':                       #判断请求固件
            try:
                listdata = list(RequestData)
                listdata[4] = '0'
                listdata[5] = 'd'
                listdata[6] = 'a'
                listdata[7] = '0'
                listdata.insert(len(listdata) - 4, '01')  # 注意数据大小为一个整体插入
                listdata.insert(len(listdata) - 4, fileread.getfilesize())
                checkdata = ''.join(listdata)
                checkdata = fileread.getcheck(checkdata[6:28])
                listdata[len(listdata) - 4] = checkdata[0]
                listdata[len(listdata) - 3] = checkdata[1]
                Firdata = ''.join(listdata)
                print "固件下载"
                sock.send(binascii.a2b_hex(Firdata))
                time.sleep(4)
                sock.sendall(fileread.postfile())
                time.sleep(7)
                Idnum = RequestData[0:18]  # 发送固件后记录版本号
            except:
                print "下载失败"

        if  RequestData[0:4]=='5aa5'and RequestData[6:8]=='30':                      # 判断固件升级情况
            try:
                listdata = list(Idnum)
                listdata[4] = '0'
                listdata[5] = '9'
                listdata[6] = 'b'
                listdata[7] = '0'
                listdata.append('1')
                listdata.append('1')
                checkdata = ''.join(listdata)
                checkdata = fileread.getcheck(checkdata[6:18])
                listdata.append(checkdata[0])
                listdata.append(checkdata[1])
                listdata.append('ee')
                print listdata
                # listdata.insert(len(listdata) - 4, '11')
                Firdata = ''.join(listdata)
                print "固件升级成功"
                sock.send(binascii.a2b_hex(Firdata))
            except:
                print '未下载固件'
                continue

        print "已返回设备"
        # sock.send(binascii.a2b_hex())                   # 发送变成大写后的数据,需先解码,再按utf-8编码,  encode()其实就是encode('utf-8')

    print '关闭连接'
    sock.close()  # 关闭连接
    print('Connection from %s:%s closed.' % addr)


# def GetVersion(RequestData):
#     listdata = list(RequestData)
#     listdata[4] = '0'
#     listdata[5] = '9'
#     listdata[6] = '9'
#     listdata[7] = '0'
#     listdata.insert(len(listdata) - 4, bbh)
#     Verdata = ''.join(listdata)
#     #return  Verdata
#     print "发送版本号"
#     sock.send(binascii.a2b_hex(Verdata))

# def GetFirmware(RequestData):
#     listdata = list(RequestData)
#     listdata[4] = '0'
#     listdata[5] = 'd'
#     listdata[6] = 'a'
#     listdata[7] = '0'
#     listdata.insert(len(listdata)-4, '01')                 #注意数据大小为一个整体插入
#     listdata.insert(len(listdata) - 4, sjdx)
#
#     Firdata = ''.join(listdata)
#     print "固件下载"
#     sock.send(binascii.a2b_hex(Firdata))
#     time.sleep(3)
#     sock.send(fileread.postfile())
#     time.sleep(10)


# def EnsureUpgrade(RequestData):
#     listdata = list(RequestData)
#     listdata[4] = '0'
#     listdata[5] = 'd'
#     listdata[6] = 'a'
#     listdata[7] = '0'
#     listdata.insert(len(listdata) - 4, '11')
#     Firdata = ''.join(listdata)
#     print "固件升级成功"
#     sock.send(binascii.a2b_hex(Firdata))

def jonnyS(client, address):                              #线程处理
    try:
        #设置超时时间
        client.settimeout(500)


        TCP(sock, addr)  # 处理连接

    except socket.timeout:
        print 'time out'

    client.close()
while True:

    sock, addr = s.accept()  # 接收一个新连接
    thread = threading.Thread(target=jonnyS, args=(sock, addr ))
    thread.start()







