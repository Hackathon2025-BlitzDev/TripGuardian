import { useCallback, useEffect, useMemo, useState } from "react";
import { useAuth } from "react-oidc-context";
import { Link, useNavigate } from "react-router-dom";
import {
  LuCalendar,
  LuFlag,
  LuMapPin,
  LuHeart,
  LuBookmark,
} from "react-icons/lu";
import { fetchSavedTrips } from "../api/savedTrips";
import type { SavedTripRecord } from "../utils/tripsStorage";

const plannedRoutes = [
  { id: 1, title: "Lisabon → Porto", start: "5. 1. 2026", status: "AI itinerár sa generuje", progress: 65 },
  { id: 2, title: "Berlín → Kodaň", start: "18. 2. 2026", status: "Čaká sa na potvrdenie", progress: 35 },
  { id: 3, title: "Tokyo → Kyoto", start: "12. 3. 2026", status: "Väčšina hotová", progress: 85 },
];

const tagColors = [
  "bg-rose-50 text-rose-500",
  "bg-emerald-50 text-emerald-600",
  "bg-indigo-50 text-indigo-600",
  "bg-amber-50 text-amber-600",
  "bg-cyan-50 text-cyan-600",
];

const FALLBACK_TRIP_IMAGE = "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=60";
const buildAttractionImageUrl = (placeName: string, locationName?: string) => {
  const terms = [placeName, locationName].filter(Boolean).join(", ").trim() || "travel destination";
  return `https://source.unsplash.com/900x600/?${encodeURIComponent(terms)}`;
};

const tryParseJson = (value: unknown): Record<string, unknown> | null => {
  if (value && typeof value === "object") return value as Record<string, unknown>;
  if (typeof value !== "string") return null;
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === "object" ? (parsed as Record<string, unknown>) : null;
  } catch {
    return null;
  }
};

const extractPlanLocations = (snapshot: unknown): unknown[] => {
  if (!snapshot) return [];
  const source = tryParseJson(snapshot);
  if (!source) return [];
  if (Array.isArray(source.locations)) return source.locations;
  if (source.planResult && typeof source.planResult === "object") {
    const nested = source.planResult as Record<string, unknown>;
    if (Array.isArray(nested.locations)) return nested.locations;
  }
  return [];
};

const extractPlaceImage = (place: unknown, locationName?: string): string | null => {
  if (!place || typeof place !== "object") return null;
  const record = place as Record<string, unknown>;
  if (Array.isArray(record.images)) {
    const valid = record.images.find((img) => typeof img === "string" && img.trim().length > 0);
    if (typeof valid === "string") return valid;
  }
  const imageLikeKeys = ["image_url", "image", "photo"] as const;
  for (const key of imageLikeKeys) {
    const value = record[key];
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }
  const name = typeof record.name === "string" ? record.name : "attraction";
  return buildAttractionImageUrl(name, locationName);
};

const deriveTripImage = (trip: SavedTripRecord): string => {
  if (trip.coverImage && trip.coverImage.trim().length > 0) return trip.coverImage;
  const snapshotSource = trip.planSnapshot ?? (trip as Record<string, unknown>).planResult;
  const locations = extractPlanLocations(snapshotSource);
  for (const location of locations) {
    if (!location || typeof location !== "object") continue;
    const record = location as Record<string, unknown>;
    const locationName = typeof record.location === "string" ? record.location : undefined;
    const places = Array.isArray(record.places) ? record.places : [];
    for (const place of places) {
      const image = extractPlaceImage(place, locationName);
      if (image) return image;
    }
  }
  return buildAttractionImageUrl(trip.title || "trip");
};

const Trips = () => {
  const auth = useAuth();
  const navigate = useNavigate();
  const [savedTrips, setSavedTrips] = useState<SavedTripRecord[]>([]);
  const [loadingTrips, setLoadingTrips] = useState(true);
  const [tripsError, setTripsError] = useState<string | null>(null);
  const welcomeCopy = useMemo(
    () => ({
      heading: "Moje výlety",
      subheading: "Prehľad všetkých naplánovaných a uložených výletov",
    }),
    []
  );
  const loadTrips = useCallback(async () => {
    setTripsError(null);
    setLoadingTrips(true);
    try {
      const data = await fetchSavedTrips();
      setSavedTrips(data);
    } catch (error) {
      console.error("Failed to load saved trips", error);
      const message = error instanceof Error ? error.message : "Nepodarilo sa načítať uložené výlety.";
      setTripsError(message);
    } finally {
      setLoadingTrips(false);
    }
  }, []);

  useEffect(() => {
    void loadTrips();
  }, [loadTrips]);

  const hasSavedTrips = savedTrips.length > 0;
  const formatDate = (value: string | null | undefined) => {
    if (!value) return "Flexibilné dátumy";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleDateString("sk-SK");
  };
  const formatDateRange = (start: string | null | undefined, end: string | null | undefined) => {
    if (start && end) return `${formatDate(start)} - ${formatDate(end)}`;
    if (start || end) return formatDate(start ?? end);
    return "Flexibilné dátumy";
  };

  const handleResumeTrip = (trip: SavedTripRecord) => {
    navigate("/dashboard", { state: { resumeTrip: trip } });
  };

  return (
    <section className="bg-slate-50 py-12">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 sm:px-6">
        <header className="space-y-2">
          <h1 className="text-3xl font-semibold text-slate-900">{welcomeCopy.heading}</h1>
          <p className="text-base text-slate-500">{welcomeCopy.subheading}</p>
        </header>

        {!auth.isAuthenticated && (
          <div className="flex flex-col gap-5 rounded-3xl border border-slate-200 bg-white px-6 py-5 shadow-[0_15px_45px_rgba(15,23,42,0.08)]">
            <div className="flex flex-col gap-2 text-slate-600 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-600">
                  <LuMapPin aria-hidden />
                  Prihláste sa pre ukladanie výletov
                </div>
                <p className="mt-3 text-sm text-slate-600">
                  Pred uložením a správou výletov sa prosím prihláste. Vaše dáta budú bezpečne uložené a dostupné na všetkých zariadeniach.
                </p>
              </div>
              <button
                onClick={() => auth.signinRedirect()}
                className="tg-btn tg-btn--primary self-start"
              >
                Prihlásiť sa
              </button>
            </div>
          </div>
        )}

        {tripsError && (
          <div className="rounded-3xl border border-red-100 bg-red-50/80 px-5 py-4 text-sm text-red-600">
            {tripsError}
            <button type="button" onClick={() => loadTrips()} className="ml-4 text-red-700 underline">
              Skúsiť znova
            </button>
          </div>
        )}

        {loadingTrips && (
          <div className="rounded-3xl border border-slate-200 bg-white/70 px-6 py-5 text-center text-sm text-slate-500">
            Načítavam uložené výlety...
          </div>
        )}

        {hasSavedTrips && !loadingTrips && !tripsError && (
          <section className="grid gap-6 md:grid-cols-2">
            {savedTrips.map((trip, index) => {
              const heroImage = deriveTripImage(trip);
              return (
                <article key={trip.id} className="overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-[0_25px_65px_rgba(15,23,42,0.08)]">
                <div className="relative aspect-[16/9] w-full overflow-hidden">
                  <img src={heroImage || FALLBACK_TRIP_IMAGE} alt={trip.title} className="h-full w-full object-cover" />
                  <span className="absolute left-4 top-4 rounded-full bg-white/90 px-3 py-1 text-xs font-semibold text-emerald-600">
                    AI itinerár
                  </span>
                  <button
                    type="button"
                    className="absolute right-4 top-4 rounded-full bg-white/90 p-2 text-slate-500 shadow hover:text-slate-900"
                    aria-label="Uložiť medzi obľúbené"
                  >
                    <LuBookmark aria-hidden />
                  </button>
                </div>
                <div className="flex flex-col gap-4 px-6 py-5">
                  <div className="flex items-center justify-between text-sm text-slate-400">
                    <span>Uložené {formatDate(trip.createdAt)}</span>
                    <span className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-emerald-500">
                      Pripravené na cestu
                    </span>
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-slate-900">{trip.title}</h2>
                    <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-slate-500">
                      <span className="inline-flex items-center gap-2">
                        <LuCalendar aria-hidden />
                        {formatDateRange(trip.startDate, trip.endDate)}
                      </span>
                      <span className="inline-flex items-center gap-2">
                        <LuFlag aria-hidden />
                        {trip.stopCount} zastávok
                      </span>
                      <span className="inline-flex items-center gap-2">
                        <LuMapPin aria-hidden />
                        Transport: {trip.transport}
                      </span>
                    </div>
                  </div>
                  {trip.summary && <p className="text-sm text-slate-600">{trip.summary}</p>}
                  <div className="flex flex-wrap gap-2">
                    {((Array.isArray(trip.categories) && trip.categories.length ? trip.categories : ["Itinerár"]) as string[]).map((tag, tagIndex) => (
                      <span
                        key={`${trip.id}-tag-${tag}-${tagIndex}`}
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${tagColors[(index + tagIndex) % tagColors.length]}`}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4">
                    <button
                      type="button"
                      onClick={() => handleResumeTrip(trip)}
                      className="tg-btn tg-btn--primary flex-1 justify-center"
                    >
                      Pokračovať v plánovaní
                    </button>
                    <button type="button" className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold text-slate-500 transition hover:text-slate-900">
                      <LuHeart aria-hidden />
                      Obľúbený
                    </button>
                  </div>
                </div>
              </article>
            );
          })}
          </section>
        )}

        {!loadingTrips && !tripsError && !hasSavedTrips && (
          <div className="rounded-3xl border border-slate-200 bg-white px-6 py-8 text-center text-slate-500 shadow-[0_20px_55px_rgba(15,23,42,0.08)]">
            <p className="text-base font-semibold text-slate-800">Zatiaľ nemáte žiadne uložené výlety.</p>
            <p className="mt-2 text-sm">Naplánujte trasu v sekcii Dashboard a kliknite na Save trip.</p>
            <Link to="/dashboard" className="tg-btn tg-btn--primary mt-4 inline-flex justify-center">
              Prejsť do plánovača
            </Link>
          </div>
        )}

        <section className="rounded-3xl border border-slate-100 bg-white px-6 py-8 shadow-[0_25px_65px_rgba(15,23,42,0.07)]">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-5">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.35em] text-cyan-500">Planned routes</p>
              <h3 className="mt-2 text-2xl font-semibold text-slate-900">Rozpracované trasy</h3>
              <p className="text-sm text-slate-500">Vaše neukončené itineráre čakajú na finalizáciu.</p>
            </div>
            <Link to="/dashboard" className="tg-btn tg-btn--secondary">
              Spravovať v plánovači
            </Link>
          </div>
          <div className="mt-6 grid gap-4">
            {plannedRoutes.map((route) => (
              <div key={route.id} className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-slate-50/60 px-5 py-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-base font-semibold text-slate-900">{route.title}</p>
                    <span className="inline-flex items-center gap-2 text-sm text-slate-500">
                      <LuFlag aria-hidden />
                      Start {route.start}
                    </span>
                  </div>
                  <span className="text-xs font-semibold uppercase tracking-wide text-indigo-500">
                    {route.status}
                  </span>
                </div>
                <div className="h-2 rounded-full bg-white">
                  <div className="h-full rounded-full bg-indigo-500" style={{ width: `${route.progress}%` }} />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
};

export default Trips;
