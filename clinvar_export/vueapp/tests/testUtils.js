// Constants
export const projectUuid = '00000000-0000-0000-0000-000000000000'
export const submissionSetUuid = '11111111-1111-1111-1111-111111111111'
export const submitterUuid = '22222222-2222-2222-2222-222222222222'
export const organisationUuid = '33333333-3333-3333-3333-333333333333'
export const submittingOrgUuid = '44444444-4444-4444-4444-444444444444'
export const assertionMethodUuid = '55555555-5555-5555-5555-555555555555'
export const submissionUuid = '66666666-6666-6666-6666-666666666666'
export const familyUuid = '77777777-7777-7777-7777-777777777777'
export const individualUuid = '88888888-8888-8888-8888-888888888888'
export const submissionIndividualUuid = '99999999-9999-9999-9999-999999999999'
export const caseUuid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
export const userUuid = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'

export const waitNT = (vm) => new Promise((resolve) => vm.$nextTick(resolve))
export const waitRAF = () =>
  new Promise((resolve) => requestAnimationFrame(resolve))

// Basic copy function for data objects
export function copy(obj) {
  return JSON.parse(JSON.stringify(obj))
}
