$(document).ready (function () {
	$("#login").click(function() {
		var email = $("#email").val();
		var pass = $("#password").val();
		var status = true;

		if (email == "") {
			$('.tooltip-email').html("Please enter your email!");
			$('.tooltip-email').slideDown("slow");
			status = false;
		}
		if (pass == "") {
			$('.tooltip-password').html("Please enter your password!");
			$('.tooltip-password').slideDown("slow");
			status = false;
		}

		if (!status)
			return;

		$.ajax({
			url:"/login/", 
			type:"post", 
			data:{
				email: email,
				pass: pass
			}
		}).done(function(res){
			//res = jQuery.parseJSON(response);
			
			if (res == 10) {
				$('.tooltip-email').html("Please enter your email!");
				$('.tooltip-email').slideDown("slow");
				$('.tooltip-password').html("Please enter your password!");
				$('.tooltip-password').slideDown("slow");
			} else if (res == 20) {
				$('.tooltip-email').html("Please enter your valid email!");
				$('.tooltip-email').slideDown("slow");
			} else if (res == 30) {
				$('.tooltip-password').html("Please enter your valid password!");
				$('.tooltip-password').slideDown("slow");
			} else if (res == 40) {
				window.location.href = "/merchant_listing/";
			}
		});
	});

	$('#email').keypress (function () {
		$('.tooltip-email').slideUp("slow");
	});

	$('#password').keypress (function () {
		$('.tooltip-password').slideUp("slow");
	});
});