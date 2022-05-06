function showVariantCarrierModal(obj, release, chromosome, start, reference, alternative) {
    const box = $(`#variantcarriermodal-${release}-${chromosome}-${start}-${reference}-${alternative}`).find('.variant-carrier-results');
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
