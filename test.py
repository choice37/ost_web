import requests
from bs4 import BeautifulSoup

def get_nasdaq_100_futures():
    url = 'https://kr.investing.com/indices/micro-nasdaq-100-futures'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    response = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 가격 정보 크롤링
    price_element = soup.find('div', {'data-test': 'instrument-price-last'})
    price = price_element.text if price_element else None
    
    # 가격 변동 정보 크롤링
    price_change_element = soup.find('span', {'data-test': 'instrument-price-change'})
    price_change = price_change_element.text if price_change_element else None
    
    # 가격 변동 퍼센트 정보 크롤링
    price_change_percent_element = soup.find('span', {'data-test': 'instrument-price-change-percent'})
    price_change_percent = price_change_percent_element.text if price_change_percent_element else None

    # 괄호 제거
    if price_change_percent.startswith('(') and price_change_percent.endswith(')'):
        price_change_percent = price_change_percent[1:-1]  # 괄호 제거
    return {
        'price': price,
        'price_change': price_change,
        'price_change_percent': price_change_percent
    }

# 결과 출력
nasdaq_100_futures = get_nasdaq_100_futures()
print(nasdaq_100_futures)
