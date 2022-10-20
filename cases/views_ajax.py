from rest_framework.authentication import SessionAuthentication

from cases.views_api import CaseCommentListApiView, CaseGeneAnnotationListApiView, CaseListApiView


class CaseListAjaxView(CaseListApiView):
    """Retrieve detail of the specified case.

    **URL:** ``/cases/ajax/case/list/{case.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class CaseCommentListAjaxView(CaseCommentListApiView):
    """Retrieve list of case comments for the given case.

    **URL:** ``/cases/ajax/case-comment/list/{case.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class CaseGeneAnnotationListAjaxView(CaseGeneAnnotationListApiView):
    """Retrieve list of case gene annotations for the given case.

    **URL:** ``/cases/ajax/case-gene-annotation/list/{case.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]
