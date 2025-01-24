// Third-party extension `ckanext-alias` uses a list as a value, 
// so code has been changed to handle such values ​​and react to the update
// button when they change.
// Also added logic to react to typing in, not just to changing the fields.

"use strict";

ckan.module("datavic_update_restrict", function($, _) {
    return {
        options: {
            pkgData: "{}"
        },

        initialize: function() {
            $.proxyAll(this, /_on/);
            this.original_data = this.options.pkgData;
            const current_data = {}
            const _this = this;

            $.each(Object.keys(this.original_data), function(idx, field){
                let temp_val = $(_this.el).find("[name='" + field + "']").val();
                if (temp_val.length === 0 && _this.original_data[field].length === 0 || field == "alias") {
                    temp_val = _this.original_data[field];
                }
                current_data[field] = temp_val;
            });

            this.new_data = current_data;
            this.el.on("keyup change", this._onChange);
            $(this.el).find(".btn-multiple-remove").on("click", this._onRemoveAlias);
            this.save_button = $(this.el).find(".form-actions .save-btn");
            this._checkData(this.new_data, this.original_data);
        },

        _onRemoveAlias: function(e) {
            this.save_button.removeAttr("disabled");
        },

        _onChange: function(e) {
            if (e.target.name == "alias") {
                // Handling array type values
                var parentElement = e.target.closest("ol");
                var inputElements = $(parentElement).find("input");
                var newArray = [];
                $.each(inputElements, function(idx, element) {
                    newArray.push(element.value);
                });
                this.new_data["alias"] = newArray;
            } else {
                this.new_data[e.target.name] = e.target.value;
            }

            this._checkData(this.new_data, this.original_data);
        },

        _checkData: function (current, original) {
            current.tag_string = current.tag_string.replace(/\s*,\s*/g, ",");
            if (JSON.stringify(current) != JSON.stringify(original)) {
                this.save_button.removeAttr("disabled");
            } else {
                this.save_button.attr("disabled", "disabled");
            }
        },
    };
});
