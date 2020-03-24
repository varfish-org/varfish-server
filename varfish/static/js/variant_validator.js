function queryVariantValidatorApi(obj, release, chromosome, start, reference, alternative) {
    let button = $(obj);
    let icon = button.find("i");
    button.attr('disabled', true);
    icon.removeClass('fa-cloud-upload').addClass('fa-refresh fa-spin');
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
            icon.removeClass('fa-refresh fa-spin').addClass('fa-cloud-upload');
            button.closest('.modal-content').find('.variant-validator-results').html(response);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert("Error during AJAX call:", textStatus, + errorThrown);
            console.log("Error during AJAX call: ", jqXHR, textStatus, errorThrown);
        }
    });
}
