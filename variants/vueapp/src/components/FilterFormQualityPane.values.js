import {
  between,
  decimal,
  integer,
  minValue,
  required,
} from '@vuelidate/validators'

export const numericKeys = Object.freeze([
  'qualMinDpHet',
  'qualMinDpHom',
  'qualMinAb',
  'qualMinGq',
  'qualMinAd',
  'qualMaxAd',
])

export const allKeys = Object.freeze(numericKeys.concat(['qualFail']))

export const failValues = Object.freeze({
  'drop-variant': 'drop variant',
  ignore: 'ignore',
  'no-call': 'no call',
})

const mustBeFailValue = (value) =>
  !value || Object.keys(failValues).includes(value)

export const rules = {
  qualMinDpHet: {
    integer,
    required,
    minValue: minValue(0),
    $autoDirty: true,
  },
  qualMinDpHom: {
    integer,
    required,
    minValue: minValue(0),
    $autoDirty: true,
  },
  qualMinAb: {
    decimal,
    required,
    between: between(0.0, 1.0),
    $autoDirty: true,
  },
  qualMinGq: {
    integer,
    required,
    minValue: minValue(0),
    $autoDirty: true,
  },
  qualMinAd: {
    integer,
    required,
    minValue: minValue(0),
    $autoDirty: true,
  },
  qualMaxAd: {
    integer,
    minValue: minValue(0),
    $autoDirty: true,
  },
  qualFail: {
    required,
    mustBeFailValue,
    $autoDirty: true,
  },
}
