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






window.onload = function () {
    if (!localStorage.mytimer) {
      var now = new Date();
      var later = new Date();
      later.setMinutes(now.getMinutes()+10);
      // Set the date we're counting down to
      var countDownDate = later.getTime();
      localStorage.setItem('mytimer', countDownDate);
      var test = localStorage.getItem('mytimer');
    }
}

// Update the count down every 1 second
var x = setInterval(function() {

    // Get todays date and time
    var now = new Date().getTime();

    // Find the distance between now an the count down date
    var distance = localStorage.getItem('mytimer') - now;

    // Time calculations for days, hours, minutes and seconds
    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Output the result in an element with id="demo"
    document.getElementById("minutes").innerHTML = minutes;
    document.getElementById("seconds").innerHTML = seconds;

    if(minutes < 0) {
      $('#minutes').addClass('opacity');
    }
    if(seconds < 0) {
      $('#seconds').addClass('opacity');
    }

    if(seconds >= 0 && seconds < 10) {
      document.getElementById("seconds").innerHTML = '0' + seconds;
    }
    if(minutes >= 0 && minutes < 10) {
      document.getElementById("minutes").innerHTML = '0' + minutes;
    }
    // If the count down is over, write some text
    if (distance < 0) {
        clearInterval(x);
        document.getElementById("minutes").innerHTML = '00';
        document.getElementById("seconds").innerHTML = '00';
    }
}, 1000);

//# sourceMappingURL=main.js.map
