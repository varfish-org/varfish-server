import isEqual from 'fast-deep-equal/es6'
import { Component } from 'vue'

import { LocalFields, Query } from '@/seqvars/types'
import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

function isKeyOfObject<T extends object>(
  key: string | number | symbol,
  obj: T,
): key is keyof T {
  return key in obj
}

type PresetDetails = SeqvarsQueryPresetsSetVersionDetails

const getPresetSetKey = <S extends string>(id: S) =>
  `seqvarsquerypresets${id}_set` as const

type QueryKey = keyof Query & keyof SeqvarsPredefinedQuery

type CreateFromPreset<Id extends QueryKey, Preset> = (
  preset: Preset,
  fv: Query[`${Id}presets`],
) => LocalFields<Query[Id]>

type GetCompareFields<Id extends keyof Query, Preset> = (
  v: LocalFields<Query[Id]> & Preset,
) => unknown[]

export class FilterGroup<
  Id extends QueryKey,
  PresetSetKey extends ReturnType<typeof getPresetSetKey<Id>>,
  Preset extends PresetSetKey extends keyof PresetDetails
    ? PresetDetails[PresetSetKey][number]
    : LocalFields<Query[Id]>,
> {
  id: Id
  title: string
  createSettingsFromPreset?: CreateFromPreset<Id, Preset>
  getCompareFields: GetCompareFields<Id, Preset>
  Component: Component

  constructor(params: {
    id: Id
    title: string
    createFromPreset?: CreateFromPreset<Id, Preset>
    getCompareFields: GetCompareFields<Id, Preset>
    Component: Component
  }) {
    this.id = params.id
    this.title = params.title
    this.createSettingsFromPreset = params.createFromPreset
    this.getCompareFields = params.getCompareFields
    this.Component = params.Component
  }

  get queryPresetKey() {
    return `${this.id}presets` as const
  }

  get presetSetKey() {
    return `seqvarsquerypresets${this.id}_set` as const
  }

  getPreset(presetDetails: PresetDetails, pq: SeqvarsPredefinedQuery) {
    if (!isKeyOfObject(this.presetSetKey, presetDetails)) return
    return presetDetails[this.presetSetKey].find(
      (p) => isKeyOfObject(this.id, pq) && p.sodar_uuid === pq[this.id],
    )
  }

  matchesPreset(
    presetDetails: PresetDetails,
    pq: SeqvarsPredefinedQuery,
    query: Query,
  ): boolean {
    const preset = this.getPreset(presetDetails, pq)
    return isEqual(
      this.getCompareFields(query[this.id] as any),
      this.getCompareFields(
        (this.createSettingsFromPreset?.(preset as any, pq[this.id] as any) ??
          preset) as any,
      ),
    )
  }
}
