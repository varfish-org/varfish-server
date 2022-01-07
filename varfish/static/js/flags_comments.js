
// --------------------------------------------------------------------------
// Summarize VariantFlags flags
// --------------------------------------------------------------------------

function summarizeFlags(data) {
    if (data["flag_summary"] != "empty") {
        return data["flag_summary"];
    }
    // Except bookmark flag as it is set automatically if not actively disabled by user.
    var boolFlags = [
        "candidate",
        "doesnt_segregate",
        "final_causative",
        "for_validation",
        "no_disease_association",
        "segregates",
    ];
    let flags = [
        "visual",
        "validation",
        "molecular",
        "phenotype_match"
    ];
    for (let i = 0; i < flags.length; ++i) {
        let flagName = "flag_" + flags[i];
        let flagValue = data[flagName];
        if (flagValue != "empty") {
            return "wip"
        }
    }
    for (let i = 0; i < boolFlags.length; ++i) {
        let flagName = "flag_" + boolFlags[i];
        if (data[flagName]) {
          return "wip"
        }
    }
    return "empty";
}

// --------------------------------------------------------------------------
// Variant Bookmark Popover / AJAX Form
// --------------------------------------------------------------------------

function clickVariantBookmark() {
  // Compile popup template.
  var bookmarkPopupTpl = $.templates("#bookmark-flags-popup");
  // Store handle outmost $(this) for later hiding popup again.
  var outerThis = $(this);
  var caseUuid = $(this).data("case");
  var icon_comment = $(this).find(".variant-comment")
  var icon_bookmark = $(this).find(".variant-bookmark")
  var cell = $(this).closest(".variant-row").find(".toggle-variant-details");

  // Get variant description from triggering bookmark icon.
  if (structural_or_small == "small") {
    var dataVariant = $(this).data("variant");
    var arrVariant = dataVariant.split("-");
    var queryArgs = {
      release: arrVariant[0],
      chromosome: arrVariant[1],
      start: arrVariant[2],
      end: arrVariant[3],
      bin: arrVariant[4],
      reference: arrVariant[5],
      alternative: arrVariant[6],
    };
  }
  else {  // structural_or_small == "structural"
    var svUuid = $(this).data("sv");
  }

  // Function callback for showing the form.
  function showPopup(data) {
    var html = $(bookmarkPopupTpl.render(data));
    html.find('[data-toggle="tooltip"]').tooltip({container: 'body'});

    // Setup the form elements so we can use AJAX for them.
    $(html).find(".cancel").click(function(event) {
      event.preventDefault();
      outerThis.popover("hide");
    });
    $(html).find(".save").click(function(event) {
      event.preventDefault();  // we will handle everything

      // Save flags
      var formData = $(this).closest("form").serialize();
      var flags_url = variant_flags_url.replace("--abcef--", caseUuid);
      if (structural_or_small == "structural") {
        flags_url = flags_url.replace("--bbccee--", svUuid);
      }
      $.ajax({
        type: "POST",
        url: flags_url,
        data: formData + "&csrfmiddlewaretoken=" + getCookie("csrftoken"),
        dataType: "json",
      }).done(function(data) {
        // successfully updated flags, update bookmark display
        if (data["flag_bookmarked"] || data["flag_for_validation"] || data["flag_candidate"] || data["flag_final_causative"]) {
          icon_bookmark.attr("src", "/icons/fa-solid/bookmark.svg");
        } else {
          icon_bookmark.attr("src", "/icons/fa-regular/bookmark.svg");
        }
        // update row color
        var variantRow = outerThis.closest(".variant-row");
        variantRow.removeClass("variant-row-positive variant-row-uncertain variant-row-negative variant-row-empty variant-row-wip");
        variantRow.addClass("variant-row-" + summarizeFlags(data));
        let dtrow = dt.row(variantRow);
        if (structural_or_small == "small" && dtrow.child() && dtrow.child().length) {
          loadVariantDetails(dtrow, cell);
        }
      }).fail(function(xhr) {
        // failed, notify user
        alert("Updating variant flags failed");
      });

      // Add comment, if any
      var commentText = $(this).closest("form").find(".comment-text").val();
      var comment_url = variant_comment_url.replace("--abcef--", caseUuid);
      if (structural_or_small == "structural") {
        comment_url = comment_url.replace("--bbccee--", svUuid);
      }
      if (commentText) {
        $.ajax({
          type: "POST",
          url: comment_url,
          data: formData + "&csrfmiddlewaretoken=" + getCookie("csrftoken"),
          dataType: "json",
        }).done(function(data) {
          // successfully updated flags, update bookmark display
          icon_comment.attr("src", "/icons/fa-solid/comment.svg");
          let dtrow = dt.row(outerThis.closest(".variant-row"));
          if (structural_or_small == "small" && dtrow.child() && dtrow.child().length) {
            loadVariantDetails(dtrow, cell);
          }
        }).fail(function(xhr) {
          // failed, notify user
          alert("Adding comment failed");
        });
      }

      // Remove pop-over
      outerThis.popover('hide').popover("dispose");
    });

    outerThis.popover({
      title: "Flags &amp; Comments",
      html: true,
      content: html,
    }).popover("show");
  }

  var flags_url = variant_flags_url.replace("--abcef--", caseUuid);
  if (structural_or_small == "structural") {
    flags_url = flags_url.replace("--bbccee--", svUuid);
  }

  // Retrieve current small variant flags from server via AJAX.
  $.ajax({
    url: flags_url,
    data: queryArgs,
    dataType: "json"
  }).done(function(data) {
    // found flags, show form with these
    showPopup(data);
  }).fail(function(xhr) {
    if (xhr.status == 404) {
      // no flags found yet, show form with defaults
      if (structural_or_small == "small") {
        var data = {
          variant: dataVariant,
          release: arrVariant[0],
          chromosome: arrVariant[1],
          start: arrVariant[2],
          end: arrVariant[3],
          bin: arrVariant[4],
          reference: arrVariant[5],
          alternative: arrVariant[6],
          flag_bookmarked: true,
          flag_for_validation: false,
          flag_candidate: false,
          flag_final_causative: false,
          flag_visual: "empty",
          flag_molecular: "empty",
          flag_validation: "empty",
          flag_phenotype_match: "empty",
          flag_summary: "empty",
        };
      }
      else {  // structural_or_small == "structural"
        var data = {
          variant: svUuid,
          flag_bookmarked: true,
          flag_for_validation: false,
          flag_candidate: false,
          flag_final_causative: false,
          flag_visual: "empty",
          flag_molecular: "empty",
          flag_validation: "empty",
          flag_phenotype_match: "empty",
          flag_summary: "empty",
        };
      }
      showPopup(data);
    } else {
      // Non-404 status code, something else failed.
      alert("Retrieving variant flags failed");
    }
  });
}

// Hide popover when clicking outside of popover.
$('body').on('click', function (e) {
    $('.variant-bookmark-comment-group, .hgmd-popover, .variant-acmg').each(function () {
        // hide any open popovers when the anywhere else in the body is clicked
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
});


// --------------------------------------------------------------------------
// Variant ACMG Rating Popover / AJAX Form
// --------------------------------------------------------------------------

function updateAcmgRating(theForm) {
  const form = $(theForm);
  const inputClassification = form.find(".acmg-class");

  const pvs = form.find(".pvs:checked").length;
  const ps = form.find(".ps:checked").length;
  const pm = form.find(".pm:checked").length;
  const pp = form.find(".pp:checked").length;

  const bas = form.find(".ba:checked").length;
  const bs = form.find(".bs:checked").length;
  const bp = form.find(".bp:checked").length;

  const isPathogenic = (
    (
      (pvs == 1) && (
        (ps >= 1) || (pm >= 2) || (pm == 1 && pp == 1) || (pp >= 2)
      )
    ) ||
    (ps >= 2) ||
    (
      (ps == 1) && (
        (pm >= 3) || (pm >= 2 && pp >= 2) || (pm == 1 && pp >= 4)
      )
    )
  )
  const isLikelyPathogenic = (
    (pvs == 1 && pm == 1) ||
    (ps == 1 && pm >= 1 && pm <= 2) ||
    (ps == 1 && pp >= 2) ||
    (pm >= 3) ||
    (pm == 2 && pp >= 2) ||
    (pm == 1 && pp >= 4)
  )
  const isLikelyBenign = ((bs >= 2) && (bp >= 1) || ((bs >= 1) && (bp >= 2)));
  const isBenign = (bas > 0) || (bs >= 2);

  const isConflicting = (isPathogenic || isLikelyPathogenic) && (isBenign || isLikelyBenign);

  let acmgClass = 3;
  if (isPathogenic) {
    acmgClass = 5
  } else if (isLikelyPathogenic) {
    acmgClass = 4
  } else if (isBenign) {
    acmgClass = 1
  } else if (isLikelyBenign) {
    acmgClass = 2
  }
  if (isConflicting) {
    acmgClass = 3;
    form.find(".warning-conflict").removeClass("d-none")
  } else {
    form.find(".warning-conflict").addClass("d-none")
  }

  inputClassification.val(acmgClass)
}

function acmgCriterionChanged(event) {
  updateAcmgRating(event.target.form)
}

function clickVariantAcmgRating() {
  // Compile popup template.
  var bookmarkPopupTpl = $.templates("#acmg-popup");
  // Store handle outmost $(this) for later hiding popup again.
  var outerThis = $(this).closest(".bookmark").find(".variant-acmg");
  var cell = $(this).closest(".variant-row").find(".toggle-variant-details");
  var row = dt.row($(this).closest(".variant-row"));

  // Get variant description from triggering bookmark icon.
  var dataVariant = $(this).data("variant");
  var caseUuid = $(this).data("case");
  var arrVariant = dataVariant.split("-");
  var queryArgs = {
    release: arrVariant[0],
    chromosome: arrVariant[1],
    start: arrVariant[2],
    end: arrVariant[3],
    bin: arrVariant[4],
    reference: arrVariant[5],
    alternative: arrVariant[6],
  };

  // Function callback for showing the form.
  function showPopup(data) {
    var html = bookmarkPopupTpl.render(data)
    html = $(html)
    html.find('[data-toggle="tooltip"]').tooltip({container: 'body'})
    html.find('input').change(acmgCriterionChanged)
    updateAcmgRating(html)  // initial computation

    // Setup the form elements so we can use AJAX for them.
    $(html).find(".cancel").click(function(event) {
      event.preventDefault();
      $(outerThis).popover("hide");
    });
    $(html).find(".save").click(function(event) {
      event.preventDefault();  // we will handle everything

      // Save flags
      const form = $(this).closest("form")
      let formValues = form.serializeArray()
      // Because serializeArray() ignores unset checkboxes and radio buttons:
      formValues = formValues.concat(
        form.find('input[type=checkbox]:not(:checked)').map(
          function() { return {"name": this.name, "value": false} }).get())
      let formData = ""
      for (let i = 0; i < formValues.length; ++i) {
        let key = formValues[i].name
        let value = formValues[i].value
        if (key.startsWith("pvs") || key.startsWith("ps") || key.startsWith("pm") || key.startsWith("pp") ||
          key.startsWith("ba") || key.startsWith("bs") || key.startsWith("bp")) {
          value = value ? 2 : 0
        }
        if (formData.length > 0) {
          formData += "&"
        }
        formData += key + "=" + value
      }
      $.ajax({
        type: "POST",
        url: acmg_rating_url.replace("--abcef--", caseUuid),
        data: formData + "&csrfmiddlewaretoken=" + getCookie("csrftoken"),
        dataType: "json",
      }).done(function(data) {
        let badge = $(outerThis).closest(".variant-row").find(".variant-acmg")
        let acmgClass = data["class_override"] || data["class_auto"]
        if (acmgClass && (acmgClass > 3)) {
          badge.addClass("badge-danger text-white")
          badge.removeClass("badge-light badge-warning badge-success text-black text-muted")
          badge.text(acmgClass)
        } else if (acmgClass && (acmgClass == 3)) {
          badge.addClass("badge-warning text-black")
          badge.removeClass("badge-light text-muted badge-danger badge-success text-white")
          badge.text(acmgClass)
        } else if (acmgClass) {
          badge.addClass("badge-success text-white")
          badge.removeClass("badge-light text-muted badge-danger badge-warning text-black")
          badge.text(acmgClass)
        } else {
          badge.removeClass("badge-danger badge-warning badge-success text-white");
          badge.addClass("badge-light text-black text-muted");
          badge.text("-");
        }
      }).fail(function(xhr) {
        // failed, notify user
        alert("Updating ACMG classification failed");
      });

      // Remove pop-over
      $(outerThis).popover('hide').popover("dispose");
    });

    outerThis.popover({
      title: "ACMG Criteria",
      html: true,
      content: html,
    }).popover("show")
  }

  // Retrieve current small variant flags from server via AJAX.
  $.ajax({
    url: acmg_rating_url.replace("--abcef--", caseUuid),
    data: queryArgs,
    dataType: "json"
  }).done(function(data) {
    // found flags, show form with these
    data["variant"] = dataVariant;
    showPopup(data);
  }).fail(function(xhr) {
    if (xhr.status == 404) {
      // no flags found yet, show form with defaults
      var data = {
        variant: dataVariant,
        release: arrVariant[0],
        chromosome: arrVariant[1],
        start: arrVariant[2],
        end: arrVariant[3],
        bin: arrVariant[4],
        reference: arrVariant[5],
        alternative: arrVariant[6],
        flag_bookmarked: true,
        flag_for_validation: false,
        flag_candidate: false,
        flag_final_causative: false,
        flag_visual: "empty",
        flag_validation: "empty",
        flag_phenotype_match: "empty",
        flag_summary: "empty",
      };
      showPopup(data);
    } else {
      // Non-404 status code, something else failed.
      alert("Retrieving small variant flags failed");
    }
  });
}

$(document).on("click", ".variant-bookmark-comment-group", clickVariantBookmark);
//$(document).on("click", ".variant-comment", clickVariantBookmark);
$(document).on("click", ".variant-acmg", clickVariantAcmgRating);
