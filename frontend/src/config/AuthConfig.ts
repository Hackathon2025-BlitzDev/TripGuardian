import {
  COGNITO_DOMAIN,
  AUTHORITY,
  CLIENT_ID,
  COGNITO_REDIRECT_URI,
  SCOPE,
  LOGOUT_URI,
} from "./cognito";

export const cognitoAuthConfig: CognitoAuthConfig = {
  authority: AUTHORITY,
  domain: COGNITO_DOMAIN,
  response_type: "code",
  client_id: CLIENT_ID,
  scope: SCOPE,
  redirect_uri: COGNITO_REDIRECT_URI,
  post_logout_redirect_uri: LOGOUT_URI,
};

export const createCognitoLogoutUrl = (config: CognitoAuthConfig) => {
  const params = new URLSearchParams({
    client_id: config.client_id,
    logout_uri: config.post_logout_redirect_uri,
  });

  return `${config.domain}/logout?${params.toString()}`;
};