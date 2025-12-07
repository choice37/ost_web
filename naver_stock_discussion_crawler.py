# -*- coding: utf-8 -*-
"""
네이버 종목토론실 크롤링 모듈
종목 코드를 입력받아 해당 종목의 종목토론실 게시글을 크롤링합니다.
"""
import requests
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict
from datetime import datetime


class NaverStockDiscussionCrawler:
    """네이버 종목토론실 크롤러 클래스"""
    
    def __init__(self, delay: float = 1.0):
        """
        Args:
            delay: 요청 간 대기 시간 (초)
        """
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def crawl_discussion_page(self, stock_code: str, page: int = 1) -> List[Dict[str, any]]:
        """
        종목토론실 특정 페이지 크롤링
        
        Args:
            stock_code: 종목 코드 (6자리 숫자)
            page: 페이지 번호 (기본값: 1)
            
        Returns:
            게시글 리스트
        """
        try:
            url = f"https://finance.naver.com/item/board.nhn?code={stock_code}&page={page}"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = []
            
            # 게시글 테이블 찾기
            table = soup.select_one('table.type2')
            if not table:
                print(f"페이지 {page}: 게시글 테이블을 찾을 수 없습니다.")
                return posts
            
            rows = table.select('tr')
            
            for row in rows:
                try:
                    # 제목 링크
                    title_link = row.select_one('td.title a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    if not title or title == '':
                        continue
                    
                    # 날짜: 첫 번째 td 안의 span 태그에서 추출
                    # <td><span class="tah p10 gray03">2025.12.07 10:00</span></td>
                    tds = row.find_all('td')
                    date_text = ''
                    if tds and len(tds) > 0:
                        first_td = tds[0]
                        date_span = first_td.select_one('span.tah.p10.gray03')
                        if date_span:
                            date_text = date_span.get_text(strip=True)
                    
                    post_data = {
                        'title': title,
                        'date': date_text,
                        'stock_code': stock_code
                    }
                    
                    posts.append(post_data)
                    
                except Exception as e:
                    continue
            
            # 요청 간 대기
            time.sleep(self.delay)
            
            return posts
            
        except Exception as e:
            print(f"페이지 {page} 크롤링 중 오류 발생: {e}")
            return []
    
    def crawl_all_pages(self, stock_code: str, max_pages: int = 10) -> List[Dict[str, any]]:
        """
        종목토론실 여러 페이지 크롤링
        
        Args:
            stock_code: 종목 코드
            max_pages: 최대 페이지 수
            
        Returns:
            모든 게시글 리스트
        """
        all_posts = []
        
        for page in range(1, max_pages + 1):
            print(f"페이지 {page}/{max_pages} 크롤링 중...")
            posts = self.crawl_discussion_page(stock_code, page)
            
            if not posts:
                print(f"페이지 {page}에 게시글이 없습니다. 크롤링 종료.")
                break
            
            all_posts.extend(posts)
            print(f"페이지 {page}: {len(posts)}개 게시글 수집")
        
        return all_posts
    
    def crawl_stock_discussion(self, stock_code: str, max_pages: int = 10) -> List[Dict[str, any]]:
        """
        종목 코드로 종목토론실 크롤링 (메인 메서드)
        
        Args:
            stock_code: 종목 코드 (6자리 숫자, 예: "005930")
            max_pages: 최대 페이지 수
            
        Returns:
            게시글 리스트
        """
        
        print(f"\n{'='*60}")
        print(f"종목 코드: {stock_code}")
        print(f"{'='*60}\n")
        
        # 종목토론실 크롤링
        posts = self.crawl_all_pages(stock_code, max_pages)
        
        print(f"\n총 {len(posts)}개의 게시글을 수집했습니다.")
        
        return posts
    
    def save_to_json(self, posts: List[Dict[str, any]], filename: str = None):
        """
        게시글 데이터를 JSON 파일로 저장
        
        Args:
            posts: 게시글 리스트
            filename: 저장할 파일명 (None이면 자동 생성)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_discussion_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        
        print(f"\n데이터가 '{filename}'에 저장되었습니다.")
        return filename
    
    def save_to_csv(self, posts: List[Dict[str, any]], filename: str = None):
        """
        게시글 데이터를 CSV 파일로 저장
        
        Args:
            posts: 게시글 리스트
            filename: 저장할 파일명 (None이면 자동 생성)
        """
        import csv
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_discussion_{timestamp}.csv"
        
        if not posts:
            print("저장할 데이터가 없습니다.")
            return None
        
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)
        
        print(f"\n데이터가 '{filename}'에 저장되었습니다.")
        return filename


def main():
    """메인 실행 함수"""
    crawler = NaverStockDiscussionCrawler(delay=1.0)
    
    # 종목 코드 입력
    stock_code = input("종목 코드를 입력하세요 (6자리 숫자, 예: 005930): ").strip()
    
    if not stock_code:
        print("종목 코드를 입력해주세요.")
        return
    
    # 페이지 수 입력
    try:
        max_pages = int(input("크롤링할 최대 페이지 수를 입력하세요 (기본값: 10): ").strip() or "10")
    except ValueError:
        max_pages = 10
    
    # 크롤링 실행
    posts = crawler.crawl_stock_discussion(stock_code, max_pages=max_pages)
    
    if posts:
        # 결과 출력
        print(f"\n{'='*60}")
        print("수집된 게시글 샘플 (최대 5개):")
        print(f"{'='*60}\n")
        
        for i, post in enumerate(posts[:5], 1):
            print(f"[{i}] {post['title']}")
            print(f"    날짜: {post['date']}")
            print()
        
        # 저장 여부 확인
        save = input("데이터를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        
        if save == 'y':
            format_choice = input("저장 형식을 선택하세요 (json/csv, 기본값: json): ").strip().lower()
            
            if format_choice == 'csv':
                crawler.save_to_csv(posts)
            else:
                crawler.save_to_json(posts)
    else:
        print("수집된 게시글이 없습니다.")


if __name__ == "__main__":
    main()

