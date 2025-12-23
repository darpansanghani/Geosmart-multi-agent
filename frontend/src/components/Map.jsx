import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const Map = ({ selectedLocation, complaints, onLocationSelect }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);
  const selectedMarkerRef = useRef(null);
  const liveLocationMarkerRef = useRef(null);
  const isInitialLoadRef = useRef(true);
  const isMountedRef = useRef(true);
  const onLocationSelectRef = useRef(onLocationSelect);

  // Keep the callback ref updated
  useEffect(() => {
    onLocationSelectRef.current = onLocationSelect;
  }, [onLocationSelect]);

  // Initialize map
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Ensure mounted flag is set
    isMountedRef.current = true;

    try {
      // Create map centered on Hyderabad
      const map = L.map(mapRef.current).setView([17.4326, 78.4071], 12);

      // Add tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
      }).addTo(map);

      // Add click handler to select location
      map.on('click', (e) => {
        console.log('Map clicked!', {
          mounted: isMountedRef.current,
          hasCallback: !!onLocationSelectRef.current,
          lat: e.latlng.lat,
          lng: e.latlng.lng
        });
        if (isMountedRef.current && onLocationSelectRef.current) {
          onLocationSelectRef.current(e.latlng.lat, e.latlng.lng);
          console.log('Location select called');
        } else {
          console.warn('Click not processed:', {
            mounted: isMountedRef.current,
            hasCallback: !!onLocationSelectRef.current
          });
        }
      });

      // Add right-click handler to deselect marker
      map.on('contextmenu', (e) => {
        e.originalEvent.preventDefault();
        if (selectedMarkerRef.current && isMountedRef.current && onLocationSelectRef.current) {
          selectedMarkerRef.current.remove();
          selectedMarkerRef.current = null;
          onLocationSelectRef.current(null, null);
        }
      });

      mapInstanceRef.current = map;

      // Request live location after map is fully initialized
      setTimeout(() => {
        if (!isMountedRef.current || !mapInstanceRef.current) return;

        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            (position) => {
              if (!isMountedRef.current || !mapInstanceRef.current) return;

              const { latitude, longitude } = position.coords;
              
              try {
                // Create custom live location icon
                const liveIcon = L.divIcon({
                  className: 'live-location-marker',
                  html: `<div style="
                    width: 16px;
                    height: 16px;
                    border-radius: 50%;
                    background: #3b82f6;
                    border: 3px solid white;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3), 0 2px 4px rgba(0,0,0,0.3);
                  "></div>`,
                  iconSize: [16, 16],
                  iconAnchor: [8, 8]
                });

                // Add live location marker
                liveLocationMarkerRef.current = L.marker([latitude, longitude], { 
                  icon: liveIcon,
                  zIndexOffset: 1000
                })
                  .addTo(mapInstanceRef.current)
                  .bindPopup('📍 Your Location');

                // Automatically select this location
                if (isMountedRef.current && onLocationSelectRef.current) {
                  onLocationSelectRef.current(latitude, longitude);
                  mapInstanceRef.current.setView([latitude, longitude], 14);
                }
                
                // Mark initial load as complete
                setTimeout(() => {
                  isInitialLoadRef.current = false;
                }, 500);
              } catch (error) {
                console.error('Error adding live location marker:', error);
                isInitialLoadRef.current = false;
              }
            },
            (error) => {
              console.warn('Geolocation error:', error.message);
              isInitialLoadRef.current = false;
            },
            {
              enableHighAccuracy: true,
              timeout: 5000,
              maximumAge: 0
            }
          );
        } else {
          isInitialLoadRef.current = false;
        }
      }, 500);
    } catch (error) {
      console.error('Error initializing map:', error);
    }

    return () => {
      // Mark as unmounted
      isMountedRef.current = false;
      
      // Cleanup markers
      if (selectedMarkerRef.current) {
        try {
          selectedMarkerRef.current.remove();
        } catch (e) {
          console.warn('Error removing selected marker:', e);
        }
        selectedMarkerRef.current = null;
      }
      
      if (liveLocationMarkerRef.current) {
        try {
          liveLocationMarkerRef.current.remove();
        } catch (e) {
          console.warn('Error removing live location marker:', e);
        }
        liveLocationMarkerRef.current = null;
      }

      markersRef.current.forEach(marker => {
        try {
          marker.remove();
        } catch (e) {
          console.warn('Error removing marker:', e);
        }
      });
      markersRef.current = [];

      // Cleanup map
      if (mapInstanceRef.current) {
        try {
          mapInstanceRef.current.remove();
        } catch (e) {
          console.warn('Error removing map:', e);
        }
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update selected location marker
  useEffect(() => {
    if (!mapInstanceRef.current || !isMountedRef.current) return;

    // Remove previous selected marker
    if (selectedMarkerRef.current) {
      try {
        selectedMarkerRef.current.remove();
      } catch (e) {
        console.warn('Error removing previous marker:', e);
      }
      selectedMarkerRef.current = null;
    }

    if (!selectedLocation) return;

    try {
      // Add new draggable marker for selected location
      const marker = L.marker([selectedLocation.lat, selectedLocation.lng], {
        draggable: true
      })
        .addTo(mapInstanceRef.current)
        .bindPopup('📍 Selected location<br><small>Drag to move • Right-click to remove</small>');

      // Handle marker drag
      marker.on('drag', (e) => {
        // Position updates happen automatically
      });

      marker.on('dragend', (e) => {
        if (isMountedRef.current && onLocationSelectRef.current) {
          const newPos = e.target.getLatLng();
          onLocationSelectRef.current(newPos.lat, newPos.lng);
        }
      });

      selectedMarkerRef.current = marker;

      // Only auto-center/pan if this is not the initial load
      if (!isInitialLoadRef.current && mapInstanceRef.current) {
        mapInstanceRef.current.panTo([selectedLocation.lat, selectedLocation.lng]);
      }
    } catch (error) {
      console.error('Error adding selected marker:', error);
    }
  }, [selectedLocation]);

  // Add complaint markers
  useEffect(() => {
    if (!mapInstanceRef.current || !complaints.length || !isMountedRef.current) return;

    // Remove old complaint markers
    markersRef.current.forEach(marker => {
      try {
        marker.remove();
      } catch (e) {
        console.warn('Error removing complaint marker:', e);
      }
    });
    markersRef.current = [];

    // Create custom icons for different severities
    const getMarkerColor = (severity) => {
      switch (severity) {
        case 'High': return '#ef4444';
        case 'Medium': return '#f59e0b';
        case 'Low': return '#10b981';
        default: return '#6b7280';
      }
    };

    complaints.forEach(complaint => {
      if (complaint.latitude && complaint.longitude && isMountedRef.current) {
        try {
          const icon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="
              width: 24px;
              height: 24px;
              border-radius: 50%;
              background: ${getMarkerColor(complaint.severity)};
              border: 3px solid white;
              box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            "></div>`,
            iconSize: [24, 24],
            iconAnchor: [12, 12]
          });

          const marker = L.marker([complaint.latitude, complaint.longitude], { icon })
            .addTo(mapInstanceRef.current)
            .bindPopup(`
              <div style="font-family: Inter, sans-serif; min-width: 200px;">
                <h4 style="margin: 0 0 8px 0; color: #111827; font-size: 14px;">
                  ${complaint.category || 'Complaint'}
                </h4>
                <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 12px;">
                  ${complaint.text.substring(0, 100)}...
                </p>
                <div style="display: flex; gap: 8px; margin-top: 8px;">
                  <span style="
                    padding: 2px 8px;
                    background: ${getMarkerColor(complaint.severity)}20;
                    color: ${getMarkerColor(complaint.severity)};
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                  ">
                    ${complaint.severity}
                  </span>
                  <span style="
                    padding: 2px 8px;
                    background: #f3f4f6;
                    color: #374151;
                    border-radius: 4px;
                    font-size: 11px;
                  ">
                    ${complaint.status}
                  </span>
                </div>
              </div>
            `);

          markersRef.current.push(marker);
        } catch (error) {
          console.error('Error adding complaint marker:', error);
        }
      }
    });
  }, [complaints]);

  return (
    <div 
      ref={mapRef} 
      style={{ 
        width: '100%', 
        height: '100%',
        borderRadius: 'var(--radius-xl)'
      }} 
    />
  );
};

export default Map;
