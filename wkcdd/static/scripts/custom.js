/**
Custom module for you to write your own javascript functions
**/
var Custom = function () {

    // private functions & variables

    var 
        county_map,
        constituencies_map,
        ENTER_KEY_CODE = 13,
        display_county_map = function() {
            county_map = new L.Map('map', {
                layers: [
                    L.tileLayer('https://{s}.tiles.mapbox.com/v3/ona.tk0jatt9/{z}/{x}/{y}.png', {
                            maxZoom: 12,
                            minZoom: 8,
                            attribution: '<a href="http://www.mapbox.com/about/maps/" target="_blank">Terms &amp; Feedback</a>'
                    })]     
            }).setView([0.38, 34.5], 9);
        },
        display_constituency_map = function() {
            constituencies_map = new L.Map('map', {
                    layers: [
                            L.tileLayer('https://{s}.tiles.mapbox.com/v3/ona.snd5z5mi/{z}/{x}/{y}.png', {
                            maxZoom: 13,
                            minZoom: 9,
                            attribution: '<a href="http://www.mapbox.com/about/maps/" target="blank"> Terms &amp; Feedback</a>'
                                })]
            }).setView([0.31, 34.5], 9);
        },
        render_geoJson_to_map = function(geoJson, map) {
            geoJson.addTo(map)
        },
        process_raw_points = function(raw_data) {
            debugger;
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
        add_data_layer_to = function(csv, map) {
            geojson_layer = omnivore.csv(csv);
            if(geojson_layer) {
                geojson_layer.options.pointToLayer = function(feature, latlong) {
                    // 1. Different project types should have different icon
                    // colours
                    return L.marker(latlong);
                };
                geojson_layer.addTo(map);
            }
        },
        init = function(){
            display_constituency_map();
        };
    
    // public functions
    return {
        init: init,
        county_map: county_map,
        constituencies_map: constituencies_map,
        render_geoJson_to_map: render_geoJson_to_map,
        filterProjectsTable: filterProjectsTable,
        process_raw_points: process_raw_points,
        add_data_layer_to: add_data_layer_to
    };

}();
