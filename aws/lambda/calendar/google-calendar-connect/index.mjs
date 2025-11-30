const GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth";

export const handler = async (event) => {
  const userId = event.queryStringParameters?.userId;

  if (!userId) {
    return {
      statusCode: 400,
      body: "Missing userId",
    };
  }

  // state – aby sme v callbacku vedeli, komu token patrí
  const stateObj = { userId };
  const state = Buffer.from(JSON.stringify(stateObj)).toString("base64url");

  const params = new URLSearchParams({
    client_id: process.env.GOOGLE_CALENDAR_CLIENT_ID,
    redirect_uri: process.env.GOOGLE_CALENDAR_REDIRECT_URI,
    response_type: "code",
    access_type: "offline",
    prompt: "consent",
    scope: "https://www.googleapis.com/auth/calendar.readonly",
    include_granted_scopes: "true",
    state,
  });

  const redirectUrl = `${GOOGLE_AUTH_URL}?${params.toString()}`;

   return {
    statusCode: 302,
    headers: {
      Location: redirectUrl,
    },
    body: "",
  };
};