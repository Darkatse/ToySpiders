#!/usr/bin/python3
from PSASpider import PSASpider
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

keywords = ['君实生物', '恒成工具']
wait_time = 10
sp = PSASpider()
sp.login()
file = open('专利.txt','r+')
file.seek(0)
file.truncate()
for k in keywords:
    print(" 查询 %s" % k)
    res = sp.make_query(k, wait_time)
    print(res)
    for i in res: #写入文件
        for j in i:
            file.write(str(j).replace(u'\u2011', u' ') + ' ' + i[j].replace(u'\u2011', u' ') + '\n') #替换\u2011字符，否则会报错
        file.write("\n")

file.close()
sp.exit()