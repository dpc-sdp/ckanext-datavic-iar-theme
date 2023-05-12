ckan.module('datavic-confirm-link-action', function (jQuery) {
    return {
      /* An object of module options */
      options: {
        /* Content can be overriden by setting data-module-content to a
         * *translated* string inside the template, e.g.
         *
         *     <a href="..."
         *        data-module="confirm-action"
         *        data-module-content="{{ _('Are you sure?') }}">
         *    {{ _('Delete') }}
         *    </a>
         */
        content: '',

        /* By default confirm-action creates a new form and submit it
         * But you can use closest to el form by setting data-module-with-data=true
         *
         *     <a href="..."
         *        data-module="confirm-action"
         *        data-module-with-data=true>
         *     {{ _('Save') }}
         *     </a>
         */
        withData: '',

        /* This is part of the old i18n system and is kept for backwards-
         * compatibility for templates which set the content via the
         * `i18n.content` attribute instead of via the `content` attribute
         * as described above.
         */
        i18n: {
          content: '',
        },

        template: [
          '<div class="modal fade">',
          '<div class="modal-dialog">',
          '<div class="modal-content">',
          '<div class="modal-header">',
          '<h3 class="modal-title"></h3>',
          '<button type="button" class="btn-close" data-bs-dismiss="modal">×</button>',
          '</div>',
          '<div class="modal-body"></div>',
          '<div class="modal-footer">',
          '<button class="btn btn-default btn-cancel"></button>',
          '<button class="btn btn-primary"></button>',
          '</div>',
          '</div>',
          '</div>',
          '</div>'
        ].join('\n')
      },

      /* Sets up the event listeners for the object. Called internally by
       * module.createInstance().
       *
       * Returns nothing.
       */
      initialize: function () {
        jQuery.proxyAll(this, /_on/);
        this.el.on('click', this._onClick);
      },

      /* Presents the user with a confirm dialogue to ensure that they wish to
       * continue with the current action.
       *
       * Examples
       *
       *   jQuery('.delete').click(function () {
       *     module.confirm();
       *   });
       *
       * Returns nothing.
       */
      confirm: function () {
        this.sandbox.body.append(this.createModal());
        this.modal.modal('show');

        // Center the modal in the middle of the screen.
        this.modal.css({
          'margin-top': this.modal.height() * -0.5,
          'top': '50%'
        });
      },

      /* Creates the modal dialog, attaches event listeners and localised
       * strings.
       *
       * Returns the newly created element.
       */
      createModal: function () {
        if (!this.modal) {
          var element = this.modal = jQuery(this.options.template);
          element.on('click', '.btn-primary', this._onConfirmSuccess);
          element.on('click', '.btn-cancel', this._onConfirmCancel);
          element.modal({show: false});

          element.find('.modal-title').text(this._('Please Confirm Action'));
          var content = this.options.content ||
                        this.options.i18n.content || /* Backwards-compatibility */
                        this._('Are you sure you want to perform this action?');
          element.find('.modal-body').text(content);
          element.find('.btn-primary').text(this._('Confirm'));
          element.find('.btn-cancel').text(this._('Cancel'));
        }
        return this.modal;
      },

      /* Event handler that displays the confirm dialog */
      _onClick: function (event) {
        console.log(event);
        this.link = jQuery(event.target).attr('href');
        event.preventDefault();
        this.confirm();
      },

      /* Event handler for the success event */
      _onConfirmSuccess: function (event) {
        window.location.href = this.link;
      },

      /* Event handler for the cancel event */
      _onConfirmCancel: function (event) {
        event.stopPropagation();
        this.modal.modal('hide');
        return false;
      }
    };
  });
