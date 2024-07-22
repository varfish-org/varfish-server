import { SeqvarsQuerySettingsDetails as QuerySettingsDetails } from '@varfish-org/varfish-api/lib'

export type LocalFields<T> = Omit<
  {
    [K in keyof T]: T[K] extends object ? LocalFields<T[K]> : T[K]
  },
  'sodar_uuid' | 'date_created' | 'date_modified' | 'querysettings'
>

export type Query = LocalFields<
  Pick<
    QuerySettingsDetails,
    'genotype' | 'frequency' | 'phenotypeprio' | 'variantprio'
  >
> &
  Pick<
    QuerySettingsDetails,
    | 'predefinedquery'
    | 'genotypepresets'
    | 'frequencypresets'
    | 'phenotypepriopresets'
    | 'variantpriopresets'
  >
