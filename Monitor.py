# -*- coding:utf-8 -*-
# author: jiakesan@gmail.com
import os
import sys
import time
from datetime import datetime

'''生成一部分固定的数据'''
timeStamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
projects = [{"name": "project001", "type": "node"}, {"name": "project002", "type": "node"},
            {"name": "project003", "type": "java"}, {"name": "project004", "type": "java"}]

period = int(sys.argv[1])


def getPid(name, type):
    """
    通过进程名称和类型获取进程ID
    :param name:进程的名称
    :param type:进程的类型：java,nodejs
    :return:进程ID
    """
    process = os.popen("ps -ef|grep %s" % name)
    output = process.readlines()
    process.close()
    for line in output:
        if line.__contains__(type):
            terms = line.split()
            return terms[1]


def topAnalyzer(path, file, pid):
    """
    对生成好的top结果文件进行解析
    :param path:top结果文件的存放目录
    :param file:top记录的文件名
    :param pid:对应top命令监控的进程ID
    :return:统计分析出的cpu/内存最大/最小和平均值
    """
    content = open("%s/%s.log" % (path, file), 'r')
    cList = []
    mList = []
    for line in content:
        terms = line.split()
        if terms.__len__() > 0 and terms[0].__eq__(pid):
            cList.append(float(terms[8]))
            mList.append(float(terms[9]))

    cpu = {"min": "%.2f" % min(cList), "max": "%.2f" % max(cList), "mean": "%.2f" % (sum(cList) / cList.__len__())}
    memory = {"min": round(min(mList), 2), "max": round(max(mList), 2), "mean": round(sum(mList) / mList.__len__(), 2)}
    return {file: {"cpu": cpu, "memory": memory}}


'''开始处理监控'''
os.popen("mkdir %s" % timeStamp)
for project in projects:
    project.update({"pid": getPid(project["name"], project["type"])})
    os.popen("top -p %s  -d 1 -n %s -b > %s/%s.log &" % (project["pid"], period, timeStamp, project["name"]))

os.popen("vmstat 1 %s > %s/system.log &" % (period, timeStamp))

'''完成统计功能'''
time.sleep(period + 10)
result = dict()
for project in projects:
    result.update(topAnalyzer(timeStamp, project["name"], project["pid"]))

summary = open("%s/summary.log" % timeStamp, 'w')
summary.write(result)
summary.close()
for key in result.keys():     print "%s\t%s\t%s" % (result[key]["cpu"]["mean"], result[key]["memory"]["max"], key)
