import os
import sys
import urllib.request
import datetime
import time
import json
import pandas as pd
import datetime
import re

search_keyword = '현대건설 특징주'

# 네이버 검색 API
client_id = "본인의 client_id"
client_secret = "본인의 client_secret"

encText = urllib.parse.quote(str(search_keyword))
today = datetime.datetime.now().strftime('%Y-%m-%d')

# 테스트용 첫 페이지만 가져오기
# https://developers.naver.com/docs/serviceapi/search/news/news.md#%EB%89%B4%EC%8A%A4 참고
url = "https://openapi.naver.com/v1/search/news.json?query=" + encText + "&start=" + str(1) + "&display=100" + "&sort=sim"

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id","e6k76YlPLmGMaiTIESbp")
request.add_header("X-Naver-Client-Secret","2B1dR9tFOT")

response = urllib.request.urlopen(request)
rescode = response.getcode()

if(rescode==200):
    response_body = response.read()
    print('request Success')
    # print(response_body.decode('utf-8'))
else:
    print("Error Code:" + rescode)


response_result = response_body.decode('utf-8')
response_result = json.loads(response_result)

print(response_result)