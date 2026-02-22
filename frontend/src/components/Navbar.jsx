import { Link, useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access");
  const user = JSON.parse(localStorage.getItem("user") || "null");

  const logout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <nav className="border-b bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/dashboard" className="text-xl font-bold text-brand">Resumix</Link>
        <div className="flex items-center gap-4 text-sm">
          {token && <Link to="/upload">Upload</Link>}
          {token && <Link to="/dashboard">Dashboard</Link>}
          {token && user?.role === "admin" && <Link to="/admin">Admin</Link>}
          {!token && <Link to="/login">Login</Link>}
          {!token && <Link to="/register">Register</Link>}
          {token && (
            <button onClick={logout} className="rounded bg-brand px-3 py-1 text-white">
              Logout
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
