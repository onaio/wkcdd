var Map = (function(root){
    var map =  new L.Map('map', {
        layers: [
            L.tileLayer('https://{s}.tiles.mapbox.com/v3/ona.i3hg15g5/{z}/{x}/{y}.png', {
                maxZoom: 13,
                minZoom: 9,
                attribution: '<a href="http://www.mapbox.com/about/maps/" target="blank"> Terms &amp; Feedback</a>'
            })]
    }).setView([0.31, 34.5], 9);

    // @todo: temporary
    var data = {
        'Bungoma': {
            community_contribution: '69.8%',
            bb_harvested_percentage: '1.7%'
        },
        'Kakamega': {
            community_contribution: '100%',
            bb_harvested_percentage: null
        },
        Busia: {
            community_contribution: '26%',
            bb_harvested_percentage: '8%'
        },
        'Siaya': {
            community_contribution: '132%',
            bb_harvested_percentage: '20%'
        },
        'Vihiga': {
            community_contribution: '75%',
            bb_harvested_percentage: null
        }
    };

    // @todo: temporary
    var lookupProperty = 'COUNTY';

    var InfoBox = L.Control.extend({
        template: _.template('<h4><%= title %></h4>' +
            '<p><%= label %>: <%= value %></p>'),
        onAdd: function (map) {
            return L.DomUtil.create('div', 'info');
        },
        update: function (title, label, value) {
            var container = this.getContainer();
            if (title && label && value) {
                container.style.display = 'block';
                container.innerHTML = this.template({
                    title: title,
                    label: label,
                    value: value
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
            '<i style="background: <%= item.color %>"></i> <%= item.label %><br />' +
            '<% }) %>'),
        options: {
            position: 'bottomright'
        },
        onAdd: function (map) {
            var container = L.DomUtil.create('div', 'info legend');
            return container;
        },
        update: function (items) {
            this.getContainer().innerHTML = this.template({
                items: items
            });
        }
    });

    var legend = new Legend();
    legend.addTo(map);
    legend.update([
        {color: '#2ECC40', label: '&gt; 80%'},
        {color: '#FFDC00', label: '60&ndash;80%'},
        {color: '#FF4136', label: '&lt; 60%'},
        {color: '#ccc', label: 'No Reports'}
    ]);

    var shapeLayer = L.geoJson(null, {
        onEachFeature: function (feature, layer) {
            layer.on({
                mouseover: function (e) {
                    var layer = e.target;
                    layer.setStyle({
                        fillOpacity: 0.5
                    });
                    info.update(
                        layer.feature.properties[lookupProperty],
                        layer.feature.properties.label,
                        layer.feature.properties.value);
                },
                mouseout: function (e) {
                    var layer = e.target;
                    layer.setStyle({
                        fillOpacity: 0.2
                    });
                    info.update();
                }
            })
        }
    }).addTo(map);

    var setGeoJSON = function (geojson) {
        shapeLayer.clearLayers();
        shapeLayer.addData(geojson);
    };

    var setIndicator = function (indicator) {
        shapeLayer.setStyle(function (feature) {
            var location = feature.properties[lookupProperty];
            var value = data[location][indicator];
            feature.properties.label = indicator;
            feature.properties.value = value;
            var intValue = parseInt(value);
            if (intValue === null) {
                return { color: "#ccc" };
            }
            else if (intValue < 60) {
                return { color: "#FF4136" };
            } else if (intValue > 60 && intValue < 80) {
                return { color: "#FFDC00" };
            } else {
                return { color: "#2ECC40" };
            }
        });
    };

    return {
        map: map,
        setGeoJSON: setGeoJSON,
        setIndicator: setIndicator
    }
})(this);