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

export const isSavedTripRecord = (value: unknown): value is SavedTripRecord => {
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
