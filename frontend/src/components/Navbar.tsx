import { useAuth } from "react-oidc-context";

type NavbarProps = {
  signOut: () => void;
};

const Navbar = ({ signOut }: NavbarProps) => {
  const auth = useAuth();

  return (
    <nav className="flex flex-row justify-end items-center p-4">
      {auth.isAuthenticated ? (
        <button onClick={signOut}>Sign out</button> 
      ) : (
        <button onClick={() => auth.signinRedirect()}>Sign in</button>
      )}
    </nav>
  );
};

export default Navbar;
