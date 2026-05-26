frappe.pages['customer-visit-map'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Customer Visit Map',
        single_column: true
    });

    page.main.innerHTML = '<div id="customer-visit-map" style="width: 100%; height: calc(100vh - 100px);"></div>';

    // Load Leaflet if not already loaded
    if (typeof L === 'undefined') {
        frappe.require([
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
        ], function() {
            initCustomerVisitMap();
        });
    } else {
        initCustomerVisitMap();
    }
};

function initCustomerVisitMap() {
    'use strict';

    let map = null;
    let markers = [];

    // Initialize map when page is ready
    function initMap() {
        const mapElement = document.getElementById('customer-visit-map');
        if (!mapElement) {
            console.error('Map container not found');
            return;
        }

        // Create map centered on Kenya
        map = L.map('customer-visit-map').setView([0.3031, 37.7669], 6);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
            minZoom: 2
        }).addTo(map);

        // Load customer visit data
        loadCustomerVisits();

        // Add controls
        addControls();

        // Handle window resize
        window.addEventListener('resize', function() {
            if (map) {
                setTimeout(() => map.invalidateSize(), 100);
            }
        });
    }

    // Load customer visits from Frappe backend
    function loadCustomerVisits() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Customer Visit',
                filters: {
                    'docstatus': 1  // Only submitted documents
                },
                fields: ['name', 'customer', 'date', 'start_latitude', 'start_longitude', 'stop_latitude', 'stop_longitude', 'sales_person', 'duration'],
                limit_page_length: 500
            },
            callback: function(r) {
                if (r.message) {
                    renderMarkers(r.message);
                    addStatistics(r.message);
                }
            },
            error: function(err) {
                console.error('Error loading customer visits:', err);
                frappe.msgprint({
                    title: 'Error',
                    message: 'Failed to load customer visits',
                    indicator: 'red'
                });
            }
        });
    }

    // Render markers on map
    function renderMarkers(visits) {
        clearMarkers();

        visits.forEach(function(visit) {
            if (visit.start_latitude && visit.start_longitude) {
                // Create start location marker
                const startMarker = L.marker(
                    [visit.start_latitude, visit.start_longitude],
                    {
                        icon: L.icon({
                            iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32"><circle cx="16" cy="16" r="14" fill="%234CAF50" stroke="white" stroke-width="2"/></svg>',
                            iconSize: [32, 32],
                            iconAnchor: [16, 32],
                            popupAnchor: [0, -32]
                        })
                    }
                );

                const popupContent = `
                    <div style="min-width: 250px; font-size: 12px;">
                        <strong style="color: #333;">${frappe.utils.escape_html(visit.customer)}</strong><br>
                        <small>Visit ID: ${frappe.utils.escape_html(visit.name)}</small><br>
                        <small>Date: ${frappe.format(visit.date, {fieldtype: 'Date'})}</small><br>
                        <small>Sales Person: ${visit.sales_person ? frappe.utils.escape_html(visit.sales_person) : 'N/A'}</small><br>
                        <small>Duration: ${visit.duration || 'N/A'}</small>
                        <hr style="margin: 8px 0;">
                        <small><strong>Start Location:</strong><br>${visit.start_latitude.toFixed(4)}, ${visit.start_longitude.toFixed(4)}</small>
                        ${visit.stop_latitude && visit.stop_longitude ? `<br><small><strong>Stop Location:</strong><br>${visit.stop_latitude.toFixed(4)}, ${visit.stop_longitude.toFixed(4)}</small>` : ''}
                        <hr style="margin: 8px 0;">
                        <a class="btn btn-sm btn-primary" href="/app/customer-visit/${frappe.utils.escape_html(visit.name)}" target="_blank" style="display: inline-block;">View Details</a>
                    </div>
                `;

                startMarker.bindPopup(popupContent);
                startMarker.addTo(map);
                markers.push(startMarker);

                // Add stop location marker if exists
                if (visit.stop_latitude && visit.stop_longitude) {
                    const stopMarker = L.marker(
                        [visit.stop_latitude, visit.stop_longitude],
                        {
                            icon: L.icon({
                                iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32"><circle cx="16" cy="16" r="14" fill="%232196F3" stroke="white" stroke-width="2"/></svg>',
                                iconSize: [32, 32],
                                iconAnchor: [16, 32],
                                popupAnchor: [0, -32]
                            })
                        }
                    );

                    const stopPopupContent = `
                        <div style="min-width: 250px; font-size: 12px;">
                            <strong>${frappe.utils.escape_html(visit.customer)} (Stop)</strong><br>
                            <small>Visit ID: ${frappe.utils.escape_html(visit.name)}</small><br>
                            <small>Stop Location:</small><br>
                            <small>${visit.stop_latitude.toFixed(4)}, ${visit.stop_longitude.toFixed(4)}</small>
                            <hr style="margin: 8px 0;">
                            <a class="btn btn-sm btn-primary" href="/app/customer-visit/${frappe.utils.escape_html(visit.name)}" target="_blank" style="display: inline-block;">View Details</a>
                        </div>
                    `;

                    stopMarker.bindPopup(stopPopupContent);
                    stopMarker.addTo(map);
                    markers.push(stopMarker);

                    // Draw line between start and stop
                    const line = L.polyline(
                        [[visit.start_latitude, visit.start_longitude], [visit.stop_latitude, visit.stop_longitude]],
                        {
                            color: '#666',
                            weight: 2,
                            opacity: 0.5,
                            dashArray: '5, 5'
                        }
                    );
                    line.addTo(map);
                }
            }
        });

        // Auto-fit map bounds
        if (markers.length > 0) {
            const group = new L.featureGroup(markers);
            map.fitBounds(group.getBounds(), { padding: [50, 50] });
        }
    }

    // Clear all markers from map
    function clearMarkers() {
        markers.forEach(function(marker) {
            map.removeLayer(marker);
        });
        markers = [];
    }

    // Add map controls
    function addControls() {
        // Add refresh button
        const refreshControl = L.Control.extend({
            options: {
                position: 'topright'
            },
            onAdd: function(map) {
                const btn = L.DomUtil.create('button', 'btn btn-sm btn-default');
                btn.innerHTML = '<i class="fa fa-refresh"></i> Refresh';
                btn.title = 'Refresh map data';
                btn.style.padding = '8px 12px';
                btn.style.backgroundColor = 'white';
                btn.style.border = '2px solid #ccc';
                btn.style.borderRadius = '4px';
                btn.style.cursor = 'pointer';
                btn.style.marginBottom = '10px';
                btn.style.zIndex = '1000';

                btn.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    loadCustomerVisits();
                };

                return btn;
            }
        });

        new refreshControl().addTo(map);

        // Add filter control
        const filterControl = L.Control.extend({
            options: {
                position: 'topleft'
            },
            onAdd: function(map) {
                const div = L.DomUtil.create('div', 'leaflet-control');
                div.style.backgroundColor = 'white';
                div.style.padding = '10px';
                div.style.borderRadius = '4px';
                div.style.border = '2px solid #ccc';
                div.style.zIndex = '1000';

                const title = L.DomUtil.create('h6', '', div);
                title.innerHTML = 'Filter';
                title.style.margin = '0 0 10px 0';
                title.style.fontSize = '14px';
                title.style.fontWeight = 'bold';

                const input = L.DomUtil.create('input', '', div);
                input.type = 'text';
                input.placeholder = 'Search by customer...';
                input.style.width = '200px';
                input.style.padding = '5px';
                input.style.marginBottom = '8px';
                input.style.border = '1px solid #ddd';
                input.style.borderRadius = '3px';
                input.style.boxSizing = 'border-box';

                input.onchange = function() {
                    filterMarkers(input.value);
                };

                return div;
            }
        });

        new filterControl().addTo(map);
    }

    // Filter markers based on search
    function filterMarkers(searchText) {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Customer Visit',
                filters: [
                    ['Customer Visit', 'docstatus', '=', 1],
                    ['Customer Visit', 'customer', 'like', '%' + searchText + '%']
                ],
                fields: ['name', 'customer', 'date', 'start_latitude', 'start_longitude', 'stop_latitude', 'stop_longitude', 'sales_person', 'duration'],
                limit_page_length: 500
            },
            callback: function(r) {
                if (r.message) {
                    renderMarkers(r.message);
                }
            }
        });
    }

    // Add statistics panel
    function addStatistics(visits) {
        const stats = {
            total_visits: visits.length,
            unique_customers: new Set(visits.map(v => v.customer)).size,
            unique_sales_people: new Set(visits.filter(v => v.sales_person).map(v => v.sales_person)).size
        };

        const statsControl = L.Control.extend({
            options: {
                position: 'bottomleft'
            },
            onAdd: function(map) {
                const div = L.DomUtil.create('div', 'leaflet-control');
                div.style.backgroundColor = 'white';
                div.style.padding = '10px';
                div.style.borderRadius = '4px';
                div.style.border = '2px solid #ccc';
                div.style.fontSize = '12px';
                div.style.zIndex = '1000';

                div.innerHTML = `
                    <strong>Customer Visits Statistics</strong><br>
                    <small>Total Visits: <strong>${stats.total_visits}</strong></small><br>
                    <small>Unique Customers: <strong>${stats.unique_customers}</strong></small><br>
                    <small>Sales People: <strong>${stats.unique_sales_people}</strong></small>
                `;

                return div;
            }
        });

        new statsControl().addTo(map);
    }

    // Start initialization
    initMap();
}
