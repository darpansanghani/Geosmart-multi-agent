import json
import math
from typing import Dict, Any, List, Optional
from shapely.geometry import Point, Polygon
from .context import AgentContext
from ..db.connection import get_pool

class GISIntelligenceAgent:
    """
    GISIntelligenceAgent - Enriches complaints with geospatial context
    """
    def __init__(self):
        self.name = 'GISIntelligenceAgent'
        self.zones_data = self._get_fallback_zone_data() # simplified to use fallback for portability

    async def execute(self, context: AgentContext) -> Dict[str, Any]:
        lat = context.get('latitude')
        lng = context.get('longitude')
        
        try:
            # Get zone/ward info
            zone_info = await self._get_zone_info(lat, lng)
            
            # Find nearby facilities
            nearby_facilities = self._get_nearby_facilities(lat, lng)
            
            # Check historical issues
            historical_issues = await self._get_historical_issues(zone_info['ward_number'])
            
            await context.update(self.name, {
                "zone_name": zone_info['zone_name'],
                "ward_number": zone_info['ward_number'],
                "nearby_facilities": nearby_facilities,
                "historical_issues": historical_issues
            })
            
            facilities_str = ", ".join(nearby_facilities) if nearby_facilities else "No major facilities nearby"
            
            return {
                "summary": f"Zone: {zone_info['zone_name']}, Ward: {zone_info['ward_number']}, Proximity: {facilities_str}"
            }
            
        except Exception as e:
            print(f"GISIntelligenceAgent error: {e}")
            await context.update(self.name, {
                "zone_name": "Central Zone",
                "ward_number": 0,
                "nearby_facilities": [],
                "historical_issues": []
            })
            return {"summary": "Zone: Central Zone, Ward: Unknown (using fallback)"}

    async def _get_zone_info(self, lat: float, lng: float) -> Dict[str, Any]:
        point = Point(lng, lat)
        
        # Check GeoJSON features (fallback data)
        if self.zones_data and "features" in self.zones_data:
            for feature in self.zones_data["features"]:
                try:
                    coords = feature["geometry"]["coordinates"][0] # Assuming simple polygon
                    polygon = Polygon(coords)
                    if polygon.contains(point):
                        props = feature["properties"]
                        return {
                            "zone_name": props.get("zone_name"),
                            "ward_number": props.get("ward_number") or (props.get("ward_numbers")[0] if props.get("ward_numbers") else 0)
                        }
                except Exception:
                    continue
        
        # Try Database
        try:
            pool = await get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow('SELECT zone_name, ward_number FROM zones LIMIT 1') # Placeholder query logic
                if row:
                    return {"zone_name": row["zone_name"], "ward_number": row["ward_number"]}
        except Exception:
            pass
            
        return {"zone_name": "Central Zone", "ward_number": 0}

    def _get_nearby_facilities(self, lat: float, lng: float) -> List[str]:
        facilities = {
            'hospitals': [
                (17.4326, 78.4071, 'Apollo Hospital'),
                (17.4400, 78.4500, 'Care Hospital'),
                (17.4200, 78.3900, 'NIMS Hospital')
            ],
            'schools': [
                (17.4350, 78.4080, 'Delhi Public School'),
                (17.4300, 78.4100, 'Jubilee Hills Public School')
            ],
            'markets': [
                (17.4300, 78.4050, 'Banjara Market'),
                (17.4380, 78.4120, 'Road No 10 Market')
            ]
        }
        
        nearby = []
        threshold = 0.01
        
        for type_, locations in facilities.items():
            for fac_lat, fac_lng, name in locations:
                distance = math.sqrt((lat - fac_lat)**2 + (lng - fac_lng)**2)
                if distance < threshold:
                    nearby.append(name)
        return nearby

    async def _get_historical_issues(self, ward_number: int) -> List[str]:
        try:
            pool = await get_pool()
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT category, COUNT(*) as count 
                    FROM complaints 
                    WHERE ward_number = $1 
                    GROUP BY category 
                    ORDER BY count DESC 
                    LIMIT 3
                    """,
                    ward_number
                )
                return [f"{r['category']} ({r['count']} times)" for r in rows]
        except Exception:
            return []

    def _get_fallback_zone_data(self):
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": { "zone_name": "Khairatabad Zone (Central)", "ward_number": 90 },
                    "geometry": {
                        "type": "Polygon", 
                        "coordinates": [[[78.40, 17.35], [78.50, 17.35], [78.50, 17.45], [78.40, 17.45], [78.40, 17.35]]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": { "zone_name": "Secunderabad Zone (North)", "ward_number": 140 },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[78.40, 17.45], [78.60, 17.45], [78.60, 17.60], [78.40, 17.60], [78.40, 17.45]]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": { "zone_name": "Charminar Zone (South)", "ward_number": 20 },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[78.40, 17.20], [78.60, 17.20], [78.60, 17.35], [78.40, 17.35], [78.40, 17.20]]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": { "zone_name": "Serilingampally Zone (West)", "ward_number": 100 },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[78.20, 17.20], [78.40, 17.20], [78.40, 17.60], [78.20, 17.60], [78.20, 17.20]]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": { "zone_name": "LB Nagar Zone (East)", "ward_number": 15 },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[78.50, 17.20], [78.70, 17.20], [78.70, 17.45], [78.50, 17.45], [78.50, 17.20]]]
                    }
                }
            ]
        }
