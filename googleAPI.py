import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive',
]

class GoogleSheet:
    worksheet = None

    def __init__(self, sheet_name, worksheet_name):
        self.worksheet = self.connect_worksheet(sheet_name, worksheet_name)

    def connect_worksheet(self, sheet_name, worksheet_name):
        json_file_name = 'bgm-537-b9fa3d50e755.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
        gc = gspread.authorize(credentials)

        return gc.open(sheet_name).worksheet(worksheet_name)
    
    # worksheet의 worksheet.get_all_records()
    def get_all_records(self):
        return self.worksheet.get_all_records()

    # worksheet dataframe으로 가져옴
    def get_as_dataframe(self):
        return pd.DataFrame(self.get_all_records())
    
    # worksheet의 모든 row를 가져옴
    def get_all_rows(self):
        return self.worksheet.get_all_values()
    
    # worksheet의 row를 가져옴
    def get_row(self, row):
        return self.worksheet.row_values(row)
    
    # worksheet의 column을 가져옴
    def get_col(self, col):
        return self.worksheet.col_values(col)
    
    # worksheet의 column 이름 보기
    def get_col_name(self):
        return self.worksheet.get_all_values()[0]
    
    # worksheet의 cell을 가져옴
    def get_cell(self, row, col):
        return self.worksheet.cell(row, col).value
    
    # worksheet의 cell을 수정함
    def update_cell(self, row, col, value):
        self.worksheet.update_cell(row, col, value)

    # worksheet의 row를 추가함
    def insert_row(self, row, value):
        self.worksheet.insert_row(value, row)

    # worksheet의 row를 마지막에 추가함
    def append_row(self, value):
        self.worksheet.append_row(value)

    # worksheet의 rows를 마지막에 추가함
    def append_rows(self, values):
        self.worksheet.append_rows(values)

    # worksheet의 value가 일치하는 row를 삭제함
    def delete_row_by_value(self, value):
        self.worksheet.delete_row(self.worksheet.find(value).row)

    # worksheet의 row를 삭제함
    def delete_row(self, row):
        self.worksheet.delete_row(row)

    # worksheet의 column을 추가함
    def insert_col(self, col, value):
        self.worksheet.insert_col(value, col)

    # worksheet의 column을 삭제함
    def delete_col(self, col):
        self.worksheet.delete_col(col)

    # worksheet의 row를 복사함
    def copy_row(self, row):
        self.worksheet.copy_row(row)

    # worksheet의 column을 복사함
    def copy_col(self, col):
        self.worksheet.copy_col(col)

    # worksheet의 row를 이동함
    def move_row(self, row, target_row):
        self.worksheet.move_row(row, target_row)

    # worksheet의 column을 이동함
    def move_col(self, col, target_col):
        self.worksheet.move_col(col, target_col)
    
    # dataframe을 worksheet에 추가함
    def append_df(self, df):
        self.worksheet.append_rows(df.values.tolist())

    # dataframe을 column 이름 일치하는것만 맞춰서 worksheet에 추가함
    def append_df_by_col_name(self, df):
        sheet_col_name = self.get_col_name()
        new_df = pd.DataFrame(columns=sheet_col_name)
        for scn in sheet_col_name:
            if scn in df.columns:
                new_df[scn] = df[scn]
        new_df = new_df.fillna('')
        
        self.append_df(new_df)

    # worksheet의 column빼고 모든 row를 삭제함
    def clear_all_rows(self):
        first_row = self.get_row(1)
        self.worksheet.batch_clear([f'A2:{chr(ord("A") + len(first_row) - 1)}'])
        
    # worksheet의 종목명과 날짜가 일치하는 row의 index를 가져옴
    def get_row_index_by_name_date(self, name, date, columns_name=['종목명', '날짜']):
        df = self.get_as_dataframe()
        df = df.loc[(df[columns_name[0]] == name) & (df[columns_name[1]] == date)]
        if df.empty:
            return -1
        else:
            return df.index[0] + 2

    # worksheet의 날짜가 일치하는 row의 index를 가져옴
    def get_row_index_by_date(self, date, columns_name=['날짜']):
        df = self.get_as_dataframe()
        df = df.loc[(df[columns_name[0]] == date)]
        if df.empty:
            return -1
        else:
            return df.index[0] + 2
        
    # worksheet의 종목명과 날짜와 상장기간이 일치하는 row의 index를 가져옴
    def get_row_index_by_name_date_period(self, name, date, listing_period, columns_name=['종목명', '날짜', '상장기간']):
        df = self.get_as_dataframe()
        df = df.loc[(df[columns_name[0]] == name) & (df[columns_name[1]] == date) & (df[columns_name[2]] == listing_period)]
        if df.empty:
            return -1
        else:
            return df.index[0] + 2
        
    def col_num_to_col_letter(self, col_num):
        col_letter = ''
        while col_num > 0:
            remainder = (col_num - 1) % 26
            col_letter = chr(65 + remainder) + col_letter
            col_num = (col_num - 1) // 26
        return col_letter

    # worksheet의 특정 row에 column 이름이 일치하는 값들만 업데이트
    def update_row_by_col_name(self, row, data_dict):
        col_names = self.get_col_name()  # 워크시트의 열 이름을 가져옴
        col_len = len(col_names)
        
        # A1 표기법으로 범위를 지정
        range_str = f"A{row}:{self.col_num_to_col_letter(col_len)}{row}"
        
        # 워크시트에서 한 번의 호출로 모든 셀을 가져옴
        cells = self.worksheet.range(range_str)

        cells_to_update = []
        
        for col_index, (cell, col_name) in enumerate(zip(cells, col_names)):
            if col_name in data_dict.keys():  # 열 이름이 data_dict의 키와 일치하면
                new_value = data_dict[col_name]
                cell.value = new_value
                cells_to_update.append(cell)

        # 여러 셀을 한 번에 업데이트
        if cells_to_update:
            self.worksheet.update_cells(cells_to_update)

# worksheet = connect_worksheet("매매기법 검증", "단기스윙 검증")