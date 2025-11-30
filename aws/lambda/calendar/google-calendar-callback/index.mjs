import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand } from "@aws-sdk/lib-dynamodb";

const ddb = DynamoDBDocumentClient.from(
  new DynamoDBClient({ region: process.env.AWS_REGION })
);

const GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token";

export const handler = async (event) => {
  try {
    const qs = event.queryStringParameters || {};
    const code = qs.code;
    const stateEncoded = qs.state;

    if (!code || !stateEncoded) {
      return {
        statusCode: 400,
        body: "Missing code or state",
      };
    }

    let userId;
    try {
      const stateJson = Buffer.from(stateEncoded, "base64url").toString("utf8");
      const state = JSON.parse(stateJson);
      userId = state.userId;
    } catch (e) {
      console.error("State decode error", e);
      return { statusCode: 400, body: "Invalid state" };
    }

    if (!userId) {
      console.error("No userId in state");
      return {
        statusCode: 400,
        headers: { "Content-Type": "text/plain" },
        body: "Missing userId in state",
      };
    }

    const params = new URLSearchParams({
      code,
      client_id: process.env.GOOGLE_CALENDAR_CLIENT_ID,
      client_secret: process.env.GOOGLE_CALENDAR_CLIENT_SECRET,
      redirect_uri: process.env.GOOGLE_CALENDAR_REDIRECT_URI,
      grant_type: "authorization_code",
    });

    const tokenResp = await fetch(GOOGLE_TOKEN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: params.toString(),
    });

    if (!tokenResp.ok) {
      const text = await tokenResp.text();
      console.error("Google token error", tokenResp.status, text);
      return { statusCode: 500, body: "Google token error" };
    }

    const tokenData = await tokenResp.json();
    console.log("Token data", tokenData);

    const refreshToken = tokenData.refresh_token;
    if (!refreshToken) {
      return {
        statusCode: 400,
        body: "No refresh_token received from Google",
      };
    }

    const now = new Date().toISOString();
    await ddb.send(
      new PutCommand({
        TableName: process.env.TABLE_NAME,
        Item: {
          userId,
          refreshToken,
          connectedAt: now,
        },
      })
    );

    const frontendRedirect =
      process.env.FRONTEND_SUCCESS_URL;

    return {
      statusCode: 302,
      headers: {
        Location: frontendRedirect,
      },
      body: "",
    };
  } catch (e) {
    console.error("Error", e);
    return {
      statusCode: 500,
      body: "Internal server error",
    };
  };
}