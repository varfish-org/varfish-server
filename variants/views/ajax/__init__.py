from rest_framework.authentication import SessionAuthentication

from variants.views.api import (
    AcmgCriteriaRatingDeleteApiView,
    AcmgCriteriaRatingListCreateApiView,
    AcmgCriteriaRatingUpdateApiView,
    CaseListQcStatsApiView,
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
    SmallVariantQueryDownloadGenerateApiView,
    SmallVariantQueryDownloadServeApiView,
    SmallVariantQueryDownloadStatusApiView,
    SmallVariantQueryHpoTermsApiView,
    SmallVariantQueryListApiView,
    SmallVariantQueryListCreateApiView,
    SmallVariantQueryResultRowRetrieveApiView,
    SmallVariantQueryResultRowListApiView,
    SmallVariantQueryResultSetListApiView,
    SmallVariantQueryResultSetRetrieveApiView,
    SmallVariantQueryRetrieveUpdateDestroyApiView,
    SmallVariantQuerySettingsShortcutApiView,
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


class SmallVariantQueryListCreateAjaxView(SmallVariantQueryListCreateApiView):
    """Create or list small variant query.

    **URL:** ``/variants/ajax/query/list-create/{case.uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryRetrieveUpdateDestroyAjaxView(SmallVariantQueryRetrieveUpdateDestroyApiView):
    """Retrieve, update or destroy small variant query.

    **URL:** ``/variants/ajax/query/retrieve-update-destroy/{smallvariantquery.uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryResultSetListAjaxView(SmallVariantQueryResultSetListApiView):
    """Create or list small variant query

    **URL:** ``/variants/ajax/query-result-set/list/{smallvariantqueryresultset.uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryResultSetRetrieveAjaxView(SmallVariantQueryResultSetRetrieveApiView):
    """Create or list small variant query

    **URL:** ``/variants/ajax/query-result-set/retrieve/{smallvariantqueryresultset.uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryResultRowListAjaxView(SmallVariantQueryResultRowListApiView):
    """Create or list small variant query

    **URL:** ``/variants/ajax/query-result-row/list/{smallvariantqueryresultset.uuid}``

    **Methods:** See base API class.

    **Parameters:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class SmallVariantQueryResultRowRetrieveAjaxView(SmallVariantQueryResultRowRetrieveApiView):
    """Create or list small variant query

    **URL:** ``/variants/ajax/query-result-row/retrieve/{smallvariantqueryresultrow.uuid}``

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


class AcmgCriteriaRatingListCreateAjaxView(AcmgCriteriaRatingListCreateApiView):
    """Create ACMG criteria rating

    **URL:** ``/variants/ajax/acmg-criteria-rating/list-create/{case.sodar_uuid}/``

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
    """A view that lists HPO terms based on a query string.
    Also includes OMIM, ORPHAN and DECIPHER terms.

    **URL:** ``/variants/ajax/hpo-terms/?query={string}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class CaseListQcStatsAjaxView(CaseListQcStatsApiView):
    """A view that lists HPO terms based on a query string.
    Also includes OMIM, ORPHAN and DECIPHER terms.

    **URL:** ``/variants/ajax/hpo-terms/?query={string}/``

    **Methods:** ``GET``

    **Returns:** List of HPO terms that were found for that term, HPO id and name.
    """

    authentication_classes = [SessionAuthentication]
