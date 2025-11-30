import os
from dotenv import load_dotenv
import requests
import polyline
import overpy
import time
import json
from typing import List, Tuple, Dict, Any, Optional
from math import radians, cos, sin, asin, sqrt
from shapely.geometry import LineString

OSRM_CAR = "https://routing.openstreetmap.de/routed-car/route/v1/driving"
OSRM_FOOT = "https://routing.openstreetmap.de/routed-foot/route/v1/walking"
load_dotenv()
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

POI_CATEGORIES = {
        "attractions": {
            "keywords": ["tourist attractions", "museums", "castles", "historical landmarks"],
            "place_types": ["tourist_attraction", "museum", "park"],
            "boost_terms": ["hrad", "zámok", "castle", "jaskyňa", "cave", "múzeum", "museum", "katedrála", "cathedral"],
            "score_multiplier": 3.0
            },
        "dining": {
            "keywords": ["restaurants", "cafes", "koliba", "traditional food"],
            "place_types": ["restaurant", "cafe", "meal_takeaway", "bakery"],
            "boost_terms": ["koliba", "reštaurácia", "tradičná"],
            "score_multiplier": 1.5
            },
        "accommodation": {
            "keywords": ["hotels", "guest houses", "hostels", "penzion"],
            "place_types": ["lodging"],
            "boost_terms": ["hotel", "penzion", "guest house"],
            "score_multiplier": 1.2
            },
        "services": {
            "keywords": ["gas stations", "supermarkets", "grocery stores"],
            "place_types": ["gas_station", "supermarket", "grocery_or_supermarket"],
            "boost_terms": [],
            "score_multiplier": 1.0
            },
        "nature": {
            "keywords": ["parks", "viewpoints", "nature reserves", "hiking trails"],
            "place_types": ["park", "campground", "rv_park"],
            "boost_terms": ["výhľad", "viewpoint", "príroda", "nature"],
            "score_multiplier": 2.0
            },
        "worship": {
            "keywords": ["churches", "cathedrals", "monasteries"],
            "place_types": ["church", "place_of_worship"],
            "boost_terms": ["kostol", "church", "katedrála", "kláštor"],
            "score_multiplier": 1.8
            }
        }
def geocode(city: str) -> Tuple[float, float]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json", "limit": 1}
    headers = {"User-Agent": "TripGuardian/1.0 (your-email@gmail.com)"}
    time.sleep(1)
    r = requests.get(url, params=params, headers=headers, timeout=10)
    data = r.json()
    if data:
        return float(data[0]["lon"]), float(data[0]["lat"])
    raise ValueError(f"Cannot find {city}")

def get_osrm_routes(start_lonlat: Tuple[float, float],
                    end_lonlat: Tuple[float, float],
                    waypoints=None,
                    alternatives=True,
                    profile="car") -> List[Dict]:
    coords = [start_lonlat] + (waypoints or []) + [end_lonlat]
    coord_str = ";".join(f"{lon},{lat}" for lon, lat in coords)
    base = OSRM_CAR if profile == "car" else OSRM_FOOT
    url = f"{base}/{coord_str}"
    params = {
            "overview": "full",
            "geometries": "polyline",
            "alternatives": "true" if alternatives else "false",
            "steps": "false"
            }
    try:
        r = requests.get(url, params=params, timeout=25)
        data = r.json()
        if data.get("code") != "Ok":
            return []
        routes = []
        for route in data["routes"][:5]:
            geom = polyline.decode(route["geometry"])
            routes.append({
                "distance_km": round(route["distance"]/1000, 1),
                "duration_min": round(route["duration"]/60),
                "geometry": geom
                })
        return routes
    except:
        return []


def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    lon1, lat1 = map(radians, coord1)
    lon2, lat2 = map(radians, coord2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))  # km

def generate_smart_scenarios(start_lonlat, end_lonlat, verbose=False) -> Dict[str, List[Tuple[float, float]]]:
    direct_distance = haversine(start_lonlat, end_lonlat)
    max_detour_km = max(150, direct_distance * 0.6)

    valid_scenarios = {"Fastest": None}

    min_lon = min(start_lonlat[0], end_lonlat[0]) - 0.5
    max_lon = max(start_lonlat[0], end_lonlat[0]) + 0.5
    min_lat = min(start_lonlat[1], end_lonlat[1]) - 0.5
    max_lat = max(start_lonlat[1], end_lonlat[1]) + 0.5

    try:
        api = overpy.Overpass()
        query = f"""
        [out:json][timeout:25];
        (
                node["place"~"city|town"]["name"]({min_lat},{min_lon},{max_lat},{max_lon});
                );
        out body;
        """

        if verbose:
            print("   Querying OpenStreetMap for cities...")

        result = api.query(query)
        candidate_waypoints = {}

        if verbose and len(result.nodes) > 0:
            print(f"   Found {len(result.nodes)} cities/towns in region")

        for node in result.nodes:
            wp_coords = (float(node.lon), float(node.lat))
            city_name = node.tags.get("name", "Unknown")

            dist_to_start = haversine(start_lonlat, wp_coords)
            dist_to_end = haversine(end_lonlat, wp_coords)

            if dist_to_start < 5 or dist_to_end < 5:
                continue

            detour = (dist_to_start + dist_to_end) - direct_distance

            if direct_distance < 100:
                is_on_route = abs(detour) < 12
                is_alternative = 12 <= detour < 25
            else:
                is_on_route = abs(detour) < 20
                is_alternative = 20 <= detour < max_detour_km

            if is_on_route or is_alternative:
                population = int(node.tags.get("population", 0)) if node.tags.get("population", "0").isdigit() else 0
                place_type = node.tags.get("place", "town")

                priority = population if population > 0 else (10000 if place_type == "city" else 5000)
                candidate_waypoints[f"via {city_name}"] = (wp_coords, detour, priority)

                if verbose:
                    route_type = "on-route" if is_on_route else "alternative"
                    print(f"         ✓ Added as {route_type} waypoint (detour: {detour:.1f}km)")

        on_route_cities = {k: v for k, v in candidate_waypoints.items() if v[1] < (12 if direct_distance < 100 else 20)}
        alternative_routes = {k: v for k, v in candidate_waypoints.items() if k not in on_route_cities}

        sorted_on_route = sorted(
                on_route_cities.items(),
                key=lambda x: haversine(start_lonlat, x[1][0])
                )

        sorted_alternatives = sorted(
                alternative_routes.items(),
                key=lambda x: -x[1][2]
                )

        for name, (wp_coords, detour, priority) in sorted_on_route[:3]:
            valid_scenarios[name] = [wp_coords]

        for name, (wp_coords, detour, priority) in sorted_alternatives[:5]:
            valid_scenarios[name] = [wp_coords]

        if verbose:
            total_found = len(sorted_on_route) + len(sorted_alternatives)
            print(f"   ✓ Found {total_found} alternative waypoints")

    except Exception as e:
        if verbose:
            print(f"   Note: Using fallback waypoints (Overpass API unavailable: {str(e)})")

        # Fallback: Use hardcoded waypoints for known destinations
        candidate_waypoints = {
                "via Poprad (Tatras)":         (20.2976, 49.0542),
                "via Žilina":                  (18.7396, 49.2224),
                "via Banská Bystrica":         (19.1462, 48.7355),
                "via Zvolen":                  (19.1151, 48.5752),
                "via Trenčín":                 (17.9960, 48.8959),
                "via Nitra":                   (18.0850, 48.3150),
                "via Tokaj (wine)":            (21.4107, 48.1219),
                "via Budapest (south)":        (19.0402, 47.4979),
                "via Liptovský Mikuláš (scenic)": (19.6990, 48.5740),
                }

        for name, wp in candidate_waypoints.items():
            detour = (haversine(start_lonlat, wp) + haversine(wp, end_lonlat)) - direct_distance
            if detour < max_detour_km:
                valid_scenarios[name] = [wp]

    return valid_scenarios

def get_pois_along_route_google(
        geometry: List[Tuple[float, float]], 
        api_key: str, 
        categories: List[str] = None,
        max_per_query: int = 15,
        verbose: bool = False
        ) -> Dict[str, List[Dict]]:
    if not api_key or "your_" in api_key:
        raise ValueError("Google API key missing")

    if categories is None:
        categories = list(POI_CATEGORIES.keys())

    line = LineString([(lon, lat) for lat, lon in geometry])
    center_lat, center_lon = line.centroid.y, line.centroid.x

    route_length_km = sum(haversine((geometry[i][1], geometry[i][0]), 
                                    (geometry[i+1][1], geometry[i+1][0])) 
                          for i in range(len(geometry)-1)) if len(geometry) > 1 else 50

    filter_radius_km = min(80, max(40, route_length_km * 0.7))
    search_radius_km = min(50, filter_radius_km)

    def nearest_city_name(lat: float, lon: float) -> str:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10}
        try:
            r = requests.get(url, params=params, timeout=5)
            data = r.json()
            city = data.get("address", {})
            return city.get("city") or city.get("town") or city.get("village") or "Slovakia"
        except:
            return "Slovakia"

    city_hint = nearest_city_name(center_lat, center_lon)

    if verbose:
        print(f"\n📍 Searching for POIs along route (length: {route_length_km:.1f}km, API radius: {search_radius_km:.1f}km, filter radius: {filter_radius_km:.1f}km)")
        print(f"   City hint: {city_hint}, Center: ({center_lat:.4f}, {center_lon:.4f})")

    results = {
            "metadata": {
                "route_center": {"lat": center_lat, "lon": center_lon},
                "location_hint": city_hint,
                "total_pois": 0,
                "categories_searched": categories
                },
            "pois_by_category": {},
            "top_rated_overall": []
            }

    all_pois = []
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}

    for category in categories:
        if category not in POI_CATEGORIES:
            continue

        category_config = POI_CATEGORIES[category]
        category_pois = []

        if verbose:
            print(f"   [{categories.index(category)+1}/{len(categories)}] {category}...", end=" ")

        text_headers = headers.copy()
        text_headers["X-Goog-FieldMask"] = "places.displayName,places.id,places.location,places.types"

        def process_places(places, label: str):
            if verbose:
                if len(places) == 0:
                    print(f"\n      ℹ️  No results for {label} near {city_hint}")
                else:
                    print(f"\n      ✓ API returned {len(places)} places for {label}")

            for place in places[:5]:
                place_id = place["id"]
                det_url = f"https://places.googleapis.com/v1/places/{place_id}"
                det_headers = headers.copy()
                det_headers["X-Goog-FieldMask"] = "rating,userRatingCount,priceLevel,photos,websiteUri,formattedAddress,currentOpeningHours"

                det_r = requests.get(det_url, headers=det_headers, timeout=15)

                if det_r.status_code != 200:
                    print(f"       ⚠️  Details fetch failed for {place.get('displayName', {}).get('text', 'Unknown')}: {det_r.status_code} - {det_r.text[:200]}")
                    details = {}
                else:
                    details = det_r.json()
                    if not details or (not details.get("rating") and not details.get("formattedAddress")):
                        print(f"       ℹ️  Empty details for {place.get('displayName', {}).get('text', 'Unknown')}: {det_r.text[:300]}")

                photos = []
                if "photos" in details:
                    for p in details.get("photos", [])[:5]:
                        photo_name = p.get("name", "")
                        if photo_name:
                            photos.append(f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=800&key={api_key}")

                rating = details.get("rating", 0)
                reviews = details.get("userRatingCount", 0)
                score = rating * (reviews ** 0.5) if reviews > 0 else 0

                name = place.get("displayName", {}).get("text", "").lower()
                if any(term in name for term in category_config["boost_terms"]):
                    score *= category_config["score_multiplier"]

                poi_lat = place["location"]["latitude"]
                poi_lon = place["location"]["longitude"]
                dist_from_center = haversine((center_lon, center_lat), (poi_lon, poi_lat))

                if verbose and len(category_pois) < 2:
                    poi_name = place.get("displayName", {}).get("text", "Unknown")
                    print(f"\n         POI: {poi_name} at ({poi_lat:.4f}, {poi_lon:.4f})")
                    print(f"         Center: ({center_lon:.4f}, {center_lat:.4f})")
                    print(f"         haversine(({center_lon:.4f}, {center_lat:.4f}), ({poi_lon:.4f}, {poi_lat:.4f})) = {dist_from_center:.1f}km")
                    print(f"         Filter: {filter_radius_km:.1f}km")

                if dist_from_center > filter_radius_km:
                    if verbose and len(category_pois) < 2:
                        print(f"         ❌ Filtered out (too far)")
                    continue

                poi = {
                        "id": place_id,
                        "name": place.get("displayName", {}).get("text", "Unnamed"),
                        "category": category,
                        "google_types": place.get("types", []),
                        "location": {
                            "lat": place["location"]["latitude"],
                            "lon": place["location"]["longitude"]
                            },
                        "rating": round(rating, 2) if rating > 0 else None,
                        "reviews": reviews,
                        "price_level": details.get("priceLevel"),
                        "website": details.get("websiteUri"),
                        "address": details.get("formattedAddress"),
                        "images": photos,
                        "score": round(score, 2),
                        "is_open_now": details.get("currentOpeningHours", {}).get("openNow"),
                        "source": "Google Places"
                        }

                category_pois.append(poi)
                all_pois.append(poi)

        nearby_used = False
        nearby_found = False
        if category_config.get("place_types"):
            nearby_used = True
            url = "https://places.googleapis.com/v1/places:searchNearby"
            payload = {
                    "includedTypes": category_config["place_types"],
                    "maxResultCount": max_per_query,
                    "rankPreference": "DISTANCE",
                    "locationRestriction": {
                        "circle": {
                            "center": {"latitude": center_lat, "longitude": center_lon},
                            "radius": search_radius_km * 1000
                            }
                        },
                    "languageCode": "sk"
                    }
            try:
                r = requests.post(url, json=payload, headers=text_headers, timeout=20)
                if r.status_code != 200:
                    if verbose:
                        print(f"\n      ❌ Nearby API error {r.status_code} for {category}: {r.text[:150]}")
                else:
                    data = r.json()
                    places = data.get("places", [])
                    nearby_found = len(places) > 0
                    process_places(places, f"{category} nearby types")
            except Exception as e:
                if verbose:
                    print(f"\n      ⚠️ Nearby search failed: {e}")

        if not nearby_used or not nearby_found:
            for keyword_set in category_config["keywords"]:
                url = "https://places.googleapis.com/v1/places:searchText"
                payload = {
                        "textQuery": f"{keyword_set} in {city_hint}",
                        "maxResultCount": max_per_query,
                        "locationBias": {
                            "circle": {
                                "center": {"latitude": center_lat, "longitude": center_lon},
                                "radius": search_radius_km * 1000
                                }
                            },
                        "rankPreference": "RELEVANCE",
                        "languageCode": "sk"
                        }

                try:
                    r = requests.post(url, json=payload, headers=text_headers, timeout=20)
                    if r.status_code != 200:
                        if verbose:
                            print(f"\n      ❌ API error {r.status_code} for '{keyword_set}': {r.text[:150]}")
                        continue
                    data = r.json()
                    places = data.get("places", [])
                    process_places(places, f"'{keyword_set}'")
                except Exception:
                    continue

        seen = set()
        unique_category_pois = []
        for p in category_pois:
            key = (p["name"].lower(), round(p["location"]["lat"], 5), round(p["location"]["lon"], 5))
            if key not in seen:
                seen.add(key)
                unique_category_pois.append(p)

        unique_category_pois.sort(key=lambda x: x["score"], reverse=True)
        results["pois_by_category"][category] = unique_category_pois[:15]

        if verbose:
            print(f"found {len(unique_category_pois)} POIs")

    all_pois.sort(key=lambda x: x["score"], reverse=True)
    seen_global = set()
    unique_all = []
    for p in all_pois:
        key = (p["name"].lower(), round(p["location"]["lat"], 5), round(p["location"]["lon"], 5))
        if key not in seen_global:
            seen_global.add(key)
            unique_all.append(p)

    results["top_rated_overall"] = unique_all[:20]
    results["metadata"]["total_pois"] = len(unique_all)

    return results

def plan_trip(
        start: str,
        end: str,
        waypoints: Optional[List[str]] = None,
        auto_discover_routes: bool = True,
        poi_categories: Optional[List[str]] = None,
        api_key: Optional[str] = None
        ) -> Dict[str, Any]:
    api_key = api_key or GOOGLE_PLACES_API_KEY

    start_coords = geocode(start)
    end_coords = geocode(end)
    waypoint_coords = []

    if waypoints:
        for wp in waypoints:
            try:
                waypoint_coords.append(geocode(wp))
            except ValueError:
                pass

    direct_dist = haversine(start_coords, end_coords)

    if auto_discover_routes and not waypoints:
        print("\n🗺️  Discovering alternative routes...")
        print("   (This may take 30-60 seconds)")
        scenarios = generate_smart_scenarios(start_coords, end_coords, verbose=True)
    elif waypoints:
        scenarios = {"Requested Route": waypoint_coords}
    else:
        scenarios = {"Direct Route": None}

    result = {
            "trip_summary": {
                "start": start,
                "end": end,
                "start_coords": {"lat": start_coords[1], "lon": start_coords[0]},
                "end_coords": {"lat": end_coords[1], "lon": end_coords[0]},
                "direct_distance_km": round(direct_dist, 1),
                "waypoints": waypoints or [],
                "total_routes": len(scenarios)
                },
            "routes": [],
            "recommendations": {
                "fastest_route": None,
                "most_scenic": None,
                "best_for_attractions": None
                }
            }

    fastest_time = float('inf')
    most_pois = 0

    print(f"\n🛣️  Analyzing {len(scenarios)} route(s)...")
    print(f"   (This may take 2-3 minutes for POI discovery)\n")

    for idx, (scenario_name, wps) in enumerate(scenarios.items(), 1):
        print(f"\n[{idx}/{len(scenarios)}] Route: {scenario_name}")
        routes = get_osrm_routes(start_coords, end_coords, wps or None)
        if not routes:
            print(f"   ✗ No route found")
            continue

        route = routes[0]
        print(f"   🔄 Calculating route... ✓ {route['distance_km']} km, {route['duration_min']} min")

        poi_data = get_pois_along_route_google(
                route["geometry"], 
                api_key,
                categories=poi_categories,
                verbose=True
                )

        route_info = {
                "name": scenario_name,
                "distance_km": route["distance_km"],
                "duration_min": route["duration_min"],
                "waypoints": wps,
                "geometry": route["geometry"],
                "poi_summary": {
                    "total_pois": poi_data["metadata"]["total_pois"],
                    "location_hint": poi_data["metadata"]["location_hint"],
                    "categories": {}
                    },
                "top_pois": poi_data["top_rated_overall"][:10],
                "pois_by_category": poi_data["pois_by_category"]
                }

        for cat, pois in poi_data["pois_by_category"].items():
            route_info["poi_summary"]["categories"][cat] = {
                    "count": len(pois),
                    "top_rated": pois[0]["name"] if pois else None
                    }

        result["routes"].append(route_info)

        if route["duration_min"] < fastest_time:
            fastest_time = route["duration_min"]
            result["recommendations"]["fastest_route"] = scenario_name

        if poi_data["metadata"]["total_pois"] > most_pois:
            most_pois = poi_data["metadata"]["total_pois"]
            result["recommendations"]["best_for_attractions"] = scenario_name

    max_nature_score = 0
    for route in result["routes"]:
        nature_count = route["poi_summary"]["categories"].get("nature", {}).get("count", 0)
        attractions_count = route["poi_summary"]["categories"].get("attractions", {}).get("count", 0)
        nature_score = nature_count + attractions_count
        if nature_score > max_nature_score:
            max_nature_score = nature_score
            result["recommendations"]["most_scenic"] = route["name"]

    return result

def ultimate_route_planner(start_city: str, end_city: str, scenarios=None):
    start = geocode(start_city)
    end = geocode(end_city)

    direct_dist = haversine(start, end)
    print(f"Direct distance: {direct_dist:.1f} km")

    if scenarios is None:
        print("Generating smart scenarios with distance guardrails...")
        scenarios = generate_smart_scenarios(start, end, verbose=True)

    results = {}
    for name, wps in scenarios.items():
        print(f"\n{name}")
        routes = get_osrm_routes(start, end, wps or None)
        if not routes:
            continue
        route = routes[0]
        print(f"   → {route['distance_km']} km | {route['duration_min']} min")

        poi_data = get_pois_along_route_google(
                route["geometry"], 
                GOOGLE_PLACES_API_KEY,
                categories=["attractions", "dining", "accommodation"]
                )

        all_pois = poi_data["top_rated_overall"]
        cultural = [p for p in all_pois if p["category"] in ["attractions", "nature", "worship"]][:10]
        practical = [p for p in all_pois if p["category"] in ["dining", "accommodation", "services"]][:10]

        results[name] = {
                "distance_km": route["distance_km"],
                "duration_min": route["duration_min"],
                "total_pois": poi_data["metadata"]["total_pois"],
                "top_cultural": cultural,
                "top_practical": practical,
                "all_pois": all_pois
                }

    return results