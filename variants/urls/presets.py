"""Presets-related urls."""
from itertools import chain

from django.conf.urls import url

import variants.views.ajax.presets as views_ajax

_entity_names = [
    "FrequencyPresets",
    "FlagsEtcPresets",
    "ImpactPresets",
    "QualityPresets",
    "ChromosomePresets",
]


def _create_urlpatterns(name):
    lower = name.lower()
    return [
        url(
            regex=rf"ajax/{lower}/list-create/(?P<presetset>[0-9a-f-]+)/?",
            view=getattr(views_ajax, f"{name}ListCreateAjaxView").as_view(),
            name=f"ajax-{lower}-listcreate",
        ),
        url(
            regex=rf"ajax/{lower}/retrieve-update-destroy/(?P<{lower}>[0-9a-f-]+)/?",
            view=getattr(views_ajax, f"{name}RetrieveUpdateDestroyAjaxView").as_view(),
            name=f"ajax-{lower}-retrieveupdatedestroy",
        ),
        url(
            regex=rf"ajax/{lower}/clone-factory-presets/(?P<name>[a-zA-Z_-]+)/?",
            view=getattr(views_ajax, f"{name}CloneFactoryPresetsAjaxView").as_view(),
            name=f"ajax-{lower}-clonefactorypresets",
        ),
        url(
            regex=rf"ajax/{lower}/clone-other/(?P<{lower}>[0-9a-f-]+)/?",
            view=getattr(views_ajax, f"{name}CloneOtherAjaxView").as_view(),
            name=f"ajax-{lower}-cloneother",
        ),
    ]


_presets_ajax_urlpatterns = [
    # "Regular" PresetSet members
    list(map(_create_urlpatterns, _entity_names))
    + [
        [
            # Quick Presets (only clone from other)
            url(
                regex=r"^ajax/quickpresets/list-create/(?P<presetset>[0-9a-f-]+)/?$",
                view=views_ajax.QuickPresetsListCreateAjaxView.as_view(),
                name="ajax-quickpresets-listcreate",
            ),
            url(
                regex=r"^ajax/quickpresets/retrieve-update-destroy/(?P<quickpresets>[0-9a-f-]+)/?$",
                view=views_ajax.QuickPresetsRetrieveUpdateDestroyAjaxView.as_view(),
                name="ajax-quickpresets-retrieveupdatedestroy",
            ),
            url(
                regex=r"^ajax/quickpresets/clone-other/(?P<quickpresets>[0-9a-f-]+)/?$",
                view=views_ajax.QuickPresetsCloneOtherAjaxView.as_view(),
                name="ajax-quickpresets-cloneother",
            ),
            # PresetSet
            url(
                regex=r"^ajax/presetset/list/?$",
                view=views_ajax.PresetSetListAllAjaxView.as_view(),
                name="ajax-presetset-listall",
            ),
            url(
                regex=r"^ajax/presetset/list-create/(?P<project>[0-9a-f-]+)/?$",
                view=views_ajax.PresetSetListCreateAjaxView.as_view(),
                name="ajax-presetset-listcreate",
            ),
            url(
                regex=r"^ajax/presetset/retrieve-update-destroy/(?P<presetset>[0-9a-f-]+)/?$",
                view=views_ajax.PresetSetRetrieveUpdateDestroyAjaxView.as_view(),
                name="ajax-presetset-retrieveupdatedestroy",
            ),
            url(
                regex=r"^ajax/presetset/clone-factory-presets/?$",
                view=views_ajax.PresetSetCloneFactoryPresetsAjaxView.as_view(),
                name="ajax-presetset-clonefactorypresets",
            ),
            url(
                regex=r"^ajax/presetset/clone-other/(?P<presetset>[0-9a-f-]+)/?$",
                view=views_ajax.PresetSetCloneOtherAjaxView.as_view(),
                name="ajax-presetset-cloneother",
            ),
        ]
    ]
]

presets_ajax_urlpatterns = list(chain(*chain(*_presets_ajax_urlpatterns)))
