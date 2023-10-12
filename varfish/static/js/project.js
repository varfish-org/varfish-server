/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$('.form-group').removeClass('row');

var effect_levels = {
  "coding_transcript_intron_variant": 1,
  "complex_substitution": 3,
  "direct_tandem_duplication": 1,
  "disruptive_inframe_deletion": 2,
  "disruptive_inframe_insertion": 2,
  "downstream_gene_variant": 1,
  "feature_truncation": 3,
  "5_prime_UTR_exon_variant": 1,
  "5_prime_UTR_intron_variant": 1,
  "frameshift_elongation": 3,
  "frameshift_truncation": 3,
  "frameshift_variant": 3,
  "inframe_deletion": 2,
  "inframe_insertion": 2,
  "intergenic_variant": 1,
  "internal_feature_elongation": 3,
  "missense_variant": 2,
  "mnv": 3,
  "non_coding_transcript_exon_variant": 1,
  "non_coding_transcript_intron_variant": 1,
  "splice_acceptor_variant": 3,
  "splice_donor_variant": 3,
  "splice_region_variant": 2,
  "start_lost": 3,
  "stop_gained": 3,
  "stop_lost": 3,
  "stop_retained_variant": 1,
  "structural_variant": 1,
  "synonymous_variant": 1,
  "three_prime_UTR_exon_variant": 1,
  "three_prime_UTR_intron_variant": 1,
  "transcript_ablation": 3,
  "upstream_gene_variant": 1,
};


function colorVariantEffects() {
  $('.color-effect').each(function (index) {
    var text = $(this).text();
    if (effect_levels[text] == 3) {
      $(this).addClass('badge-danger');
    } else if (effect_levels[text] == 2) {
      $(this).addClass('badge-warning');
    } else {
      $(this).addClass('badge-secondary');
    }
  });
}


$(document).ready(function() {
  /* Add IE note */
  if (navigator.appName === 'Microsoft Internet Explorer' ||
        !!(navigator.userAgent.match(/Trident/) ||
          navigator.userAgent.match(/rv:11/)) || (
            typeof $.browser !== "undefined" && $.browser.msie === 1)) {
    let parentElem = $('div.sodar-app-container');

    if (!parentElem.length) {
      parentElem = $('div.sodar-content-container').find(
        'div.container-fluid').first()
    }

    if (!$('div.sodar-alert-container').length) {
      parentElem.prepend(
        '<div class="container-fluid sodar-alert-container"></div>')
    }
    $('div.sodar-alert-container').prepend(
      '<div class="alert alert-danger sodar-alert-top">' +
      '<i class="iconify" data-icon="bi:exclamation-circle"></i> ' +
      'VarFish doesn\'t support Microsoft Internet Explorer. We recommend using ' +
      '<a href="https://www.mozilla.org/firefox/new" target="_blank">Mozilla Firefox</a> or ' +
      '<a href="https://www.google.com/chrome" target="_blank">Google Chrome</a>.' +
      '</div>')
  }
  /* Display the django_su warning when switching a user */
  if (is_su) {
    let parentElem = $('div.sodar-app-container');

    if (!parentElem.length) {
      parentElem = $('div.sodar-content-container').find(
        'div.container-fluid').first()
    }

    if (!$('div.sodar-alert-container').length) {
      parentElem.prepend(
        '<div class="container-fluid sodar-alert-container"></div>')
    }

    $('div.sodar-alert-container').prepend(
      '<div class="alert alert-danger sodar-alert-top">' +
      '<i class="iconify" data-icon="bi:exclamation-circle"></i> ' +
      'You have assumed the identity of another account! <a href="' + su_escape_url + '">Escape</a>' +
      '</div>')
  }
});
