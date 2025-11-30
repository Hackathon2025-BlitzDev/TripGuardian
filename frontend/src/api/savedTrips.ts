import type { SavedTripRecord } from "../utils/tripsStorage";

const buildApiUrl = (path: string) => {
  const base = import.meta.env.VITE_API_BASE_URL;
  if (!base) {
    throw new Error("Missing VITE_API_BASE_URL environment variable");
  }
  try {
    const normalizedPath = path.startsWith("/") ? path.slice(1) : path;
    return new URL(normalizedPath, base).toString();
  } catch (error) {
    console.error("Invalid API base URL", error);
    throw new Error("Invalid API base URL");
  }
};

export const fetchSavedTrips = async (): Promise<SavedTripRecord[]> => {
  const url = buildApiUrl("api/trips");
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`Unable to load saved trips (${response.status})`);
  }
  return (await response.json()) as SavedTripRecord[];
};

export const createSavedTrip = async (trip: SavedTripRecord): Promise<SavedTripRecord> => {
  const url = buildApiUrl("api/trips");
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(trip),
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Failed to save trip");
  }
  return (await response.json()) as SavedTripRecord;
};
