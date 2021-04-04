$(function () {
  $(document).scroll(function () {
    var $nav = $(".navbar");
    var $nav_item = $(".nav-item");
    $nav.toggleClass('scrolled', $(this).scrollTop() > $nav.height());
    $nav_item.toggleClass('scrolled', $(this).scrollTop() > $nav.height());
  });
});