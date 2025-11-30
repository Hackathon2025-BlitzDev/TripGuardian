import { useAuth } from "react-oidc-context";
import { getCalendarConnectUrl } from "../api/calendar";

export function ConnectGoogleCalendarButton() {
  const auth = useAuth();

  const handleClick = () => {
    const user = auth.user;
    const sub = user?.profile?.sub as string | undefined;

    if (!sub) {
      console.error("User not logged in or sub missing");
      return;
    }

    const url = getCalendarConnectUrl(sub);
    window.location.href = url; // spustí OAuth flow
  };

  const disabled = !auth.isAuthenticated;

  return (
    <button disabled={disabled} onClick={handleClick}>
      Connect Google Calendar
    </button>
  );
}