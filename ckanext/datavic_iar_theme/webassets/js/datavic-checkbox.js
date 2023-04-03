ckan.module("datavic-checkbox", function ($, _) {
    "use strict";

    return {
        options: {},
        initialize: function () {
            $('.rpl-checkbox').on('click', function (e) {
                if ($('.rpl-checkbox').children('input[type="checkbox"]').is(":checked")) {
                    $('.rpl-checkbox').children('input[type="checkbox"]').prop("checked", false);
                    $('.rpl-checkbox').children('rpl-checkbox__box').removeClass('rpl-checkbox__box--checked');
                    $('.rpl-checkbox__box').children('.rpl-icon').hide();
                }
                else {
                    $('.rpl-checkbox').children('input[type="checkbox"]').prop("checked", true);
                    $('.rpl-checkbox').children('rpl-checkbox__box').addClass('rpl-checkbox__box--checked');
                    $('.rpl-checkbox__box ').children('.rpl-icon').show();
                }
                e.preventDefault();
            });
        },
    };
});
