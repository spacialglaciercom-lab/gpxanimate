import streamlit as st
import gpxpy
import gpxpy.gpx
import json
import math
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="GPX Route Animator",
    page_icon="🗺️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #0D0D1A;
        color: white;
    }
    .stFileUploader {
        background-color: #1a1a2e;
        border-radius: 10px;
        padding: 20px;
    }
    .stats-container {
        background-color: #1a1a2e;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .control-btn {
        background-color: #6c5ce7;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        margin: 5px;
    }
    .control-btn:hover {
        background-color: #a29bfe;
    }
    </style>
""", unsafe_allow_html=True)

def parse_gpx_file(gpx_file):
    """Parse GPX file and extract route data"""
    try:
        # Read the uploaded file
        gpx_content = gpx_file.read()
        
        # Parse using gpxpy
        gpx = gpxpy.parse(gpx_content)
        
        # Extract track points
        coordinates = []
        elevations = []
        times = []
        
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    coordinates.append({
                        'latitude': point.latitude,
                        'longitude': point.longitude
                    })
                    elevations.append(point.elevation if point.elevation else 0)
                    times.append(point.time.timestamp() if point.time else 0)
        
        # Calculate distances between points
        distances = [0.0]
        total_distance = 0.0
        
        for i in range(1, len(coordinates)):
            dist = calculate_distance(coordinates[i-1], coordinates[i])
            total_distance += dist
            distances.append(total_distance)
        
        return {
            'coordinates': coordinates,
            'elevations': elevations,
            'times': times,
            'distances': distances,
            'total_distance': total_distance,
            'point_count': len(coordinates)
        }
        
    except Exception as e:
        st.error(f"Error parsing GPX file: {e}")
        return None

def calculate_distance(point1, point2):
    """Calculate distance between two points in meters using Haversine formula"""
    R = 6371000  # Earth radius in meters
    
    lat1 = math.radians(point1['latitude'])
    lat2 = math.radians(point2['latitude'])
    lon1 = math.radians(point1['longitude'])
    lon2 = math.radians(point2['longitude'])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def get_route_stats(route_data):
    """Generate statistics for the route"""
    if not route_data or len(route_data['coordinates']) < 2:
        return None
    
    stats = {
        'total_distance_km': round(route_data['total_distance'] / 1000, 2),
        'total_distance_miles': round(route_data['total_distance'] * 0.000621371, 2),
        'point_count': route_data['point_count'],
        'segment_count': route_data['point_count'] - 1,
        'elevation_gain': 0,
        'elevation_loss': 0,
        'duration': 0
    }
    
    # Calculate elevation changes
    if len(route_data['elevations']) > 1:
        elevation_changes = []
        for i in range(1, len(route_data['elevations'])):
            elevation_changes.append(route_data['elevations'][i] - route_data['elevations'][i-1])
        stats['elevation_gain'] = round(max(0, sum(x for x in elevation_changes if x > 0)), 2)
        stats['elevation_loss'] = round(abs(min(0, sum(x for x in elevation_changes if x < 0))), 2)
    
    # Calculate duration
    if len(route_data['times']) > 1 and any(route_data['times']):
        time_diff = max(route_data['times']) - min(t for t in route_data['times'] if t > 0)
        if time_diff > 0:
            stats['duration'] = round(time_diff / 3600, 2)  # hours
    
    return stats

def main():
    st.title("🗺️ GPX Route Animator")
    st.markdown("Upload a GPX file to visualize and animate your route")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a GPX file", type=["gpx"])
    
    if uploaded_file is not None:
        # Parse the GPX file
        with st.spinner("Parsing GPX file..."):
            route_data = parse_gpx_file(uploaded_file)
        
        if route_data and len(route_data['coordinates']) > 1:
            # Display route statistics
            stats = get_route_stats(route_data)
            
            if stats:
                st.subheader("📊 Route Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Distance", f"{stats['total_distance_km']} km")
                    st.metric("Points", stats['point_count'])
                with col2:
                    st.metric("Elevation Gain", f"{stats['elevation_gain']} m")
                with col3:
                    st.metric("Elevation Loss", f"{stats['elevation_loss']} m")
                with col4:
                    if stats['duration'] > 0:
                        st.metric("Duration", f"{stats['duration']} hours")
            
            # Prepare data for JavaScript component
            map_data = {
                'coordinates': route_data['coordinates'],
                'total_distance': route_data['total_distance'],
                'point_count': route_data['point_count']
            }
            
            # HTML component for the map
            st.subheader("🗺️ Route Map")
            
            # Create a container for the map
            map_html = '''
            <div id="map-container" style="height: 600px; width: 100%; border-radius: 10px; overflow: hidden;">
                <div id="map" style="height: 100%; width: 100%"></div>
            </div>
            
            <div id="controls" style="margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap;">
                <button class="control-btn" onclick="playAnimation()">▶ Play</button>
                <button class="control-btn" onclick="pauseAnimation()">⏸ Pause</button>
                <button class="control-btn" onclick="resetAnimation()">🔄 Reset</button>
                <button class="control-btn" onclick="rewindAnimation()">⏪ Rewind</button>
                <button class="control-btn" onclick="forwardAnimation()">⏩ Forward</button>
                <div style="flex: 1; min-width: 300px; display: flex; gap: 5px; justify-content: center;">
                    <button class="control-btn" onclick="setSpeed(0.5)" style="min-width: 40px;">0.5x</button>
                    <button class="control-btn" onclick="setSpeed(1)" style="min-width: 40px;">1x</button>
                    <button class="control-btn" onclick="setSpeed(2)" style="min-width: 40px;">2x</button>
                    <button class="control-btn" onclick="setSpeed(4)" style="min-width: 40px;">4x</button>
                    <button class="control-btn" onclick="setSpeed(8)" style="min-width: 40px;">8x</button>
                </div>
            </div>
            
            <div id="progress" style="margin-top: 10px;">
                <div style="display: flex; justify-content: space-between;">
                    <span>Progress: <span id="progressValue">0%</span></span>
                    <span>Distance: <span id="distanceValue">0 km</span> / ''' + str(stats['total_distance_km']) + ''' km</span>
                </div>
                <input type="range" id="progressSlider" min="0" max="''' + str(route_data['point_count'] - 1) + '''", value="0" 
                       style="width: 100%;" oninput="seekTo(this.value)">
            </div>
            
            <script>
            // Route data from Python
            const routeData = ''' + json.dumps(map_data) + ''';
            
            // Map initialization
            let map;
            let polyline;
            let completedPolyline;
            let currentPositionMarker;
            let directionArrows = [];
            let animationInterval;
            let currentIndex = 0;
            let isPlaying = false;
            let speed = 1.0;
            
            // Initialize map
            function initMap() {
                const lat = ''' + str(map_data['coordinates'][0]['latitude']) + ''';
                const lng = ''' + str(map_data['coordinates'][0]['longitude']) + ''';
                map = L.map('map').setView([lat, lng], 13);
                
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);
                
                // Create polylines
                const allCoords = routeData.coordinates.map(c => [c.latitude, c.longitude]);
                
                // Completed route (red)
                completedPolyline = L.polyline([], {
                    color: '#E74C3C',
                    weight: 5,
                    opacity: 0.8
                }).addTo(map);
                
                // Pending route (yellow)
                polyline = L.polyline(allCoords, {
                    color: '#F7DC6F',
                    weight: 5,
                    opacity: 0.8
                }).addTo(map);
                
                // Current position marker
                currentPositionMarker = L.circleMarker(allCoords[0], {
                    radius: 8,
                    fillColor: '#2980B9',
                    color: '#fff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }).addTo(map);
                
                // Fit map to route bounds
                const bounds = L.latLngBounds(allCoords);
                map.fitBounds(bounds);
                
                // Update UI
                updateUI();
            }
            
            // Animation functions
            function playAnimation() {
                if (isPlaying) return;
                isPlaying = true;
                
                animationInterval = setInterval(() => {
                    if (currentIndex < routeData.coordinates.length - 1) {
                        currentIndex++;
                        updateUI();
                    } else {
                        pauseAnimation();
                    }
                }, 500 / speed);
            }
            
            function pauseAnimation() {
                if (!isPlaying) return;
                isPlaying = false;
                clearInterval(animationInterval);
            }
            
            function resetAnimation() {
                pauseAnimation();
                currentIndex = 0;
                updateUI();
            }
            
            function rewindAnimation() {
                if (currentIndex > 5) {
                    currentIndex -= 5;
                } else {
                    currentIndex = 0;
                }
                updateUI();
            }
            
            function forwardAnimation() {
                if (currentIndex < routeData.coordinates.length - 6) {
                    currentIndex += 5;
                } else {
                    currentIndex = routeData.coordinates.length - 1;
                }
                updateUI();
            }
            
            function seekTo(index) {
                currentIndex = parseInt(index);
                updateUI();
            }
            
            function setSpeed(newSpeed) {
                speed = parseFloat(newSpeed);
                // Update visual feedback for selected speed
                const buttons = document.querySelectorAll('[onclick^="setSpeed"]');
                buttons.forEach(btn => {
                    if (btn.textContent === newSpeed + 'x') {
                        btn.style.backgroundColor = '#2980B9';
                    } else {
                        btn.style.backgroundColor = '#6c5ce7';
                    }
                });
                if (isPlaying) {
                    pauseAnimation();
                    playAnimation();
                }
            }
            
            // Initialize with 1x speed
            setSpeed(1);
            
            function updateUI() {
                // Update polylines
                const completedCoords = routeData.coordinates.slice(0, currentIndex + 1).map(c => [c.latitude, c.longitude]);
                const pendingCoords = routeData.coordinates.slice(currentIndex + 1).map(c => [c.latitude, c.longitude]);
                
                completedPolyline.setLatLngs(completedCoords);
                polyline.setLatLngs(pendingCoords);
                
                // Update current position marker
                const currentCoord = [routeData.coordinates[currentIndex].latitude, routeData.coordinates[currentIndex].longitude];
                currentPositionMarker.setLatLng(currentCoord);
                
                // Update progress
                const progressPercent = Math.round((currentIndex / (routeData.coordinates.length - 1)) * 100);
                const progressDistance = (routeData.total_distance * currentIndex / (routeData.coordinates.length - 1)) / 1000;
                
                document.getElementById('progressValue').textContent = progressPercent + '%';
                document.getElementById('distanceValue').textContent = progressDistance.toFixed(2) + ' km';
                document.getElementById('progressSlider').value = currentIndex;
                
                // Center map on current position if needed
                if (currentIndex % 10 === 0) {
                    map.panTo(currentCoord);
                }
            }
            
            // Initialize when page loads
            document.addEventListener('DOMContentLoaded', function() {{
                // Load Leaflet library
                if (typeof L === 'undefined') {{
                    const script = document.createElement('script');
                    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
                    script.onload = initMap;
                    document.head.appendChild(script);
                    
                    const link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
                    document.head.appendChild(link);
                }} else {{
                    initMap();
                }}
            }});
            </script>
            '''
            
            st.components.v1.html(map_html, height=700)
            
            # Display raw data for debugging
            with st.expander("🔍 Raw Route Data"):
                st.json(route_data)
        else:
            st.error("No valid route data found in the GPX file. Make sure it contains track points.")

if __name__ == "__main__":
    main()