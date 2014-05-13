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
                            L.tileLayer('https://{s}.tiles.mapbox.com/v3/ona.i3hmlj38/{z}/{x}/{y}.png', {
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
                    'Banana': {label:'b', color:'#d8c22f'},
                    'Catering': {label:'c', color:'#e8ffb9'},
                    'Dairy Cows': {label: 'slaughterhouse', color:'#a28245'},
                    'Dairy Goat': {label:'g', color:'#f3c368'},
                    'Field Industrial Crops': {label:'garden', color:'#21b01d'},
                    'Fish Farming': {label:'wetland', color:'#2c34c7'},
                    'Motor Cycle': {label:'m', color:'#000000'},
                    'Oxen Plough': {label:'o', color:'#697690'},
                    'Piggery': {label:'p', color:'#b54282'},
                    'Poultry': {label:'p', color:'#ae241a'},
                    'Tailoring': {label:'t', color:'#3aa32a'}
                };
            $.each(raw_data, function(index, data){
                latlng = L.latLng(data.lat, data.lng);
                icon = L.MakiMarkers.icon({
                    icon:icon_sector_map[data.sector].label,
                    color:icon_sector_map[data.sector].color,
                    size:'s'});
                marker = L.marker(latlng, {icon: icon, title: data.name}).addTo(map);
                marker.bindPopup(data.name);
            });
        },
        searchProjectsTable = function() {
            $("#search_term").keypress(function(e) {
                var search_term, filter_url;

                if (e.which == ENTER_KEY_CODE) {
                    search_term = $("#search_term").val();
                    filter_url = "?filter=1&search="+search_term
                    window.location = filter_url;
                }
            });
        },

        addFilterFormAction = function(form, default_url) {
            form_action = null
            county_url = $('select[name=county]').find(":selected").attr('url');
            sub_county_url = $('select[name=sub_county]').find(":selected").attr('url');
            constituency_url = $('select[name=constituency]').find(":selected").attr('url');
            community_url = $('select[name=community]').find(":selected").attr('url');
            view_by = $('select[name=view_by]').val()

            if(community_url !== undefined) {
                form_action = community_url;
            } else if(constituency_url !== undefined) {
                form_action = constituency_url;
            } else if (sub_county_url !== undefined) {
                form_action = sub_county_url;
            } else if (county_url !== undefined) {
                form_action = county_url;
            }else {
                form_action = default_url
            }

            //load the form action
            $(form).attr('action', form_action);
            $(form).submit();
        },

        init = function(){
        };

        $('.selectpicker').selectpicker();
    
    // public functions
    return {
        init: init,
        display_constituency_map: display_constituency_map,
        display_county_map: display_county_map,
        searchProjectsTable: searchProjectsTable,
        process_raw_points: process_raw_points,
        addFilterFormAction: addFilterFormAction
    };

}();

var LocationSelect = function() {
    var
        level0 = "county",
        level1 = "sub_county",
        level2 = "constituency",
        level3 = "community",
        get_filtered_location_list = function(location_type, location_id) {
            filtered_location_list = [];
            $.each(this.data_map, function(idx, elem){
                if(elem[location_type].id == location_id) {
                    filtered_location_list.push(elem)
                }
            });
            return filtered_location_list;
        },
        update_select = function(select, options, default_value) {
            // TODO Instead of creating new elements all the time, 
            // Cache them and just loop over them
            var url_root = this.url,
                optionList = [],
                default_option = $('<option />', {
                    text: default_value,
                    value: ""
                });
            optionList.push(default_option);

            $.each(options, function(idx, elem){
                option = $('<option />', {
                    text: elem.name,
                    value: elem.id,
                    url: url_root + elem.id
                });
                optionList.push(option);
            });
            select.empty().append(optionList);
        },
        set_select_value = function(select, option) {
            select.val(option.id);
        }
        contains = function(object, list) {
            var contains = false;

            $.each(list, function(idx, elem){
                if(elem.id == object.id) {
                    contains = true;
                    return false
                }
                else {
                    contains = false;
                }
            });

            return contains;
        },
        level0ChangeListener = function(element) {
            var 
                county_id = $(element).val(),
                locations = get_filtered_location_list(level0, county_id),
                sub_county_list = [],
                constituency_list = [],
                community_list = [];

            if(locations.length == 0) {
                locations = this.data_map;
                setViewByValue('counties');
            }
                else setViewByValue('sub_counties');

            $.each(locations, function(idx, elem){

                if(!contains(elem['sub_county'], sub_county_list)) {
                    sub_county_list.push(elem['sub_county']);
                }

                if(!contains(elem['constituency'], constituency_list)) {
                    constituency_list.push(elem['constituency']);
                }

                //Communities are all unique
                community_list.push(elem['community']);
            });
            update_select($('select[name=sub_county]'), sub_county_list, "All Sub-Counties");
            update_select($('select[name=constituency]'), constituency_list, "All Constituencies");
            update_select($('select[name=community]'), community_list, "All Communities");
        },
        level1ChangeListener = function(element) {
            //update level 0,2 and 3
            var 
                sub_county_id = $(element).val(),
                locations = get_filtered_location_list(level1, sub_county_id),
                county = null,
                constituency_list = [],
                community_list = [];

            if(locations.length == 0) {
                //refresh filter based on parent
                setViewByValue('sub_counties');
                return;
            }

            $.each(locations, function(idx, elem){
                county = elem['county'];

                if(!contains(elem['constituency'], constituency_list)) {
                    constituency_list.push(elem['constituency']);
                }

                //Communities are all unique
                community_list.push(elem['community']);
            });
            set_select_value($('select[name=county]'), county);
            update_select($('select[name=constituency]'), constituency_list, "All Constituencies");
            update_select($('select[name=community]'), community_list, "All Communities");
            setViewByValue('constituencies');
        },
        level2ChangeListener = function(element) {
            //update level 0,1 and 3
            var 
                constituency_id = $(element).val(),
                locations = get_filtered_location_list(level2, constituency_id),
                county = null,
                sub_county = null,
                community_list = [];

            if(locations.length == 0) {
                //refresh filter based on parent
                setViewByValue('constituencies');
                return;
            }

            $.each(locations, function(idx, elem){
                county = elem['county'];
                sub_county = elem['sub_county'];
                community_list.push(elem['community']);
            });
            set_select_value($('select[name=county]'), county);
            set_select_value($('select[name=sub_county]'), sub_county);
            update_select($('select[name=community]'), community_list, "All Communities");
            setViewByValue('communities');
        }
        level3ChangeListener = function(element) {
            //update level 0, 1 and 2
            var 
                community_id = $(element).val(),
                locations = get_filtered_location_list(level3, community_id),
                county = '',
                sub_county = '',
                constituency = '';

            if(locations.length == 0) {
                //refresh filter based on parent
                 setViewByValue('communities');
                return;
            }else{
                county = locations[0].county,
                sub_county = locations[0].sub_county,
                constituency = locations[0].constituency
            }

            set_select_value($('select[name=county]'), county);
            set_select_value($('select[name=sub_county]'), sub_county);
            set_select_value($('select[name=constituency]'), constituency);
            setViewByValue('projects');
        },
        setViewByValue = function(value) {
            //udate view_by dropdown based on selected location type

            var
                view_by = $('select[name=view_by]'),
                sub_county = $('select[name=sub_county]').val(),
                constituency = $('select[name=constituency]').val(),
                community = $('select[name=constituency]').val();

            view_by = this.view_by.clone();
            view_by.val(value);
            switch (value)
            {
                case "sub_counties":
                    view_by.children('option[value=counties]').remove();
                break;
                case "constituencies":
                    view_by.children('option[value=counties]').remove();
                    view_by.children('option[value=sub_counties]').remove();
                break;
                case "communities":
                    view_by.children('option[value=counties]').remove();
                    view_by.children('option[value=sub_counties]').remove();
                    view_by.children('option[value=constituencies]').remove();
                break;
                case "projects":
                    view_by.children('option[value=counties]').remove();
                    view_by.children('option[value=sub_counties]').remove();
                    view_by.children('option[value=constituencies]').remove();
                    view_by.children('option[value=communities]').remove();
                break;
            }
            $('select[name=view_by]').replaceWith(view_by);
        };

    this.data_map = {};
    this.url = '';
    this.view_by = $('select[name=view_by]').clone();
    this.get_filtered_location_list = get_filtered_location_list;
    this.level0ChangeListener = level0ChangeListener;
    this.level1ChangeListener = level1ChangeListener;
    this.level2ChangeListener = level2ChangeListener;
    this.level3ChangeListener = level3ChangeListener;
    this.update_select = update_select;

    return this;
}();
