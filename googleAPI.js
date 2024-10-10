// const { google } = require('googleapis');
// const fs = require('fs');
import { google } from 'googleapis';
import fs from 'fs';

export class GoogleSheet {
    constructor(sheetName, worksheetName) {
        this.sheetName = "1sscViRHXKS1t9SRHkvqtfJ8Q5HswyaeTFGT2jv8yUhQ";
        this.worksheetName = worksheetName;
        this.auth = null;
        this.sheets = null;
        this.worksheetId = null;
        this.initialize();
    }

    async initialize() {
        this.auth = await this.authenticate();
        this.sheets = google.sheets({ version: 'v4', auth: this.auth });
        this.worksheetId = await this.getWorksheetId();
    }

    // 인증 처리
    async authenticate() {
        const credentials = JSON.parse(fs.readFileSync('bgm-537-b9fa3d50e755.json'));
        const { client_email, private_key } = credentials;

        console.log(client_email);
        
        const auth = new google.auth.JWT({
            email: client_email,
            key: private_key,
            scopes: ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        });

        return auth;
    }

    // 워크시트 ID 가져오기
    async getWorksheetId() {
        const response = await this.sheets.spreadsheets.get({ // this.sheets로 변경
            auth: this.auth,
            spreadsheetId: this.sheetName,
        });
        
        const sheets = response.data.sheets;
        const worksheet = sheets.find(sheet => sheet.properties.title === this.worksheetName);
        return worksheet.properties.sheetId;
    }

    // 모든 레코드 가져오기
    async getAllRecords() {
        const response = await this.sheets.spreadsheets.values.get({ // 수정: this.sheets
            auth: this.auth,
            spreadsheetId: this.sheetName,
            range: this.worksheetName,
        });
        return response.data.values;
    }

    // 데이터프레임으로 가져오기
    async getAsDataFrame() {
        const records = await this.getAllRecords();
        return records.map(row => Object.assign({}, ...row.map((cell, index) => ({ [records[0][index]]: cell }))));
    }

    // 모든 행 가져오기
    async getAllRows() {
        return await this.getAllRecords();
    }

    // 특정 행 가져오기
    async getRow(row) {
        const rows = await this.getAllRows();
        return rows[row - 1];
    }

    // 특정 열 가져오기
    async getCol(col) {
        const rows = await this.getAllRows();
        return rows.map(row => row[col - 1]);
    }

    // 열 이름 보기
    async getColName() {
        const records = await this.getAllRecords();
        return records[0];
    }

    // 특정 셀 가져오기
    async getCell(row, col) {
        const rows = await this.getAllRows();
        return rows[row - 1][col - 1];
    }

    // 특정 셀 수정하기
    async updateCell(row, col, value) {
        await this.sheets.spreadsheets.values.update({ // 수정: this.sheets
            auth: this.auth,
            spreadsheetId: this.sheetName,
            range: `${this.worksheetName}!${this.colNumToColLetter(col)}${row}`,
            valueInputOption: 'RAW',
            resource: {
                values: [[value]],
            },
        });
    }

    // 행 추가하기
    async insertRow(row, values) {
        const range = `${this.worksheetName}!A${row}`;
        await this.sheets.spreadsheets.values.insert({ // 수정: this.sheets
            auth: this.auth,
            spreadsheetId: this.sheetName,
            range: range,
            valueInputOption: 'RAW',
            resource: {
                values: [values],
            },
        });
    }

    // 마지막 행에 추가하기
    async appendRow(values) {
        const range = `${this.worksheetName}!A1`;
        await this.sheets.spreadsheets.values.append({ // 수정: this.sheets
            auth: this.auth,
            spreadsheetId: this.sheetName,
            range: range,
            valueInputOption: 'RAW',
            resource: {
                values: [values],
            },
        });
    }

    // 특정 값을 가진 행 삭제하기
    async deleteRowByValue(value) {
        const rows = await this.getAllRows();
        const rowIndex = rows.findIndex(row => row.includes(value));
        if (rowIndex !== -1) {
            await this.deleteRow(rowIndex + 1);
        }
    }

    // 특정 행 삭제하기
    async deleteRow(row) {
        const batchUpdateRequest = {
            requests: [{
                deleteDimension: {
                    range: {
                        sheetId: this.worksheetId,
                        dimension: 'ROWS',
                        startIndex: row - 1,
                        endIndex: row,
                    },
                },
            }],
        };
        await this.sheets.spreadsheets.batchUpdate({ // 수정: this.sheets
            auth: this.auth,
            spreadsheetId: this.sheetName,
            resource: batchUpdateRequest,
        });
    }

    // 셀 업데이트
    async updateRowByColName(row, data) {
        const colNames = await this.getColName();
        const values = colNames.map(col => (data[col] !== undefined ? data[col] : ''));
        
        await this.sheets.spreadsheets.values.update({ // 수정: this.sheets
            auth: this.auth,
            spreadsheetId: this.sheetName,
            range: `${this.worksheetName}!A${row}:${this.colNumToColLetter(colNames.length)}${row}`,
            valueInputOption: 'RAW',
            resource: {
                values: [values],
            },
        });
    }

    // 열 번호를 문자로 변환
    colNumToColLetter(colNum) {
        let letter = '';
        while (colNum > 0) {
            const remainder = (colNum - 1) % 26;
            letter = String.fromCharCode(65 + remainder) + letter;
            colNum = Math.floor((colNum - 1) / 26);
        }
        return letter;
    }
}

// module.exports = GoogleSheet;
