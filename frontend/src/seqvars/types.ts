import {
  SeqvarsQuerySettingsDetails as QuerySettingsDetails,
  SeqvarsGenotypePresetChoice,
  SeqvarsQuerySettingsFrequency,
} from '@varfish-org/varfish-api/lib'

export type LocalFields<T> = Omit<
  T,
  'sodar_uuid' | 'date_created' | 'date_modified' | 'querysettings'
>

export type Query = {
  // genotype: LocalFields<QuerySettingsDetails['genotype']>
  // genotypepresets?: { choice?: SeqvarsGenotypePresetChoice | null }
  frequency: LocalFields<SeqvarsQuerySettingsFrequency>
} & Pick<QuerySettingsDetails, 'predefinedquery' | 'frequencypresets'>
