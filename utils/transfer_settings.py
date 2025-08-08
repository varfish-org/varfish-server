import uuid
from variants.models.presets import QuickPresets, ChromosomePresets, FlagsEtcPresets, FrequencyPresets, ImpactPresets, PresetSet, QualityPresets
from projectroles.models import Project
from django.db import transaction

src = 'Test Project'
dst = 'Test Project Copy'

src_project = Project.objects.get(title=src)
dst_project = Project.objects.get(title=dst)

mapping_presetset = {}
mapping_presets = {
    ChromosomePresets: {},
    QualityPresets: {},
    ImpactPresets: {},
    FrequencyPresets: {},
    FlagsEtcPresets: {},
}

dry_run = False

if dry_run:
    print('DRY RUN, not committing changes')

with transaction.atomic():
    # Clean destination preset sets before copying
    print("Deleting presetsets and preset in destination")
    dst_project.presetset_set.all().delete()
    for presetset in list(src_project.presetset_set.all()):
        old_uuid = presetset.sodar_uuid
        presetset.pk = None
        presetset.sodar_uuid = uuid.uuid4()
        presetset.project = dst_project
        presetset.save()
        mapping_presetset[old_uuid] = presetset.sodar_uuid
        print(f'Copied presetset "{presetset.label}" from {src} to {dst}')
    
    for presetset_uuid in mapping_presetset.keys():
        presetset = PresetSet.objects.get(sodar_uuid=presetset_uuid)
        for preset_model in mapping_presets.keys():
            for preset in list(preset_model.objects.filter(presetset=presetset)):
                old_uuid = preset.sodar_uuid
                preset.pk = None
                preset.sodar_uuid = uuid.uuid4()
                preset.presetset = PresetSet.objects.get(sodar_uuid=mapping_presetset[preset.presetset.sodar_uuid])
                preset.save()
                mapping_presets[preset_model][old_uuid] = preset.sodar_uuid
                print(f'Copied {preset_model.__name__} "{preset.label}"')
        for preset in QuickPresets.objects.filter(presetset=presetset):
            preset.pk = None
            preset.sodar_uuid = uuid.uuid4()
            preset.presetset = PresetSet.objects.get(sodar_uuid=mapping_presetset[preset.presetset.sodar_uuid])
            for subpreset in mapping_presets.keys():
                link = subpreset.__name__.replace('Presets', '').lower()
                setattr(preset, link, subpreset.objects.get(sodar_uuid=mapping_presets[subpreset][getattr(preset, link).sodar_uuid]))
            preset.save()
            print(f'Copied quick preset "{preset.label}"')
    
    if dry_run:
        raise Exception('DRY RUN, rolling back')
    
    print('Committing changes')