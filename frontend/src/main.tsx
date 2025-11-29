import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./index.css";
import App from "./App.tsx";
import { AuthProvider } from "react-oidc-context";
import { cognitoAuthConfig } from "./config/AuthConfig.ts";
import { AuthWrapper } from "./auth/AuthWrapper.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider {...cognitoAuthConfig}>
        <AuthWrapper>
          <App />
        </AuthWrapper>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
