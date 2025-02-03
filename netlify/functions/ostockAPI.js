exports.handler = async (event, context) => {
    const url = "http://13.125.209.13:8000/command"; // FastAPI 서버의 IP 주소와 포트
    const data = {
        command: "start", // 호출할 명령어
        args: [] // 인자
    };

    try {
        const response = await fetch(url, {
            method: "POST", // HTTP 메서드
            headers: {
                "Content-Type": "application/json" // 요청 헤더 설정
            },
            body: JSON.stringify(data) // 요청 본문을 JSON 문자열로 변환
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json(); // 응답을 JSON으로 변환

        return {
            statusCode: 200,
            body: JSON.stringify(result)
        };
    } catch (error) {
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};