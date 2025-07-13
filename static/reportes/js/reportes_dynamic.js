// reportes/js/reportes_dynamic.js

$(function() {
  // Initialize Manpower
  $('#manpower-forms').formset({
    prefix: 'manpower',
    addText: 'Add Row',
    deleteText: 'Remove Row',
    addCssClass: 'btn btn-sm btn-outline-primary formset-add',
    deleteCssClass: 'btn btn-sm btn-outline-danger formset-delete'
  });

  // Initialize Equipment
  $('#equipment-forms').formset({
    prefix: 'equipment',
    addText: 'Add Row',
    deleteText: 'Remove Row',
    addCssClass: 'btn btn-sm btn-outline-primary formset-add',
    deleteCssClass: 'btn btn-sm btn-outline-danger formset-delete'
  });

  // Initialize Activities
  $('#activities-forms').formset({
    prefix: 'activity',
    addText: 'Add Row',
    deleteText: 'Remove Row',
    addCssClass: 'btn btn-sm btn-outline-primary formset-add',
    deleteCssClass: 'btn btn-sm btn-outline-danger formset-delete'
  });

  // (Your weather_widget.js remains unchanged)
});
