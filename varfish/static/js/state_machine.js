/*
Build state machine for managing the background filtering job.
 */

// Define states
const STATE_INITIAL = 'initial';
const STATE_IDLE = 'idle';
const STATE_GET_JOB_ID = 'get-job-id';
const STATE_WAIT_JOB_RESULTS = 'wait-job-results';

// Define events
const EVENT_START = 'start';
const EVENT_GOT_JOB_ID = 'got-job-id';
const EVENT_STILL_WAITING = 'still-waiting';
const EVENT_GOT_RESULT = 'got-result';
const EVENT_CANCEL = 'cancel';
const EVENT_SUBMIT = 'submit';
const EVENT_NO_JOB_ID = 'no-job-id';
const EVENT_ERROR = 'error';

// Other global variables to manage the state machine.
let currentState = STATE_INITIAL;
let ajaxCall = null;
let filterButton = $("#submitFilter");
let resultsTable = $("#resultsTable");
let timer = null;
let dt = null;

/*
Handle form error responses from Django AJAX JSON response.
*/

// Define which fields that could receive a warning belong to which tabs. (E.g. checkboxes are not in our cases).
let INPUT_TAB_AFFILIATION = {
  'genotype-tab': [
    /_gt$/
  ],
  'frequency-tab': [
    /^thousand_genomes_/,
    /^exac_/,
    /^gnomad_genomes_/,
    /^gnomad_exomes_/,
    /^mtdb_/,
    /^helixmtdb_/,
    /^mitomap_/,
  ],
  'effect-tab': [
    /^max_exon_dist$/,
  ],
  'quality-tab': [
    /_dp_het$/,
    /_dp_hom$/,
    /_ab$/,
    /_gq$/,
    /_ad$/,
    /_fail$/
  ],
  'blocklist-tab': [
    /^gene_blocklist$/,
    /^gene_allowlist$/,
    /^genomic_region$/
  ],
  'flags-tab': [
    /^flag_/
  ],
  'clinvar-tab': [
    /^require_in_/,
    /^clinvar_include_/
  ],
  'export-tab': [
    /export/,
    /^file_type$/
  ],
  'misc-tab': [
    /^result_rows_limit$/
  ],
  'settings-tab': [
    /^settingsDump$/
  ],
  // More tab needs to exists with an empty entry, will be filled afterwards.
  'more-tab': []
};
// Find out which tabs are hidden in more tab (we need to convert an array-like object to an actual array).
let IN_MORE_TAB = $.makeArray($("#more-tab").next().children(".dropdown-item")).map(x => x.id);
// All fields from tabs in more tab will be merged and put into more tab dict entry.
for (let key in INPUT_TAB_AFFILIATION) {
  if (IN_MORE_TAB.includes(key)) {
    $.merge(INPUT_TAB_AFFILIATION['more-tab'], INPUT_TAB_AFFILIATION[key]);
  }
}

function findTabToInput(input) {
  let result = [];
  $.each(INPUT_TAB_AFFILIATION, function(key, value) {
    $.each(value, function(index, pattern) {
      if (pattern.test(input)) {
        result.push(key);
      }
    });
  });
  return result;
}

function updateTableDisplay() {
  $("#table-config").attr("class",
    "display-" + $("#result-display-frequencies").val() +
    " display-" + $("#result-display-constraints").val() +
    " display-" + $("#result-display-info").val()
  );
  $('[data-toggle="tooltip"]').tooltip({boundary: 'window', container: 'body'});
  $('[data-toggle="popover"]').popover({boundary: 'window', container: 'body'});
  var whitelist = $.fn.tooltip.Constructor.Default.whiteList
  whitelist.iframe = ['src', 'style', 'width', 'height', 'frameborder', 'vspace', 'hspace']
  // Alternative: skip sanitize function entirely
  //$('[data-toggle="popover"]').popover({sanitizeFn: function(content) { return content }})
}

function displayConnectionError() {
  displayError("Error in request. Probably the server is not responding or offline.");
}

function displayError(msg) {
  currentState = STATE_IDLE;
  animateFilterButtonSubmit();
  resultsTable.empty();
  resultsTable.html(
    '<div class="alert alert-danger">' +
    '<i class="iconify" data-icon="bi:exclamation-circle"></i> ' +
    '<strong>' + msg + '</strong>' +
    '</div>'
  );
}

// Helper function to switch the state of the submit button (make it "Submit").
function animateFilterButtonSubmit() {
  let icon = $("svg", filterButton).clone();
  filterButton.text(" Filter & Display");
  icon.prependTo(filterButton);
  filterButton.attr("data-event-type", EVENT_SUBMIT);
  icon.removeClass("spin");
}

function toggleLogs() {
  let x = $("#logger");
  if (x.hasClass("d-none")) {
    x.removeClass("d-none");
    $("#togglelogs").text("Hide Logs");
    setCookie("logs", "1");
  }
  else {
    x.addClass("d-none");
    $("#togglelogs").text("Show Logs");
    setCookie("logs", "0");
  }
}

// Helper function to switch the state of the submit button (make it "Cancel").
function animateSubmitButtonCancel() {
  let icon = $("svg", filterButton).clone();
  filterButton.text(" Cancel");
  icon.prependTo(filterButton);
  filterButton.attr("data-event-type", EVENT_CANCEL);
  resultsTable.empty();
  resultsTable.html(
    '<div class="alert alert-info">' +
    '<i class="iconify spin" data-icon="fa-solid:circle-notch"></i> ' +
    '<strong id="infoBoxTitle">Loading ...</strong> <button id="togglelogs" class="ml-3 btn btn-sm btn-info" onclick="toggleLogs()">Show Logs</button>' +
    '<div id="logger" class="d-none"></div>' +
    '</div>'
  );
  if (getCookie("logs") == "1") {
    toggleLogs();
  }
  icon.addClass("spin");
}

function setInfoBoxTitle(title) {
  let infobox = $("#infoBoxTitle");
  if (infobox.length) {
    infobox.html(title);
  }
}

function stopTimer() {
  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
}

function doVisualErrorResponseOnTabs(data) {
  $.each(data, function(element_name, error_texts) {
    let tabs = findTabToInput(element_name);
    $.each(tabs, function(index, tab_name) {
      $("#" + tab_name).addClass("border border-danger text-white bg-danger form-error-border");
    });
  });
}

function doVisualErrorResponseOnForms(data) {
  $.each(data, function(element_id, error_texts) {
    let element = $("#id_" + element_id);
    let text = "";
    $.each(error_texts, function(index, error) {
      text += error + "<br />";
    });
    element.addClass("border border-danger form-error-border");
    element.after("<div class='alert alert-danger form-error-info' role='alert'>" + text + "</div>");
  });
}

function removeVisualErrorResponse() {
  $(".form-error-border").each(function(index) {
    $(this).removeClass("border border-danger text-white bg-danger form-error-border");
  });
  $(".form-error-info").each(function(index) {
    $(this).remove();
  });
}

// Handle state INITIAL
function handleEventStateInitial(eventType, event) {
  if (eventType == EVENT_START) {
    currentState = STATE_GET_JOB_ID;
    animateSubmitButtonCancel();
    setInfoBoxTitle("Looking for previous results ...");
    ajaxCall = $.ajax({
      type: "GET",
      dataType: "json",
      url: filterButton.data('url-request-last-job'),
      success: function(result) {
        let filter_job_uuid = result['filter_job_uuid'];
        if (filter_job_uuid) {
          return handleEvent(EVENT_GOT_JOB_ID, {'filter_job_uuid': filter_job_uuid});
        }
        return handleEvent(EVENT_NO_JOB_ID, null);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        resultsTable.empty();
        animateFilterButtonSubmit();
        switch (jqXHR.status) {
          case 0:
            displayConnectionError();
            break;
          default:
            alert("Error during AJAX call: " + textStatus + " " +  errorThrown + " in state " + currentState);
            console.log("Error during AJAX call: ", jqXHR, textStatus, errorThrown, currentState);
            handleEvent(EVENT_ERROR, null);
        }
      }
    });
  } else {
    console.log("unexpected event", eventType, event, "in state", currentState);
  }
}

// Handle state IDLE
function handleEventStateIdle(eventType, event) {
  if (eventType == EVENT_SUBMIT) {
    currentState = STATE_GET_JOB_ID;
    animateSubmitButtonCancel();
    setInfoBoxTitle("Filtering variants ...");
    removeVisualErrorResponse();
    let data = $("#filterForm").serializeArray().reduce(
      (accumulator, current) => (accumulator[current.name] = current.value, accumulator), {}
    );
    data[filterButton.attr("name")] = filterButton.attr("value");
    ajaxCall = $.ajax({
      type: "POST",
      dataType: "json",
      url: filterButton.data("url"),
      data: data,
      success: function (result) {
        handleEvent(EVENT_GOT_JOB_ID, {'filter_job_uuid': result['filter_job_uuid']});
      },
      error: function(jqXHR, textStatus, errorThrown) {
        resultsTable.empty();
        animateFilterButtonSubmit();
        switch (jqXHR.status) {
          case 0:
            displayConnectionError();
            // aborted ajax call.
            break;
          case 400:
            removeVisualErrorResponse();
            doVisualErrorResponseOnForms(jqXHR.responseJSON);
            doVisualErrorResponseOnTabs(jqXHR.responseJSON);
            handleEvent(EVENT_ERROR, null);
            break;
          default:
            alert("Error during AJAX call: " + textStatus + " " + errorThrown + " in state " + currentState);
            console.log("Error during AJAX call: ", jqXHR, textStatus, errorThrown, currentState);
            handleEvent(EVENT_ERROR, null);
        }
      }
    });
  } else {
    console.log("unexpected event", eventType, event, "in state", currentState);
  }
}

// Handle state GET_JOB_ID
function handleEventStateGetJobId(eventType, event) {
  if (eventType == EVENT_GOT_JOB_ID) {
    setInfoBoxTitle("Filtering variants ...");
    currentState = STATE_WAIT_JOB_RESULTS;
    ajaxCall = $.ajax({
      type: "GET",
      dataType: "json",
      url: filterButton.data("url-status"),
      data: event,
      success: function (data) {
        $("#logger").html("<pre>" + data["messages"].join("<br>") + "</pre>");
        // possible job states: initial, running, done, failed
        if (data['status'] == 'done') {
          return handleEvent(EVENT_GOT_RESULT, event);
        }
        else if (data['status'] == 'failed') {
          stopTimer();
          displayError(data['messages'][data['messages'].length-1]);
        }
        else {
          return handleEvent(EVENT_STILL_WAITING, event);
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        resultsTable.empty();
        animateFilterButtonSubmit();
        switch (jqXHR.status) {
          case 0:
            displayConnectionError();
            break;
          default:
            alert("Error during AJAX call: " + textStatus + " " + errorThrown + " in state " + currentState);
            console.log("Error during AJAX call: ", jqXHR, textStatus, errorThrown, currentState);
            handleEvent(EVENT_ERROR, null);
        }
      }
    });
  } else if (eventType == EVENT_NO_JOB_ID) {
    currentState = STATE_IDLE;
    animateFilterButtonSubmit();
    resultsTable.empty();
    resultsTable.html(
      '<div class="alert alert-info">' +
      '  <strong>No query has been started yet.</strong><br>' +
      '   Click <span class="badge badge-primary"><i class="iconify" data-icon="mdi:refresh"></i> Filter & Display</span> to start filtering and create results to display here.' +
      '   You may want to adjust the filter settings to your needs first.' +
      '</div>'
    );
  } else if (eventType == EVENT_CANCEL) {
    currentState = STATE_IDLE;
    if (ajaxCall) {
      ajaxCall.abort("Aborting AJAX call ...");
      ajaxCall = null;
    }
    resultsTable.empty();
    animateFilterButtonSubmit();
  } else if (eventType == EVENT_ERROR) {
    currentState = STATE_IDLE;
    animateFilterButtonSubmit();
    resultsTable.empty();
  } else {
    console.log("unexpected event", eventType, event, "in state", currentState);
  }
}

// Handle state WAIT_JOB_RESULTS
function handleEventStateWaitJobResults(eventType, event) {
  if (eventType == EVENT_STILL_WAITING) {
    setInfoBoxTitle("Filtering variants ...");
    timer = setTimeout(
      function(event, eventData) {
        currentState = STATE_GET_JOB_ID;
        handleEvent(event, eventData);
      },
      5000,
      EVENT_GOT_JOB_ID, event
    );
  } else if (eventType == EVENT_CANCEL) {
    currentState = STATE_IDLE;
    stopTimer();
    if (ajaxCall) {
      ajaxCall.abort("Aborting AJAX call ...");
      ajaxCall = null;
    }
    resultsTable.empty();
    animateFilterButtonSubmit();
  } else if (eventType == EVENT_ERROR) {
    currentState = STATE_IDLE;
    stopTimer();
    resultsTable.empty();
    animateFilterButtonSubmit();
  } else if (eventType == EVENT_GOT_RESULT) {
    setInfoBoxTitle("Filtering is complete, creating results table ...");
    let data = {
      "csrfmiddlewaretoken": getCookie("csrftoken"),
      "filter_job_uuid": event["filter_job_uuid"]
    };
    ajaxCall = $.ajax({
      url: filterButton.data("url-reload"),
      method: "GET",
      data: data,
      success: function(data) {
        currentState = STATE_IDLE;
        animateFilterButtonSubmit();
        resultsTable.html(data);
        dt = $('#main').DataTable(
            {
              "searching": false,
              "info": false,
              "paging": false,
              "order": [[ 1, "asc" ]],
              'aoColumnDefs': [
                {
                  'aTargets': [0,2,3,5,6,8,9,28,-1], /* column index */
                  'bSortable': false, /* true or false */
                },
              ]
            }
        );
        updateTableDisplay();
      },
      error: function(jqXHR, textStatus, errorThrown) {
        resultsTable.empty();
        animateFilterButtonSubmit();
        switch (jqXHR.status) {
          case 0:
            displayConnectionError();
            break;
          case 500:
            displayError("msg" in jqXHR.responseJSON ? jqXHR.responseJSON["msg"] : textStatus + " " + errorThrown);
            break;
          default:
            alert("Error during AJAX call: " + textStatus + " " + errorThrown + " in state " + currentState);
            console.log("Error during AJAX call: ", jqXHR, textStatus, errorThrown, currentState);
            handleEvent(EVENT_ERROR, null);
        }
      }
    });
  }
  else {
    console.log("unexpected event", eventType, event, "in state", currentState);
  }
}

// Event handler function
function handleEvent(eventType, event) {
  if (currentState == STATE_INITIAL) {
    return handleEventStateInitial(eventType, event);
  } else if (currentState == STATE_IDLE) {
    return handleEventStateIdle(eventType, event);
  } else if (currentState == STATE_GET_JOB_ID) {
    return handleEventStateGetJobId(eventType, event);
  } else if (currentState == STATE_WAIT_JOB_RESULTS) {
    return handleEventStateWaitJobResults(eventType, event);
  } else {
    console.log("unexpected state", currentState)
  }
}

// Hide popover when clicking outside of popover.
$('body').on('click', function (e) {
    let logPopover = $('#logPopover');
    if (!logPopover.is(e.target) && logPopover.has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
        logPopover.popover('hide');
    }
});
