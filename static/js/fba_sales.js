$(document).ready (function () {

    var marketplaceid = 'ATVPDKIKX0DER';
    var report_type = '_GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_';

    $.ajax({
		url:"/get_sellerid/", 
	}).done(function(res){
        console.log("sellerid : " + res);
        sellerid = res;

	    var fb = new Firebase('https://accelerlist.firebaseio.com/reports/' + sellerid + '/' + marketplaceid + '/' + report_type + '/');

        fb.limitToFirst(10).on("value", function(snap) {
            console.log("snap : " + snap.key());
            snap.forEach(function (data) {
                console.log ("key : " + data.key() + " - val : " + data.val());
            });
        });

        var html = "";
        fb.startAt(null, '1002368594').limitToFirst(10).once("value", function(snap) {
            console.log("snap : " + snap.key());
            snap.forEach(function (data) {
                console.log ("key : " + data.key() + " - val : " + data.val());
            });
        });

    });
});
