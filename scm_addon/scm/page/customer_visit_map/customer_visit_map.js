frappe.pages['customer-visit-map'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Customer Visit Map',
        single_column: true
    });

    var styles = `
        <style>
            .map-page-header {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 15px;
                background: white;
                border-bottom: 1px solid #e0e0e0;
                flex-wrap: wrap;
            }
            .date-range-group {
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .date-range-group input[type="date"] {
                padding: 6px 10px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                font-size: 13px;
                color: #333;
                cursor: pointer;
                outline: none;
                transition: border-color 0.2s;
            }
            .date-range-group input[type="date"]:focus {
                border-color: #2196F3;
            }
            .date-range-sep { color: #999; font-size: 13px; }
            .view-toggle-group {
                display: flex;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                overflow: hidden;
            }
            .view-toggle-btn {
                padding: 6px 14px;
                background: white;
                border: none;
                font-size: 13px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 5px;
                color: #555;
                transition: background 0.2s, color 0.2s;
            }
            .view-toggle-btn.active { background: #2196F3; color: white; }
            .view-toggle-btn:not(:last-child) { border-right: 1px solid #d0d0d0; }
            .header-filter-select {
                padding: 6px 10px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                font-size: 13px;
                color: #333;
                min-width: 180px;
                outline: none;
                cursor: pointer;
            }
            .map-wrapper {
                position: relative;
                height: calc(100vh - 145px);
                width: 100%;
            }
            #customer-visit-map { width: 100%; height: 100%; }

            /* Sidebar — pushed below zoom controls (~80px from top) */
            #map-sidebar {
                position: absolute;
                top: 80px;
                left: 10px;
                width: 220px;
                background: white;
                border-radius: 6px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                z-index: 1000;
                max-height: calc(100vh - 260px);
                overflow-y: auto;
            }
            #sidebar-header {
                padding: 10px 14px;
                font-weight: 600;
                font-size: 13px;
                color: #333;
                border-bottom: 1px solid #eee;
            }
            #salesmen-list { padding: 8px 10px; }
            .salesman-item {
                padding: 8px 10px;
                margin-bottom: 5px;
                border-radius: 4px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 13px;
                transition: background 0.2s;
                user-select: none;
            }
            .salesman-item:hover { background: #f5f5f5; }
            .salesman-item.inactive { opacity: 0.4; }
            .color-dot { width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0; }
            .salesman-name { flex: 1; font-weight: 500; font-size: 12px; line-height: 1.3; }
            .visit-count {
                font-size: 11px; color: #888;
                background: #eee; padding: 1px 6px; border-radius: 8px;
            }
            .no-data { text-align: center; padding: 15px; color: #aaa; font-size: 12px; }
            .routing-status {
                position: absolute;
                bottom: 30px; right: 10px;
                background: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px; color: #555;
                box-shadow: 0 1px 4px rgba(0,0,0,0.2);
                z-index: 1000;
                display: none;
            }
        </style>
    `;
    $(page.body).append(styles);

    // ── Header toolbar ─────────────────────────────────────────────────────────
    var header = $(`
        <div class="map-page-header">
            <div class="date-range-group">
                <input type="date" id="date-from" />
                <span class="date-range-sep">→</span>
                <input type="date" id="date-to" />
            </div>
            <div class="view-toggle-group">
                <button class="view-toggle-btn active" id="btn-map-view">📍 Map View</button>
                <button class="view-toggle-btn" id="btn-table-view">📋 Table View</button>
            </div>
            <select class="header-filter-select" id="sales-rep-filter">
                <option value="">Filter by sales rep</option>
            </select>
        </div>
    `);
    $(page.main).append(header);

    // ── Map wrapper ────────────────────────────────────────────────────────────
    var mapWrapper = $(`
        <div class="map-wrapper">
            <div id="map-sidebar">
                <div id="sidebar-header">Salesmen</div>
                <div id="salesmen-list"><div class="no-data">Loading...</div></div>
            </div>
            <div id="customer-visit-map"></div>
            <div class="routing-status" id="routing-status">Computing road routes...</div>
        </div>
    `);
    $(page.main).append(mapWrapper);

    // ── Default dates (today) ──────────────────────────────────────────────────
    const today = new Date().toISOString().split('T')[0];
    $('#date-from').val(today);
    $('#date-to').val(today);

    // ── Auto-apply on any filter change ───────────────────────────────────────
    function triggerReload() {
        const df = $('#date-from').val();
        const dt = $('#date-to').val();
        if (df && dt && df > dt) {
            frappe.msgprint({ title: 'Error', message: 'From date cannot be after To date', indicator: 'red' });
            return;
        }
        if (window._visitMapInstance) window._visitMapInstance.reload();
    }

    $('#date-from').on('change', triggerReload);
    $('#date-to').on('change', triggerReload);
    $('#sales-rep-filter').on('change', function() {
        if (window._visitMapInstance) window._visitMapInstance.filterBySalesRep($(this).val());
    });

    // ── Table view → navigate to list ─────────────────────────────────────────
    $('#btn-table-view').on('click', function() {
        frappe.set_route('List', 'Customer Visit');
    });

    $('#btn-map-view').on('click', function() {
        // already here, just ensure active state
        $(this).addClass('active');
        $('#btn-table-view').removeClass('active');
    });

    // ── Init map ───────────────────────────────────────────────────────────────
    setTimeout(function() {
        if (typeof L === 'undefined') { console.error('Leaflet not loaded'); return; }
        window._visitMapInstance = initCustomerVisitMap();
    }, 100);
};


function initCustomerVisitMap() {
    'use strict';

    let map = null;
    let markers = [];
    let routeLayers = [];
    let allVisits = [];
    let salesmenData = {};
    let isMapInitialized = false;

    const colorPalette = [
        '#E91E63','#F44336','#2196F3','#4CAF50',
        '#FF9800','#9C27B0','#00BCD4','#FF5722',
        '#3F51B5','#009688','#8BC34A','#FFC107'
    ];

    // ── Init map ───────────────────────────────────────────────────────────────
    function initMap() {
        if (isMapInitialized) return;
        const el = document.getElementById('customer-visit-map');
        if (!el) return;

        map = L.map('customer-visit-map').setView([-0.0236, 37.9062], 7);
        isMapInitialized = true;

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19, minZoom: 2
        }).addTo(map);

        // Map / Satellite toggle (top-right, won't conflict with zoom which is top-left)
        const SatControl = L.Control.extend({
            options: { position: 'topright' },
            onAdd: function() {
                const div = L.DomUtil.create('div');
                div.innerHTML = `
                    <div style="background:white;border-radius:4px;box-shadow:0 1px 5px rgba(0,0,0,.3);
                                overflow:hidden;display:flex;margin-bottom:5px;">
                        <button id="lf-map-btn" style="padding:5px 12px;border:none;font-size:12px;
                            cursor:pointer;background:#2196F3;color:white;font-weight:600;">Map</button>
                        <button id="lf-sat-btn" style="padding:5px 12px;border:none;font-size:12px;
                            cursor:pointer;background:white;color:#555;">Satellite</button>
                    </div>`;
                return div;
            }
        });
        new SatControl().addTo(map);

        let satLayer = null;
        $(document).on('click', '#lf-sat-btn', function() {
            if (!satLayer) {
                satLayer = L.tileLayer(
                    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    { attribution: 'Tiles © Esri', maxZoom: 19 }
                ).addTo(map);
            }
            satLayer.addTo(map);
            $('#lf-sat-btn').css({ background: '#2196F3', color: 'white', fontWeight: '600' });
            $('#lf-map-btn').css({ background: 'white', color: '#555', fontWeight: 'normal' });
        });
        $(document).on('click', '#lf-map-btn', function() {
            if (satLayer) map.removeLayer(satLayer);
            $('#lf-map-btn').css({ background: '#2196F3', color: 'white', fontWeight: '600' });
            $('#lf-sat-btn').css({ background: 'white', color: '#555', fontWeight: 'normal' });
        });

        window.addEventListener('resize', () => map && setTimeout(() => map.invalidateSize(), 100));
        loadVisitData();
    }

    // ── Load visits ────────────────────────────────────────────────────────────
    function loadVisitData() {
        const dateFrom = $('#date-from').val();
        const dateTo   = $('#date-to').val();

        let filters = [['docstatus', '!=', 2]];
        if (dateFrom) filters.push(['date', '>=', dateFrom]);
        if (dateTo)   filters.push(['date', '<=', dateTo]);

        const activeSalesRep = $('#sales-rep-filter').val();
        if (activeSalesRep) filters.push(['sales_person', '=', activeSalesRep]);

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Customer Visit',
                filters: filters,
                fields: ['name', 'customer', 'date', 'sales_person', 'duration'],
                limit_page_length: 1000,
                order_by: 'sales_person asc, date asc'
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    allVisits = r.message;
                    loadCustomerLocations();
                } else {
                    allVisits = [];
                    clearMap();
                    $('#salesmen-list').html('<div class="no-data">No visits found</div>');
                }
            }
        });
    }

    // ── Load customer lat/lng ──────────────────────────────────────────────────
    function loadCustomerLocations() {
        const customerNames = [...new Set(allVisits.map(v => v.customer))];

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Customer',
                filters: [['name', 'in', customerNames]],
                fields: ['name', 'custom_latitude', 'custom_longitude'],
                limit_page_length: 1000
            },
            callback: function(r) {
                const locs = {};
                (r.message || []).forEach(c => {
                    locs[c.name] = {
                        lat: parseFloat(c.custom_latitude) || null,
                        lng: parseFloat(c.custom_longitude) || null
                    };
                });
                processVisits(locs);
                populateSalesRepFilter();
                renderSalesmenList();
                renderVisits();
            }
        });
    }

    // ── Process visits ─────────────────────────────────────────────────────────
    function processVisits(locs) {
        salesmenData = {};
        let ci = 0;

        allVisits.forEach(v => {
            const sm = v.sales_person || 'Unassigned';
            if (!salesmenData[sm]) {
                salesmenData[sm] = {
                    name: sm,
                    visits: [],
                    color: colorPalette[ci++ % colorPalette.length],
                    visible: true
                };
            }
            const loc = locs[v.customer];
            if (loc && loc.lat && loc.lng) {
                salesmenData[sm].visits.push({ ...v, lat: loc.lat, lng: loc.lng });
            }
        });
    }

    // ── Populate sales rep dropdown (preserve selection) ───────────────────────
    function populateSalesRepFilter() {
        const sel = $('#sales-rep-filter');
        const current = sel.val();
        sel.find('option:not(:first)').remove();
        Object.keys(salesmenData).sort().forEach(name => {
            sel.append(`<option value="${frappe.utils.escape_html(name)}">${frappe.utils.escape_html(name)}</option>`);
        });
        if (current) sel.val(current);
    }

    // ── Sidebar ────────────────────────────────────────────────────────────────
    function renderSalesmenList() {
        const list = $('#salesmen-list').empty();
        const names = Object.keys(salesmenData).sort().filter(n => salesmenData[n].visits.length > 0);

        if (!names.length) {
            list.html('<div class="no-data">No data</div>');
            return;
        }

        names.forEach(name => {
            const sm = salesmenData[name];
            const item = $(`
                <div class="salesman-item ${sm.visible ? '' : 'inactive'}" data-sm="${frappe.utils.escape_html(name)}">
                    <div class="color-dot" style="background:${sm.color};"></div>
                    <div class="salesman-name">${frappe.utils.escape_html(name)}</div>
                    <div class="visit-count">${sm.visits.length}</div>
                </div>
            `);
            item.on('click', function() {
                sm.visible = !sm.visible;
                $(this).toggleClass('inactive', !sm.visible);
                renderVisits();
            });
            list.append(item);
        });
    }

    // ── OSRM road routing ──────────────────────────────────────────────────────
    async function getRoadRoute(coords) {
        if (coords.length < 2) return null;
        const waypoints = coords.map(c => `${c[1]},${c[0]}`).join(';');
        const url = `https://router.project-osrm.org/route/v1/driving/${waypoints}?overview=full&geometries=geojson`;
        try {
            const resp = await fetch(url);
            if (!resp.ok) return null;
            const data = await resp.json();
            if (data.code !== 'Ok' || !data.routes || !data.routes[0]) return null;
            return data.routes[0].geometry.coordinates.map(c => [c[1], c[0]]);
        } catch (e) {
            console.warn('OSRM routing failed, falling back to straight line:', e);
            return null;
        }
    }

    // ── Render visits + road routes ────────────────────────────────────────────
    async function renderVisits() {
        clearMap();

        const activeSalesRep = $('#sales-rep-filter').val();
        const names = Object.keys(salesmenData).sort();

        const activeRoutes = names.filter(n =>
            salesmenData[n].visible &&
            salesmenData[n].visits.length > 1 &&
            (!activeSalesRep || n === activeSalesRep)
        ).length;

        if (activeRoutes > 0) {
            $('#routing-status').text(`Computing road routes (0/${activeRoutes})...`).show();
        }

        let routed = 0;

        for (const name of names) {
            const sm = salesmenData[name];
            if (!sm.visible) continue;
            if (activeSalesRep && name !== activeSalesRep) continue;
            if (sm.visits.length === 0) continue;

            const visits = [...sm.visits].sort((a, b) => new Date(a.date) - new Date(b.date));
            const coords  = visits.map(v => [v.lat, v.lng]);

            // Road route
            if (visits.length > 1) {
                let routePoints = [];
                const chunkSize = 25;
                for (let i = 0; i < coords.length; i += chunkSize - 1) {
                    const chunk = coords.slice(i, i + chunkSize);
                    if (chunk.length < 2) break;
                    const road = await getRoadRoute(chunk);
                    routePoints = routePoints.concat(road || chunk);
                }
                if (routePoints.length > 1) {
                    const polyline = L.polyline(routePoints, {
                        color: sm.color, weight: 4, opacity: 0.85
                    }).addTo(map);
                    routeLayers.push(polyline);
                }
                routed++;
                $('#routing-status').text(`Computing road routes (${routed}/${activeRoutes})...`);
            }

            // Markers
            visits.forEach((visit, idx) => {
                const icon = L.divIcon({
                    className: '',
                    html: `<div style="
                        background:${sm.color};color:white;border-radius:50%;
                        width:30px;height:30px;display:flex;align-items:center;
                        justify-content:center;font-weight:700;font-size:13px;
                        border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.35);
                    ">${idx + 1}</div>`,
                    iconSize: [30, 30], iconAnchor: [15, 15], popupAnchor: [0, -15]
                });

                const marker = L.marker([visit.lat, visit.lng], { icon });
                marker.bindPopup(`
                    <div style="min-width:220px;font-size:12px;">
                        <div style="font-size:14px;font-weight:600;margin-bottom:4px;">
                            Sales Rep: ${frappe.utils.escape_html(visit.sales_person || 'Unassigned')}
                        </div>
                        <div style="color:#555;">Customer: ${frappe.utils.escape_html(visit.customer)}</div>
                        <hr style="margin:6px 0;">
                        <div><strong>Date:</strong> ${frappe.format(visit.date, {fieldtype:'Date'})}</div>
                        <div><strong>Duration:</strong> ${visit.duration || 'N/A'}</div>
                        <hr style="margin:6px 0;">
                        <a class="btn btn-xs btn-primary"
                           onclick="frappe.set_route('Form','Customer Visit','${frappe.utils.escape_html(visit.name)}');return false;"
                           href="#">View Details</a>
                    </div>
                `);
                marker.addTo(map);
                markers.push(marker);
            });
        }

        $('#routing-status').fadeOut(1000);

        if (markers.length > 0) {
            map.fitBounds(new L.featureGroup(markers).getBounds(), { padding: [50, 50] });
        }
    }

    // ── Public API ─────────────────────────────────────────────────────────────
    function filterBySalesRep(name) {
        renderVisits();
    }

    function reload() {
        clearMap();
        $('#salesmen-list').html('<div class="no-data">Loading...</div>');
        loadVisitData();
    }

    function clearMap() {
        [...markers, ...routeLayers].forEach(l => { try { map.removeLayer(l); } catch(e){} });
        markers = [];
        routeLayers = [];
    }

    initMap();
    return { reload, filterBySalesRep };
}
