// netlify/functions/getEnvVariables.js
exports.handler = async function(event, context) {
    const repoOwner = process.env.REPO_OWNER;  // 환경변수에서 repoOwner 가져오기
    const repoName = process.env.REPO_NAME;    // 환경변수에서 repoName 가져오기
    const accessToken = process.env.ACCESS_TOKEN; // 환경변수에서 accessToken 가져오기
  
    return {
      statusCode: 200,
      body: JSON.stringify({ repoOwner, repoName, accessToken }),  // JSON 형태로 반환
    };
  };