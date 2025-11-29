//src/auth/AuthWrapper.tsx
import { type ReactNode, useMemo } from "react";
import { useAuth } from "react-oidc-context";
import LoadingScreen from "../components/LoadingScreen";
import Navbar from "../components/Navbar";
import { cognitoAuthConfig, createCognitoLogoutUrl } from "../config/AuthConfig";

export function AuthWrapper({ children }: { children: ReactNode }) {
  const auth = useAuth();
  const params = new URLSearchParams(window.location.search);
  const oauthErrorDesc = params.get("error_description");

  const signOut = async () => {
    await auth.removeUser();
    const href = createCognitoLogoutUrl(cognitoAuthConfig);
    window.location.href = href;
  };

  const errorMessage = useMemo(() => {
    if (!oauthErrorDesc) return null;

    if (oauthErrorDesc.includes("Unauthorized")) {
      return "Your account is not authorized to access this interface.";
    }

    return oauthErrorDesc;
  }, [oauthErrorDesc]);

  switch (auth.activeNavigator) {
    case "signinSilent":
      return <div>Signing you in...</div>;
    case "signoutRedirect":
      return <div>Signing you out...</div>;
  }

  if (auth.isLoading) return <LoadingScreen />;

  if (auth.error) return <div>Oops... {auth.error.message}</div>;

  if (errorMessage) return <div>Oops... {errorMessage}</div>;

  // if (!auth.isAuthenticated) return <div>Please log in</div>;

  // if (auth.error) return <LoginPage errorMessage={auth.error.message} />;

  // if (errorMessage) return <LoginPage errorMessage={errorMessage} />;

  // if (!auth.isAuthenticated) return <LoginPage />;

  return (
    <>
      <Navbar signOut={signOut}/>
      {children}
    </>
  );
}