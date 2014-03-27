/**
Custom module for you to write your own javascript functions
**/
var Custom = function () {

    // private functions & variables

    var ENTER_KEY_CODE = 13;
    var filterProjectsTable = function() {
        $("#search_term").keypress(function(e) {
            var search_term, filter_url;
            if (e.which == ENTER_KEY_CODE) {
                search_term = $("#search_term").val();
                filter_url = "?search="+search_term
                window.location = filter_url;
            }
        });
    }

    // public functions
    return {

        //main function
        init: function () {
            //initialize here something.            
        },
        //filterProjectsTable function
        filterProjectsTable: filterProjectsTable

    };

}();

/***
Usage
***/
//Custom.init();
//Custom.doSomeStuff();