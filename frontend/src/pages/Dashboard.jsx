import { useEffect, useState } from "react";
import api from "../services/api";

function Dashboard() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const { data } = await api.get("/api/resume/history/");
        setItems(data);
      } catch (err) {
        setError("Failed to load history");
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      {error && <p className="text-red-600">{error}</p>}
      <div className="grid gap-4">
        {items.map((item) => (
          <div key={item.id} className="rounded-lg bg-white p-4 shadow">
            <p className="font-medium">Predicted Role: {item.predicted_role}</p>
            <p className="text-sm">Match: {item.match_score}%</p>
            <p className="text-sm">Missing: {item.skills_missing.join(", ") || "None"}</p>
            <p className="text-xs text-slate-500">{new Date(item.created_at).toLocaleString()}</p>
          </div>
        ))}
        {items.length === 0 && <p className="text-sm text-slate-500">No analysis history found.</p>}
      </div>
    </div>
  );
}

export default Dashboard;
