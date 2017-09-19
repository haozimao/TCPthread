#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import binascii
import chardet
import pymysql
from os.path import join, getsize
#------------获取路径----------------
def filepath():
        filepath=os.path.abspath('.') #获取程序路径
        filepath=filepath+'/FET.bin'
        return filepath
#--------- 发送bin函数---------------
def postfile():
        getpath=filepath()
        binfile=open(getpath,'rb').read() #解析bin
       # resultone = chardet.detect(binfile)#识别数据类型
       #  test1 = str(binascii.b2a_hex(binfile))#16转ASCII

        binfile.replace('', ' ')

        binfilelist=list(binfile)
        binfile= ''.join(binfilelist)
        return binfile
#----------获取文件大小--------------
def getfilesize():

        getpath=filepath()
        size=hex(getsize(getpath))#大小转化为UTF-8 hex
        sizelist=list(size)
        del sizelist[0:2]    #去头0x 去尾L
        sizelist.pop()
        if len(sizelist)<8:  #高位补0
                Dvlue=8-len(sizelist)
                while Dvlue :
                        Dvlue-=1
                        sizelist.insert(0,'0')

        size = ''.join(sizelist)
        return size

# ------------获取数据库版本号---------
def sqlread(): #sql读取

  db = pymysql.connect(host='127.0.0.1',
    port=3306,
    user='hh',
    passwd='',#此处为数据库的密码
    db='data')
  cursor = db.cursor()
  sql="SELECT * FROM DATAinfo  "
  # refreshsql="UPDATE DATAinfo"
  try:
        # cursor.execute(refreshsql)
        cursor.execute(sql)

        results=cursor.fetchall()

  except :
        print("no people")
  db.close()
  cursor.close()
  return results
def lastver():     #获取版本号
    data = sqlread()
    datalen=len(data)
    return int(eval(data[datalen-1][0]))#str->float->int
def getver():
    num=hex(lastver())
    num=list(num)
    del num[0:2]  # 去头0x 去尾L
    if len(num)<2:
            num.insert(0,'0')
    num = ''.join(num)
    return num

#--------------检验码-------
def getcheck(check):
    checknum=[]
    checksum=0
    i=0
    # a='9000000001010a'
    a=check
    long=len(a)
    while True:
        checknum.append(a[i:i+2])
        if i+2==long:
                    break
        i=i+2
    i=0
    listlong=len(checknum)
    while True:
        checknum[i]='0x'+checknum[i]
        if i==listlong-1:
                break
        i=i+1
    i=0
    # while True:
    #     checknum[i] = ''.join(checknum[i])
    #     if i==listlong-1:
    #             break
    #     i=i+1
    while True:
        checksum=int(checknum[i],16)+checksum
        if i==listlong-1:
                break
        i=i+1
    checksum=str(hex(checksum))
    checksum=checksum[len(checksum)-2:len(checksum)]

    return checksum

if __name__ == '__main__':
 print  postfile()
