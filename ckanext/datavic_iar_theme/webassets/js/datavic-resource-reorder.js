// Update CKAN core resource-reorder script
// Add Cancel button to Reorder resource page 

ckan.module("datavic-resource-reorder", function ($, _) {
    const parentModule = ckan.module.registry["resource-reorder"];

    overrides = {
        template: {
            title: '<h1></h1>',
            help_text: '<p></p>',
            button: [
                '<a href="javascript:;" class="btn btn-default">',
                '<i class="fa fa-bars"></i>',
                '<span></span>',
                '</a>'
            ].join('\n'),
            form_actions: [
                '<div class="form-actions">',
                '<a href="javascript:;" class="cancel btn btn-primary"></a>',
                '<a href="javascript:;" class="save btn btn-primary"></a>',
                '</div>'
            ].join('\n'),
            handle: [
                '<a href="javascript:;" class="handle">',
                '<i class="fa fa-arrows"></i>',
                '</a>'
            ].join('\n'),
            saving: [
                '<span class="saving text-muted m-right">',
                '<i class="fa fa-spinner fa-spin"></i>',
                '<span></span>',
                '</span>'
            ].join('\n')
        },
    }

    return $.extend({}, parentModule.prototype, overrides);
});
