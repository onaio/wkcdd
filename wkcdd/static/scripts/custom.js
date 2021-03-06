/**
Custom module for you to write your own javascript functions
**/
var Custom = function () {
    // private functions & variables
    var 
        chartDataSet,
        ENTER_KEY_CODE = 13,
        searchProjectsTable = function() {
            $("#search_term").keypress(function(e) {
                var search_term, filter_url;

                if (e.which == ENTER_KEY_CODE) {
                    search_term = $("#search_term").val();
                    filter_url = "?filter=1&search="+search_term;
                    window.location = filter_url;
                }
            });
        },
        setChartDataset = function(dataset) {
            chartDataSet = dataset;
        },
        addFilterFormAction = function(form, default_url) {
            form_action = null;
            county_url = $('select[name=county]').find(":selected").attr('url');
            sub_county_url = $('select[name=sub_county]').find(":selected").attr('url');
            constituency_url = $('select[name=constituency]').find(":selected").attr('url');
            community_url = $('select[name=community]').find(":selected").attr('url');
            view_by = $('select[name=view_by]').val();

            if(community_url !== undefined) {
                form_action = community_url;
            } else if(constituency_url !== undefined) {
                form_action = constituency_url;
            } else if (sub_county_url !== undefined) {
                form_action = sub_county_url;
            } else if (county_url !== undefined) {
                form_action = county_url;
            }else {
                form_action = default_url;
            }

            //load the form action
            $(form).attr('action', form_action);
            $(form).submit();
        },
        drawIndicatorChart = function(labels, series) {

            // Can specify a custom tick Array.
            // Ticks should match up one for each y value (category) in the series.
            var 
                ticks = labels,
                plot1 = $.jqplot('chart', [series], {
                // The "seriesDefaults" option is an options object that will
                // be applied to all series in the chart.
                seriesDefaults:{
                    renderer:$.jqplot.BarRenderer,
                    rendererOptions: {
                        fillToZero: true,
                        barDirection: 'horizontal'
                    },
                    pointLabels: {
                        show: true,
                        formatString: '%.2f',
                        location: 'w',
                        hideZeros: true},
                    shadow: false
                },
                grid: {
                    background:'#ffffff',
                    shadow: false
                },
                axes: {
                    xaxis: {
                    	min: 0,
                        pad: 1.05,
                        tickOptions: {formatString: '%d'}
                    },
                    yaxis: {
                        renderer: $.jqplot.CategoryAxisRenderer,
                        ticks: ticks,
                        tickOptions:{
                            formatString:'%b&nbsp;%d'
                        } 
                    }
                },
            });
        },
        init = function(){
            $('.indicator-selector').click(function () {
                var indicator = $(this).data('indicator');
                Map.setIndicator(indicator);
               $('.selected-indicator').html($(this).html());
               //redraw chart for the selected indicator
                $('#chart').empty();
                drawIndicatorChart(chartDataSet.labels, chartDataSet.series[indicator]);
            });
            $('.selectpicker').selectpicker();

            $("input[name=update_report]").click(function(){
                var 
                    reports = $("input[name=reports]"),
                    report_ids = reports.val(),
                    value = $(this).val();
                    if(this.checked) {
                        reports.val(report_ids + value + ",");
                    } else {
                        reports.val(report_ids.replace(value + ",", ""));
                    }
            });

            $('#show-projects').click(function(){
                Map.displayMarkers(Map.project_geolocations);
            });
        };
        init();
    
    // public functions
    return {
        init: init,
        searchProjectsTable: searchProjectsTable,
        addFilterFormAction: addFilterFormAction,
        drawIndicatorChart: drawIndicatorChart,
        setChartDataset: setChartDataset
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
                    filtered_location_list.push(elem);
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
        },
        contains = function(object, list) {
            var contains = false;

            $.each(list, function(idx, elem){
                if(elem.id == object.id) {
                    contains = true;
                    return false;
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

            if(locations.length === 0) {
                locations = this.data_map;
                setViewByValue('counties');
            } else {
                setViewByValue('sub_counties');
            }

            $.each(locations, function(idx, elem){

                if(!contains(elem.sub_county, sub_county_list)) {
                    sub_county_list.push(elem.sub_county);
                }

                if(!contains(elem.constituency, constituency_list)) {
                    constituency_list.push(elem.constituency);
                }

                //Communities are all unique
                community_list.push(elem.community);
            });
            updateLocationLabel('county');
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

            if(locations.length === 0) {
                //refresh filter based on parent
                setViewByValue('sub_counties');
                updateLocationLabel('county');
                return;
            }

            $.each(locations, function(idx, elem){
                county = elem.county;

                if(!contains(elem.constituency, constituency_list)) {
                    constituency_list.push(elem.constituency);
                }

                //Communities are all unique
                community_list.push(elem.community);
            });
            updateLocationLabel('sub_county');
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

            if(locations.length === 0) {
                //refresh filter based on parent
                setViewByValue('constituencies');
                updateLocationLabel('sub_county');
                return;
            }

            $.each(locations, function(idx, elem){
                county = elem.county;
                sub_county = elem.sub_county;
                community_list.push(elem.community);
            });
            updateLocationLabel('constituency');
            set_select_value($('select[name=county]'), county);
            set_select_value($('select[name=sub_county]'), sub_county);
            update_select($('select[name=community]'), community_list, "All Communities");
            setViewByValue('communities');
        },
        level3ChangeListener = function(element) {
            //update level 0, 1 and 2
            var 
                community_id = $(element).val(),
                locations = get_filtered_location_list(level3, community_id),
                county = '',
                sub_county = '',
                constituency = '';

            if(locations.length === 0) {
                //refresh filter based on parent
                 setViewByValue('communities');
                 updateLocationLabel('constituency');
                return;
            }else{
                county = locations[0].county;
                sub_county = locations[0].sub_county;
                constituency = locations[0].constituency;
            }

            updateLocationLabel('community');
            set_select_value($('select[name=county]'), county);
            set_select_value($('select[name=sub_county]'), sub_county);
            set_select_value($('select[name=constituency]'), constituency);
            setViewByValue('projects');
        },
        setViewByValue = function(value) {
            //update view_by dropdown based on selected location type

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
        },
	    updateLocationLabel = function(field){
		    // Update location labels
			var currField = $("select[name="+field+"] option:selected");
    		var currLoc = currField.text();
    		var updateLabel = $("#currLocation");
    		
	    	field = field.replace('_',' ');
	    	
    		var updateTxt = '';
	    	
    		//Check if top item ie. 'All Counties' is selected
            updateTxt = currField.val() === '' ? updateTxt += currLoc : updateTxt += currLoc+" "+field;
	    	updateLabel.text(updateTxt);
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
    this.setViewByValue = setViewByValue;
    this.updateLocationLabel = updateLocationLabel;

    return this;
}();
