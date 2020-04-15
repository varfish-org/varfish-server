function handleEmptyMessage(id) {
    if ($("#" + id).find(".list-item").length) {
        $("#" + id + "-empty").hide();
    }
    else {
        $("#" + id + "-empty").show();
    }
}

function commentDeleteToggle() {
    var list_element = $(this).closest(".list-item");
    var list = $(this).closest(".list");
    var uuid = list_element.data("sodar-uuid");
    $("#delete-comment-" + uuid).toggle();
    $("#display-comment-" + uuid).toggle();
    list.animate({scrollTop: list[0].scrollHeight}, 'slow');
}

function commentEditToggle() {
    var list_element = $(this).closest(".list-item");
    var list = $(this).closest(".list");
    var uuid = list_element.data("sodar-uuid");
    $("#edit-comment-" + uuid).toggle();
    $("#display-comment-" + uuid).toggle();
    $("#text-comment-" + uuid).val(list_element.find("em").text());
    list.animate({scrollTop: list[0].scrollHeight}, 'slow');
}

function commentDeleteSubmit() {
    var list_element = $(this).closest(".list-item");
    var list = $(this).closest(".list");
    $.ajax({
        type: "POST",
        url: list.data("url-delete"),
        data: {sodar_uuid: list_element.data("sodar-uuid")},
        dataType: "json",
        success: function (data) {
            list_element.remove();
            handleEmptyMessage(list.attr("id"));
            updateCaseCommentsCount();
        },
        error: function (jqXHR, textStatus, errorThrown) {
            let msg = "Error during AJAX call: " + textStatus + " " + errorThrown;
            if (jqXHR.status === 500 && "result") {
                msg += " " + jqXHR.responseJSON["result"]
            }
            alert(msg);
            console.log("Error during AJAX call: ", textStatus, errorThrown);
        }
    });
}

function commentEditSubmit() {
    var list_element = $(this).closest(".list-item");
    var list = $(this).closest(".list");
    var comment_uuid = list_element.data("sodar-uuid");
    $.ajax({
        type: "POST",
        url: list.data("url-submit"),
        data: $(this).closest("form").serialize() + "&sodar_uuid=" + comment_uuid,
        dataType: "json",
        success: function (data) {
            list_element.find("em").html(data["comment"]);
            $("#edit-comment-" + comment_uuid).toggle();
            $("#display-comment-" + comment_uuid).toggle();
            list.animate({scrollTop: list[0].scrollHeight}, 'slow');
            updateCaseCommentsCount();
        },
        error: function (jqXHR, textStatus, errorThrown) {
            let msg = "Error during AJAX call: " + textStatus + " " + errorThrown;
            if (jqXHR.status === 500 && "result") {
                msg += " " + jqXHR.responseJSON["result"]
            }
            alert(msg);
            console.log(msg);
        }
    });
}

function commentSubmit() {
    var textbox = $(this).closest("form").find("textarea");
    var list = $(this).closest(".comment-group").find(".list");
    if (textbox.val() !== "") {
        $.ajax({
            type: "POST",
            url: list.data("url-submit"),
            data: $(this).closest("form").serialize(),
            dataType: "json",
            success: function (data) {
                list.append(`<li class="list-group-item list-item" data-sodar-uuid="${data["sodar_uuid"]}">
  <div id="display-comment-${data["sodar_uuid"]}">
    <span class="small text-muted">
      <strong>${data["user"]}</strong>
      ${data["date_created"]}:
    </span>
    <em>${data["comment"]}</em>
    <a href="#" class="pl-2 text-secondary comment-button-edit"><i class="fa fa-pencil"></i></a>
    <a href="#" class="pl-2 text-secondary comment-button-delete"><i class="fa fa-times-circle"></i></a>
  </div>
  <div id="edit-comment-${data["sodar_uuid"]}" style="display: none;">
    <form>
      <textarea id="text-comment-${data["sodar_uuid"]}" name="comment" rows="1" cols="40" class="form-control"></textarea>
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
  <div id="delete-comment-${data["sodar_uuid"]}" style="display: none;">
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
</li>`);
                list.animate({scrollTop: list[0].scrollHeight}, 'slow');
                textbox.val("");
                $('*[data-sodar-uuid="' + data["sodar_uuid"] + '"').find(".comment-button-delete").on("click", commentDeleteToggle);
                $('*[data-sodar-uuid="' + data["sodar_uuid"] + '"').find(".comment-button-delete-cancel").on("click", commentDeleteToggle);
                $('*[data-sodar-uuid="' + data["sodar_uuid"] + '"').find(".comment-button-delete-submit").on("click", commentDeleteSubmit);
                $('*[data-sodar-uuid="' + data["sodar_uuid"] + '"').find(".comment-button-edit").on("click", commentEditToggle);
                $('*[data-sodar-uuid="' + data["sodar_uuid"] + '"').find(".comment-button-edit-cancel").on("click", commentEditToggle);
                $('*[data-sodar-uuid="' + data["sodar_uuid"] + '"').find(".comment-button-edit-submit").on("click", commentEditSubmit);
                handleEmptyMessage(list.attr("id"))
                updateCaseCommentsCount();
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert("Error during AJAX call: " + textStatus + " " + errorThrown);
                console.log("Error during AJAX call: ", textStatus, errorThrown);
            }
        });
    }
}


function updateCaseCommentsCount() {
    var counter = $("#case-comments-count");
    $.ajax({
        url: counter.data("url"),
        success: function (data) {
            counter.text(data["count"]);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            let msg = "Error during AJAX call: " + textStatus + " " + errorThrown;
            if (jqXHR.status === 500 && "result") {
                msg += " " + jqXHR.responseJSON["result"]
            }
            alert(msg);
            console.log(msg);
        }
    });
}
