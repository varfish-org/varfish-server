function showVariantCarrierModal(obj, release, chromosome, start, reference, alternative) {
    const box = $(`#variantcarriermodal`).find('.variant-carrier-results');
    box.html(`<div class="text-center"><i class="iconify spin" data-icon="fa-solid:spinner"></i></div>`);
    $.ajax({
        type: 'GET',
        url: `${variant_carriers_url}?release=${release}&chromosome=${chromosome}&position=${start}` +
            `&reference=${reference}&alternative=${alternative}`,
        success: (response) => {
            // icon.removeClass('spin').attr('data-icon', 'fa-solid:cloud-upload');
            box.html(response);
        },
        error: (jqXHR, textStatus, errorThrown) => {
            alert("Error during AJAX call:", textStatus, + errorThrown);
        },
        timeout: 0
    });
}

function showSecondHitModal(tag, database, geneId, release, chromosome, start, reference, alternative, svUuid, hasSmallVars, hasSvs) {
    const smallVarsBox = $(`#secondhitmodal-small-vars`)
    smallVarsBox.html(`<div class="text-center"><i class="iconify spin" data-icon="fa-solid:spinner"></i></div>`)

    const svsBox = $(`#secondhitmodal-svs`)
    svsBox.html(`<div class="text-center"><i class="iconify spin" data-icon="fa-solid:spinner"></i></div>`)

    const caseUuid = $(tag).data("case")
    const secondHitUrlSmallVars = second_hit_url_small_vars
        .replace("--abcef--", caseUuid)
        .replace("$database", database)
        .replace("$gene_id", geneId)
    const secondHitUrlSvs = second_hit_url_svs
        .replace("--abcef--", caseUuid)
        .replace("$database", database)
        .replace("$gene_id", geneId)

    const smallVarLi = $("#secondhitmodal-small-var-li")
    const svLi = $("#secondhitmodal-sv-li")

    if (hasSmallVars && hasSvs) {
        smallVarLi.addClass("active")
        svLi.removeClass("active")
        smallVarLi.show()
        svLi.show()
    } else if (hasSmallVars) {
        smallVarLi.addClass("active")
        svLi.removeClass("active")
        smallVarLi.show()
        svLi.hide()
    } else {  // hasSvs
        smallVarLi.removeClass("active")
        svLi.addClass("active")
        smallVarLi.hide()
        svLi.show()
    }

    if (hasSmallVars) {
        let url = secondHitUrlSmallVars
        if (release) {
            url = `${url}?release=${release}&chromosome=${chromosome}&position=${start}` +
                `&reference=${reference}&alternative=${alternative}`
        }
        $.ajax({
            type: 'GET',
            url: url,
            success: (response) => {
                smallVarsBox.html(response);
            },
            error: (jqXHR, textStatus, errorThrown) => {
                alert("Error during AJAX call:", textStatus, +errorThrown);
            },
            timeout: 0
        });
    }

    if (hasSvs) {
        let url = secondHitUrlSvs
        if (svUuid) {
            url = `${url}?sv_uuid=${svUuid}`
        }
        $.ajax({
            type: 'GET',
            url: url,
            success: (response) => {
                svsBox.html(response);
            },
            error: (jqXHR, textStatus, errorThrown) => {
                alert("Error during AJAX call:", textStatus, +errorThrown);
            },
            timeout: 0
        });
    }
}
