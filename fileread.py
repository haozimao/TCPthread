# -*- coding: UTF-8 -*-
# /**
#  *                             _ooOoo_
#  *                            o8888888o
#  *                            88" . "88
#  *                            (| -_- |)
#  *                            O\  =  /O
#  *                         ____/`---'\____
#  *                       .'  \\|     |//  `.
#  *                      /  \\|||  :  |||//  \
#  *                     /  _||||| -:- |||||-  \
#  *                     |   | \\\  -  /// |   |
#  *                     | \_|  ''\---/''  |   |
#  *                     \  .-\__  `-`  ___/-. /
#  *                   ___`. .'  /--.--\  `. . __
#  *                ."" '<  `.___\_<|>_/___.'  >'"".
#  *               | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#  *               \  \ `-.   \_ __\ /__ _/   .-` /  /
#  *          ======`-.____`-.___\_____/___.-`____.-'======
#  *                             `=---='
#  *          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#  *                     佛祖保佑        永无BUG
#  *            佛曰:
#  *                   写字楼里写字间，写字间里程序员；
#  *                   程序人员写程序，又拿程序换酒钱。
#  *                   酒醒只在网上坐，酒醉还来网下眠；
#  *                   酒醉酒醒日复日，网上网下年复年。
#  *                   但愿老死电脑间，不愿鞠躬老板前；
#  *                   奔驰宝马贵者趣，公交自行程序员。
#  *                   别人笑我忒疯癫，我笑自己命太贱；
#  *                   不见满街漂亮妹，哪个归得程序员？
# */
import os
import binascii
import chardet
import pymysql, datetime
from os.path import join, getsize
# -----------------------------获取路径----------------
def filepath():
    filepath = os.path.abspath('.')  # 获取程序路径
    filepath = filepath + '/FET.bin'
    return filepath


# ------------------------------ 发送bin函数---------------
def postfile():
    getpath = filepath()
    binfile = open(getpath, 'rb').read()  # 解析bin
    # resultone = chardet.detect(binfile)#识别数据类型
    #  test1 = str(binascii.b2a_hex(binfile))#16转ASCII

    binfile.replace('', ' ')

    binfilelist = list(binfile)
    binfile = ''.join(binfilelist)
    return binfile


# -------------------------------获取文件大小--------------
def getfilesize():
    getpath = filepath()
    size = hex(getsize(getpath))  # 大小转化为UTF-8 hex
    sizelist = list(size)
    del sizelist[0:2]  # 去头0x 去尾L
    sizelist.pop()
    if len(sizelist) < 8:  # 高位补0
        Dvlue = 8 - len(sizelist)
        while Dvlue:
            Dvlue -= 1
            sizelist.insert(0, '0')

    size = ''.join(sizelist)
    return size


# -----------------------------获取数据库版本号---------
def sqlread():  # sql读取

    db = pymysql.connect(host='127.0.0.1',
                         port=3306,
                         user='hh',
                         passwd='hu19950615',
                         db='data')
    cursor = db.cursor()
    sql = "SELECT * FROM DATAinfo  "
    # refreshsql="UPDATE DATAinfo"
    try:
        # cursor.execute(refreshsql)
        cursor.execute(sql)

        results = cursor.fetchall()

    except:
        print("no people")
    db.close()
    cursor.close()
    return results


def lastver():  # 获取版本号
    data = sqlread()
    datalen = len(data)
    return int(eval(data[datalen - 1][0]))  # str->float->int


def getver():
    num = hex(lastver())
    num = list(num)
    del num[0:2]  # 去头0x 去尾L
    if len(num) < 2:
        num.insert(0, '0')
    num = ''.join(num)
    return num


# -------------------------------检验码--------------------------
def getcheck(check):
    checknum = []
    checksum = 0
    i = 0
    # a='9000000001010a'
    a = check
    long = len(a)
    while True:
        checknum.append(a[i:i + 2])
        if i + 2 == long:
            break
        i = i + 2
    i = 0
    listlong = len(checknum)
    while True:
        checknum[i] = '0x' + checknum[i]
        if i == listlong - 1:
            break
        i = i + 1
    i = 0
    # while True:
    #     checknum[i] = ''.join(checknum[i])
    #     if i==listlong-1:
    #             break
    #     i=i+1
    while True:
        checksum = int(checknum[i], 16) + checksum
        if i == listlong - 1:
            break
        i = i + 1
    checksum = str(hex(checksum))
    checksum = checksum[len(checksum) - 2:len(checksum)]

    return checksum


# -------------------------记录设备信息-----------------------------
def getshowid(showid):
    idlen = '0x' + showid[8:10]
    idlen = int(idlen, 16)
    idinfo = showid[10:10 + idlen]
    return idinfo


def writeinfo(showId, showtype, versionnum, formatDate):
    db = pymysql.connect(host='127.0.0.1',
                         port=3306,
                         user='root',
                         passwd='hu19950615',
                         db='data')
    cursor = db.cursor()
    sql = "INSERT INTO Userinfo(showId,showtype,versionnum, formatDate) \
               VALUES ( '%s','%s','%s','%s')" % \
          (showId, showtype, versionnum, formatDate)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print("no")
    db.close()
    cursor.close()


# ---------------------------数据库初始化----------------恢复重建数据放入if执行
def creatsql():
    db = pymysql.connect(host='127.0.0.1',
                         port=3306,
                         user='root',
                         passwd='hu19950615',
                         db='data'
                         )
    cursor = db.cursor()

    sql = """CREATE TABLE Userinfo (
             showId  CHAR(20) NOT NULL,
             showtype CHAR (20),
             versionnum CHAR(20),
             formatDate VARCHAR (50))"""
    try:
        cursor.execute(sql)
    except:
        print("no")
    db.close()
    cursor.close()


if __name__ == '__main__':
    time = datetime.datetime.now().strftime('%Y/%m/%d   %H:%M:%S')
    print  writeinfo('458', 'a1', '11', time)

