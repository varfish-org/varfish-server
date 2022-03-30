function queryVariantValidatorApi(obj, release, chromosome, start, reference, alternative) {
    let button = $(obj);
    let icon = button.find("img");
    let box = button.closest('.modal-content').find('.variant-validator-results');
    button.attr('disabled', true);
    icon.attr('src', '/icons/mdi/refresh.svg').addClass('spin');
    box.html('<div class="text-center"><i class="iconify spin" data-icon="fa-solid:spinner"></i></div>');
    $.ajax({
        type: 'POST',
        url: variant_validator_url,
        data: {
            "release": release,
            "chromosome": chromosome,
            "position": start,
            "reference": reference,
            "alternative": alternative,
        },
        success: function (response) {
            button.attr('disabled', false);
            icon.removeClass('spin').attr('data-icon', 'fa-solid:cloud-upload');
            box.html(response);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert("Error during AJAX call:", textStatus, + errorThrown);
            console.log("Error during AJAX call: ", jqXHR, textStatus, errorThrown);
        },
        timeout: 0
    });
}
