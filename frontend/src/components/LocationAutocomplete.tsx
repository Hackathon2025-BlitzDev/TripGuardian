import { useEffect, useRef, useState } from "react";

type Suggestion = {
  id: string;
  label: string;
};

type LocationAutocompleteProps = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
};

const MIN_QUERY_LENGTH = 2;
const DEBOUNCE_MS = 350;

const LocationAutocomplete = ({ value, onChange, placeholder, className }: LocationAutocompleteProps) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const debounceRef = useRef<number | undefined>(undefined);
  const blurTimeoutRef = useRef<number | undefined>(undefined);
  const controllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (debounceRef.current) window.clearTimeout(debounceRef.current);

    if (!value || value.trim().length < MIN_QUERY_LENGTH) {
      controllerRef.current?.abort();
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    debounceRef.current = window.setTimeout(async () => {
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      setIsLoading(true);

      try {
        const url = new URL("https://nominatim.openstreetmap.org/search");
        url.searchParams.set("format", "json");
        url.searchParams.set("addressdetails", "1");
        url.searchParams.set("limit", "5");
        url.searchParams.set("q", value);

        const response = await fetch(url.toString(), {
          signal: controller.signal,
          headers: {
            Accept: "application/json",
          },
        });

        if (!response.ok) throw new Error("Failed to fetch suggestions");

        const data: Array<{ place_id: string; display_name: string }> = await response.json();
        setSuggestions(
          data.map((item) => ({
            id: item.place_id,
            label: item.display_name,
          }))
        );
        setIsOpen(true);
      } catch (error) {
        if ((error as Error).name !== "AbortError") {
          console.error("Location autocomplete error", error);
          setSuggestions([]);
        }
      } finally {
        setIsLoading(false);
      }
    }, DEBOUNCE_MS);

    return () => {
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
    };
  }, [value]);

  useEffect(() => {
    return () => {
      if (blurTimeoutRef.current) window.clearTimeout(blurTimeoutRef.current);
    };
  }, []);

  const handleSelect = (label: string) => {
    onChange(label);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        onFocus={() => {
          if (blurTimeoutRef.current) window.clearTimeout(blurTimeoutRef.current);
          if (value.trim().length >= MIN_QUERY_LENGTH && suggestions.length > 0) setIsOpen(true);
        }}
        onBlur={() => {
          blurTimeoutRef.current = window.setTimeout(() => setIsOpen(false), 120);
        }}
        className={className}
      />
      {isOpen && (
        <div className="absolute left-0 right-0 top-full z-20 mt-2 rounded-2xl border border-slate-100 bg-white shadow-[0_25px_45px_rgba(15,23,42,0.12)]">
          {isLoading && (
            <div className="px-4 py-3 text-sm text-slate-500">Searching…</div>
          )}
          {!isLoading && suggestions.length === 0 && (
            <div className="px-4 py-3 text-sm text-slate-500">No results found</div>
          )}
          {!isLoading &&
            suggestions.map((suggestion) => (
              <button
                key={suggestion.id}
                type="button"
                onMouseDown={(event) => {
                  event.preventDefault();
                  handleSelect(suggestion.label);
                }}
                className="flex w-full items-start gap-3 px-4 py-3 text-left text-sm text-slate-600 transition hover:bg-slate-50"
              >
                <span className="mt-0.5 h-2 w-2 rounded-full bg-slate-300" aria-hidden />
                <span className="leading-snug">{suggestion.label}</span>
              </button>
            ))}
        </div>
      )}
    </div>
  );
};

export default LocationAutocomplete;
