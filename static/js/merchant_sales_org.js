$(document).ready (function () {

    var marketplaceid = 'ATVPDKIKX0DER';
    var report_type = '_GET_MERCHANT_LISTINGS_DATA_';
    var fb;
    var last_sku;

    //document.getElementById('order_list').innerHTML = "<img src='/static/images/loading.gif' style='top:50%;left:50%;' class='loading' />";
    $('.list_modal').show();
//    altair_helpers.content_preloader_show();

    $.ajax({
        url:"/get_sellerid/", 
    }).done(function(res){
        console.log("sellerid : " + res);
        sellerid = res;

        fb = new Firebase('https://accelerlist.firebaseio.com/reports/' + sellerid + '/' + marketplaceid + '/' + report_type + '/');

        var html = "";
        fb.limitToFirst(20).on("value", function(snap) {

            snap.forEach(function (data) {
                sku = data.key();
                list = data.val();

                last_sku = sku;

                list_key = Object.keys(list)[0];
                order = list[list_key];

                item_marketplace = order['item_is_marketplace'];
                fulfillment_channel = order['fulfillment_channel'];

                //if (item_marketplace == 'y' && fulfillment_channel == 'DEFAULT') {
                if (item_marketplace == 'y' && fulfillment_channel == 'AMAZON_NA') {
                    item_name = order['item_name'];
                    product_id = order['product_id'];
                    sku = order['seller_sku'];
                    price = order['price'];
                    item_note = order['item_note'];
                    open_date = order['open_date'];
                    asin = order['asin1'];
                    var date = new Date(open_date);
                    var options = {year: 'numeric', month: 'short', day: 'numeric' };
                    open_date = date.toLocaleDateString();

                    html += ''
                        + '<li style="visibility:visible;">'
                            + '<div class="md-card-list-item-menu" data-uk-dropdown="{mode:\'click\',pos:\'bottom-right\'}">'
                                + '<a href="#" class="md-icon material-icons">&#xE5D4;</a>'
                                + '<div class="uk-dropdown uk-dropdown-small">'
                                    + '<ul class="uk-nav">'
                                        + '<li><a href="#"><i class="material-icons">&#xE15E;</i> Reply</a></li>'
                                        + '<li><a href="#"><i class="material-icons">&#xE149;</i> Archive</a></li>'
                                        + '<li><a href="#"><i class="material-icons">&#xE872;</i> Delete</a></li>'
                                    + '</ul>'
                                + '</div>'
                            + '</div>'
                            + '<span class="md-card-list-item-date">' + open_date + '</span>'
                            + '<span class="md-card-list-item-date">N/A</span>'
                            + '<span class="md-card-list-item-date">63.46%</span>'
                            + '<span class="md-card-list-item-date">($0.00)</span>'
                            + '<span class="md-card-list-item-date">$' + price + '</span>'
                            + '<div class="md-card-list-item-select">'
                                + '<input type="checkbox" data-md-icheck />'
                            + '</div>'
                            + '<div class="md-card-list-item-avatar-wrapper">'
                                //+ '<img src="/static/assets/img/avatars/avatar_10_tn.png" class="md-card-list-item-avatar" alt="" />'
                                + 'Estmated'
                            + '</div>'
                            + '<div class="md-card-list-item-sender">'
                                + '<span>' + sku + '</span>'
                            + '</div>'
                            + '<div class="md-card-list-item-subject">'
                                + '<div class="md-card-list-item-sender-small">'
                                    + '<span>' + product_id + '</span>'
                                + '</div>'
                                + '<span>' + item_name + '</span>'
                            + '</div>'
                            + '<div class="md-card-list-item-content-wrapper">'
                                + '<div class="md-card-list-item-content">'
                                    + item_note
                                + '</div>'
                                + '<form class="md-card-list-item-reply">'
                                    + '<label for="mailbox_reply_1872">ASIN : <span>' + asin + '</span></label>'
                                    + '<textarea class="md-input md-input-full" name="mailbox_reply_1872" id="mailbox_reply_1872" cols="30" rows="4"></textarea>'
                                    + '<button class="md-btn md-btn-flat md-btn-flat-primary">View Details</button>'
                                + '</form>'
                            + '</div>'
                        + '</li>';
                }
                //html += document.getElementById('order_list').innerHTML
                document.getElementById('order_list').innerHTML = html;
                $('.list_modal').hide();
//                altair_helpers.content_preloader_hide();
            });
        });
    });


    var sIndex = 11, offSet = 10, isPreviousEventComplete = true, isDataAvailable = true;

    $(window).scroll(function () {
        if ($(document).height() - 50 <= $(window).scrollTop() + $(window).height()) {
            if (isPreviousEventComplete && isDataAvailable) {

                /*$('#list_modal').removeClass('list_modal');
                $('#list_modal').addClass('sub_list_modal');
                $('#list_modal').show();*/
                altair_helpers.content_preloader_show();

                isPreviousEventComplete = false;

                console.log("last_sku : " + last_sku);

                fb.startAt(null, last_sku).limitToFirst(50).once("value", function(snap) {
                    var html = '';
                    snap.forEach(function (data) {
                        sku = data.key();
                        list = data.val();

                        last_sku = sku;

                        list_key = Object.keys(list)[0];
                        order = list[list_key];

                        item_marketplace = order['item_is_marketplace'];
                        fulfillment_channel = order['fulfillment_channel'];

                        //if (item_marketplace == 'y' && fulfillment_channel == 'DEFAULT') {
                        if (item_marketplace == 'y' && fulfillment_channel == 'AMAZON_NA') {
                            item_name = order['item_name'];
                            product_id = order['product_id'];
                            sku = order['seller_sku'];
                            price = order['price'];
                            item_condition = order['item_condition'];
                            open_date = order['open_date'];
                            var date = new Date(open_date);
                            var options = {year: 'numeric', month: 'short', day: 'numeric' };
                            open_date = date.toLocaleDateString();

                            html = ''
                                + '<li style="visibility:visible;">'
                                    + '<div class="md-card-list-item-menu" data-uk-dropdown="{mode:\'click\',pos:\'bottom-right\'}">'
                                        + '<a href="#" class="md-icon material-icons">&#xE5D4;</a>'
                                        + '<div class="uk-dropdown uk-dropdown-small">'
                                            + '<ul class="uk-nav">'
                                                + '<li><a href="#"><i class="material-icons">&#xE15E;</i> Reply</a></li>'
                                                + '<li><a href="#"><i class="material-icons">&#xE149;</i> Archive</a></li>'
                                                + '<li><a href="#"><i class="material-icons">&#xE872;</i> Delete</a></li>'
                                            + '</ul>'
                                        + '</div>'
                                    + '</div>'
                                    + '<span class="md-card-list-item-date">' + open_date + '</span>'
                                    + '<span class="md-card-list-item-date">N/A</span>'
                                    + '<span class="md-card-list-item-date">63.46%</span>'
                                    + '<span class="md-card-list-item-date">($0.00)</span>'
                                    + '<span class="md-card-list-item-date">$' + price + '</span>'
                                    + '<div class="md-card-list-item-select">'
                                        + '<input type="checkbox" data-md-icheck />'
                                    + '</div>'
                                    + '<div class="md-card-list-item-avatar-wrapper">'
                                        //+ '<img src="/static/assets/img/avatars/avatar_10_tn.png" class="md-card-list-item-avatar" alt="" />'
                                        + 'Estmated'
                                    + '</div>'
                                    + '<div class="md-card-list-item-sender">'
                                        + '<span>' + sku + '</span>'
                                    + '</div>'
                                    + '<div class="md-card-list-item-subject">'
                                        + '<div class="md-card-list-item-sender-small">'
                                            + '<span>' + product_id + '</span>'
                                        + '</div>'
                                        + '<span>' + item_name + '</span>'
                                    + '</div>'
                                    + '<div class="md-card-list-item-content-wrapper">'
                                        + '<div class="md-card-list-item-content">'
                                            + item_condition
                                        + '</div>'
                                        + '<form class="md-card-list-item-reply">'
                                            + '<label for="mailbox_reply_1872">Reply to <span>Vernice Wiza I</span></label>'
                                            + '<textarea class="md-input md-input-full" name="mailbox_reply_1872" id="mailbox_reply_1872" cols="30" rows="4"></textarea>'
                                            + '<button class="md-btn md-btn-flat md-btn-flat-primary">View Details</button>'
                                        + '</form>'
                                    + '</div>'
                                + '</li>';

                            $('#order_list').append(html);
                        }
                        isPreviousEventComplete = true;
                        //$('#list_modal').hide();
                        altair_helpers.content_preloader_hide();
                    });
                });
            }
        }
    });
});
