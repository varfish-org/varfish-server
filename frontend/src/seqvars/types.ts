import { SeqvarsQuerySettingsDetails } from '@varfish-org/varfish-api/lib'

export type LocalFields<T> = Omit<
  { [K in keyof T]: T[K] extends object ? LocalFields<T[K]> : T[K] },
  | 'sodar_uuid'
  | 'date_created'
  | 'date_modified'
  | 'querysettings'
  | 'session'
  | 'presetssetversion'
>

export type Query = LocalFields<SeqvarsQuerySettingsDetails> & { label: string }
