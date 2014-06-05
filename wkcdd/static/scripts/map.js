var Map = (function(root){
    var map =  new L.Map('map', {
        fullscreenControl: true
    }).setView([0.31, 34.5], 9);
    
    var initBaseMap = function(map_url){
    	//'https://{s}.tiles.mapbox.com/v3/ona.i42dk97b/{z}/{x}/{y}.png'
    	var map_data = 'https://{s}.tiles.mapbox.com/v3/'+map_url+'/{z}/{x}/{y}.png';
    	
		L.tileLayer(map_data, {
            maxZoom: 13,
            minZoom: 9,
            attribution: '<a href="http://www.mapbox.com/about/maps/" target="blank"> Terms &amp; Feedback</a>'
        }).addTo(map);
        //alert("Map URL: "+map_data);
    };
    
    var data = {};

    // @todo: temporary
	var lookupProperty = 'location';

    var InfoBox = L.Control.extend({
    	options: {
    		position: 'bottomleft'
    	},
        template: _.template('' +
            '<h4><%= title %></h4>' +
            '<p><%= label %>: <%= value %></p>'),
        onAdd: function (map){
            return L.DomUtil.create('div', 'info');
        },
        update: function (title, label, value) {
            var container = this.getContainer();
            if (title !== undefined && label !== undefined && value !== undefined) {
                container.style.display = 'block';
                container.innerHTML = this.template({
                    title: title,
                    label: label,
                    value: value !== null? Math.floor(value) :'No Reports'
                });
            } else {
                container.innerHTML = '';
                container.style.display = 'none';
            }
        }
    });

    // control that shows state info on hover
    var info = new InfoBox();
    info.addTo(map);
    info.update();

    // Map legend
    var Legend = L.Control.extend({
        template: _.template('<% _.each(items, function (item) { %>' +
            '<span><i style="background: <%= item.color %>"></i> <%= item.label %></span><br />' +
            '<% }) %>'),
        options: {
            position: 'bottomright'
        },
        onAdd: function (map) {
            return L.DomUtil.create('div', 'info legend');
        },
        update: function (items) {
            this.getContainer().innerHTML = this.template({
                items: items
            });
        }
    });

    // Control for printing the map
    var PrintControl = L.Control.extend({
        options: {
            position: 'topleft',
            title: 'Print Map'
        },
        onAdd: function(map) {
            var container, className = 'print-btn';
            this._map = map;

            container = L.DomUtil.create('div', 'leaflet-bar pull-right leaflet-print-control');
            this._createPrintButton(this.options.title, className, container, this.printMap, map);
            return container;
        },
        _createPrintButton: function(title, className, container, fn, context) {
            var link = L.DomUtil.create('a', className, container);
            link.innerHTML = '<i class="icon-save"></i>';
            link.href = '#';
            link.title = title;

            L.DomEvent
                .addListener(link, 'click', L.DomEvent.stopPropagation)
                .addListener(link, 'click', L.DomEvent.preventDefault)
                .addListener(link, 'click', fn, context);

            return link;
        },
        printMap: function(){
            var map = this;
            // toggle processing state
            $('a.print-btn').children('i').addClass("hidden");
            $('a.print-btn').addClass('export-spinner');

            leafletImage(map, function(err, canvas) {

                var mapID = 'map';

                var canvasWidth = canvas.width;
                var canvasHeight = canvas.height;
                var ctx = canvas.getContext("2d");

                //draw map legend
                var html_legend = $('#' + mapID + ' .legend');

                if(html_legend.length) {
                    // define helper functions
                    function cssvalue(elem, prop) {
                        return parseInt(elem.css(prop).replace('px', ''));
                    }
                    function roundRect(ctx, x, y, width, height, radius, fill, stroke) {
                        if (typeof stroke == "undefined" ) {
                            stroke = true;
                        }
                        if (typeof radius === "undefined") {
                            radius = 5;
                        }
                        ctx.beginPath();
                        ctx.moveTo(x + radius, y);
                        ctx.lineTo(x + width - radius, y);
                        ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
                        ctx.lineTo(x + width, y + height - radius);
                        ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
                        ctx.lineTo(x + radius, y + height);
                        ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
                        ctx.lineTo(x, y + radius);
                        ctx.quadraticCurveTo(x, y, x + radius, y);
                        ctx.closePath();
                        if (stroke) {
                            ctx.stroke();
                        }
                        if (fill) {
                            ctx.fill();
                        }
                    }

                    var legendWidth = cssvalue(html_legend, 'width');
                    var legendHeight = cssvalue(html_legend, 'height');
                    var legendMarginRight = cssvalue(html_legend, 'margin-right');
                    var legendMarginBottom = cssvalue(html_legend, 'margin-bottom');
                    var legendPaddingLeft = cssvalue(html_legend, 'padding-left');
                    var legendPaddingTop = cssvalue(html_legend, 'padding-top');
                    var legendX = canvasWidth - legendWidth - legendMarginRight;
                    var legendY = canvasHeight - legendHeight - legendMarginBottom;
                    ctx.fillStyle = "rgba(255,255,255, 0.8)";
                    ctx.strokeStyle = '#bbbbbb';
                    roundRect(ctx, legendX, legendY,
                              legendWidth, legendHeight, 5, true, true);
                    // draw legend text
                    ctx.shadowOffsetX = 0;
                    ctx.shadowOffsetY = 0;
                    ctx.shadowBlur = 0;
                    var legendTextX = legendX + legendPaddingLeft;
                    var legendTextY = legendY + legendPaddingTop;
                    var currentLegendTextY = legendTextY;
                    html_legend.children('span').each(function (index, spanElem) {
                        var span = $(spanElem);
                        var i = span.children('i');
                        var width = cssvalue(i, 'width');
                        var height = cssvalue(i, 'height');
                        var text = span.text();
                        ctx.fillStyle = i.css('background-color');
                        ctx.fillRect(legendTextX, currentLegendTextY,
                                      width, height);
                        // text
                        ctx.fillStyle = "#555";
                        ctx.font = "14px 'Open Sans',sans-serif";
                        ctx.textAlign = "left";
                        ctx.textBaseline = "middle";
                        ctx.fillText(text,
                                     legendTextX + width,
                                     currentLegendTextY + height / 2);
                        currentLegendTextY += height;
                    });
                }

                var img = document.createElement('img');
                var dimensions = map.getSize();
                img.width = dimensions.x;
                img.height = dimensions.y;
                img.src = canvas.toDataURL().replace(/^data:image\/[^;]/, 'data:application/octet-stream');
                location.href = img.src;
                // cleanup processing state
                $('a.print-btn').removeClass('export-spinner');
                $('a.print-btn').children('i').removeClass("hidden");
            });
            
        }
    });

    var printer = new PrintControl();
    printer.addTo(map);

    var colors = {
        GREY: '#ccc',
        RED: '#FF4136',
        AMBER: '#FFDC00',
        GREEN: '#2ECC40'
    };

    var histogramColors = ['#edf8fb', '#ccece6', '#99d8c9', '#66c2a4', '#2ca25f', '#006d2c'];
    var isHistogram = false;

    var legend = new Legend();
    //legend.addTo(map);
    /*legend.update([
        {color: colors.GREEN, label: '&gt; 80%'},
        {color: colors.AMBER, label: '60&ndash;80%'},
        {color: colors.RED, label: '&lt; 60%'},
        {color: colors.GREY, label: 'No Reports'}
    ]);*/

    var markerLayer = L.layerGroup()
        .addTo(map);

    var shapeLayer = L.geoJson(null, {
        onEachFeature: function (feature, layer) {
            layer.on({
                mouseover: function (e) {
                    var layer = e.target;
                    layer.setStyle({
                        fillOpacity: 0.7
                    });
                    info.update(
                        layer.feature.properties.title,
                        layer.feature.properties.label,
                        layer.feature.properties.value);
                },
                mouseout: function (e) {
                    var layer = e.target;
                    layer.setStyle({
                        fillOpacity: 0.5
                    });
                    info.update();
                }
            });
        }
    });

    var setData = function (newData, isImpactData) {
        data = newData;
        isHistogram = isImpactData || false;

        // get the min amd max values
        /*console.log(data);
        _.each(data, function (row) {
            var values = _.map(row, function (indicator) {
                return parseInt(indicator.value);
            });
            d3.max(values);
            d3.min(values);
        });*/
    };

    var setGeoJSON = function (geoJson) {
        shapeLayer.clearLayers();
        shapeLayer.addData(geoJson);
    };

    var setIndicator = function (indicator_id) {
        var bins;
        map.removeLayer(markerLayer);
        map.removeLayer(shapeLayer);
        if(legend._map)
            map.removeControl(legend);

        // add them back
        shapeLayer.addTo(map);
        legend.addTo(map);

        if (isHistogram) {
            // get the max value for the indicator
            var values = _.map(data, function (row) {
                return parseInt(row[indicator_id].value);
            });
            var max = d3.max(values);

            // bin me
            bins = d3.layout.histogram().bins(6)(values);
            var legendData = _.map(bins, function (bin, index) {
                var label = Math.round(bin.x) + ' &ndash; ' + Math.round(bin.x + bin.dx);
                if (index == bins.length - 1) {
                    label = "> " + Math.round(bin.x);
                }
                return { color: histogramColors[index], label: label};
            });
            legend.update(legendData);
        } else {
            legend.update([
                {color: colors.GREEN, label: '&gt; 80%'},
                {color: colors.AMBER, label: '60&ndash;80%'},
                {color: colors.RED, label: '&lt; 60%'},
                {color: colors.GREY, label: 'No Reports'}
            ]);
        }

        shapeLayer.setStyle(function (feature) {
            var location = feature.properties[lookupProperty];
            if(data[location] && data[location][indicator_id]){
                var indicator = data[location][indicator_id];
                var value = indicator.value;
                feature.properties.title = location;
                feature.properties.label = indicator.label;
                feature.properties.value = indicator.value;
                var intValue = parseInt(value);
                var fillColor;
                if (isHistogram) {
                    fillColor = getHistogramColor(intValue, bins);
                } else {
                    fillColor = getColor(intValue);
                }
                return {
                    fillColor: fillColor,
                    weight: 1,
                    color: '#fff',
                    opacity: 1,
                    fillOpacity: 0.5
                };
            } else {
                return {
                    fillColor: colors.GREY,
                    weight: 1,
                    color: '#fff',
                    opacity: 1,
                    fillOpacity: 0.2
                };
            }
        });
    };

    var getHistogramColor = function(value, bins) {
        var colorIndex = _.map(bins, function (item, index) {
            return item.indexOf(value) > -1?0:-1;
        }).indexOf(0);
        return histogramColors[colorIndex];
    };

    var getColor = function (value) {
        if (value === null || isNaN(value)) {
            return colors.GREY;
        }
        else if (value < 60) {
            return colors.RED;
        } else if (value > 60 && value < 80) {
            return colors.AMBER;
        } else {
            return colors.GREEN;
        }
    };

    var displayMarkers = function(raw_data) {
        var latlng, icon,
            icon_sector_map = {
                'Banana': {label: 'b', color: '#d8c22f'},
                'Catering': {label: 'c', color: '#e8ffb9'},
                'Dairy Cows': {label: 'slaughterhouse', color: '#a28245'},
                'Dairy Goat': {label: 'g', color: '#f3c368'},
                'Field Industrial Crops': {label: 'garden', color: '#21b01d'},
                'Fish Farming': {label: 'wetland', color: '#2c34c7'},
                'Motor Cycle': {label: 'm', color: '#000000'},
                'Oxen Plough': {label: 'o', color: '#697690'},
                'Piggery': {label: 'p', color: '#b54282'},
                'Poultry': {label: 'p', color: '#ae241a'},
                'Tailoring': {label: 't', color: '#3aa32a'}
            };
        $.each(raw_data, function (index, data) {
            var marker;
            latlng = L.latLng(data.lat, data.lng);
            icon = L.MakiMarkers.icon({
                icon: icon_sector_map[data.sector].label,
                color: icon_sector_map[data.sector].color,
                size: 's'});
            marker = L.marker(latlng, {icon: icon, title: data.name});
            description = buildProjectDescriptionTable(data.name, data.image_link, data.description);
            marker.bindPopup(description.html());
            markerLayer.addLayer(marker);
        });
    };

    var buildProjectDescriptionTable = function(name, img, description) {
        var
            responsiveDiv = $('<div />', {class: 'table-responsive'}),
            table = $('<table />', {
                class: 'table table-striped table-bordered table-hover'
            });
        responsiveDiv.append("<div class='bold text-center'>" + name + "</div>");
        responsiveDiv.append("<div class=''> <img src=" + img + " class='project-img img-responsive' alt='No Image'></div>");
        $.each(description, function(idx, row_values) {
            var row = $('<tr />').append($('<td />').html(row_values[0])).append($('<td />').html(row_values[1]));
            table.append(row);
        });
        return responsiveDiv.append(table);
    };

    return {
        map: map,
        initBaseMap: initBaseMap,
        setData: setData,
        setGeoJSON: setGeoJSON,
        setIndicator: setIndicator,
        displayMarkers: displayMarkers
    };
})(this);