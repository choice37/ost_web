exports.handler = async function(event, context) {
    const accessToken = process.env.accessToken;
    return {
      statusCode: 200,
      body: JSON.stringify({ accessToken })
    };
  };