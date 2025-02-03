// API 호출 함수
async function callApi() {
    const url = "http://14.52.72.42:8000/command"; // FastAPI 서버의 IP 주소와 포트
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
        console.log("응답:", result); // 응답 출력
    } catch (error) {
        console.error("오류 발생:", error); // 오류 처리
    }
}

// API 호출 실행
callApi();