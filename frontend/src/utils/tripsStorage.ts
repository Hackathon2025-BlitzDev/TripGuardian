export type SavedTripBasics = {
  start: string;
  destination: string;
  stops: string[];
  startDate: string | null;
  endDate: string | null;
  flexibleDates: boolean;
};

export type SavedTripPreferences = {
  categories: string[];
  transport: string;
  budget: string;
  notes: string;
};

export type SavedTripRecord = {
  id: string;
  title: string;
  createdAt: string;
  startDate: string | null;
  endDate: string | null;
  categories: string[];
  transport: string;
  summary: string;
  stopCount: number;
  coverImage: string;
  planSnapshot: unknown;
  basics: SavedTripBasics;
  preferences: SavedTripPreferences;
};

const STORAGE_KEY = "tripguardian:savedTrips";
export const SAVED_TRIPS_EVENT = "tripguardian:savedTripsUpdated";
const PLANNER_RESUME_KEY = "tripguardian:plannerResume";

const isSavedTripRecord = (value: unknown): value is SavedTripRecord => {
  if (!value || typeof value !== "object") return false;
  const record = value as Record<string, unknown>;
  return (
    typeof record.id === "string" &&
    typeof record.title === "string" &&
    typeof record.createdAt === "string" &&
    (typeof record.startDate === "string" || record.startDate === null || record.startDate === undefined) &&
    (typeof record.endDate === "string" || record.endDate === null || record.endDate === undefined) &&
    Array.isArray(record.categories) &&
    typeof record.transport === "string" &&
    typeof record.summary === "string" &&
    typeof record.stopCount === "number" &&
    typeof record.coverImage === "string" &&
    record.basics != null &&
    typeof (record.basics as SavedTripBasics).start === "string" &&
    typeof (record.basics as SavedTripBasics).destination === "string" &&
    Array.isArray((record.basics as SavedTripBasics).stops) &&
    typeof (record.basics as SavedTripBasics).flexibleDates === "boolean" &&
    (typeof (record.basics as SavedTripBasics).startDate === "string" || (record.basics as SavedTripBasics).startDate === null) &&
    (typeof (record.basics as SavedTripBasics).endDate === "string" || (record.basics as SavedTripBasics).endDate === null) &&
    record.preferences != null &&
    Array.isArray((record.preferences as SavedTripPreferences).categories) &&
    typeof (record.preferences as SavedTripPreferences).transport === "string" &&
    typeof (record.preferences as SavedTripPreferences).budget === "string" &&
    typeof (record.preferences as SavedTripPreferences).notes === "string"
  );
};

const readStorage = (): SavedTripRecord[] => {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((item): item is SavedTripRecord => isSavedTripRecord(item));
  } catch (error) {
    console.warn("Failed to read saved trips", error);
    return [];
  }
};

const writeStorage = (records: SavedTripRecord[]) => {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
  window.dispatchEvent(new Event(SAVED_TRIPS_EVENT));
};

export const loadSavedTrips = (): SavedTripRecord[] => readStorage();

export const saveTripToStorage = (trip: SavedTripRecord): SavedTripRecord[] => {
  const existing = readStorage().filter((item) => item.id !== trip.id);
  const next = [trip, ...existing];
  writeStorage(next);
  return next;
};

export const clearSavedTrips = () => writeStorage([]);

export const stagePlannerResume = (trip: SavedTripRecord) => {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(PLANNER_RESUME_KEY, JSON.stringify(trip));
};

export const consumePlannerResume = (): SavedTripRecord | null => {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(PLANNER_RESUME_KEY);
  if (!raw) return null;
  window.localStorage.removeItem(PLANNER_RESUME_KEY);
  try {
    const parsed = JSON.parse(raw);
    return isSavedTripRecord(parsed) ? parsed : null;
  } catch (error) {
    console.warn("Invalid planner resume payload", error);
    return null;
  }
};
