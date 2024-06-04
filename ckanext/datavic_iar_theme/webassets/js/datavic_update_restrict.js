"use strict";

ckan.module('datavic_update_restrict', function($, _){
    return {
        options: {
            pkgData: '{}'
        },
        initialize: function(){
            $.proxyAll(this, /_on/);
            this.original_data = this.options.pkgData;

            const current_data = {}
            const _this = this.el;
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has("metadata") && urlParams.get("metadata").toLowerCase() == 'true') {
                $.each(Object.keys(this.original_data), function(idx, field){
                    current_data[field] = $(_this).find('div [name="' + field + '"]').val();
                });
                this.new_data = current_data;
                this.el.on('change', this._onChange);
                this.save_button = $(this.el).find('.form-actions button[name="save"]');
                this._checkData(this.new_data, this.original_data);
            }

        },

        _onChange: function(e) {
            this.new_data[e.target.name] = e.target.value;
            this._checkData(this.new_data, this.original_data);
        },
        _checkData: function (current, original) {
            if (JSON.stringify(this.new_data) != JSON.stringify(this.original_data)) {
                this.save_button.removeAttr("disabled");
            } else {
                this.save_button.attr("disabled", "disabled");
            }
        },
    };
});
