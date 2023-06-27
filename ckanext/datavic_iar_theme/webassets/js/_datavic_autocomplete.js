ckan.module("-datavic-autocomplete", function ($) {
  /**
   * Patch CKAN core autocomplete widget with the following behaviors:
   * * add role and aria-expanded attributes to autocomplete dropdowns
   * * [...] mention here all additional changes
   */
  const module = ckan.module.registry["autocomplete"];
  if (!module) {
    console.warn("`autocomplete` module is not registered");
    return;
  }

  const newRole = "combobox";
  const _setup = module.prototype.setupAutoComplete;

  module.prototype.setupAutoComplete = function () {
    _setup.call(this);

    const target = this._select2.focusser;
    // dropdowns have focusser element. If it's missing, we are looking at
    // tag-input, probably
    if (!target) {
      return;
    }

    console.debug(
      "[-datavic-autocomplete] Change %o role from %s to %s",
      target,
      target.attr("role"),
      newRole
    );
    target.attr("role", newRole);

    console.debug("[-datavic-autocomplete] Set aria-expanded on %o", target);
    target.attr("aria-expanded", "false");

    // remove duplicate labels
    $('.select2-search-field').children('label').remove();
    $('.select2-container').children('label').remove();
    $('.select2-search').children('label').remove();
  };
});
