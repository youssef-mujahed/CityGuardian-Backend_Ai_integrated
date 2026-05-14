import openrouteservice
from openrouteservice.directions import directions
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from app.core.config import settings
from app.models.hospital import Hospital
from app.models.route import Route
from typing import List, Dict, Any

# Initialize OpenRouteService client
client = openrouteservice.Client(key=settings.OPENROUTESERVICE_API_KEY)

class RoutingService:
    
    @staticmethod
    def get_all_hospitals(db: Session, active_only: bool = True) -> List[Hospital]:
        """Get all hospitals"""
        query = db.query(Hospital)
        if active_only:
            query = query.filter(Hospital.is_active == True)
        return query.order_by(Hospital.name).all()
    
    @staticmethod
    def add_hospital(db: Session, hospital_data: dict) -> Hospital:
        """Add a new hospital (admin only)"""
        new_hospital = Hospital(**hospital_data)
        db.add(new_hospital)
        db.commit()
        db.refresh(new_hospital)
        return new_hospital
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
        """Calculate straight-line distance in meters (fallback)"""
        R = 6371000  # Earth's radius in meters
        lat1_r = radians(lat1)
        lat2_r = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return int(R * c)
    
    @staticmethod
    def find_nearest_hospital_by_distance(
        db: Session, 
        latitude: float, 
        longitude: float
    ) -> Dict[str, Any]:
        """Find the nearest hospital by straight-line distance (fallback)"""
        hospitals = RoutingService.get_all_hospitals(db)
        
        if not hospitals:
            raise ValueError("No hospitals found in database")
        
        nearest = min(hospitals, key=lambda h: RoutingService.calculate_distance(
            latitude, longitude, h.latitude, h.longitude
        ))
        
        distance = RoutingService.calculate_distance(latitude, longitude, nearest.latitude, nearest.longitude)
        
        return {
            "hospital": nearest,
            "distance_meters": distance
        }
    
    @staticmethod
    def get_route(
        db: Session,
        incident_id: UUID,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        hospital_id: UUID
    ) -> Dict[str, Any]:
        """Get driving route using OpenRouteService"""
        
        try:
            # Prepare coordinates (OpenRouteService expects [lng, lat] format)
            start = [origin_lng, origin_lat]
            end = [dest_lng, dest_lat]
            
            # Get directions
            routes = directions(
                client=client,
                coordinates=[start, end],
                profile='driving-car',
                format='geojson',
                preference='fastest'
            )
            
            if not routes or 'features' not in routes or not routes['features']:
                raise ValueError("No route found")
            
            route = routes['features'][0]
            properties = route['properties']
            geometry = route['geometry']
            segments = properties['segments'][0]
            
            # Extract route data
            distance_meters = int(segments['distance'])
            duration_seconds = int(segments['duration'])
            
            # Extract steps for turn-by-turn directions
            steps = []
            for step in segments.get('steps', []):
                steps.append({
                    "instruction": step.get('instruction', ''),
                    "distance": step.get('distance', 0),
                    "duration": step.get('duration', 0)
                })
            
            result = {
                "distance_meters": distance_meters,
                "distance_km": round(distance_meters / 1000, 1),
                "duration_seconds": duration_seconds,
                "duration_minutes": round(duration_seconds / 60),
                "duration_text": f"{round(duration_seconds / 60)} minutes",
                "route_geometry": geometry.get('coordinates', []),
                "steps": steps,
                "source": "OpenRouteService"
            }
            
            # Save route to database
            new_route = Route(
                incident_id=incident_id,
                hospital_id=hospital_id,
                origin_lat=origin_lat,
                origin_lng=origin_lng,
                destination_lat=dest_lat,
                destination_lng=dest_lng,
                distance_meters=result["distance_meters"],
                eta_seconds=result["duration_seconds"],
                route_geometry=result
            )
            db.add(new_route)
            db.commit()
            
            return result
            
        except Exception as e:
            print(f"OpenRouteService API error: {e}")
            # Fallback to straight-line calculation
            distance = RoutingService.calculate_distance(origin_lat, origin_lng, dest_lat, dest_lng)
            # Assume average speed of 15 m/s (~54 km/h) for estimation
            duration = int(distance / 15)
            
            return {
                "distance_meters": distance,
                "distance_km": round(distance / 1000, 1),
                "duration_seconds": duration,
                "duration_minutes": round(duration / 60),
                "duration_text": f"{round(duration / 60)} minutes (estimated)",
                "route_geometry": None,
                "steps": [],
                "source": "Estimate (API fallback)",
                "note": "Using straight-line distance estimate"
            }
    
    @staticmethod
    def get_best_route_to_hospital(
        db: Session,
        incident_id: UUID,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """Get best route from incident to nearest hospital"""
        
        # Get all active hospitals
        hospitals = RoutingService.get_all_hospitals(db, active_only=True)
        
        if not hospitals:
            raise ValueError("No hospitals available")
        
        # Calculate route to each hospital and find the fastest
        best_route = None
        best_duration = float('inf')
        best_hospital = None
        
        for hospital in hospitals:
            try:
                route_data = RoutingService.get_route(
                    db, incident_id, latitude, longitude,
                    hospital.latitude, hospital.longitude,
                    hospital.id
                )
                
                if route_data["duration_seconds"] < best_duration:
                    best_duration = route_data["duration_seconds"]
                    best_route = route_data
                    best_hospital = hospital
                    
            except Exception as e:
                print(f"Error calculating route to {hospital.name}: {e}")
                continue
        
        if not best_route:
            raise ValueError("Could not calculate route to any hospital")
        
        return {
            "incident_id": incident_id,
            "hospital": {
                "id": best_hospital.id,
                "name": best_hospital.name,
                "latitude": best_hospital.latitude,
                "longitude": best_hospital.longitude,
                "address": best_hospital.address,
                "phone": best_hospital.phone
            },
            "route": best_route
        }
    
    @staticmethod
    def get_saved_route_for_incident(db: Session, incident_id: UUID) -> Route:
        """Get the most recent saved route for an incident"""
        route = db.query(Route).filter(
            Route.incident_id == incident_id,
            Route.is_active == True
        ).order_by(Route.created_at.desc()).first()
        
        if not route:
            raise ValueError("No route found for this incident")
        
        return route