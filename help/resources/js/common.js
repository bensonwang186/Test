$(document).ready(function() {
    $(".nav_linkBox").sticky({ topSpacing: 50 });
});

$(window).scroll(function() {

    if ($(this).scrollTop() > 0) {
        $('h1').addClass("animated fadeOut")
    } else {
    	$('h1').removeClass("fadeOut")
        $('h1').addClass("animated fadeIn")
    }
});