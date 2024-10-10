const { google } = require('googleapis');
const fs = require('fs');

class GoogleSheet {
    constructor(sheetName, worksheetName) {
        this.sheetName = sheetName;
        this.worksheetName = worksheetName;
        this.auth = null;
        this.sheets = null;
        this.worksheetId = null;
    }

    async initialize() {
        this.auth = await this.authenticate();
        this.sheets = google.sheets({ version: 'v4', auth: this.auth });
    }

    async authenticate() {
        // const credentials = JSON.parse(fs.readFileSync('bgm-537-b9fa3d50e755.json'));
        // const { client_email, private_key } = credentials;
        const client_email = process.env.client_email;  // 환경변수에서 repoOwner 가져오기
        const private_key = process.env.private_key;    // 환경변수에서 repoName 가져오기
        console.log(client_email);

        const auth = new google.auth.JWT({
            email: client_email,
            key: private_key,
            scopes: ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        });

        return auth;
    }

    async getAllRecords() {
        const response = await this.sheets.spreadsheets.values.get({
            auth: this.auth,
            spreadsheetId: this.sheetName,
            range: this.worksheetName,
        });
        return response.data.values;
    }
}

exports.handler = async (event, context) => {
    try {
        const { sheetName, worksheetName } = JSON.parse(event.body); // 클라이언트에서 전달받은 시트 정보
        const googleSheet = new GoogleSheet(sheetName, worksheetName);
        await googleSheet.initialize(); // Google Sheets API 초기화
        const records = await googleSheet.getAllRecords(); // 모든 레코드 가져오기

        return {
            statusCode: 200,
            body: JSON.stringify(records), // 레코드를 JSON으로 반환
        };
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Internal Server Error' }),
        };
    }
};
