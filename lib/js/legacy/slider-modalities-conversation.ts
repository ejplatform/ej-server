var nextArrow = document.createElement('i');
var prevArrow = document.createElement('i');

nextArrow.setAttribute('class', 'fas fa-angle-right');
prevArrow.setAttribute('class', 'fas fa-angle-left');
$(".swiper-button-next").css('cssText', 'background-image: none');
$(".swiper-button-prev").css('cssText', 'background-image: none');
var nextBtnDiv = $(".swiper-button-next");
var prevBtnDiv = $(".swiper-button-prev");
nextBtnDiv.append(nextArrow);
prevBtnDiv.append(prevArrow);


var swiper = new Swiper('.swiper-container', {
    pagination: {
        el: '.swiper-pagination',
    },
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
});

document.querySelector('.next-slide-1').addEventListener('click', function (e) {
  e.preventDefault();
  swiper.slideTo(1, 0);
});

document.querySelector('.next-slide-2').addEventListener('click', function (e) {
  e.preventDefault();
  swiper.slideTo(2, 0);
});
