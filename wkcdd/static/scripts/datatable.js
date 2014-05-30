'use strict';

$(document).ready(function () {
    // var responsiveHelper = undefined;
    // var breakpointDefinition = {
        // tablet: 1024,
        // phone : 480
    // };
    
    var tableElement = $('.wk-datatable');
    // tableElement.dataTable({
        // autoWidth        : true,
        // preDrawCallback: function () {
            // // Initialize the responsive datatables helper once.
            // if (!responsiveHelper) {
                // responsiveHelper = new ResponsiveDatatablesHelper(tableElement, breakpointDefinition);
            // }
        // },
        // rowCallback    : function (nRow) {
            // responsiveHelper.createExpandIcon(nRow);
        // },
        // drawCallback   : function (oSettings) {
            // responsiveHelper.respond();
        // }
    // });
    
    tableElement.dataTable();
    tableElement.find("input").addClass(".form-control");
});