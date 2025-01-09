const fetch = require("node-fetch");

exports.handler = async (event) => {
  const NOTION_API_KEY = "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"; // Notion API 키
  const DATABASE_ID = "176bf32b3c57802881e5ff483f23b37a"; // 데이터베이스 ID

  // HTTP POST 요청만 허용
  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      body: JSON.stringify({ message: "Only POST requests are allowed" }),
    };
  }

  try {
    const { title, content } = JSON.parse(event.body); // 요청 본문에서 데이터 추출

    // Notion API 호출
    const response = await fetch("https://api.notion.com/v1/pages", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${NOTION_API_KEY}`,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
      },
      body: JSON.stringify({
        parent: { database_id: DATABASE_ID },
        properties: {
          "제목 ": {
            title: [
              {
                text: {
                  content: title,
                },
              },
            ],
          },
          "내용": {
            rich_text: [
              {
                text: {
                  content: content,
                },
              },
            ],
          },
        },
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || "Failed to add data to Notion");
    }

    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Success", url: result.url }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ message: error.message }),
    };
  }
};
