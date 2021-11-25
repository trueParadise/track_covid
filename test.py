import time
import re
import os
import threading
# # 13/05/2020 17:45:06
# print(time.strftime("%d/%m/%Y %H:%M:%S",time.localtime()))
# lock = threading.Lock()
# deposit = 100
# def add_profit():
#     global deposit
#     for i in range(1000000):
#         lock.acquire()
#         deposit += 10
#         lock.release()
#
# def pay_bill():
#     global deposit
#     for i in range(1000000):
#         lock.acquire()
#         deposit -= 10
#         lock.release()
#
#
# t1 = threading.Thread(target=add_profit, args=())
# t2 = threading.Thread(target=pay_bill, args=())
#
# t1.start()
# t2.start()
#
# t1.join()
# t2.join()
#
# print(deposit)

# import threading
# #定义线程要调用的方法，*add可接收多个以非关键字方式传入的参数
# def action(*add):
#     for arc in add:
#         #调用 getName() 方法获取当前执行该程序的线程名
#         print(threading.current_thread().getName() +" "+ arc)
# #定义为线程方法传入的参数
# my_tuple = ("http://c.biancheng.net/python/",\
#             "http://c.biancheng.net/shell/",\
#             "http://c.biancheng.net/java/")
# #创建线程
# thread = threading.Thread(target = action,args =my_tuple)
# #启动线程
# thread.start()
# thread.join()
# #主线程执行如下语句
# for i in range(5):
#     print(threading.current_thread().getName())

# t = "12345678901234567890 13/05/2020 17:45:06 13/05/2020 18:00:05"
# match = re.match(r'(\w+) (\d+/\d+/\d+ \d+:\d+:\d+) (\d+/\d+/\d+ \d+:\d+:\d+)',t)
# print(match.group(2))
# print(match.group(3))




# time_tuple = time.strptime("06/08/2020 15:18:16", "%d/%m/%Y %H:%M:%S")
# print(time.mktime(time_tuple))


# lines = [l for l in open("myfile.txt", "r") if l.find("20150723", 0, 8) == -1]
# print(lines)
# fd = open("myfile.txt", "w")
# fd.writelines(lines)
# fd.close()

# f = open("myfile.txt", "r")
# ok = f.readline()
# print(ok)
# f.close()

# lines = [line for line in open("myfile.txt", 'r')
#                          if time.mktime(time.strptime(re.match(r'(\w+) (\d+/\d+/\d+ \d+:\d+:\d+) (\d+/\d+/\d+ \d+:\d+:\d+)',line).group(2), "%d/%m/%Y %H:%M:%S"))
#                          +5*60 > time.time()]
# print(lines)
# f = open("myfile.txt", "w")
# f.writelines(lines)
# f.close()


# 找到是0， 找不到是-1
# a = "1234iii"
# print(a.find("123", 0,3))

with open("tempIDs.txt") as fp:
    lines = fp.readlines()
    for line in lines:
        ls = line.strip().split(" ")
        print(ls[0], ls[1])