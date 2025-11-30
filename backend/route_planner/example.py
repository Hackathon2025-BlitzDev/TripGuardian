"""
Simple example showing how to use the route planner tool.
Configure your trip parameters and run this file.
"""

from route_planer import plan_trip
import json

# ============================================================================
# CONFIGURATION - Edit these values for your trip
# ============================================================================

START_CITY = "Kosice, Slovakia"
END_CITY = "Bardejov, Slovakia"

# Option 1: Auto-discover routes (finds cities along the way)
AUTO_DISCOVER = True
WAYPOINTS = []  # Leave empty for auto-discovery

# Option 2: Specify custom waypoints
# AUTO_DISCOVER = False
# WAYPOINTS = ["Poprad", "Banska Bystrica"]  # Cities to pass through

# POI categories to search for
# Available: "attractions", "dining", "accommodation", "services", "nature", "worship"
POI_CATEGORIES = ["attractions", "dining", "accommodation"]

# ============================================================================
# RUN THE PLANNER
# ============================================================================

print(f"Planning trip: {START_CITY} → {END_CITY}")
print(f"POI Categories: {', '.join(POI_CATEGORIES)}")
print("-" * 80)

result = plan_trip(
    start=START_CITY,
    end=END_CITY,
    waypoints=WAYPOINTS if not AUTO_DISCOVER else None,
    auto_discover_routes=AUTO_DISCOVER,
    poi_categories=POI_CATEGORIES
)

# ============================================================================
# DISPLAY RESULTS
# ============================================================================

print(f"\n📍 Trip Summary:")
print(f"   Start: {result['trip_summary']['start']}")
print(f"   End: {result['trip_summary']['end']}")
print(f"   Direct Distance: {result['trip_summary']['direct_distance_km']} km")
print(f"   Routes Found: {result['trip_summary']['total_routes']}")

print(f"\n🎯 Recommendations:")
print(f"   ⚡ Fastest: {result['recommendations']['fastest_route']}")
print(f"   🌄 Most Scenic: {result['recommendations']['most_scenic']}")
print(f"   🏛️  Best for Attractions: {result['recommendations']['best_for_attractions']}")

print(f"\n🛣️  Route Details:")
for route in result["routes"]:
    print(f"\n   {route['name']}")
    print(f"      Distance: {route['distance_km']} km")
    print(f"      Duration: {route['duration_min']} min")
    print(f"      Total POIs: {route['poi_summary']['total_pois']}")
    
    # Show category breakdown
    for category, info in route["poi_summary"]["categories"].items():
        if info["count"] > 0:
            print(f"         • {category}: {info['count']} found (top: {info['top_rated']})")

# ============================================================================
# SAVE FULL RESULTS
# ============================================================================

output_file = "trip_plan.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n✅ Full results saved to: {output_file}")
print("\nThe JSON file contains:")
print("   • All routes with detailed waypoint coordinates")
print("   • Complete POI lists with ratings, reviews, photos, addresses")
print("   • Categorized POIs for each route")
print("   • Metadata and recommendations")
