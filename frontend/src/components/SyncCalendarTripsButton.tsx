import { useState } from "react";
import { useAuth } from "react-oidc-context";
import { fetchCalendarTrips } from "../api/calendar";

export function SyncCalendarTripsButton() {
  const auth = useAuth();
  const [loading, setLoading] = useState(false);
  const [trips, setTrips] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleClick = async () => {
    setError(null);
    setLoading(true);

    try {
      const user = auth.user;
      if (!user) {
        throw new Error("Not authenticated");
      }

      // react-oidc-context typicky drží id_token aj access_token:
      const idToken =
        (user as any).id_token || (user as any).access_token || user?.access_token;

      if (!idToken) {
        throw new Error("Missing ID/access token");
      }

      const data = await fetchCalendarTrips(idToken);
      setTrips(data.trips);
    } catch (e: any) {
      console.error(e);
      setError(e.message ?? "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleClick} disabled={loading || !auth.isAuthenticated}>
        {loading ? "Syncing..." : "Sync trips from Google Calendar"}
      </button>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {trips && (
        <ul>
          {trips.map((t) => (
            <li key={t.id}>
              {t.summary} – {t.start?.dateTime || t.start?.date}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
