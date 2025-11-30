import { useState } from "react";
import { useAuth } from "react-oidc-context";
import { fetchCalendarTrips } from "../api/calendar";

export function SyncCalendarTripsButton() {
  const auth = useAuth();
  const [loading, setLoading] = useState(false);
  const [trips, setTrips] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [synced, setSynced] = useState(false);

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
      setSynced(true);
    } catch (e: any) {
      console.error(e);
      setError(e.message ?? "Unknown error");
      setSynced(false);
    } finally {
      setLoading(false);
    }
  };

  const disabled = loading || !auth.isAuthenticated;
  const label = loading ? "Syncing trips..." : synced ? "Calendar synced" : " Sync Calendar Trips";
  const buttonTone = synced && !loading ? "border-emerald-200 bg-emerald-50 text-emerald-700" : "border-slate-200 bg-white text-slate-700 hover:-translate-y-0.5 hover:bg-slate-50";

  return (
    <div className="flex flex-col items-stretch text-left">
      <button
        onClick={handleClick}
        disabled={disabled}
        className={`rounded-full border px-5 py-2 text-sm font-semibold transition ${
          disabled
            ? "cursor-not-allowed border-slate-200 bg-slate-100 text-slate-400"
            : buttonTone
        }`}
      >
        {label}
      </button>

      {error && <p className="mt-2 text-xs text-red-500">Error: {error}</p>}

      {!error && synced && !loading && (
        <p className="mt-2 text-xs text-emerald-600">Calendar is in sync with your trips.</p>
      )}

      {trips && trips.length > 0 && (
        <ul className="mt-2 max-h-48 w-64 overflow-y-auto rounded-2xl border border-slate-200 bg-white p-3 text-xs text-slate-600 shadow-lg">
          {trips.map((t) => (
            <li key={t.id} className="py-1">
              <p className="font-semibold text-slate-800">{t.summary}</p>
              <p className="text-[0.7rem] text-slate-500">{t.start?.dateTime || t.start?.date}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
