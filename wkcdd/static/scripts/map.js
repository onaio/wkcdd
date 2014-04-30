var Map = (function(root){
    var map =  new L.Map('map', {
        layers: [
            L.tileLayer('https://{s}.tiles.mapbox.com/v3/ona.i3hg15g5/{z}/{x}/{y}.png', {
                maxZoom: 13,
                minZoom: 9,
                attribution: '<a href="http://www.mapbox.com/about/maps/" target="blank"> Terms &amp; Feedback</a>'
            })]
    }).setView([0.31, 34.5], 9);

    var data = {};

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
            if (title !== undefined && label !== undefined && value !== undefined) {
                container.style.display = 'block';
                container.innerHTML = this.template({
                    title: title,
                    label: label,
                    value: value !== null?value:'No Reports'
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
            return L.DomUtil.create('div', 'info legend');
        },
        update: function (items) {
            this.getContainer().innerHTML = this.template({
                items: items
            });
        }
    });

    var colors = {
        GREY: '#ccc',
        RED: '#FF4136',
        AMBER: '#FFDC00',
        GREEN: '#2ECC40'
    };

    var legend = new Legend();
    legend.addTo(map);
    legend.update([
        {color: colors.GREEN, label: '&gt; 80%'},
        {color: colors.AMBER, label: '60&ndash;80%'},
        {color: colors.RED, label: '&lt; 60%'},
        {color: colors.GREY, label: 'No Reports'}
    ]);

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
            })
        }
    }).addTo(map);

    var setData = function (newData) {
        data = newData;
    };

    var setGeoJSON = function (geoJson) {
        shapeLayer.clearLayers();
        shapeLayer.addData(geoJson);
    };

    var setIndicator = function (indicator_id) {
        shapeLayer.setStyle(function (feature) {
            var location = feature.properties[lookupProperty];
            var indicator = data[location][indicator_id];
            var value = indicator.value;
            feature.properties.title = location;
            feature.properties.label = indicator.label;
            feature.properties.value = indicator.value;
            var intValue = parseInt(value);
            return {
                fillColor: getColor(intValue),
                weight: 1,
                color: '#fff',
                opacity: 1,
                fillOpacity: 0.5
            };
        });
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

    return {
        map: map,
        setData: setData,
        setGeoJSON: setGeoJSON,
        setIndicator: setIndicator
    }
})(this);