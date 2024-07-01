from projectroles.models import Project
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from cohorts.views_api import (
    AccessibleProjectsCasesApiView,
    CohortCaseCreateApiView,
    CohortCaseDestroyApiView,
    CohortCaseListApiView,
    CohortListCreateApiView,
    CohortRetrieveUpdateDestroyApiView,
)
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning


class CohortListCreateAjaxView(CohortListCreateApiView):
    """List cohorts of a project or create a cohort in the project.

    **URL:** ``/cohorts/ajax/cohort/list-create/{project.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    schema = None
    authentication_classes = [SessionAuthentication]


class CohortRetrieveUpdateDestroyAjaxView(CohortRetrieveUpdateDestroyApiView):
    """Retrieve, update or destroy a given cohort.

    **URL:** ``/cohorts/ajax/cohort/retrieve-update-destroy/{cohort.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    schema = None
    authentication_classes = [SessionAuthentication]


class CohortCaseCreateAjaxView(CohortCaseCreateApiView):
    """Create cohortcase in the current project.

    **URL:** ``/cohorts/ajax/cohortcase/create/{project.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    schema = None
    authentication_classes = [SessionAuthentication]


class CohortCaseListAjaxView(CohortCaseListApiView):
    """List all cohortcase for a given cohort.

    **URL:** ``/cohorts/ajax/cohortcase/list/{cohort.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    schema = None
    authentication_classes = [SessionAuthentication]


class CohortCaseDestroyAjaxView(CohortCaseDestroyApiView):
    """Destroy a given cohortcase.

    **URL:** ``/cohorts/ajax/cohortcase/destroy/{cohortcase.sodar_uuid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    schema = None
    authentication_classes = [SessionAuthentication]


class AccessibleProjectsCasesAjaxView(AccessibleProjectsCasesApiView):
    """List all accessible projects including cases for a user.

    **URL:** ``/cohorts/ajax/accessible-projects-cases/list/{project.sodar_uid}/``

    **Methods:** See base API class.

    **Returns:** See base API class.
    """

    schema = None
    authentication_classes = [SessionAuthentication]


class ProjectUserPermissionsAjaxView(APIView):
    """Retrieve permissions of current user in project.

    **URL:** ``/cohorts/ajax/user-permissions/{project.sodar_uuid}/``

    **Methods:** ``GET``

    **Returns:** List of permissions that the user has in the project for the ``cohorts`` app.
    """

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning

    def get(self, *args, **kwargs):
        project = Project.objects.get(sodar_uuid=self.kwargs["project"])
        all_perms = ("cohorts.view_data",)
        result = [p for p in all_perms if self.request.user.has_perm(p, project)]
        return Response(result)
