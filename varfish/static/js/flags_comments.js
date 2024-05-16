
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
        if (data["flag_bookmarked"] || data["flag_for_validation"] || data["flag_candidate"] || data["flag_final_causative"] || data["flag_no_disease_association"] || data["flag_segregates"] || data["flag_doesnt_segregate"]) {
          icon_bookmark.attr("src", "/icons/fa-solid/bookmark.svg");
        } else {
          icon_bookmark.attr("src", "/icons/fa-regular/bookmark.svg");
        }
        // update row color
        var variantRow = outerThis.closest(".variant-row");
        variantRow.removeClass("variant-row-positive variant-row-uncertain variant-row-negative variant-row-empty variant-row-wip");
        variantRow.addClass("variant-row-" + summarizeFlags(data));
        if (structural_or_small === "small") {
          let dtrow = dt.row(variantRow);
          if (dtrow.child() && dtrow.child().length) {
            loadVariantDetails(dtrow, cell);
          }
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
          flag_no_disease_association: false,
          flag_segregates: false,
          flag_doesnt_segregate: false,
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
          flag_no_disease_association: false,
          flag_segregates: false,
          flag_doesnt_segregate: false,
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
    $('.variant-bookmark-comment-group, .variant-acmg').each(function () {
        // hide any open popovers when the anywhere else in the body is clicked
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
});

function clickMultiVariantBookmark(event) {
  // Compile template.
  var bookmarkModalTpl = $.templates("#multi-bookmark-flags-modal");

  let selector = $(event.target).data('selector')
  if (!selector) {
    selector = $(event.target).closest('.btn').data('selector')
  }
  const multiVars = $(selector);
  const variantList = [];
  const rowIds = [];
  multiVars.each(function(i, e) {
    if (structural_or_small === "small") {
      const dataVariant = $(e).val();
      const arrVariant = dataVariant.split("-");
      variantList.push({
        case: $(e).data("case"),
        release: arrVariant[0],
        chromosome: arrVariant[1],
        start: arrVariant[2],
        end: arrVariant[3],
        bin: arrVariant[4],
        reference: arrVariant[5],
        alternative: arrVariant[6],
      })
      rowIds.push("#" + $(e).data("case") + "-" + dataVariant)
    }
    else {  // structural_or_small == "structural"
      variantList.push({
        case: $(e).data("case"),
        sv_uuid: $(e).val(),
      })
      rowIds.push("#" + $(e).data("case") + "-" + $(e).val());
    }
  });

  var modal = $("#multiVarBookmarkCommentModal");

  // Retrieve current small variant flags from server via AJAX.
  $.ajax({
    url: multi_variant_flags_comment_url,
    data: "variant_list=" + JSON.stringify(variantList),
    dataType: "json"
  }).done(function(data) {
    var flags_bool = {
      flag_bookmarked: true,
      flag_for_validation: false,
      flag_candidate: false,
      flag_final_causative: false,
      flag_no_disease_association: false,
      flag_segregates: false,
      flag_doesnt_segregate: false,
    }
    var flags_string = {
      flag_visual: "empty",
      flag_molecular: "empty",
      flag_validation: "empty",
      flag_phenotype_match: "empty",
      flag_summary: "empty",
    }
    var flags = Object.assign({}, flags_bool, flags_string);
    var flags_color = {
      positive: "img-red",
      uncertain: "img-gold",
      negative: "img-green",
      empty: "img-gray",
    }
    var flags_img = {
      positive: "/icons/fa-solid/exclamation-circle.svg",
      uncertain: "/icons/fa-solid/question.svg",
      negative: "/icons/fa-solid/minus-circle.svg",
      empty: "/icons/fa-solid/times.svg",
    }
    $.each(data["flags"], function(k, v) {
      if ($.inArray(k, data["flags_interfering"]) > -1) {
        flags[k + "_warning"] = true
        flags["warning_exists"] = true
      }
      if (v !== null) {
        flags[k] = v
      }
    })
    flags["number_selected_variants"] = data["variant_list"].length
    $("#multiVarBookmarkCommentModalContent").html($(bookmarkModalTpl.render(flags)));
    $(modal).find(".save").click(function(event) {
      event.preventDefault();  // we will handle everything
      $(this).addClass("disabled");
      // Save flags
      var formData = $(this).closest(".modal-content").find("form").serialize();
      $.ajax({
        type: "POST",
        url: multi_variant_flags_comment_url,
        data: formData + "&variant_list=" + JSON.stringify(variantList) + "&csrfmiddlewaretoken=" + getCookie("csrftoken"),
        dataType: "json",
      }).done(function(data) {
        if (data["message"] === "OK") {
          $.each(rowIds, function(i, e) {
            var d = data["flags"]
            // update filter results
            if (filter_or_case_details === "filter") {
              var iconBookmark = $(e).find(".variant-bookmark")
              var iconComment = $(e).find(".variant-comment")

              iconBookmark.attr("src", "/icons/fa-regular/bookmark.svg");
              $.each(flags_bool, function(flag, _) {
                if (d[flag]) {
                  iconBookmark.attr("src", "/icons/fa-solid/bookmark.svg");
                }
              })

              if (data["comment"]["text"]) {
                iconComment.attr("src", "/icons/fa-solid/comment.svg");
              }

              $(e).removeClass("variant-row-positive variant-row-uncertain variant-row-negative variant-row-empty variant-row-wip");
              $(e).addClass("variant-row-" + summarizeFlags(d));
              if (structural_or_small === "small") {
                let dtrow = dt.row($(e));
                if (dtrow.child() && dtrow.child().length) {
                  loadVariantDetails(dtrow, cell);
                }
              }
            }
            else { // case_details
              // update case detail page
              $.each(flags_bool, function (flag, _) {
                var iconFlag = $(e + "-" + flag)
                if (d[flag]) {
                  iconFlag.addClass("img-dark-gray")
                  iconFlag.removeClass("img-light-gray")
                } else {
                  iconFlag.addClass("img-light-gray")
                  iconFlag.removeClass("img-dark-gray")
                }
              })
              $.each(flags_string, function(flag, _) {
                var iconFlag = $(e + "-" + flag)

                $.each(flags_color, function(color, _class) {
                  iconFlag.removeClass(_class)
                })

                iconFlag.addClass(flags_color[d[flag]])
                iconFlag.attr("src", flags_img[d[flag]])
              })

              if (data["comment"]["text"]) {
                var uuid = data["comment"]["uuids"][e.substring(1)]
                $(e + "-small-variant-comment").append(`
                <li class="list-group-item list-item" id="comment-${uuid}" data-sodar-uuid="${uuid}">
                  <div id="display-comment-${uuid}">
                    <span class="small text-muted">
                      <strong>${data["comment"]["user"]}</strong>
                      ${data["comment"]["dates_created"][e.substring(1)]}:
                    </span>
                    <em>${data["comment"]["text"]}</em>
                    <a href="#" class="pl-2 text-secondary comment-button-edit"><i class="iconify" data-icon="mdi:pencil"></i></a>
                    <a href="#" class="pl-2 text-secondary comment-button-delete"><i class="iconify" data-icon="fa-solid:times-circle"></i></a>
                  </div>
                  <div id="edit-comment-${uuid}" style="display: none;">
                    <form>
                      <textarea id="text-comment-${uuid}" name="variant_comment" rows="1" cols="40" class="form-control"></textarea>
                      <span class="btn-group d-flex">
                        <button
                            type="button"
                            class="btn btn-sm btn-primary w-100 comment-button-edit-submit">
                            Submit
                        </button>
                        <button
                            type="button"
                            class="btn btn-sm btn-secondary w-100 comment-button-edit-cancel">
                            Cancel
                        </button>
                      </span>
                    </form>
                  </div>
                  <div id="delete-comment-${uuid}" style="display: none;">
                    <span class="btn-group d-flex">
                      <button
                          type="button"
                          class="btn btn-sm btn-danger w-100 comment-button-delete-submit">
                          Delete
                      </button>
                      <button
                          type="button"
                          class="btn btn-sm btn-secondary w-100 comment-button-delete-cancel">
                          Cancel
                      </button>
                    </span>
                  </div>
                </li>
                `);
              }
            }
          });
        }
      }).fail(function(xhr) {
        // failed, notify user
        alert("Updating variant flags failed");
      });

      $(modal).modal("hide");
      $(this).removeClass("disabled");
    });
  }).fail(function(xhr) {
    alert("Retrieving variant flags failed");
  });
  // Setup the form elements so we can use AJAX for them.
}

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
  const isLikelyBenign = (((bs >= 1) && (bp >= 1)) || (bp >= 2));
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

function clickVariantAcmgRatingModal(event) {
  const outerThis = $(this)
  // Compile template.
  const acmgRatingModalTpl = $.templates("#single-acmg-criteria-modal")

  let selector = $(event.target).data('selector')
  if (!selector) {
    selector = $(event.target).closest('.btn').data('selector')
  }
  const multiVars = $(selector)
  const variantList = []
  const rowIds = []
  let caseUuid = null

  multiVars.each(function(i, e) {
    const dataVariant = $(e).val();
    const arrVariant = dataVariant.split("-");
    caseUuid = $(e).data("case")
    variantList.push({
      case: $(e).data("case"),
      dataVariant: dataVariant,
      release: arrVariant[0],
      chromosome: arrVariant[1],
      start: arrVariant[2],
      end: arrVariant[3],
      bin: arrVariant[4],
      reference: arrVariant[5],
      alternative: arrVariant[6],
    })
    rowIds.push("#" + $(e).data("case") + "-" + dataVariant)
  })
  // TODO: we only consider the first variant
  const singleVar = variantList[0]

  const modal = $("#singleVarAcmgRatingModal")

  // Save ACMG rating.
  function saveForm(event) {
    console.log('saving form')
    event.preventDefault()  // we will handle everything

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
      $(modal).modal("hide");
    }).fail(function(xhr) {
      // failed, notify user
      alert("Updating ACMG classification failed");
      $(modal).modal("hide");
    });
  }

  // Show modal when ACMG rating has been retrieved.
  function showModal(data) {
    const rawHtml = acmgRatingModalTpl.render(data)
    const html = $(rawHtml)
    html.find('[data-toggle="tooltip"]').tooltip()
    html.find('input').change(acmgCriterionChanged)
    updateAcmgRating(html)  // initial computation
    html.find('.btn.save').click(saveForm)
    html.find('.btn.clear').click(function(e) {
      $(this).closest('form').find(':checkbox').prop('checked', false)
      $(this).closest('form').find(':text').val('')
    })

    $("#singleVarAcmgRatingModalContent").html(html);
  }

  // Retrieve current small variant flags from server via AJAX.
  $.ajax({
    url: acmg_rating_url.replace("--abcef--", singleVar.case),
    data: singleVar,
    dataType: "json"
  }).done(function(data) {
    // found flags, show form with these
    data["variant"] = singleVar.dataVariant
    showModal(data)
  }).fail(function(xhr) {
    if (xhr.status == 404) {
      // no flags found yet, show form with defaults
      var data = {
        variant: singleVar.dataVariant,
        release: singleVar.release,
        chromosome: singleVar.chromosome,
        start: singleVar.start,
        end: singleVar.end,
        bin: singleVar.bin,
        reference: singleVar.reference,
        alternative: singleVar.alternative,
        flag_bookmarked: true,
        flag_for_validation: false,
        flag_candidate: false,
        flag_final_causative: false,
        flag_no_disease_association: false,
        flag_segregates: false,
        flag_doesnt_segregate: false,
        flag_visual: "empty",
        flag_validation: "empty",
        flag_phenotype_match: "empty",
        flag_summary: "empty",
      }
      showModal(data)
    } else {
      // Non-404 status code, something else failed.
      alert("Retrieving ACMG ratings failed failed")
    }
  })
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
        flag_no_disease_association: false,
        flag_segregates: false,
        flag_doesnt_segregate: false,
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


function toggleMultiVarOptionsDropdown() {
  var button = $("#multiVarButton")
  var option1 = $("#multivar-bookmark-comment")

  if ($(".multivar-selector:checked").length > 1) {
    option1.removeClass("disabled")
    button.removeClass("btn-outline-secondary")
    button.addClass("btn-secondary")
  }

  else {
    option1.addClass("disabled")
    button.addClass("btn-outline-secondary")
    button.removeClass("btn-secondary")
  }
}


$(document).on("click", ".variant-bookmark-comment-group", clickVariantBookmark);
$(document).on("click", ".variant-acmg", clickVariantAcmgRating);
$(document).on("click", "#multivar-bookmark-comment", clickMultiVariantBookmark);
$(document).on("click", ".singlevar-bookmark-comment", clickMultiVariantBookmark);
$(document).on("click", ".singlevar-acmg-rating", clickVariantAcmgRatingModal);
$(document).on("click", ".multivar-selector", toggleMultiVarOptionsDropdown);

