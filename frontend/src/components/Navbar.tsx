import { Link } from "react-router-dom";
import { useAuth } from "react-oidc-context";

type NavbarProps = {
  signOut: () => void;
};

const Navbar = ({ signOut }: NavbarProps) => {
  const auth = useAuth();

  return (
    <header className="sticky top-0 z-30 w-full bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <Link to="/" className="flex flex-col items-center gap-3 text-center sm:flex-row sm:text-left">
          <img src="/logo1.png" alt="TripGuardian logo" className="h-10 w-10 rounded-full" />
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.35em] text-slate-400">TripGuardian</p>
            <p className="text-base font-semibold text-slate-900">AI Travel Planner</p>
          </div>
        </Link>

        <div className="flex flex-wrap items-center justify-center gap-3 text-sm font-medium text-slate-600 sm:justify-end">
          <Link
            to="/trips"
            className="rounded-full border border-transparent px-5 py-2 transition hover:border-slate-200 hover:bg-slate-50"
          >
            My Trips
          </Link>
          {auth.isAuthenticated ? (
            <button
              onClick={signOut}
              className="rounded-full border border-slate-200 px-5 py-2 font-semibold text-color transition hover:-translate-y-0.5 hover:bg-slate-900 hover:text-white"
            >
              Sign out
            </button>
          ) : (
            <button
              onClick={() => auth.signinRedirect()}
              className="rounded-full bg-slate-900 px-5 py-2 font-semibold text-color shadow-[0_15px_30px_rgba(15,23,42,0.35)] transition hover:-translate-y-0.5 hover:bg-slate-800"
            >
              Sign in
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
