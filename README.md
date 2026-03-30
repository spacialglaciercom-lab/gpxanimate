# GPX Route Animator - Web Version

A Streamlit web application for animating GPX file routes, adapted from the original React Native mobile app.

## Features

- **GPX File Upload**: Upload GPX files directly from your browser
- **Route Visualization**: 
  - 🔴 **Red** for completed/traversed segments
  - 🟡 **Yellow** for pending segments
- **Interactive Map**: Leaflet.js map with OpenStreetMap tiles
- **Playback Controls**:
  - Play/Pause animation
  - Rewind (jump back 5 segments)
  - Forward (jump ahead 5 segments)
  - Reset to beginning
  - Seek slider for precise navigation
- **Speed Control**: Adjustable playback speed (0.5x, 1x, 2x, 4x, 8x)
- **Stats Display**: Progress percentage, completed distance, total distance, elevation gain/loss
- **Route Statistics**: Distance, elevation gain/loss, duration, point count

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup

```bash
# Clone or download this repository
cd gpx-route-animator-web

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the Streamlit app
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

### Using the App
1. **Upload a GPX File**: Click "Choose a GPX file" button and select your GPX file
2. **View Statistics**: See route distance, elevation, and other stats
3. **Play Animation**: Press the play button to start route animation
4. **Adjust Speed**: Click speed buttons (0.5x to 8x) to change animation speed
5. **Navigate**: Use rewind/forward buttons or drag the slider to jump to specific segments
6. **View Full Route**: The map automatically fits to show the entire route

## GPX File Format

The app supports standard GPX files with track points (`<trkpt>`), waypoints (`<wpt>`), or route points (`<rtept>`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1">
  <trk>
    <trkseg>
      <trkpt lat="40.7128" lon="-74.0060"></trkpt>
      <trkpt lat="40.7138" lon="-74.0050"></trkpt>
      <!-- more points -->
    </trkseg>
  </trk>
</gpx>
```

## Dependencies

- `streamlit` - Web application framework
- `gpxpy` - GPX file parsing

## Technical Details

### Architecture
This is a hybrid Streamlit + JavaScript application:
- **Backend**: Streamlit (Python) handles file upload and GPX parsing
- **Frontend**: JavaScript/Leaflet.js handles interactive map and animation
- **Communication**: Data is passed from Python to JavaScript via Streamlit's `components.html()`

### Key Components

1. **GPX Parsing**: Uses `gpxpy` library to extract coordinates, elevations, and timestamps
2. **Distance Calculation**: Haversine formula for accurate distance between points
3. **Map Rendering**: Leaflet.js with OpenStreetMap tiles (no API key required)
4. **Animation**: JavaScript interval-based animation with speed control
5. **UI Controls**: HTML/CSS buttons and sliders with event handlers

## Customization

### Colors
Edit the colors in the JavaScript section of `streamlit_app.py`:
- Completed route: `#E74C3C` (red)
- Pending route: `#F7DC6F` (yellow)
- Current position: `#2980B9` (blue)

### Animation Speed
Modify the base interval in the `playAnimation()` function (default: 500ms)

### Map Tiles
Change the tile layer URL to use different map providers

## Troubleshooting

**Map not showing?**
- Check browser console for JavaScript errors
- Ensure internet connection for loading Leaflet.js and map tiles
- Try a different browser

**GPX file not loading?**
- Check file format matches standard GPX structure
- Ensure file contains valid track points

**Animation stuttering?**
- Reduce playback speed
- GPX files with thousands of points may need optimization
- Try a simpler route file

## Limitations

- Large GPX files (>10,000 points) may cause performance issues
- Animation is client-side only (no server-side processing)
- Requires internet connection for map tiles
- Mobile browser support may vary

## License

MIT License - Feel free to use and modify for your projects.

## Credits

- Original React Native app: GPX Route Animator
- Mapping: Leaflet.js and OpenStreetMap
- Web framework: Streamlit