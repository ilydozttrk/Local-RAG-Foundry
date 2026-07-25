import { useEffect, useState } from "react";
import { getHealth } from "../services/api";

export default function Status() {
  const [online, setOnline] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await getHealth();
        setOnline(true);
      } catch {
        setOnline(false);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  if (loading) {
    return <p>Checking backend...</p>;
  }

  return (
    <div>
      {online ? (
        <p>🟢 Backend Online</p>
      ) : (
        <p>🔴 Backend Offline</p>
      )}
    </div>
  );
}