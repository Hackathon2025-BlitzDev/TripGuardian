import { Navigate, Route, Routes } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "react-oidc-context";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";

const PrivateRoute = ({ children }: { children: ReactNode }) => {
  const auth = useAuth();

  if (!auth.isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

function App() {
  const auth = useAuth();

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="*"
        element={<Navigate to={auth.isAuthenticated ? "/dashboard" : "/"} replace />}
      />
    </Routes>
  );
}

export default App;
