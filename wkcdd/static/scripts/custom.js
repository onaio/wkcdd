/**
Custom module for you to write your own javascript functions
**/
var Custom = function () {

    // private functions & variables

    var 
        map;
        ENTER_KEY_CODE = 13,
        display_county_map = function() {
            if(map) map = null;
            county_map = new L.Map('map', {
                layers: [
                    L.tileLayer('https://{s}.tiles.mapbox.com/v3/ona.tk0jatt9/{z}/{x}/{y}.png', {
                            maxZoom: 12,
                            minZoom: 8,
                            attribution: '<a href="http://www.mapbox.com/about/maps/" target="_blank">Terms &amp; Feedback</a>'
                    })]     
            }).setView([0.38, 34.5], 9);
            map = county_map;
            return map
        },
        display_constituency_map = function() {
            if(map) map = null;
            constituencies_map = new L.Map('map', {
                    layers: [
                            L.tileLayer('https://{s}.tiles.mapbox.com/v3/ona.snd5z5mi/{z}/{x}/{y}.png', {
                            maxZoom: 13,
                            minZoom: 9,
                            attribution: '<a href="http://www.mapbox.com/about/maps/" target="blank"> Terms &amp; Feedback</a>'
                                })]
            }).setView([0.31, 34.5], 9);
            map = constituencies_map;
            return map;
        },
        process_raw_points = function(raw_data, map) {
            var latlng, icon,
                icon_sector_map = {
                    'Banana': {label:'b', color:'yellow'},
                    'Catering': {label:'c', color:'orange'},
                    'Dairy Cows': {label: 'slaughterhouse', color:'brown'},
                    'Dairy Goat': {label:'g', color:'light-brown'},
                    'Field Industrial Crops': {label:'garden', color:'green'},
                    'Fish Farming': {label:'wetland', color:'blue'},
                    'Motor Cycle': {label:'m', color:'black'},
                    'Oxen Plough': {label:'o', color:'grey'},
                    'Piggery': {label:'p', color:'pink'},
                    'Poultry': {label:'p', color:'light-pink'},
                    'Tailoring': {label:'t', color:'light-green'}
                };
            $.each(raw_data, function(index, data){
                latlng = L.latLng(data.lat, data.lng);
                icon = L.MakiMarkers.icon({icon:icon_sector_map[data.sector].label, size:'s'});
                marker = L.marker(latlng, {icon: icon, title: data.name}).addTo(map);
                marker.bindPopup(data.name);
            });
        },
        filterProjectsTable = function() {
            $("#search_term").keypress(function(e) {
                var search_term, filter_url;
                if (e.which == ENTER_KEY_CODE) {
                    search_term = $("#search_term").val();
                    filter_url = "?search="+search_term
                    window.location = filter_url;
                }
            });
        },
        init = function(){
        };
    
    // public functions
    return {
        init: init,
        display_constituency_map: display_constituency_map,
        display_county_map: display_county_map,
        filterProjectsTable: filterProjectsTable,
        process_raw_points: process_raw_points
    };

}();
