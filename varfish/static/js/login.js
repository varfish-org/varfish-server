/* Autofill domain in login username ---------------------------------------- */

$(document).ready(function() {
     $('#sodar-login-username').keyup(function(event) {
        var maxLength = 255;
        v = $(this).val();

        // Fill domain
        if (event.keyCode !== 8 && v.length > 3 &&
            v.indexOf('@') > 0 && v.indexOf('@') < v.length - 1) {
            var domainName = null;

            if (v.charAt(v.indexOf('@') + 1).toUpperCase() === 'C') {
                $(this).removeClass('text-danger');
                $('#sodar-login-submit').removeClass('disabled');
                domainName = 'CHARITE';
            }

            else if (v.charAt(v.indexOf('@') + 1).toUpperCase() === 'M') {
                $(this).removeClass('text-danger');
                $('#sodar-login-submit').removeClass('disabled');
                domainName = 'MDC-BERLIN';
            }

            // Gently inform the user of an invalid domain :)
            else {
                $(this).addClass('text-danger');
                $('#sodar-login-submit').addClass('disabled');
            }

            if (domainName !== null) {
                $(this).val(v.substring(0, v.indexOf('@') + 1) + domainName);
                $(this).attr('maxlength', $(this).val().length);
            }
         }

        // Erase domain if backspace is pressed
        else if (event.keyCode === 8 && v.indexOf('@') > 0) {
            $(this).val(v.substring(0, v.indexOf('@') + 1));
            $(this).addClass('text-danger');
            $('#sodar-login-submit').addClass('disabled');
            $(this).attr('maxlength', maxLength);
        }

        // Don't allow login if there is an empty domain
        if (v.indexOf('@') === v.length - 1) {
            $(this).addClass('text-danger');
            $('#sodar-login-submit').addClass('disabled');
        }

        // User without domain is OK (only for local admin/test users)
        else if (v.indexOf('@') === -1) {
            $(this).removeClass('text-danger');
            $('#sodar-login-submit').removeClass('disabled');
            $(this).attr('maxlength', maxLength);
        }
     });
 });
