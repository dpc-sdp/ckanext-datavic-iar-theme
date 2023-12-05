this.ckan.module("datavic-dropdown", function ($) {
    "use strict";

    return {
        options: {},
        initialize: function () {

            $(".rpl-site-header__inner").addClass("dropdown-hidden");

            this.el.click(function () {
                var header
                var dropdown_top

                if ($(window).width() <= 991) {
                    header = $("#mobile-menu").children(".rpl-site-header__inner");
                    dropdown_top = $(this).offset().top
                    $(this).next(".dropdown").css("transform", `translate(40px, ${dropdown_top}px)`);
                } else {
                    header = $("#main-menu").children(".rpl-site-header__inner");
                    dropdown_top = header.offset().top + header.outerHeight(true) - 2
                    var dropdown_height = $("body").outerHeight() - dropdown_top
                    $(this).next(".dropdown").css("transform", `translate(40px, ${dropdown_top}px)`);
                    $(this).next(".dropdown").css("height", `${dropdown_height}px`);
                }
                $(this).next(".dropdown").slideToggle();
                $(this).toggleClass("show")
                $(this).next(".dropdown").toggleClass("dropdown-shown");
                header.toggleClass("dropdown-hidden").toggleClass("dropdown-shown");


            });
        },
    };
});
