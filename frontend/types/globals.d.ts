type ApiSourceRecord = {
  source_id: string;
  city?: string;
  country?: string;
  enabled?: boolean;
  lat_est?: number;
  lon_est?: number;
  name?: string;
  platform?: string;
  schedule_cron?: string;
  status?: string;
  type?: string;
  url?: string;
};

type SourceRecord = {
  sourceId: string;
  city: string;
  country: string;
  enabled: boolean;
  latEst: number;
  lonEst: number;
  name: string;
  platform: string;
  scheduleCron: string;
  status: string;
  type: string;
  url: string;
};

type CognitoAuthConfig = {
  authority: string;
  domain: string;
  client_id: string;
  response_type: "code";
  scope: string;
  redirect_uri: string;
  post_logout_redirect_uri: string;
};

type LoginCallbackUriType = {
  domain: string;
  client_id: string;
  response_type: string;
  scope: string;
  redirect_uri: string;
};

type LogoutCallbackUriType = {
  domain: string;
  client_id: string;
  post_logout_redirect_uri: string;
};

type User = {
  email: string;
  createdAt?: string;
  createdBy?: string;
  deleted?: boolean | null;
};

interface SlideArrowButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  text?: string;
  primaryColor?: string;
  secondaryColor?: string;
}