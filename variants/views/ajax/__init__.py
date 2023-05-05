from rest_framework.authentication import SessionAuthentication

from variants.views.api import (
    AcmgCriteriaRatingCreateApiView,
    AcmgCriteriaRatingDeleteApiView,
    AcmgCriteriaRatingUpdateApiView,
    CaseRetrieveApiView,
    ExtraAnnoFieldsApiView,
    HpoTermsApiView,
    SmallVariantCommentDeleteApiView,
    SmallVariantCommentListCreateApiView,
    SmallVariantCommentUpdateApiView,
    SmallVariantDetailsApiView,
    SmallVariantFlagsDeleteApiView,
    SmallVariantFlagsListCreateApiView,
    SmallVariantFlagsUpdateApiView,
    SmallVariantQueryCreateApiView,
    SmallVariantQueryDownloadGenerateApiView,
    SmallVariantQueryDownloadServeApiView,
    SmallVariantQueryDownloadStatusApiView,
    SmallVariantQueryFetchExtendedResultsApiView,
    SmallVariantQueryFetchExtendedResultsCaddPhenoPrioritizationApiView,
    SmallVariantQueryFetchExtendedResultsCaddPrioritizationApiView,
    SmallVariantQueryFetchExtendedResultsPhenoPrioritizationApiView,
    SmallVariantQueryFetchResultsApiView,
    SmallVariantQueryHpoTermsApiView,
    SmallVariantQueryListApiView,
    SmallVariantQueryRetrieveApiView,
    SmallVariantQuerySettingsShortcutApiView,
    SmallVariantQueryStatusApiView,
    SmallVariantQueryUpdateApiView,
)


class CaseRetrieveAjaxView(CaseRetrieveApiView):
    """Retrieve detail of the specified case.

    **URL:** ``/variants/ajax/case/retrieve/{case.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryListAjaxView(SmallVariantQueryListApiView):
    """List small variant queries for the given Case.

    **URL:** ``/variants/ajax/query-case/list/{case.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryCreateAjaxView(SmallVariantQueryCreateApiView):
    """Create new small variant query for the given case.

    **URL:** ``/variants/ajax/query-case/create/{case.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryRetrieveAjaxView(SmallVariantQueryRetrieveApiView):
    """Retrieve small variant query details for the qiven query.

    **URL:** ``/variants/ajax/query-case/retrieve/{query.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryStatusAjaxView(SmallVariantQueryStatusApiView):
    """Returns the status of the small variant query.

    **URL:** ``/variants/ajax/query-case/status/{query.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryUpdateAjaxView(SmallVariantQueryUpdateApiView):
    """Update small variant query for the qiven query.

    **URL:** ``/variants/ajax/query-case/update/{query.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryFetchResultsAjaxView(SmallVariantQueryFetchResultsApiView):
    """Fetch results for small variant query.

    Will return an HTTP 503 if the results are not ready yet.

    **URL:** ``/variants/ajax/query-case/results/{query.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryFetchExtendedResultsAjaxView(SmallVariantQueryFetchExtendedResultsApiView):
    """Fetch extended results for small variant query.

    Will return an HTTP 503 if the results are not ready yet.

    **URL:** ``/variants/ajax/query-case/results-extended/{query.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryFetchExtendedResultsCaddPrioritizationAjaxView(
    SmallVariantQueryFetchExtendedResultsCaddPrioritizationApiView
):
    """Fetch extended results with CADD scoring for small variant query.

    Will return an HTTP 503 if the results are not ready yet.

    **URL:** ``/variants/ajax/query-case/results-extended-cadd/{query.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryFetchExtendedResultsPhenoPrioritizationAjaxView(
    SmallVariantQueryFetchExtendedResultsPhenoPrioritizationApiView
):
    """Fetch extended results with phenotype scoring for small variant query.

    Will return an HTTP 503 if the results are not ready yet.

    **URL:** ``/variants/ajax/query-case/results-extended-pheno/{query.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryFetchExtendedResultsCaddPhenoPrioritizationAjaxView(
    SmallVariantQueryFetchExtendedResultsCaddPhenoPrioritizationApiView
):
    """Fetch extended results with CADD and phenotype scoring for small variant query.

    Will return an HTTP 503 if the results are not ready yet.

    **URL:** ``/variants/ajax/query-case/results-extended-cadd-pheno/{query.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQuerySettingsShortcutAjaxView(SmallVariantQuerySettingsShortcutApiView):
    """Generate query settings for a given case by certain shortcuts.

    **URL:** ``/variants/ajax/query-case/query-settings-shortcut/{case.uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryHpoTermsAjaxView(SmallVariantQueryHpoTermsApiView):
    """Fetch HPO terms of a small variant query.

    **URL:** ``/variants/ajax/query-case/hpo-terms/{query.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryDownloadGenerateAjaxView(SmallVariantQueryDownloadGenerateApiView):
    """Start generating results for download of a small variant query.

    **URL:** ``/variants/ajax/query-case/download/generate/tsv/{query.sodar_uuid}``

    **URL:** ``/variants/ajax/query-case/download/generate/vcf/{query.sodar_uuid}``

    **URL:** ``/variants/ajax/query-case/download/generate/xlsx/{query.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryDownloadServeAjaxView(SmallVariantQueryDownloadServeApiView):
    """Serve download results of a small variant query.

    **URL:** ``/variants/ajax/query-case/download/serve/{exportfilebgjob.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryDownloadStatusAjaxView(SmallVariantQueryDownloadStatusApiView):
    """Get status of generating results for download of a small variant query.

    **URL:** ``/variants/ajax/query-case/download/status/{exportfilebgjob.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantDetailsAjaxView(SmallVariantDetailsApiView):
    """Fetch HPO terms of a small variant query.

    **URL:** ``/variants/ajax/small-variant-details/{case.sodar_uuid}/{case.release}-{small_var.chromosome}-{small_var.start}-{small_var.end}-{small_var.reference}-{small_var.alternative}/{query.database}/{small_var.gene_id}/

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantCommentListCreateAjaxView(SmallVariantCommentListCreateApiView):
    """Create small variant comment

    **URL:** ``/variants/ajax/small-variant-comment/list-create/{case.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantFlagsListCreateAjaxView(SmallVariantFlagsListCreateApiView):
    """Create small variant flags

    **URL:** ``/variants/ajax/small-variant-flags/list-create/{case.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantFlagsUpdateAjaxView(SmallVariantFlagsUpdateApiView):
    """Update small variant flags

    **URL:** ``/variants/ajax/small-variant-flags/update/{smallvariantflags.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantFlagsDeleteAjaxView(SmallVariantFlagsDeleteApiView):
    """Delete small variant flags

    **URL:** ``/variants/ajax/small-variant-flags/delete/{smallvariantflags.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantCommentUpdateAjaxView(SmallVariantCommentUpdateApiView):
    """Update small variant comment

    **URL:** ``/variants/ajax/small-variant-comment/update/{smallvariantcomment.sodar_uuid}/``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantCommentDeleteAjaxView(SmallVariantCommentDeleteApiView):
    """Delete small variant comment

    **URL:** ``/variants/ajax/small-variant-comment/delete/{smallvariantcomment.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class AcmgCriteriaRatingCreateAjaxView(AcmgCriteriaRatingCreateApiView):
    """Create ACMG criteria rating

    **URL:** ``/variants/ajax/acmg-criteria-rating/create/{case.sodar_uuid}/``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class AcmgCriteriaRatingUpdateAjaxView(AcmgCriteriaRatingUpdateApiView):
    """Update ACMG criteria rating

    **URL:** ``/variants/ajax/acmg-criteria-rating/update/{acmgcriteriarating.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class AcmgCriteriaRatingDeleteAjaxView(AcmgCriteriaRatingDeleteApiView):
    """Delete ACMG criteria rating

    **URL:** ``/variants/ajax/acmg-criteria-rating/delete/{acmgcriteriarating.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class ExtraAnnoFieldsAjaxView(ExtraAnnoFieldsApiView):
    """Delete ACMG criteria rating

    **URL:** ``/variants/ajax/acmg-criteria-rating/delete/{acmgcriteriarating.sodar_uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class HpoTermsAjaxView(HpoTermsApiView):
    """A view that queries HPO terms for a given string.

    **URL:** ``/variants/ajax/hpo-terms/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]
