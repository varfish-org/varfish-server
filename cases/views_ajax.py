from projectroles.models import Project
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from cases.views_api import (
    CaseCommentListCreateApiView,
    CaseCommentRetrieveUpdateDestroyApiView,
    CaseGeneAnnotationListApiView,
    CaseListApiView,
    CasePhenotypeTermsListCreateApiView,
    CasePhenotypeTermsRetrieveUpdateDestroyApiView,
    CaseUpdateApiView,
)
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning


class CaseListAjaxView(CaseListApiView):
    """Retrieve detail of the specified case.

    **URL:** ``/cases/ajax/case/list/{case.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class CaseUpdateAjaxView(CaseUpdateApiView):
    """Update details of the specified case.

    **URL:** ``/cases/ajax/case/update/{case.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class CasePhenotypeTermsListCreateAjaxView(CasePhenotypeTermsListCreateApiView):
    """Retrieve list of case phenotype terms for the given case.

    **URL:** ``/cases/ajax/case-phenotype-terms/list-create/{case.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class CasePhenotypeTermsRetrieveUpdateDestroyAjaxView(
    CasePhenotypeTermsRetrieveUpdateDestroyApiView
):
    """Retrieve list of case phenotype terms for the given case.

    **URL:** ``/cases/ajax/case-phenotype-terms/retrieve-update-destroy/{case_phenotype_terms.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class CaseCommentListCreateAjaxView(CaseCommentListCreateApiView):
    """Retrieve list of case comments for the given case.

    **URL:** ``/cases/ajax/case-comment/list-create/{case.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    authentication_classes = [SessionAuthentication]


class CaseCommentRetrieveUpdateDestroyAjaxView(CaseCommentRetrieveUpdateDestroyApiView):
    """Retrieve list of case comments for the given case.

    **URL:** ``/cases/ajax/case-comment/retrieve-update-destroy/{case_comment.sodar_uuid}/``

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


class ProjectUserPermissionsAjaxView(APIView):
    """Retrieve permissions of current user in project.

    **URL:** ``/cases/ajax/user-permissions/{project.sodar_uuid}/``

    **Methods:** ``GET``

    **Returns:** List of permissions that the user has in the project for the ``cases`` app.
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get(self, *args, **kwargs):
        project = Project.objects.get(sodar_uuid=self.kwargs["project"])
        all_perms = (
            "cases.view_data",
            "cases.add_case",
            "cases.update_case",
            "cases.sync_remote",
            "cases.delete_case",
        )
        result = [p for p in all_perms if self.request.user.has_perm(p, project)]
        return Response(result)
