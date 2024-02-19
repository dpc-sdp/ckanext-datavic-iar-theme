this.ckan.module("datavic-dropdown", function ($) {
    "use strict";

    return {
        options: {
            isMobile: false
        },
        initialize: function () {
            $.proxyAll(this, /_/);

            $(".rpl-site-header__inner").addClass("dropdown-hidden");

            this.el.find(".vic-dropdown-menu .dropdown-toggle").click(this._onDropdownClick);
        },

        _onDropdownClick: function (e) {
            var dropdownItem = e.target;
            var header
            var dropdown_top

            if (this.options.isMobile) {
                header = $("#mobile-menu").children(".rpl-site-header__inner");
                dropdown_top = $(dropdownItem).offset().top
                // $(dropdownItem).next(".dropdown").css("transform", `translate(40px, ${dropdown_top}px)`);
            } else {
                header = $("#main-menu").children(".rpl-site-header__inner");
                dropdown_top = header.offset().top + header.outerHeight(true) - 2
                var dropdown_height = $("body").outerHeight() - dropdown_top
                $(dropdownItem).next(".dropdown").css("transform", `translate(40px, ${dropdown_top}px)`);
                $(dropdownItem).next(".dropdown").css("height", `${dropdown_height}px`);
            }

            this.el.find(".rpl-link.dropdown-toggle").each((_, el) => {
                if (dropdownItem === el) {
                    return;
                }

                $(el).next(".dropdown").hide();
                $(el).removeClass("show");
                $(el).next(".dropdown").removeClass("dropdown-shown");
            })

            $(dropdownItem).next(".dropdown").slideToggle();
            $(dropdownItem).toggleClass("show")
            $(dropdownItem).next(".dropdown").toggleClass("dropdown-shown");

            if ($(".rpl-link.dropdown-toggle.show").length) {
                header.removeClass("dropdown-hidden")
                header.addClass("dropdown-shown");
            }
            else {
                header.addClass("dropdown-hidden")
                header.removeClass("dropdown-shown");
            }
        },
    };
});
