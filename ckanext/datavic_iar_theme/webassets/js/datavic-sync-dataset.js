"use strict";

ckan.module('datavic_sync_dataset', function($, _){
    return {
        initialize: function(){
            $.proxyAll(this, /_on/);
            this.el.on('click', this._onClick);
        },

        _onClick: function() {
            this.sandbox.client.call(
                "POST",
                this.options.action,
                this.options.payload,
                this._onSuccess,
                this._onError
            );
            $('#syncModal').modal('hide');
        },
        _onSuccess: function (result) {
            if (this.options.reloadOnSuccess) {
                window.location.reload();
            } else if (this.options.flashSuccess) {
                this.sandbox.notify("", this.options.flashSuccess, "success");
            }
        },
        _onError: function (err) {
            console.error(err);
            const details = err.responseJSON.error;
            if (details) {
                console.debug(details);
            }
            if (this.options.flashError) {
                this.sandbox.notify("", this.options.flashError, "error");
            }
        },
    };
});
