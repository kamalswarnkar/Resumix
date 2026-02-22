import { useEffect, useState } from "react";
import api from "../services/api";

function Admin() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadAdminData = async () => {
      try {
        const [usersRes, statsRes] = await Promise.all([
          api.get("/api/admin/users/"),
          api.get("/api/admin/stats/"),
        ]);
        setUsers(usersRes.data);
        setStats(statsRes.data);
      } catch (err) {
        setError("Unable to load admin data");
      }
    };

    loadAdminData();
  }, []);

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold">Admin Dashboard</h1>
      {error && <p className="text-red-600">{error}</p>}

      {stats && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded bg-white p-4 shadow">Users: {stats.total_users}</div>
          <div className="rounded bg-white p-4 shadow">Resumes: {stats.total_resumes}</div>
          <div className="rounded bg-white p-4 shadow">Analyses: {stats.total_analyses}</div>
          <div className="rounded bg-white p-4 shadow">Avg Match: {stats.average_match_score}%</div>
        </div>
      )}

      <div className="rounded-lg bg-white p-4 shadow">
        <h2 className="mb-2 text-lg font-semibold">Users</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b">
                <th className="p-2">Email</th>
                <th className="p-2">Name</th>
                <th className="p-2">Role</th>
                <th className="p-2">Active</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-b">
                  <td className="p-2">{user.email}</td>
                  <td className="p-2">{user.first_name} {user.last_name}</td>
                  <td className="p-2">{user.role}</td>
                  <td className="p-2">{String(user.is_active)}</td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td className="p-2 text-slate-500" colSpan={4}>No users found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Admin;
