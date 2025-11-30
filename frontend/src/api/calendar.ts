const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

if (!API_BASE_URL) {
  console.warn("VITE_API_BASE_URL is not set");
}

export function getCalendarConnectUrl(userId: string) {
  const url = new URL("/api/calendar/connect", API_BASE_URL);
  url.searchParams.set("userId", userId);
  return url.toString();
}

export async function fetchCalendarTrips(idToken: string) {
  const res = await fetch(`${API_BASE_URL}/api/calendar/sync`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${idToken}`,
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Calendar sync failed: ${res.status} ${text}`);
  }

  return res.json() as Promise<{ trips: any[] }>;
}