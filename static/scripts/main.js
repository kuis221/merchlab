$(function() {
  $('#owl-carousel2').owlCarousel({
    loop:true,
    margin:10,
    nav:true,
    dots: true,
    center: true,
    navText: ["<img src='/static/images//arrow_left.svg'>","<img src='/static/images//arrow_right.svg'>"],
    responsive : {
    0 : {
        items: 1
      },
    1024 : {
        items: 3
      }
    }
  });
  var wow = new WOW(
    {
      boxClass:     'wow',      // animated element css class (default is wow)
      animateClass: 'animated', // animation css class (default is animated)
      offset:       0,          // distance to the element when triggering the animation (default is 0)
      mobile:       false       // trigger animations on mobile devices (true is default)
    }
  );
  wow.init();
  //menu
  $( ".menu-open" ).click(function(e) {
    e.stopPropagation();
    $('.hidden-menu').addClass('active');
    $('body').addClass('open');
  });

  $( ".close-btn" ).click(function() {
    $('.hidden-menu').removeClass('active');
    $('body').removeClass('open');
  });

  $("body").click(function(){
    $(".hidden-menu").removeClass("active");
  });

  $(".hidden-menu").click(function(e){
    e.stopPropagation();
  });
});;


//# sourceMappingURL=main.js.map
