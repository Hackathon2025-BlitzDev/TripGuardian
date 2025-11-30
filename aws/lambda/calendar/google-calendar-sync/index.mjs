import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";

const ddb = DynamoDBDocumentClient.from(
  new DynamoDBClient({ region: process.env.AWS_REGION })
);

const GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token";

export const handler = async (event) => {
  // const claims = event.requestContext?.authorizer?.jwt?.claims;

  // if (!claims || !claims.sub) {
  //   return { statusCode: 401, body: "Unauthorized" };
  // }

  // const userId = claims.sub;

  const method = event.requestContext?.http?.method;

  if (method === "OPTIONS") {
    return {
      statusCode: 204,
      headers: {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Headers": "Authorization,Content-Type",
        "Access-Control-Allow-Methods": "GET,OPTIONS",
      },
      body: "",
    };
  }

  const authHeader =
    event.headers?.authorization || event.headers?.Authorization;

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return {
      statusCode: 401,
      headers: {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Headers": "Authorization,Content-Type",
        "Access-Control-Allow-Methods": "GET,OPTIONS",
      },
      body: "Missing or invalid Authorization header",
    };
  }

  const token = authHeader.slice("Bearer ".length);

  let userId;
  try {
    const [, payloadBase64] = token.split(".");
    const payloadJson = Buffer.from(payloadBase64, "base64").toString("utf8");
    const payload = JSON.parse(payloadJson);
    userId = payload.sub;
  } catch (e) {
    console.error("Failed to parse JWT", e);
    return {
      statusCode: 401,
      headers: {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Headers": "Authorization,Content-Type",
        "Access-Control-Allow-Methods": "GET,OPTIONS",
      },
      body: "Invalid token",
    };
  }

  if (!userId) {
    return {
      statusCode: 401,
      headers: {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Headers": "Authorization,Content-Type",
        "Access-Control-Allow-Methods": "GET,OPTIONS",
      },
      body: "No sub in token",
    };
  }

  const dbResp = await ddb.send(
    new GetCommand({
      TableName: process.env.TABLE_NAME,
      Key: { userId },
    })
  );

  const record = dbResp.Item;
  if (!record || !record.refreshToken) {
    return {
      statusCode: 400,
      body: "Google Calendar not connected",
    };
  }

  const refreshToken = record.refreshToken;

  const params = new URLSearchParams({
    client_id: process.env.GOOGLE_CALENDAR_CLIENT_ID,
    client_secret: process.env.GOOGLE_CALENDAR_CLIENT_SECRET,
    refresh_token: refreshToken,
    grant_type: "refresh_token",
  });

  const tokenResp = await fetch(GOOGLE_TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params.toString(),
  });

  if (!tokenResp.ok) {
    const text = await tokenResp.text();
    console.error("Google refresh error", tokenResp.status, text);
    return { statusCode: 500, body: "Google refresh error" };
  }

  const tokenData = await tokenResp.json();
  const accessToken = tokenData.access_token;

  // Call Google Calendar API
  const timeMin = new Date().toISOString();
  const timeMax = new Date(Date.now() + 7 * 24 * 3600 * 1000).toISOString();

  const eventsResp = await fetch(
    "https://www.googleapis.com/calendar/v3/calendars/primary/events?" +
    new URLSearchParams({
      singleEvents: "true",
      orderBy: "startTime",
      timeMin,
      timeMax,
    }),
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!eventsResp.ok) {
    const text = await eventsResp.text();
    console.error("Calendar API error", eventsResp.status, text);
    return { statusCode: 500, body: "Calendar API error" };
  }

  const eventsData = await eventsResp.json();

  const trips = (eventsData.items || []).map((e) => ({
    id: e.id,
    summary: e.summary,
    start: e.start,
    end: e.end,
    location: e.location,
  }));

  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "*"
      // "Access-Control-Allow-Origin": "http://localhost:5173",
      // "Access-Control-Allow-Headers": "Authorization,Content-Type"
    },
    body: JSON.stringify({ trips }),
  };
};