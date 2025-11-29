import { useEffect, useMemo, useRef, useState } from "react";
import type { IconType } from "react-icons";
import {
  LuCheck,
  LuChevronDown,
  LuFerrisWheel,
  LuHeartPulse,
  LuLandmark,
  LuLightbulb,
  LuMountain,
  LuPalette,
  LuPartyPopper,
  LuPiggyBank,
  LuShoppingBag,
  LuTreePine,
  LuTrophy,
  LuUsers,
  LuUtensils,
  LuTrash2,
} from "react-icons/lu";
import {
  FaBicycle,
  FaBusSimple,
  FaCarSide,
  FaPersonHiking,
  FaPlane,
  FaShip,
  FaTrainSubway,
} from "react-icons/fa6";
import DatePickerInput from "../components/DatePickerInput";
import LocationAutocomplete from "../components/LocationAutocomplete";

const stats = [
//   { label: "Active trips", value: "3" },
  { label: "Planned routes", value: "12" },
  { label: "Saved places", value: "28" },
];

const categories: { label: string; icon: IconType }[] = [
  { label: "Culture", icon: LuLandmark },
  { label: "Nature", icon: LuTreePine },
  { label: "Food", icon: LuUtensils },
  { label: "Sports", icon: LuTrophy },
  { label: "Family", icon: LuUsers },
  { label: "Low budget", icon: LuPiggyBank },
  { label: "Shopping", icon: LuShoppingBag },
  { label: "Nightlife", icon: LuPartyPopper },
  { label: "Art & Galleries", icon: LuPalette },
  { label: "Hiking & Outdoor", icon: LuMountain },
  { label: "Relax & Wellness", icon: LuHeartPulse },
  { label: "Thrill & Parks", icon: LuFerrisWheel },
  { label: "Unique places", icon: LuLightbulb },
];

const transportOptions: { label: string; value: string; icon: IconType }[] = [
  { label: "Car", value: "car", icon: FaCarSide },
  { label: "Train", value: "train", icon: FaTrainSubway },
  { label: "Plane", value: "plane", icon: FaPlane },
  { label: "Bus", value: "bus", icon: FaBusSimple },
  { label: "Bicycle", value: "bicycle", icon: FaBicycle },
  { label: "On foot", value: "foot", icon: FaPersonHiking },
  { label: "Boat", value: "boat", icon: FaShip },
];

const steps = [
  { id: 1, label: "Basic info" },
  { id: 2, label: "Preferences" },
];

type BasicsState = {
  start: string;
  destination: string;
  stops: string[];
  startDate: Date | null;
  endDate: Date | null;
  flexibleDates: boolean;
};

const Dashboard = () => {
  const [activeStep, setActiveStep] = useState(1);
  const [basics, setBasics] = useState<BasicsState>({
    start: "",
    destination: "",
    stops: [""],
    startDate: null,
    endDate: null,
    flexibleDates: false,
  });
  const [preferences, setPreferences] = useState({
    categories: [] as string[],
    transport: transportOptions[0].value,
    budget: "",
    notes: "",
  });
  const [plannerMode, setPlannerMode] = useState<"trip" | "places" | null>(null);
  const [placeExplore, setPlaceExplore] = useState({
    location: "",
    radius: "",
    description: "",
  });
  const transportRef = useRef<HTMLDivElement>(null);
  const [transportOpen, setTransportOpen] = useState(false);
  const selectedTransport = useMemo(
    () => transportOptions.find((option) => option.value === preferences.transport) ?? transportOptions[0],
    [preferences.transport]
  );
  const SelectedTransportIcon = selectedTransport?.icon;
  const [isMobile, setIsMobile] = useState(false);
  const [mobileCategoriesOpen, setMobileCategoriesOpen] = useState(false);

  const today = useMemo(() => new Date(), []);
  const progress = useMemo(() => (activeStep / steps.length) * 100, [activeStep]);
  const locationInputClass = "rounded-2xl border border-slate-200 px-4 py-3 text-base shadow-inner";

  useEffect(() => {
    if (!transportOpen) return;
    const handleClickOutside = (event: MouseEvent) => {
      if (transportRef.current && !transportRef.current.contains(event.target as Node)) {
        setTransportOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [transportOpen]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(min-width: 640px)");
    const update = (event?: MediaQueryListEvent) => {
      const matches = event ? event.matches : mq.matches;
      const mobile = !matches;
      setIsMobile(mobile);
      setMobileCategoriesOpen((prev) => (mobile ? false : prev || true));
    };
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  const updateStop = (value: string, index: number) => {
    setBasics((prev) => {
      const copy = [...prev.stops];
      copy[index] = value;
      return { ...prev, stops: copy };
    });
  };

  const addStop = () => {
    setBasics((prev) => ({ ...prev, stops: [...prev.stops, ""] }));
  };

  const removeStop = (index: number) => {
    setBasics((prev) => {
      const filtered = prev.stops.filter((_, i) => i !== index);
      return { ...prev, stops: filtered.length ? filtered : [""] };
    });
  };

  const handleFlexibleToggle = (checked: boolean) => {
    setBasics((prev) => ({
      ...prev,
      flexibleDates: checked,
      ...(checked ? { startDate: null, endDate: null } : {}),
    }));
  };

  const toggleCategory = (label: string) => {
    setPreferences((prev) => {
      const exists = prev.categories.includes(label);
      return {
        ...prev,
        categories: exists
          ? prev.categories.filter((item) => item !== label)
          : [...prev.categories, label],
      };
    });
  };

  const handleGenerateTrip = () => {
    console.log("Trip payload", { basics, preferences });
    alert("Thanks! Your planning request has been saved.");
  };

  const handlePlanTripToggle = () => {
    setPlannerMode((prev) => (prev === "trip" ? null : "trip"));
    setActiveStep(1);
  };

  const handleFindPlaces = () => {
    setPlannerMode((prev) => (prev === "places" ? null : "places"));
  };

  const handlePlaceSearch = () => {
    console.log("Place search", placeExplore);
    alert("Search saved! We'll look for great spots matching your description.");
  };

  const lastStop = basics.stops[basics.stops.length - 1] ?? "";
  const canAddStop = lastStop.trim().length > 0;

  return (
    <section className="min-h-[70vh] bg-slate-50 py-16">
      <div className="mx-auto max-w-6xl rounded-3xl bg-white px-8 py-12 shadow-[0_35px_75px_rgba(15,23,42,0.12)]">
        <div className="flex flex-col gap-4">
          <p className="text-sm font-semibold uppercase tracking-[0.35em] text-amber-500">
            Dashboard
          </p>
          <div className="flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="text-3xl font-semibold text-slate-900">Welcome back to TripGuardian</h1>
              <p className="mt-2 max-w-2xl text-base text-slate-500">
                Manage your active trips, monitor itineraries, and adjust plans in real time.
                Pick up a work-in-progress trip or start a brand new adventure.
              </p>
            </div>
            <button className="tg-btn tg-btn--primary">
              Create new trip
            </button>
          </div>
        </div>

        <div className="mt-12 grid gap-4 sm:grid-cols-3">
          {stats.map((stat) => (
            <article key={stat.label} className="rounded-2xl border border-slate-100 bg-slate-50 px-6 py-5">
              <p className="text-sm uppercase tracking-[0.35em] text-slate-400">{stat.label}</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">{stat.value}</p>
            </article>
          ))}
        </div>

        <div className="mt-10 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handlePlanTripToggle}
            className={`tg-btn ${plannerMode === "trip" ? "tg-btn--primary" : "tg-btn--secondary"}`}
            aria-expanded={plannerMode === "trip"}
          >
            Plan trip
          </button>
          <button
            type="button"
            onClick={handleFindPlaces}
            className={`tg-btn ${plannerMode === "places" ? "tg-btn--primary" : "tg-btn--secondary"}`}
            aria-expanded={plannerMode === "places"}
          >
            Find places
          </button>
        </div>

        {plannerMode === null && (
          <div className="mt-8 rounded-3xl border border-dashed border-slate-200 bg-slate-50/70 px-6 py-10 text-center text-sm text-slate-500">
            Tap "Plan trip" to open the detailed planner or jump directly to saved preferences with "Find places".
          </div>
        )}

        {plannerMode === "trip" && (
          <div className="mt-12 rounded-3xl border border-slate-100 px-6 py-8 shadow-[0_20px_45px_rgba(15,23,42,0.08)]">
            <div className="flex flex-col gap-6">
              <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                <div className="flex flex-wrap items-center gap-6">
                  {steps.map((step) => {
                    const isActive = activeStep === step.id;
                    return (
                      <div key={step.id} className="flex items-center gap-3">
                        <button
                          type="button"
                          onClick={() => setActiveStep(step.id)}
                          className={`flex h-12 w-12 items-center justify-center rounded-full text-color font-semibold shadow-sm transition ${
                            isActive ? "bg-indigo-500 text-color" : "bg-slate-100 text-color"
                          }`}
                        >
                          {step.id}
                        </button>
                        <div className="flex flex-col">
                          <span className={`text-sm font-semibold ${isActive ? "text-indigo-600" : "text-slate-400"}`}>
                            {step.label}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="hidden h-2 flex-1 rounded-full bg-slate-100 lg:block ml-8">
                  <div className="h-full rounded-full bg-indigo-500 transition-all" style={{ width: `${progress}%` }} />
                </div>
              </div>


              {activeStep === 1 && (
                <div className="mt-6 rounded-3xl border border-slate-100 bg-white px-6 py-8">
                  <div>
                    <p className="text-base font-semibold text-slate-900">Basic trip information</p>
                    <p className="text-sm text-slate-500">Tell us where you are going and the timeframe for the trip.</p>
                  </div>
                  <div className="mt-6 grid gap-5">
                    <label className="grid gap-2 text-sm font-medium text-slate-600">
                      Starting point *
                      <LocationAutocomplete
                        value={basics.start}
                        onChange={(newValue) => setBasics((prev) => ({ ...prev, start: newValue }))}
                        placeholder="e.g., Bratislava"
                        className={locationInputClass}
                      />
                    </label>
                    <label className="grid gap-2 text-sm font-medium text-slate-600">
                      Destination *
                      <LocationAutocomplete
                        value={basics.destination}
                        onChange={(newValue) => setBasics((prev) => ({ ...prev, destination: newValue }))}
                        placeholder="e.g., Prague"
                        className={locationInputClass}
                      />
                    </label>
                    <div className="grid gap-3">
                      <p className="text-sm font-medium text-slate-600">Stopovers (optional)</p>
                      {basics.stops.map((stop, index) => (
                        <div key={`stop-${index}`} className="flex items-start gap-3">
                          <LocationAutocomplete
                            value={stop}
                            onChange={(newValue) => updateStop(newValue, index)}
                            placeholder="Add stop"
                            className={`${locationInputClass} flex-1`}
                          />
                          <button
                            type="button"
                            onClick={() => removeStop(index)}
                            className="rounded-full border border-slate-200 p-2 text-slate-400 transition hover:border-slate-300 hover:text-slate-600"
                            aria-label={`Remove stop ${index + 1}`}
                          >
                            <LuTrash2 className="text-base" aria-hidden />
                          </button>
                        </div>
                      ))}
                      <button
                        type="button"
                        onClick={addStop}
                        className={`tg-btn tg-btn--secondary tg-btn--sm w-fit ${!canAddStop ? "cursor-not-allowed opacity-50" : ""}`}
                        disabled={!canAddStop}
                      >
                        + Add stop
                      </button>
                    </div>
                    <label className="inline-flex items-center gap-3 text-sm text-slate-600">
                      <input
                        type="checkbox"
                        checked={basics.flexibleDates}
                        onChange={(e) => handleFlexibleToggle(e.target.checked)}
                        className="h-4 w-4 rounded border-slate-300"
                      />
                      Dates are still flexible
                    </label>
                    {!basics.flexibleDates && (
                      <div className="grid gap-4 md:grid-cols-2">
                        <label className="grid gap-2 text-sm font-medium text-slate-600">
                          Start date (optional)
                          <DatePickerInput
                            value={basics.startDate}
                            onChange={(date) => setBasics((prev) => ({ ...prev, startDate: date }))}
                            placeholder="Select start date"
                            minDate={today}
                          />
                        </label>
                        <label className="grid gap-2 text-sm font-medium text-slate-600">
                          End date (optional)
                          <DatePickerInput
                            value={basics.endDate}
                            onChange={(date) => setBasics((prev) => ({ ...prev, endDate: date }))}
                            placeholder="Select end date"
                            minDate={basics.startDate ?? today}
                          />
                        </label>
                      </div>
                    )}
                  </div>
                  <div className="mt-6 flex justify-end">
                    <button
                      type="button"
                      onClick={() => setActiveStep(2)}
                      className="tg-btn tg-btn--primary"
                    >
                      Continue
                      <span aria-hidden>➜</span>
                    </button>
                  </div>
                </div>
              )}

              {activeStep === 2 && (
                <div className="mt-6 rounded-3xl border border-slate-100 bg-white px-6 py-8">
                  <div>
                    <p className="text-base font-semibold text-slate-900">Preferences & categories</p>
                    <p className="text-sm text-slate-500">Pick attraction categories and how you plan to travel.</p>
                  </div>
                  <div className="mt-6 grid gap-5">
                    <div className="grid gap-3">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-slate-600">Preferred attraction categories *</p>
                        {isMobile && (
                          <button
                            type="button"
                            onClick={() => setMobileCategoriesOpen((prev) => !prev)}
                            className="tg-btn tg-btn--secondary tg-btn--xs sm:hidden gap-1"
                          >
                            {mobileCategoriesOpen ? "Hide" : "Show"}
                            <LuChevronDown
                              className={`text-sm transition ${mobileCategoriesOpen ? "rotate-180" : "rotate-0"}`}
                              aria-hidden
                            />
                          </button>
                        )}
                      </div>
                      {(!isMobile || mobileCategoriesOpen) && (
                        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                          {categories.map((category) => {
                            const isSelected = preferences.categories.includes(category.label);
                            const Icon = category.icon;
                            return (
                              <button
                                key={category.label}
                                type="button"
                                onClick={() => toggleCategory(category.label)}
                                className={`flex items-center gap-3 rounded-2xl border px-4 py-3 text-left text-sm font-semibold transition ${
                                  isSelected
                                    ? "border-indigo-500 bg-indigo-50 text-indigo-600"
                                    : "border-slate-200 bg-white text-slate-600"
                                }`}
                              >
                                <Icon className="text-xl" aria-hidden />
                                <span className="flex-1">{category.label}</span>
                                {isSelected && (
                                  <span className="ml-auto rounded-full bg-indigo-500/10 p-1 text-indigo-500">
                                    <LuCheck aria-hidden />
                                  </span>
                                )}
                              </button>
                            );
                          })}
                        </div>
                      )}
                    </div>

                    <div className="grid gap-2 text-sm font-medium text-slate-600">
                      <span>Transportation mode</span>
                      <div ref={transportRef} className="relative">
                        <button
                          type="button"
                          onClick={() => setTransportOpen((prev) => !prev)}
                          className="flex w-full items-center gap-3 rounded-2xl border border-slate-200 px-4 py-3 text-left text-base shadow-inner"
                          aria-haspopup="listbox"
                          aria-expanded={transportOpen}
                        >
                          {SelectedTransportIcon && <SelectedTransportIcon className="text-xl" aria-hidden />}
                          <span className="flex-1">{selectedTransport?.label}</span>
                          <LuChevronDown className={`text-lg transition ${transportOpen ? "rotate-180" : "rotate-0"}`} aria-hidden />
                        </button>
                        {transportOpen && (
                          <div className="absolute z-10 mt-2 w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
                            <ul role="listbox">
                              {transportOptions.map((option) => {
                                const Icon = option.icon;
                                const isActive = option.value === preferences.transport;
                                return (
                                  <li key={option.value}>
                                    <button
                                      type="button"
                                      onClick={() => {
                                        setPreferences((prev) => ({ ...prev, transport: option.value }));
                                        setTransportOpen(false);
                                      }}
                                      className={`flex w-full items-center gap-3 px-4 py-3 text-left text-sm font-semibold transition hover:bg-slate-50 ${
                                        isActive ? "text-indigo-600" : "text-slate-600"
                                      }`}
                                      role="option"
                                      aria-selected={isActive}
                                    >
                                      <Icon className="text-lg" aria-hidden />
                                      <span className="flex-1">{option.label}</span>
                                      {isActive && <LuCheck className="text-indigo-500" aria-hidden />}
                                    </button>
                                  </li>
                                );
                              })}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>

                    <label className="grid gap-2 text-sm font-medium text-slate-600">
                      Budget (optional, EUR)
                      <input
                        type="number"
                        placeholder="e.g., 500"
                        value={preferences.budget}
                        onChange={(e) => setPreferences((prev) => ({ ...prev, budget: e.target.value }))}
                        className="rounded-2xl border border-slate-200 px-4 py-3 text-base"
                      />
                    </label>

                    <label className="grid gap-2 text-sm font-medium text-slate-600">
                      Extra information for AI
                      <textarea
                        rows={4}
                        placeholder="Preferences, constraints, pace, must-see spots..."
                        value={preferences.notes}
                        onChange={(e) => setPreferences((prev) => ({ ...prev, notes: e.target.value }))}
                        className="rounded-2xl border border-slate-200 px-4 py-3 text-base"
                      />
                      <span className="text-xs text-slate-400">
                        Example: "Traveling with kids, love local markets and evening bars, want to avoid tourist crowds."
                      </span>
                    </label>
                  </div>
                  <div className="mt-6 flex flex-wrap justify-between gap-4">
                    <button
                      type="button"
                      onClick={() => setActiveStep(1)}
                      className="tg-btn tg-btn--secondary"
                    >
                      ← Back
                    </button>
                    <button
                      type="button"
                      onClick={handleGenerateTrip}
                      className="tg-btn tg-btn--primary gap-4"
                    >
                      Generate trip
                      <span className="inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-1.5 text-sm font-semibold">
                        {SelectedTransportIcon && <SelectedTransportIcon aria-hidden className="text-lg" />}
                        <span>Plan</span>
                      </span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {plannerMode === "places" && (
          <div className="mt-12 rounded-3xl border border-slate-100 px-6 py-8 shadow-[0_20px_45px_rgba(15,23,42,0.08)]">
            <div className="flex flex-col gap-6">
              <div>
                <p className="text-base font-semibold text-slate-900">Find interesting places</p>
                <p className="text-sm text-slate-500">Save standout spots for later exploration.</p>
              </div>
              <div className="grid gap-5">
                <label className="grid gap-2 text-sm font-medium text-slate-600">
                  Location
                  <LocationAutocomplete
                    value={placeExplore.location}
                    onChange={(value) => setPlaceExplore((prev) => ({ ...prev, location: value }))}
                    placeholder="E.g., Lisbon old town"
                    className={locationInputClass}
                  />
                </label>
                <label className="grid gap-2 text-sm font-medium text-slate-600">
                  Distance radius (km)
                  <input
                    type="number"
                    min={1}
                    placeholder="e.g., 5"
                    value={placeExplore.radius}
                    onChange={(e) => setPlaceExplore((prev) => ({ ...prev, radius: e.target.value }))}
                    className="rounded-2xl border border-slate-200 px-4 py-3 text-base"
                  />
                </label>
                <label className="grid gap-2 text-sm font-medium text-slate-600">
                  What kind of attractions are you looking for?
                  <textarea
                    rows={4}
                    placeholder="Describe styles, vibes, must-see corners, or any preferences."
                    value={placeExplore.description}
                    onChange={(e) => setPlaceExplore((prev) => ({ ...prev, description: e.target.value }))}
                    className="rounded-2xl border border-slate-200 px-4 py-3 text-base"
                  />
                </label>
              </div>
              <div className="flex flex-wrap gap-3">
                <button type="button" onClick={handlePlaceSearch} className="tg-btn tg-btn--primary">
                  Save search
                </button>
                <button type="button" onClick={() => setPlannerMode(null)} className="tg-btn tg-btn--ghost">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default Dashboard;
