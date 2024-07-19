import {
  SeqvarsQuerySettingsDetails as QuerySettingsDetails,
  SeqvarsQuerySettingsFrequency,
} from '@varfish-org/varfish-api/lib'

export type LocalFields<T> = Omit<
  {
    [K in keyof T]: T[K] extends object ? LocalFields<T[K]> : T[K]
  },
  'sodar_uuid' | 'date_created' | 'date_modified' | 'querysettings'
>

export type Query = {
  genotype: LocalFields<QuerySettingsDetails['genotype']>
  frequency: LocalFields<SeqvarsQuerySettingsFrequency>
} & Pick<
  QuerySettingsDetails,
  'predefinedquery' | 'frequencypresets' | 'genotypepresets'
>
