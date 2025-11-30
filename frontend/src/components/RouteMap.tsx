import { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, Polyline, CircleMarker, Tooltip, useMap } from "react-leaflet";
import type { LatLngExpression } from "leaflet";
import L from "leaflet";

export type Coordinates = {
  lat: number;
  lon: number;
};

export type RouteMapMarker = {
  id: string;
  name: string;
  coordinates: Coordinates;
  type: "start" | "destination" | "place";
  location?: string;
};

type RouteMapProps = {
  markers: RouteMapMarker[];
  routeLine: Coordinates[];
  currentLocation?: Coordinates | null;
  focusCoordinate?: Coordinates | null;
};

const FitBounds = ({ positions }: { positions: LatLngExpression[] }) => {
  const map = useMap();

  useEffect(() => {
    if (!positions.length) return;
    const bounds = L.latLngBounds(positions);
    map.fitBounds(bounds, { padding: [32, 32] });
  }, [map, positions]);

  return null;
};

const FocusLocation = ({ coordinate }: { coordinate: Coordinates | null | undefined }) => {
  const map = useMap();

  useEffect(() => {
    if (!coordinate) return;
    map.flyTo([coordinate.lat, coordinate.lon], 11, { animate: true, duration: 1.2 });
  }, [coordinate, map]);

  return null;
};

const colorForMarker = (type: RouteMapMarker["type"]) => {
  if (type === "start") return "#22c55e";
  if (type === "destination") return "#f97316";
  return "#0ea5e9";
};

const RouteMap = ({ markers, routeLine, currentLocation, focusCoordinate }: RouteMapProps) => {
  const markerPositions = useMemo<LatLngExpression[]>(
    () => markers.map((marker) => [marker.coordinates.lat, marker.coordinates.lon] as LatLngExpression),
    [markers]
  );

  const routePositions = useMemo<LatLngExpression[]>(
    () => routeLine.map((coord) => [coord.lat, coord.lon] as LatLngExpression),
    [routeLine]
  );

  const fitPositions = useMemo(() => {
    if (focusCoordinate) return [];
    if (markerPositions.length) return markerPositions;
    if (routePositions.length) return routePositions;
    if (currentLocation) return [[currentLocation.lat, currentLocation.lon] as LatLngExpression];
    return [];
  }, [markerPositions, routePositions, currentLocation, focusCoordinate]);

  return (
    <MapContainer className="tg-route-map" center={[48.1486, 17.1077]} zoom={5} zoomControl={false} scrollWheelZoom={false} attributionControl={false}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
      {routePositions.length >= 2 && (
        <Polyline positions={routePositions} pathOptions={{ color: "#6366f1", weight: 4, opacity: 0.85, lineCap: "round" }} />
      )}
      {markers.map((marker) => {
        const color = colorForMarker(marker.type);
        return (
          <CircleMarker
            key={marker.id}
            center={[marker.coordinates.lat, marker.coordinates.lon]}
            radius={marker.type === "place" ? 7 : 9}
            pathOptions={{
              color,
              fillColor: color,
              fillOpacity: 0.9,
              weight: marker.type === "place" ? 1.5 : 2,
            }}
          >
            <Tooltip direction="top" offset={[0, -6]} opacity={1} className="text-xs">
              <div className="text-xs font-semibold text-slate-900">{marker.name}</div>
              {marker.location && <div className="text-[0.65rem] font-normal text-slate-500">{marker.location}</div>}
            </Tooltip>
          </CircleMarker>
        );
      })}
      {currentLocation && (
        <CircleMarker
          center={[currentLocation.lat, currentLocation.lon]}
          radius={10}
          pathOptions={{ color: "#f43f5e", fillColor: "#f43f5e", fillOpacity: 0.95, weight: 2 }}
        >
          <Tooltip direction="top" offset={[0, -6]} opacity={1} className="text-xs">
            <div className="text-xs font-semibold text-slate-900">Aktuálna poloha</div>
          </Tooltip>
        </CircleMarker>
      )}
      {focusCoordinate ? <FocusLocation coordinate={focusCoordinate} /> : <FitBounds positions={fitPositions} />}
    </MapContainer>
  );
};

export default RouteMap;
