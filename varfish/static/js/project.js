/**
 * Included in sodar-core templates.
 *
 * Code for
 *
 * - warning about browser compatibility
 * - django-su indication of having assumed other user's identity
 */

/** Add MSIE note. */
function addMsieNote() {
  if (
    navigator.appName === "Microsoft Internet Explorer" ||
    !!(
      navigator.userAgent.match(/Trident/) || navigator.userAgent.match(/rv:11/)
    ) ||
    (typeof $.browser !== "undefined" && $.browser.msie === 1)
  ) {
    let parentElem = $("div.sodar-app-container");

    if (!parentElem.length) {
      parentElem = $("div.sodar-content-container")
        .find("div.container-fluid")
        .first();
    }

    if (!$("div.sodar-alert-container").length) {
      parentElem.prepend(
        '<div class="container-fluid sodar-alert-container"></div>'
      );
    }
    $("div.sodar-alert-container").prepend(
      '<div class="alert alert-danger sodar-alert-top">' +
        '<i class="iconify" data-icon="bi:exclamation-circle"></i> ' +
        "VarFish doesn't support Microsoft Internet Explorer. We recommend using " +
        '<a href="https://www.mozilla.org/firefox/new" target="_blank">Mozilla Firefox</a> or ' +
        '<a href="https://www.google.com/chrome" target="_blank">Google Chrome</a>.' +
        "</div>"
    );
  }
}

/* Display the django_su warning when switching a user */
function addDjangoSuNote() {
  if (is_su) {
    let parentElem = $("div.sodar-app-container");

    if (!parentElem.length) {
      parentElem = $("div.sodar-content-container")
        .find("div.container-fluid")
        .first();
    }

    if (!$("div.sodar-alert-container").length) {
      parentElem.prepend(
        '<div class="container-fluid sodar-alert-container"></div>'
      );
    }

    $("div.sodar-alert-container").prepend(
      '<div class="alert alert-danger sodar-alert-top">' +
        '<i class="iconify" data-icon="bi:exclamation-circle"></i> ' +
        'You have assumed the identity of another account! <a href="' +
        su_escape_url +
        '">Escape</a>' +
        "</div>"
    );
  }
}

/* Execute after document has been loaded completely. */
$(document).ready(function () {
  addMsieNote();
  addDjangoSuNote();
});
