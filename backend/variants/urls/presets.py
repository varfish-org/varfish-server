"""Presets-related urls."""

from django.conf.urls import url

import variants.views.ajax.presets as views_ajax

presets_ajax_urlpatterns = [
    ###################################
    ### "Regular" PresetSet members ###
    ###################################
    # FrequencyPresets
    url(
        regex=r"^ajax/frequencypresets/list-create/(?P<presetset>[0-9a-f-]+)/?$",
        view=views_ajax.FrequencyPresetsListCreateAjaxView.as_view(),
        name="ajax-frequencypresets-listcreate",
    ),
    url(
        regex=r"^ajax/frequencypresets/retrieve-update-destroy/(?P<frequencypresets>[0-9a-f-]+)/?$",
        view=views_ajax.FrequencyPresetsRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-frequencypresets-retrieveupdatedestroy",
    ),
    url(
        regex=r"^ajax/frequencypresets/clone-factory-presets/(?P<name>[a-zA-Z_-]+)/?$",
        view=views_ajax.FrequencyPresetsCloneFactoryPresetsAjaxView.as_view(),
        name="ajax-frequencypresets-clonefactorypresets",
    ),
    url(
        regex=r"ajax/frequencypresets/clone-other/(?P<frequencypresets>[0-9a-f-]+)/?$",
        view=views_ajax.FrequencyPresetsCloneOtherAjaxView.as_view(),
        name="ajax-frequencypresets-cloneother",
    ),
    # FlagsEtcPresets
    url(
        regex=r"^ajax/flagsetcpresets/list-create/(?P<presetset>[0-9a-f-]+)/?$",
        view=views_ajax.FlagsEtcPresetsListCreateAjaxView.as_view(),
        name="ajax-flagsetcpresets-listcreate",
    ),
    url(
        regex=r"^ajax/flagsetcpresets/retrieve-update-destroy/(?P<flagsetcpresets>[0-9a-f-]+)/?$",
        view=views_ajax.FlagsEtcPresetsRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-flagsetcpresets-retrieveupdatedestroy",
    ),
    url(
        regex=r"^ajax/flagsetcpresets/clone-factory-presets/(?P<name>[a-zA-Z_-]+)/?$",
        view=views_ajax.FlagsEtcPresetsCloneFactoryPresetsAjaxView.as_view(),
        name="ajax-flagsetcpresets-clonefactorypresets",
    ),
    url(
        regex=r"ajax/flagsetcpresets/clone-other/(?P<flagsetcpresets>[0-9a-f-]+)/?$",
        view=views_ajax.FlagsEtcPresetsCloneOtherAjaxView.as_view(),
        name="ajax-flagsetcpresets-cloneother",
    ),
    # ImpactPresets
    url(
        regex=r"^ajax/impactpresets/list-create/(?P<presetset>[0-9a-f-]+)/?$",
        view=views_ajax.ImpactPresetsListCreateAjaxView.as_view(),
        name="ajax-impactpresets-listcreate",
    ),
    url(
        regex=r"^ajax/impactpresets/retrieve-update-destroy/(?P<impactpresets>[0-9a-f-]+)/?$",
        view=views_ajax.ImpactPresetsRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-impactpresets-retrieveupdatedestroy",
    ),
    url(
        regex=r"^ajax/impactpresets/clone-factory-presets/(?P<name>[a-zA-Z_-]+)/?$",
        view=views_ajax.ImpactPresetsCloneFactoryPresetsAjaxView.as_view(),
        name="ajax-impactpresets-clonefactorypresets",
    ),
    url(
        regex=r"ajax/impactpresets/clone-other/(?P<impactpresets>[0-9a-f-]+)/?$",
        view=views_ajax.ImpactPresetsCloneOtherAjaxView.as_view(),
        name="ajax-impactpresets-cloneother",
    ),
    # QualityPresets
    url(
        regex=r"^ajax/qualitypresets/list-create/(?P<presetset>[0-9a-f-]+)/?$",
        view=views_ajax.QualityPresetsListCreateAjaxView.as_view(),
        name="ajax-qualitypresets-listcreate",
    ),
    url(
        regex=r"^ajax/qualitypresets/retrieve-update-destroy/(?P<qualitypresets>[0-9a-f-]+)/?$",
        view=views_ajax.QualityPresetsRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-qualitypresets-retrieveupdatedestroy",
    ),
    url(
        regex=r"^ajax/qualitypresets/clone-factory-presets/(?P<name>[a-zA-Z_-]+)/?$",
        view=views_ajax.QualityPresetsCloneFactoryPresetsAjaxView.as_view(),
        name="ajax-qualitypresets-clonefactorypresets",
    ),
    url(
        regex=r"ajax/qualitypresets/clone-other/(?P<qualitypresets>[0-9a-f-]+)/?$",
        view=views_ajax.QualityPresetsCloneOtherAjaxView.as_view(),
        name="ajax-qualitypresets-cloneother",
    ),
    # ChromosomePresets
    url(
        regex=r"^ajax/chromosomepresets/list-create/(?P<presetset>[0-9a-f-]+)/?$",
        view=views_ajax.ChromosomePresetsListCreateAjaxView.as_view(),
        name="ajax-chromosomepresets-listcreate",
    ),
    url(
        regex=r"^ajax/chromosomepresets/retrieve-update-destroy/(?P<chromosomepresets>[0-9a-f-]+)/?$",
        view=views_ajax.ChromosomePresetsRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-chromosomepresets-retrieveupdatedestroy",
    ),
    url(
        regex=r"^ajax/chromosomepresets/clone-factory-presets/(?P<name>[a-zA-Z_-]+)/?$",
        view=views_ajax.ChromosomePresetsCloneFactoryPresetsAjaxView.as_view(),
        name="ajax-chromosomepresets-clonefactorypresets",
    ),
    url(
        regex=r"ajax/chromosomepresets/clone-other/(?P<chromosomepresets>[0-9a-f-]+)/?$",
        view=views_ajax.ChromosomePresetsCloneOtherAjaxView.as_view(),
        name="ajax-chromosomepresets-cloneother",
    ),
    #############################################
    ### Quick Presets (only clone from other) ###
    #############################################
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
    #################
    ### PresetSet ###
    #################
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
    url(
        regex=r"^ajax/project-default-presetset/retrieve/(?P<project>[a-zA-Z0-9\._-]+)/?$",
        view=views_ajax.ProjectDefaultPresetSetRetrieveAjaxView.as_view(),
        name="ajax-project-default-presetset-retrieve",
    ),
]