import os
import time
import random
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import Calendar
from pykrx import stock
import pandas as pd

# 전역 변수 (크롤링 진행 상황 관리)
stop_event = threading.Event()
tickers_list = []     # 전체 종목 리스트
current_index = 0     # 현재 진행 인덱스 (이어하기 시 사용)
total = 0             # 전체 종목 수
result_list = []      # 각 종목의 DataFrame 저장 리스트
has_run = False       # 한 번이라도 수집하기 버튼을 누른 여부
resume_params = {}    # 처음 실행 시 저장한 입력값(시장, 시작 날짜, 종료 날짜, 폴더)

# --- UI 제어 관련 함수 ---
def set_control_buttons(mode):
    """
    mode에 따라 제어 버튼들의 상태를 설정합니다.
    mode:
      "idle"    - 수집 중이 아닐 때: 수집하기 버튼은 항상 보임, 
                  has_run가 True이면 이어하기 버튼 보임.
      "running" - 수집 실행 중: 중단 버튼만 보임.
      "stopped" - 수집이 중단된 후: 수집하기, 이어하기 버튼 보임.
    """
    if mode == "idle":
        start_button.grid()  # 수집하기 버튼 항상 보임
        if has_run:
            resume_button.grid()
        else:
            resume_button.grid_remove()
        stop_button.grid_remove()
    elif mode == "running":
        start_button.grid_remove()
        resume_button.grid_remove()
        stop_button.grid()   # 중단 버튼만 보임
    elif mode == "stopped":
        start_button.grid()
        resume_button.grid()
        stop_button.grid_remove()

def show_progress_widgets():
    progress_bar.grid()
    progress_label.grid()

def hide_progress_widgets():
    progress_bar.grid_remove()
    progress_label.grid_remove()

# --- 입력 관련 함수 ---
def select_folder():
    """저장할 폴더 선택 함수"""
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)

def open_calendar(date_var):
    """달력 팝업을 띄워 날짜를 선택하고, 선택한 날짜를 date_var에 저장"""
    top = tk.Toplevel(root)
    top.grab_set()  # 팝업이 열려있는 동안 다른 창 조작 방지
    cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    cal.pack(padx=10, pady=10)
    
    def on_date_selected():
        date_var.set(cal.get_date())
        top.destroy()
    
    ttk.Button(top, text="날짜 선택", command=on_date_selected).pack(pady=10)

def update_progress(idx):
    """진행률 업데이트 (메인 스레드에서 실행)"""
    progress_bar["value"] = idx
    percent = int((idx / total) * 100) if total > 0 else 0
    progress_label["text"] = f"{percent}% 완료"
    root.update_idletasks()

# --- 데이터 수집 함수 ---
def do_collect_data():
    """백그라운드 스레드에서 실행되는 데이터 수집 함수 (중단/이어하기 지원)"""
    global current_index, tickers_list, total, result_list, has_run

    # 입력값 가져오기 (이어가기 시에도 현재 입력값을 사용)
    market = market_combobox.get()
    start_date = start_date_var.get()
    end_date = end_date_var.get()
    folder = folder_var.get()

    # 날짜 형식 변환: YYYY-mm-dd -> YYYYMMDD (pykrx 함수에서 사용)
    start_date_str = start_date.replace("-", "")
    end_date_str = end_date.replace("-", "")
    
    # 최초 실행 시(새로 시작) 종목 리스트 가져오기
    if current_index == 0:
        try:
            tickers_list = stock.get_market_ticker_list(market=market)
        except Exception as e:
            messagebox.showerror("오류", f"종목 리스트를 가져오는 중 오류 발생: {e}")
            set_control_buttons("idle")
            return

        if not tickers_list:
            messagebox.showwarning("경고", "해당 시장의 종목을 찾을 수 없습니다.")
            set_control_buttons("idle")
            return
        total = len(tickers_list)
        progress_bar["maximum"] = total

    # 수집 실행 중에는 중단 버튼만 보임
    set_control_buttons("running")
    show_progress_widgets()
    
    for idx in range(current_index, total):
        if stop_event.is_set():
            current_index = idx  # 중단 시 현재 진행 인덱스 저장
            set_control_buttons("stopped")
            return

        ticker = tickers_list[idx]
        try:
            # OHLCV 데이터 가져오기 (시가, 고가, 저가, 종가, 거래량)
            df_ohlcv = stock.get_market_ohlcv_by_date(start_date_str, end_date_str, ticker)
            if df_ohlcv.empty:
                pass
            else:
                # 거래대금 데이터 가져오기 (get_market_cap_by_date 사용)
                df_cap = stock.get_market_cap_by_date(start_date_str, end_date_str, ticker)
                if not df_cap.empty and "거래대금" in df_cap.columns:
                    # 날짜(index)를 기준으로 병합 (왼쪽 기준)
                    df_merged = df_ohlcv.join(df_cap[["거래대금"]], how="left")
                else:
                    df_merged = df_ohlcv.copy()
                
                # 등락률 칼럼이 있으면 소수 둘째 자리까지 반올림
                if "등락률" in df_merged.columns:
                    df_merged["등락률"] = df_merged["등락률"].round(2)
                
                # 종목코드와 종목명 추가
                df_merged["종목코드"] = ticker
                종목명 = stock.get_market_ticker_name(ticker)
                df_merged["종목명"] = 종목명
                
                result_list.append(df_merged)
        except Exception as e:
            print(f"Ticker {ticker} 데이터 수집 오류: {e}")
        
        update_progress(idx + 1)
        time.sleep(random.uniform(1, 3))
    
    # 전체 데이터 합치기
    if result_list:
        combined_df = pd.concat(result_list)
    else:
        combined_df = pd.DataFrame()

    # 파일명 생성: {시장이름}_{시작날짜}_{종료날짜}.csv
    filename = f"{market}_{start_date}_{end_date}.csv"
    file_path = os.path.join(folder, filename)
    try:
        combined_df.to_csv(file_path, encoding='utf-8-sig', index=True)
        msg = f"{market} 시장의 전체 데이터가\n'{file_path}' 에 저장되었습니다."
    except Exception as e:
        msg = f"파일 저장 중 오류 발생: {e}"
    
    # 초기화
    current_index = 0
    tickers_list.clear()
    total = 0
    result_list.clear()
    hide_progress_widgets()
    set_control_buttons("idle")
    messagebox.showinfo("완료", msg)

# --- 버튼 클릭 관련 함수 ---
def start_collecting(is_resume):
    """
    is_resume가 False이면 새롭게 시작(현재 진행 상황 초기화)하고,
    True이면 이어하기 실행 전에 기존 입력값과 현재 입력값이 동일한지 검사합니다.
    """
    global resume_params, current_index, result_list, has_run

    # 현재 입력값 가져오기
    market = market_combobox.get()
    start_date = start_date_var.get()
    end_date = end_date_var.get()
    folder = folder_var.get()

    # 필수 입력값 확인
    if not (market and start_date and end_date and folder):
        messagebox.showerror("오류", "모든 항목을 입력해 주세요.")
        set_control_buttons("idle")
        return

    if is_resume:
        # 이어하기 실행 시, 이전 입력값(resume_params)과 현재 입력값 비교
        if resume_params.get("market") != market or \
           resume_params.get("start_date") != start_date or \
           resume_params.get("end_date") != end_date or \
           resume_params.get("folder") != folder:
            messagebox.showerror("오류", "입력값이 변경되어 이어서 진행할 수 없습니다.\n새로 수집하기 버튼을 눌러주세요.")
            # 이어하기 버튼은 그대로 남아있으므로 사용자가 입력을 다시 기존대로 맞출 수 있습니다.
            return
    else:
        # 새로 시작하는 경우, 기존 진행 상황 초기화 및 resume_params 업데이트
        current_index = 0
        result_list.clear()
        resume_params = {
            "market": market,
            "start_date": start_date,
            "end_date": end_date,
            "folder": folder
        }
    
    # 중단 이벤트 초기화 및 수집 실행
    stop_event.clear()
    threading.Thread(target=do_collect_data, daemon=True).start()

def stop_collecting():
    """중단 버튼 클릭 시 실행"""
    stop_event.set()
    set_control_buttons("stopped")

# --- UI 생성 ---
root = tk.Tk()
root.title("주식 데이터 크롤링 프로그램")

# 메인 프레임
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# --- 입력 영역 ---
# 시장 선택
ttk.Label(frame, text="시장 선택:").grid(row=0, column=0, sticky=tk.W, pady=5)
market_combobox = ttk.Combobox(frame, values=["KOSPI", "KOSDAQ"], state="readonly", width=20)
market_combobox.grid(row=0, column=1, pady=5)
market_combobox.current(0)

# 시작 날짜 선택 (읽기 전용 Entry + 달력 팝업)
ttk.Label(frame, text="시작 날짜:").grid(row=1, column=0, sticky=tk.W, pady=5)
start_date_var = tk.StringVar()
start_date_entry = ttk.Entry(frame, textvariable=start_date_var, width=22, state="readonly")
start_date_entry.grid(row=1, column=1, pady=5)
ttk.Button(frame, text="달력 열기", command=lambda: open_calendar(start_date_var)).grid(row=1, column=2, padx=5, pady=5)

# 종료 날짜 선택 (읽기 전용 Entry + 달력 팝업)
ttk.Label(frame, text="종료 날짜:").grid(row=2, column=0, sticky=tk.W, pady=5)
end_date_var = tk.StringVar()
end_date_entry = ttk.Entry(frame, textvariable=end_date_var, width=22, state="readonly")
end_date_entry.grid(row=2, column=1, pady=5)
ttk.Button(frame, text="달력 열기", command=lambda: open_calendar(end_date_var)).grid(row=2, column=2, padx=5, pady=5)

# 저장 폴더 선택
ttk.Label(frame, text="저장 폴더:").grid(row=3, column=0, sticky=tk.W, pady=5)
folder_var = tk.StringVar()
folder_entry = ttk.Entry(frame, textvariable=folder_var, width=30, state="readonly")
folder_entry.grid(row=3, column=1, pady=5)
ttk.Button(frame, text="폴더 선택", command=select_folder).grid(row=3, column=2, padx=5, pady=5)

# --- 진행률 영역 (기본 숨김) ---
progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, pady=10)
progress_bar.grid_remove()

progress_label = ttk.Label(frame, text="진행률 없음")
progress_label.grid(row=5, column=0, columnspan=3)
progress_label.grid_remove()

# --- 제어 버튼 영역 ---
control_frame = ttk.Frame(frame)
control_frame.grid(row=6, column=0, columnspan=3, pady=10)

# 수집하기 버튼 (새로 시작) -> is_resume=False
start_button = ttk.Button(control_frame, text="수집하기", command=lambda: start_collecting(False))
start_button.grid(row=0, column=0, padx=5)

# 이어하기 버튼 -> is_resume=True (한 번 수집 실행 후 항상 보임)
resume_button = ttk.Button(control_frame, text="이어하기", command=lambda: start_collecting(True))
resume_button.grid(row=0, column=1, padx=5)
resume_button.grid_remove()  # 초기에는 숨김

# 중단 버튼 (수집 실행 중에만 보임)
stop_button = ttk.Button(control_frame, text="중단", command=stop_collecting)
stop_button.grid(row=0, column=2, padx=5)
stop_button.grid_remove()

# 초기 버튼 상태 설정 (idle 상태)
set_control_buttons("idle")

root.mainloop()
