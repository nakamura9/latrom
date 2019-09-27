//shrink jumbotrons on scroll

var scrolling = false;
$(document).scroll(function () {
    scrolling = true;
});

function isScrollable() {
    var windowHeight = $(window).height();
    var pageHeight = $(document).height();
    return pageHeight / windowHeight > 1.3;
}

function inIframe() {
    try {
        return window.self !== window.top;
    } catch (e) {
        return true;
    }
}

setInterval(function () {
    if (scrolling) {
        scrolling = false;
        if ($(document).scrollTop() > 0 && isScrollable()) {
            $(".jumbotron").addClass("shrink");
        }
        if ($(document).scrollTop() === 0 && !inIframe()) {
            $(".jumbotron").removeClass("shrink");
        }
    }
}, 100)

// for employees deduction page
$(document).ready(function () {
    if ($('#id_deduction_method').length > 0) {
        $('.custom-options').hide();
        $('.fixed-options').hide();
        $('input[type=submit]').hide();
        $('#id_deduction_method').on('change', function () {
            $('input[type=submit]').show();
            if ($(this).val() == 0) {
                $('.custom-options').show();
                $('.fixed-options').hide();
            } else {
                $('.custom-options').hide();
                $('.fixed-options').show();
            }
        })
    }
})