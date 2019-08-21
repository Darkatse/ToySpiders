#!/usr/bin/python3
from PSASpider import PSASpider
import io
import sys
import json

keywords = ['君实生物', '恒成工具']
wait_time = 10
sp = PSASpider()
sp.login()
file = open('专利.json', 'a', encoding="utf-8")
file.seek(0)
file.truncate()
for k in keywords:
    print(" 查询 %s" % k)
    res = sp.make_query(k, wait_time)
    print(res)
    jsObj = json.dumps(res, ensure_ascii=False, indent=4, sort_keys=True)
    file.write(jsObj)
    file.write("\n")

file.close()
sp.exit()