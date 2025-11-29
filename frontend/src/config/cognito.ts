export const COGNITO_DOMAIN = import.meta.env.VITE_COGNITO_DOMAIN as string;

export const COGNITO_REGION = import.meta.env.VITE_COGNITO_REGION as string;

export const AUTHORITY = import.meta.env.VITE_COGNITO_AUTHORITY as string;

export const CLIENT_ID = import.meta.env
  .VITE_COGNITO_CLIENT_ID as string;

export const COGNITO_REDIRECT_URI = import.meta.env
  .VITE_COGNITO_REDIRECT_URI as string;
export const APP_LOGOUT_REDIRECT = import.meta.env
  .VITE_APP_LOGOUT_REDIRECT as string;

export const SCOPE = import.meta.env.VITE_COGNITO_SCOPE as string;
export const LOGOUT_URI = import.meta.env.VITE_COGNITO_POST_LOGOUT_REDIRECT_URI as string;