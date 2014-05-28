var TrendCharts = (function(self){
    var chartDataSet = {};

    var drawTrend = function(labels, series, seriesLabels) {
        // Can specify a custom tick Array.
        // Ticks should match up one for each y value (category) in the series.
        var getSeriesLabels = function(seriesLabels) {
            seriesLabelList = []
            $.each(seriesLabels, function(idx, seriesLabel) {
                seriesLabelList.push({label: seriesLabel});
            });
            return seriesLabelList;
        }
        var 
            ticks = labels,
            plot1 = $.jqplot('chart', series, {
            seriesDefaults:{
                rendererOptions: {
                    fillToZero: true,
                },
                pointLabels: {show: true, formatString: '%.2f'}
            },
            grid: {
                background:'#ffffff'
            },
            axes: {
                xaxis: {
                    renderer: $.jqplot.CategoryAxisRenderer,
                    ticks: ticks,
                },
                yaxis: {
                    pad: 1.05,
                }
            },
            series: getSeriesLabels(seriesLabels),
            legend: {
                show: true,
                placement: 'outsideGrid'
            }
        });
    };

    var init = function() {
        $('.trend-indicator-selector').click(function () {
            var indicator = $(this).data('indicator');
           $('.selected-trend-indicator').html($(this).html());
           //redraw chart for the selected indicator
            $('#chart').empty();
            drawTrend(self.chartDataSet.labels, self.chartDataSet.series[indicator], self.chartDataSet.seriesLabels);
        });
    };

    // call class init method
    init();
    self.chartDataSet = chartDataSet;

    return {
        drawTrend: drawTrend,
        chartDataSet: chartDataSet
    };
})(this);