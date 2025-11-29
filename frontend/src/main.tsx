import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import { AuthProvider } from "react-oidc-context";
import { cognitoAuthConfig } from "./config/AuthConfig.ts";
import { AuthWrapper } from "./auth/AuthWrapper.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AuthProvider {...cognitoAuthConfig}>
      <AuthWrapper>
        <App />
      </AuthWrapper>
    </AuthProvider>
  </StrictMode>
);
