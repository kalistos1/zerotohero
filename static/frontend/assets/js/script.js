/*
Author       : Dreamguys
Template Name: Mentoring - Bootstrap Template
Version      : 1.0
*/

(function ($) {
	"use strict";

	// Toggle Password
	if ($('.toggle-password').length > 0) {
		$(document).on('click', '.toggle-password', function () {
			const $icon = $(this).find('i');
			const $input = $(this).closest('.input-group').find('.pass-input');
			if ($input.attr('type') === 'password') {
				$input.attr('type', 'text');
				$icon.removeClass('icon-eye-off').addClass('icon-eye');
			} else {
				$input.attr('type', 'password');
				$icon.removeClass('icon-eye').addClass('icon-eye-off');
			}
		});
	}


	// Stick Sidebar

	if ($(window).width() > 767) {
		if ($('.theiaStickySidebar').length > 0) {
			$('.theiaStickySidebar').theiaStickySidebar({
				// Settings
				additionalMarginTop: 30
			});
		}
	}

	// Sidebar

	if ($(window).width() <= 991) {
		var Sidemenu = function () {
			this.$menuItem = $('.main-nav a');
		};

		function init() {
			var $this = Sidemenu;
			$('.main-nav a').on('click', function (e) {
				if ($(this).parent().hasClass('has-submenu')) {
					e.preventDefault();
				}
				if (!$(this).hasClass('submenu')) {
					$('ul', $(this).parents('ul:first')).hide(350);
					$('a', $(this).parents('ul:first')).removeClass('submenu');
					$(this).next('ul').show(350);
					$(this).addClass('submenu');
				} else if ($(this).hasClass('submenu')) {
					$(this).removeClass('submenu');
					$(this).next('ul').hide(350);
				}
			});
		}

		// Sidebar Initiate
		init();
	}




	// Select 2

	if ($('.select').length > 0) {
		$('.select').select2({
			minimumResultsForSearch: -1,
			width: '100%'
		});
	} 

	// Date Time Picker

	if ($('.datetimepicker').length > 0) {
		$('.datetimepicker').datetimepicker({
			format: 'DD/MM/YYYY',
			icons: {
				up: "fas fa-chevron-up",
				down: "fas fa-chevron-down",
				next: 'fas fa-chevron-right',
				previous: 'fas fa-chevron-left'
			}
		});
	}

	// Timepicker
	if ($('.timepicker').length > 0) {
		$('.timepicker').datetimepicker({
			format: 'HH:mm A',
			icons: {
				up: "icon-chevron-up",
				down: "icon-chevron-down",
				next: 'icon-chevron-right',
				previous: 'icon-chevron-left'
			}
		});
	}

	// Initialize Flatpickr on elements with data-provider="flatpickr"
	document.querySelectorAll('[data-provider="flatpickr"]').forEach(el => {
		const config = {
			disableMobile: true
		};
		if (el.hasAttribute('data-date-format')) {
			config.dateFormat = el.getAttribute('data-date-format');
		}
		if (el.hasAttribute('data-enable-time')) {
			config.enableTime = true;
			config.dateFormat = config.dateFormat ? `${config.dateFormat} H:i` : 'Y-m-d H:i';
		}
		if (el.hasAttribute('data-altFormat')) {
			config.altInput = true;
			config.altFormat = el.getAttribute('data-altFormat');
		}
		if (el.hasAttribute('data-minDate')) {
			config.minDate = el.getAttribute('data-minDate');
		}
		if (el.hasAttribute('data-maxDate')) {
			config.maxDate = el.getAttribute('data-maxDate');
		}
		if (el.hasAttribute('data-default-date')) {
			const defaultDate = el.getAttribute('data-default-date');
			// Check if it's a valid date string
			if (!["true", "false", "", null].includes(defaultDate) && !isNaN(Date.parse(defaultDate))) {
				config.defaultDate = defaultDate;
			}
		}
		if (el.hasAttribute('data-multiple-date')) {
			config.mode = 'multiple';
		}
		if (el.hasAttribute('data-range-date')) {
			config.mode = 'range';
		}
		if (el.hasAttribute('data-inline-date')) {
			config.inline = true;
			const inlineDate = el.getAttribute('data-inline-date');
			if (!["true", "false", "", null].includes(inlineDate) && !isNaN(Date.parse(inlineDate))) {
				config.defaultDate = inlineDate;
			}
		}
		if (el.hasAttribute('data-disable-date')) {
			config.disable = el.getAttribute('data-disable-date').split(',');
		}
		if (el.hasAttribute('data-week-number')) {
			config.weekNumbers = true;
		}
		flatpickr(el, config);
	});

	// Floating Label

	if ($('.floating').length > 0) {
		$('.floating').on('focus blur', function (e) {
			$(this).parents('.form-focus').toggleClass('focused', (e.type === 'focus' || this.value.length > 0));
		}).trigger('blur');
	}

	// Mobile menu sidebar overlay

	$('body').append('<div class="sidebar-overlay"></div>');
	$(document).on('click', '#mobile_btn', function () {
		$('main-wrapper').toggleClass('slide-nav');
		$('.sidebar-overlay').toggleClass('opened');
		$('html').toggleClass('menu-opened');
		return false;
	});

	$(document).on('click', '.sidebar-overlay', function () {
		$('html').removeClass('menu-opened');
		$(this).removeClass('opened');
		$('main-wrapper').removeClass('slide-nav');
	});

	// Menu Close
	$(document).on('click', '#menu_close', function() {
		$('html').removeClass('menu-opened');
		$('.sidebar-overlay').removeClass('opened');
		$('main-wrapper').removeClass('slide-nav');
	});


	// Header Eight
	$(window).scroll(function () {
		var scroll = $(window).scrollTop();
		if (scroll > 70) {
			$(".header-eight").addClass("sticky");
		}
		else {
			$(".header-eight").removeClass("sticky");
		}
	})

	// Sticky Header
	$(window).scroll(function () {
		const $header = $("header.header");
		if ($(this).scrollTop() > 130) {
			$header.addClass("fixed");
		} else {
			$header.removeClass("fixed").addClass("fadeInUp");
		}
	});

	// Tooltip

	var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
	var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
		return new bootstrap.Tooltip(tooltipTriggerEl)
	})

	// Home popular mentor slider

	if ($('.owl-carousel.mentoring-course').length > 0) {
		var owl = $('.owl-carousel.mentoring-course');
		owl.owlCarousel({
			margin: 24,
			nav: false,
			nav: true,
			loop: true,
			responsive: {
				0: {
					items: 1
				},
				768: {
					items: 2
				},
				1000: {
					items: 3,

				},
				1170: {
					items: 4
				}
			}
		});
	}

	// Popular course two

	if ($('.owl-carousel.popular-course-slide-two').length > 0) {
		var owl = $('.owl-carousel.popular-course-slide-two');
		owl.owlCarousel({
			margin: 24,
			dots: false,
			nav: true,
			loop: true,
			responsive: {
				0: {
					items: 1
				},
				768: {
					items: 2
				},
				1170: {
					items: 3
				}
			}
		});
	}

	// Slick testimonial two

	if ($('.say-about.slider-for').length > 0) {
		$('.say-about.slider-for').slick({
			slidesToShow: 1,
			slidesToScroll: 1,
			arrows: true,
			fade: true,
			asNavFor: '.client-img.slider-nav'
		});
	}

	if ($('.client-img.slider-nav').length > 0) {
		$('.client-img.slider-nav').slick({
			slidesToShow: 5,
			slidesToScroll: 1,
			asNavFor: '.say-about.slider-for',
			dots: true,
			arrows: false,
			centerMode: true,
			focusOnSelect: true

		});
	}

	// Slick testimonial three

	if ($('.mentor-testimonial.lazy').length > 0) {
		$(".mentor-testimonial.lazy").slick({
			lazyLoad: 'ondemand',
			infinite: true
		});
	}

	// Service slider five
	$('.service-slider-three').each(function () {
		const $slider = $(this);
		if (!$slider.hasClass('slick-initialized')) {
			$slider.slick({
				dots: false,
				infinite: true,
				speed: 2000,
				slidesToShow: 5,
				slidesToScroll: 1,
				autoplay: true,
				arrows: false,
				centerMode: true,
				responsive: [
					{
						breakpoint: 1400,
						settings: { slidesToShow: 5, slidesToScroll: 1 }
					},
					{
						breakpoint: 1200,
						settings: { slidesToShow: 3, slidesToScroll: 1 }
					},
					{
						breakpoint: 992,
						settings: { slidesToShow: 3, slidesToScroll: 1 }
					},
					{
						breakpoint: 768,
						settings: { slidesToShow: 2, slidesToScroll: 1, variableWidth: false, centerMode: false  }
					},
					{
						breakpoint: 576,
						settings: { slidesToShow: 1, slidesToScroll: 1, variableWidth: false, centerMode: false  }
					}
				]
			});
		}
	});

	// JQuery counterUp

	// if($('.counterUp').length > 0) {
	// 	$('.counterUp').counterUp({
	//         delay: 15,
	// 		speed:100,
	//         time: 1500
	//     });
	// }

	// CounterUp Initialization
	if ($(".counter").length > 0) {
		$(".counter").counterUp({
			delay: 10,
			time: 2000,
		});
		$(".counter").addClass("animated fadeInDownBig");
	}


	// Home four header

	$(window).scroll(function () {
		var sticky = $('.scroll-sticky'),
			scroll = $(window).scrollTop();

		if (scroll >= 100) sticky.addClass('add-header-bg');
		else sticky.removeClass('add-header-bg');
	});

	// Home three header

	$(window).scroll(function () {
		var sticky = $('.scroll-sticky-three'),
			scroll = $(window).scrollTop();

		if (scroll >= 100) sticky.addClass('add-header-three');
		else sticky.removeClass('add-header-three');
	});

	// Back to top

	if ($('.back-to-top-icon').length > 0) {
		var scrollTrigger = 100, // px
			backToTop = function () {
				var scrollTop = $(window).scrollTop();
				if (scrollTop > scrollTrigger) {
					$('.back-to-top-icon').addClass('show');
				} else {
					$('.back-to-top-icon').removeClass('show');
				}
			};
		backToTop();
		$(window).on('scroll', function () {
			backToTop();
		});
		$('.back-to-top-icon').on('click', function (e) {
			e.preventDefault();
			$('html,body').scrollTop({
			}, 700);
		});
	}

	// Fade in scroll

	if ($('.main-wrapper .aos').length > 0) {
		AOS.init({
			duration: 1200,
			once: true
		});
	}


	// Date Range Picker
	if ($('#reportrange').length > 0) {
		const start = moment().subtract(0, "days");
		const end = moment();
		const report_range = (start, end) => {
			$("#reportrange span").html(`${start.format("D MMM YY")} - ${end.format("D MMM YY")}`);
		};
		$("#reportrange").daterangepicker(
			{
				startDate: start,
				endDate: end,
				ranges: {
					'Today': [moment(), moment()],
					'Yesterday': [moment().subtract(1, "days"), moment().subtract(1, "days")],
					"Last 7 Days": [moment().subtract(6, "days"), moment()],
					"Last 30 Days": [moment().subtract(29, "days"), moment()],
					"This Month": [moment().startOf("month"), moment().endOf("month")],
					"Last Month": [
						moment().subtract(1, "month").startOf("month"),
						moment().subtract(1, "month").endOf("month")
					]
				}
			},
			report_range
		);
		report_range(start, end); 
	}


	// Add More Hours

	$(".hours-info").on('click', '.trash', function () {
		$(this).closest('.hours-cont').remove();
		return false;
	});

	$(".add-hours").on('click', function () {

		var hourscontent = '<div class="row form-row hours-cont">' +
			'<div class="col-12 col-md-10">' +
			'<div class="row form-row">' +
			'<div class="col-12 col-md-6">' +
			'<div class="form-group">' +
			'<label>Start Time</label>' +
			'<select class="form-control form-select">' +
			'<option>Select</option>' +
			'<option>12.00 am</option>' +
			'<option>1.00 am</option>' +
			'<option>2.00 am</option>' +
			'<option>3.00 am</option>' +
			'<option>4.00 am</option>' +
			'<option>5.00 am</option>' +
			'<option>6.00 am</option>' +
			'<option>7.00 am</option>' +
			'<option>8.00 am</option>' +
			'<option>9.00 am</option>' +
			'<option>10.00 am</option>' +
			'<option>11.00 am</option>' +
			'<option>1.00 pm</option>' +
			'<option>2.00 pm</option>' +
			'<option>3.00 pm</option>' +
			'<option>4.00 pm</option>' +
			'<option>5.00 pm</option>' +
			'<option>6.00 pm</option>' +
			'<option>7.00 pm</option>' +
			'<option>8.00 pm</option>' +
			'<option>9.00 pm</option>' +
			'<option>10.00 pm</option>' +
			'<option>11.00 pm</option>' +
			'</select>' +
			'</div>' +
			'</div>' +
			'<div class="col-12 col-md-6">' +
			'<div class="form-group">' +
			'<label>End Time</label>' +
			'<select class="form-control form-select">' +
			'<option>Select</option>' +
			'<option>12.00 am</option>' +
			'<option>1.00 am</option>' +
			'<option>2.00 am</option>' +
			'<option>3.00 am</option>' +
			'<option>4.00 am</option>' +
			'<option>5.00 am</option>' +
			'<option>6.00 am</option>' +
			'<option>7.00 am</option>' +
			'<option>8.00 am</option>' +
			'<option>9.00 am</option>' +
			'<option>10.00 am</option>' +
			'<option>11.00 am</option>' +
			'<option>1.00 pm</option>' +
			'<option>2.00 pm</option>' +
			'<option>3.00 pm</option>' +
			'<option>4.00 pm</option>' +
			'<option>5.00 pm</option>' +
			'<option>6.00 pm</option>' +
			'<option>7.00 pm</option>' +
			'<option>8.00 pm</option>' +
			'<option>9.00 pm</option>' +
			'<option>10.00 pm</option>' +
			'<option>11.00 pm</option>' +
			'</select>' +
			'</div>' +
			'</div>' +
			'</div>' +
			'</div>' +
			'<div class="col-12 col-md-2"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
			'</div>';

		$(".hours-info").append(hourscontent);
		return false;
	});

	// Content div min height set

	function resizeInnerDiv() {
		var height = $(window).height();
		var header_height = $(".header").height();
		var footer_height = $(".footer").height();
		var setheight = height - header_height;
		var trueheight = setheight - footer_height;
		$(".content").css("min-height", trueheight);
	}

	if ($('.content').length > 0) {
		resizeInnerDiv();
	}

	$(window).resize(function () {
		if ($('.content').length > 0) {
			resizeInnerDiv();
		}

	});

	// Date Range Picker

	if ($('.bookingrange').length > 0) {
		var start = moment().subtract(6, 'days');
		var end = moment();

		function booking_range(start, end) {
			$('.bookingrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
		}

		$('.bookingrange').daterangepicker({
			startDate: start,
			endDate: end,
			ranges: {
				'Today': [moment(), moment()],
				'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
				'Last 7 Days': [moment().subtract(6, 'days'), moment()],
				'Last 30 Days': [moment().subtract(29, 'days'), moment()],
				'This Month': [moment().startOf('month'), moment().endOf('month')],
				'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
			}
		}, booking_range);

		booking_range(start, end);
	}

	// Chat

	var chatAppTarget = $('.chat-window');
	(function () {
		if ($(window).width() > 991)
			chatAppTarget.removeClass('chat-slide');

		$(document).on("click", ".chat-window .chat-users-list a.media", function () {
			if ($(window).width() <= 991) {
				chatAppTarget.addClass('chat-slide');
			}
			return false;
		});
		$(document).on("click", "#back_user_list", function () {
			if ($(window).width() <= 991) {
				chatAppTarget.removeClass('chat-slide');
			}
			return false;
		});
	})();

	// Preloader

	$(window).on('load', function () {
		if ($('#loader').length > 0) {
			$('#loader').delay(350).hide('slow');
			$('body').delay(350).css({ 'overflow': 'visible' });
		}
	})

	// Testimonial Slider

	if ($('#customers-testimonials').length > 0) {
		$('#customers-testimonials').owlCarousel({
			nav: true,
			items: 1,
			autoplay: true,
			loop: true,
			autoplayTimeout: 5000,
			navText: ["<i class='fas fa-chevron-left owl-nav-left'></i>", "<i class='fas fa-chevron-right owl-nav-right'></i>"],
		});
	}

	$('.favourite').on('click', function () {
		$(this).toggleClass('selected');
	});

	// Slick Slider

	if ($('.mendor-slider').length > 0) {
		$('.mendor-slider').slick({
			dots: false,
			autoplay: false,
			infinite: true,
			variableWidth: false,
			slidesToShow: 4,
			slidesToScroll: 1,
			swipeToSlide: true,
			responsive: [
				{
					breakpoint: 1024,
					settings: {
						slidesToShow: 3,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 992,
					settings: {
						slidesToShow: 3,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 2,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 500,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				}
			]
		});
	}

	// Review Slider

	if ($('.customer-slider').length > 0) {
		$('.customer-slider').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: false,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			navText: ["<i class='fa-solid fa-arrow-left'></i>", "<i class='fa-solid fa-arrow-right'></i>"],
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 1,

				},
				768: {
					items: 2,

				},
				1000: {
					items: 3,

				},
				1300: {
					items: 3,

				}
			}
		})
	}

	if ($('.popular-cat-slider').length > 0) {
		$('.popular-cat-slider').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: false,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			navText: ["<i class='fa-solid fa-arrow-left'></i>", "<i class='fa-solid fa-arrow-right'></i>"],
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 1,

				},
				768: {
					items: 2,

				},
				1000: {
					items: 3,

				},
				1300: {
					items: 4,

				}
			}
		})
	}

	if ($('.trend-course-tab-slider').length > 0) {
		$('.trend-course-tab-slider').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: false,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			navText: ["<i class='fa-solid fa-arrow-left'></i>", "<i class='fa-solid fa-arrow-right'></i>"],
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 1,

				},
				768: {
					items: 2,

				},
				1000: {
					items: 3,

				},
				1300: {
					items: 3,

				}
			}
		})
	}

	if ($('.instructor-slider').length > 0) {
		$('.instructor-slider').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: false,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			navText: ["<i class='fa-solid fa-arrow-left'></i>", "<i class='fa-solid fa-arrow-right'></i>"],
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 1,

				},
				768: {
					items: 2,

				},
				1000: {
					items: 3,

				},
				1300: {
					items: 4,

				}
			}
		})
	}

	if ($('.trusted-list').length > 0) {
		$('.trusted-list').owlCarousel({
			loop: true,
			autoplay: true,
			margin: 24,
			dots: false,
			nav: false,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			navText: ["<i class='fa-solid fa-arrow-left'></i>", "<i class='fa-solid fa-arrow-right'></i>"],
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 2,

				},
				768: {
					items: 3,

				},
				1000: {
					items: 4,

				},
				1300: {
					items: 5,

				}
			}
		})
	}

	if ($('.user-review-slide').length > 0) {
		$('.user-review-slide').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: false,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 1,

				},
				768: {
					items: 1,

				},
				1000: {
					items: 1,

				},
				1300: {
					items: 1,

				}
			}
		})
	}

	if ($('.job-area-slider').length > 0) {
		$('.job-area-slider').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: true,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			navText: ["<i class='fas fa-chevron-left'></i>", "<i class='fas fa-chevron-right'></i>"],
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 1,

				},
				768: {
					items: 2,

				},
				1000: {
					items: 3,

				},
				1300: {
					items: 4,

				}
			}
		})
	}
	if ($('.browse-cat-slider').length > 0) {
		$('.browse-cat-slider').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			navText: ["<i class='fas fa-chevron-left'></i>", "<i class='fas fa-chevron-right'></i>"],
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 1,

				},
				768: {
					items: 2,

				},
				1000: {
					items: 4,

				},
				1300: {
					items: 4,

				}
			}
		})
	}

	if ($('.news-card-slider').length > 0) {
		$('.news-card-slider').owlCarousel({
			loop: true,
			margin: 24,
			dots: false,
			nav: true,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			navText: ["<i class='fas fa-chevron-left'></i>", "<i class='fas fa-chevron-right'></i>"],
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 1,

				},
				768: {
					items: 2,

				},
				1000: {
					items: 2,

				},
				1300: {
					items: 3,

				}
			}
		})
	}

	if ($('.testi-customer-slider').length > 0) {
		$('.testi-customer-slider').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: true,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			navText: ["<i class='fas fa-chevron-left'></i>", "<i class='fas fa-chevron-right'></i>"],
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 1,

				},
				768: {
					items: 2,

				},
				1000: {
					items: 3,

				},
				1300: {
					items: 3,

				}
			}
		})
	}

	if (typeof WOW !== "undefined") {
		new WOW({
			offset: 0,
			mobile: true
		}).init();
	}

	if ($('.instructor-slider-two').length > 0) {
		$('.instructor-slider-two').owlCarousel({
			loop: true,
			margin: 24,
			dots: true,
			nav: true,
			smartSpeed: 1000,
			dotsSpeed: 500,
			dragEndSpeed: 1000,
			navText: ["<i class='fas fa-chevron-left'></i>", "<i class='fas fa-chevron-right'></i>"],
			navContainer: '.mynav1',
			responsive: {
				0: {
					items: 1,

				},
				500: {
					items: 1,

				},
				768: {
					items: 2,

				},
				1000: {
					items: 3,

				},
				1300: {
					items: 4,

				}
			}
		})
	}

	if ($('.testimonial-slider').length > 0) {
		$('.testimonial-slider').slick({
			dots: false,
			autoplay: false,
			infinite: true,
			arrows: false,
			speed: 2000,
			variableWidth: false,
			slidesToShow: 3,
			slidesToScroll: 1,
			swipeToSlide: true,
			responsive: [
				{
					breakpoint: 1024,
					settings: {
						slidesToShow: 2,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 992,
					settings: {
						slidesToShow: 2,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 500,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				}
			]
		});
	}

	if ($('.partners-slider').length > 0) {
		$('.partners-slider').slick({
			dots: false,
			autoplay: false,
			infinite: true,
			arrows: false,
			speed: 2000,
			variableWidth: false,
			slidesToShow: 5,
			slidesToScroll: 1,
			swipeToSlide: true,
			responsive: [
				{
					breakpoint: 1400,
					settings: {
						slidesToShow: 5,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 1024,
					settings: {
						slidesToShow: 4,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 992,
					settings: {
						slidesToShow: 3,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 2,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 500,
					settings: {
						slidesToShow: 2,
						slidesToScroll: 1
					}
				}
			]
		});
	}

	if ($('.testimonial-five-slider').length > 0) {
		$('.testimonial-five-slider').slick({
			dots: false,
			autoplay: false,
			infinite: true,
			arrows: false,
			speed: 2000,
			variableWidth: false,
			slidesToShow: 2,
			slidesToScroll: 1,
			swipeToSlide: true,
			responsive: [
				{
					breakpoint: 1024,
					settings: {
						slidesToShow: 2,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 992,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				},
				{
					breakpoint: 500,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				}
			]
		});
	}

	// Pricnig Plan
	document.addEventListener("DOMContentLoaded", function () {
		const switchInput = document.querySelector(".pricingSwitch");
		const monthlyTab = document.querySelector("#monthly");
		const yearlyTab = document.querySelector("#yearly");
		const labels = document.querySelectorAll(".billing-btn.label");

		if (!switchInput || !monthlyTab || !yearlyTab || labels.length < 2) {
	   			return;
		}

		function updateDisplay() {
			const isYearly = switchInput.checked;

			if (isYearly) {
				monthlyTab.classList.remove("show", "active");
				yearlyTab.classList.add("show", "active");

				// UI Label updates
				labels[0].classList.remove("active");
				labels[1].classList.add("active");
			} else {
				yearlyTab.classList.remove("show", "active");
				monthlyTab.classList.add("show", "active");

				// UI Label updates
				labels[0].classList.add("active");
				labels[1].classList.remove("active");
			}
		}

		if (switchInput) {
			switchInput.addEventListener("change", updateDisplay);

			labels.forEach((btn, index) => {
				btn.addEventListener("click", () => {
					// index 0 = monthly, index 1 = yearly
					switchInput.checked = (index === 1);
					updateDisplay();
				});
			});

			// Initialize
			updateDisplay();
		}
	});

	// Datatable
	if ($('.datatable').length > 0) {
		$('.datatable').DataTable({
			bFilter: true,
			sDom: 'fBtp',   // ❌ removed l (length) and i (info)
			ordering: true,

			lengthChange: false, // ❌ remove sLengthMenu
			info: false,         // ❌ remove info text

			language: {
				search: ' ',
				searchPlaceholder: "Search",
				paginate: {
					next: '<i class="icon-chevron-right"></i>',
					previous: '<i class="icon-chevron-left"></i>'
				}
			},

			responsive: true,
			autoWidth: false,

			initComplete: function () {
				$('.dataTables_filter').appendTo('#tableSearch');
				$('.dataTables_filter').appendTo('.search-input');
			}
		});
	}

	//  Horizontal Slide
	document.addEventListener("DOMContentLoaded", function () {
		const scrollers = document.querySelectorAll(".horizontal-slide");
		scrollers.forEach((scroller) => {
			scroller.setAttribute("data-animated", true);
			const scrollerInner = scroller.querySelector(".slide-list");
			const scrollerContent = Array.from(scrollerInner.children);
			scrollerContent.forEach((item) => {
				const duplicatedItem = item.cloneNode(true);
				duplicatedItem.setAttribute("aria-hidden", true);
				scrollerInner.appendChild(duplicatedItem);
			});
		});
	});

	document.querySelectorAll(".animate-button").forEach((e) => {
		const t = e.getAttribute("data-text"),
			n = e.querySelector(".button-text");
		n.innerHTML = "";
		const s = t.split(""),
			o = 360 / s.length;
		s.forEach((e, t) => {
			const s = document.createElement("span");
			(s.textContent = e),
				s.style.setProperty("--index", t),
				s.style.setProperty("--angle", o),
				n.appendChild(s);
		});
	});

	// Video
	const allVideos = document.querySelectorAll('.video');

	allVideos.forEach(video => {
		video.addEventListener('click', function() {
			if (video.paused) {
				// Pause all others first
				allVideos.forEach(v => v.pause());
				// Then play this one
				video.play();
			} else {
				video.pause();
			}
		});
	});

	// Partners Slider
	$('.banner-slider').each(function () {
		const $slider = $(this);
		if (!$slider.hasClass('slick-initialized')) {
			$slider.slick({
				dots: false,
				infinite: true,
				speed: 2000,
				slidesToShow: 6,
				centerMode: true,
				centerPadding: '100px',
				slidesToScroll: 1,
				autoplay: true,
				arrows: false,
				responsive: [
					{
						breakpoint: 1400,
						settings: { slidesToShow: 5 }
					},
					{
						breakpoint: 1200,
						settings: { slidesToShow: 4 }
					},
					{
						breakpoint: 992,
						settings: { slidesToShow: 3 }
					},
					{
						breakpoint: 768,
						settings: { slidesToShow: 3 }
					},
					{
						breakpoint: 576,
						settings: { slidesToShow: 1 }
					}
				]
			});
		}
	});

	// Fav Icon
	$('.fav-icon').on('click', function() {
		$(this).toggleClass('selected');
	});

	// Progress Scroll
	window.addEventListener('scroll', function() {
		let scrollProgress = document.getElementById("scroll-progress");
		let progressValue = document.getElementById("progress-value");

		// Check if the elements exist on the current page
		if (scrollProgress && progressValue) {
			let pos = document.documentElement.scrollTop;
			let calcHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
			
			// Prevent division by zero if page is not scrollable
			if (calcHeight > 0) {
				let scrollValue = Math.round((pos * 100) / calcHeight);
				progressValue.innerText = `${scrollValue}%`;
			}
		}
	});

	// Service Slider
	$('.service-slider').each(function () {
		const $slider = $(this);
		if (!$slider.hasClass('slick-initialized')) {
			$slider.slick({
				dots: false,
				infinite: true,
				speed: 2000,
				slidesToShow: 4,
				centerMode: true,
				centerPadding: '100px',
				slidesToScroll: 1,
				autoplay: true,
				arrows: false,
				responsive: [
					{
						breakpoint: 1200,
						settings: { slidesToShow: 3 }
					},
					{
						breakpoint: 992,
						settings: { slidesToShow: 2 }
					},
					{
						breakpoint: 768,
						settings: { slidesToShow: 2, centerMode: false, }
					},
					{
						breakpoint: 576,
						settings: { slidesToShow: 1, centerMode: false, }
					}
				]
			});
		}
	});

	// Aricle Hover
	const items = document.querySelectorAll('.team-item-four');
		items.forEach(item => {
		item.addEventListener('mouseenter', () => {
			// remove active from all
			items.forEach(i => i.classList.remove('active'));
			// add active only to hovered one
			item.classList.add('active');
		});

		item.addEventListener('mouseleave', () => {
			// optional: remove active when leaving
			// item.classList.remove('active');
		});
	});

	// Testimonial Slider
	if ($('.testimonial-slider-four').length > 0) {
		$('.slider-for').slick({
			infinite: true,
			speed: 2000,
			slidesToShow: 1,
			slidesToScroll: 1,
			//centerMode: true,
			autoplay: false,
			arrows: false,
			asNavFor: '.slider-nav'
		});

		$('.slider-nav').slick({
			slidesToShow: 4,
			slidesToScroll: 1,
			asNavFor: '.slider-for',
			dots: false,
			arrows: false,
			focusOnSelect: true,
			//centerMode: true,       
			//centerPadding: '0px',
			infinite: true, 
			speed: 1, 
			responsive: [
			{
				breakpoint: 992,
				settings: { slidesToShow: 3 }
			},
			{
				breakpoint: 768,
				settings: { slidesToShow: 2 }
			},
			{
				breakpoint: 576,
				settings: { slidesToShow: 1 }
			}
			]
		});
	}

// Map

    $("#map-list").on('click', function () {
        $(this).closest(".container").addClass('container-fluid');
        $(this).closest(".container-fluid").removeClass('container');
        $(".map-view").removeClass('col-xl-12').addClass('col-xl-9');
        $(".map-right").css('display', 'block');
        $('.time-slot-slider')[0].slick.refresh();
    });

})(jQuery);

