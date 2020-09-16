$(document).ready(function() {
  const panelsList = $("#genomics-england-panels");
  const panelArea = $("#id_gene_whitelist");
  let panels = [];

  function showPanels() {
    panelsList.empty();
    for (let i = 0; i < panels.length; ++i) {
      panelsList.append(
        $(
          "<a class=\"dropdown-item panel-entry\" href=\"#\" data-panel-id=\"" + panels[i].id + "\" data-panel-version=\"" + panels[i].version + "\">\n" +
          "  " + panels[i].name + " (v" + panels[i].version + ")" +
          "</a>"
        )
      )
    }

    panelsList.children(".panel-entry").click(function() {
      const panelId = $(this).data("panel-id");
      const panelVersion = $(this).data("panel-version");
      const minConfidence = parseInt($("#genomics-england-confidence").val());
      console.log("minConfidence", minConfidence);

      let ajaxCall = $.ajax({
        type: "GET",
        dataType: "json",
        url: "/proxy/panelapp/v1/panels/" + panelId + "/?version=" + panelVersion,
        success: function (result) {
          console.log("RESULT", result)
          let symbols = [];

          for (let i = 0; i < result.genes.length; ++i) {
            const gene = result.genes[i];
            const confidence = parseInt(gene.confidence_level);
            if (confidence >= minConfidence) {
              symbols.push(gene.gene_data.gene_symbol);
            }
          }
          console.log("SYMBOLS", symbols);

          if (panelArea.val()) {
            panelArea.val(panelArea.val() + " " + symbols.join(" "));
          } else {
            panelArea.val(symbols.join(" "));
          }
        },
        error: function (jqXHR, textStatus, errorThrown) {
          console.log("Problem loading panel", textStatus, errorThrown);
          alert("Problem loading panel: " + textStatus);
        }
      })
    })
  }

  function loadPanelPage(page) {
    let ajaxCall = $.ajax({
        type: "GET",
        dataType: "json",
        url: "/proxy/panelapp/v1/panels/?page=" + page,
        success: function (result) {
          panels = panels.concat(result["results"]);
          if (result["next"]) {
            loadPanelPage(page + 1);
          } else {
            showPanels();
          }
        },
        error: function(jqXHR, textStatus, errorThrown) {
          console.log("FAILED", jqXHR, textStatus, errorThrown);
          panelsList.html($(
            "<a class=\"dropdown-item disabled\" href=\"#\">\n" +
            "<i class=\"fa fa-times fa-fw\"></i> Loading Panels failed!</a>"
          ))
        }
      });
  }

  if ($("#panel-app-is-testing").length === 0) {  // unless testing
    loadPanelPage(1);
  }
  else {
    console.log("In testing mode, not loading panel app page ...")
  }
})
