# TCPthread

基于python的多线程TCP通讯,作为service端,硬件主动连接,进行升级,升级文件为bin格式

在此程序中需要注意以下几个问题

1 通讯过程延时问题,localhost多线程测试时,延迟需在60ms以上不会粘包,由于采用的是循环测试发送,所以在实际情况在这个问题不会太明显,后面版本会进行修补

2 python线程的通病,变量值混乱,这个暂时未发现,不过存在这样的隐患

3 在win下转化hex会出现带L的情况,采用了笨办法,转化成列表,去掉

        del sizelist[0:2]    #去头0x 去尾L
        
        sizelist.pop()
