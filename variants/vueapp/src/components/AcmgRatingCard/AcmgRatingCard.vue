<script setup lang="ts">
import isEqual from 'lodash.isequal'
import { State } from '@varfish/storeUtils'
import { getAcmgBadge } from '@variants/helpers'
import { useVariantAcmgRatingStore } from '@variants/stores/variantAcmgRating'
import { useVariantDetailsStore } from '@variants/stores/variantDetails'
import { computed, onMounted, ref, watch } from 'vue'
import { copy } from '@variants/helpers'

import { emptyAcmgRatingTemplate } from './constants'

const props = defineProps({
  smallVariant: Object,
})

const acmgRatingStore = useVariantAcmgRatingStore()
const variantDetailsStore = useVariantDetailsStore()

const acmgRatingToSubmit = ref({ ...emptyAcmgRatingTemplate })
const acmgRatingConflicting = ref(false)

const unsetAcmgRating = () => {
  acmgRatingToSubmit.value = { ...emptyAcmgRatingTemplate }
}

const resetAcmgRating = () => {
  if (acmgRatingStore.acmgRating) {
    acmgRatingToSubmit.value.pvs1 = acmgRatingStore.acmgRating.pvs1
    acmgRatingToSubmit.value.ps1 = acmgRatingStore.acmgRating.ps1
    acmgRatingToSubmit.value.ps2 = acmgRatingStore.acmgRating.ps2
    acmgRatingToSubmit.value.ps3 = acmgRatingStore.acmgRating.ps3
    acmgRatingToSubmit.value.ps4 = acmgRatingStore.acmgRating.ps4
    acmgRatingToSubmit.value.pm1 = acmgRatingStore.acmgRating.pm1
    acmgRatingToSubmit.value.pm2 = acmgRatingStore.acmgRating.pm2
    acmgRatingToSubmit.value.pm3 = acmgRatingStore.acmgRating.pm3
    acmgRatingToSubmit.value.pm4 = acmgRatingStore.acmgRating.pm4
    acmgRatingToSubmit.value.pm5 = acmgRatingStore.acmgRating.pm5
    acmgRatingToSubmit.value.pm6 = acmgRatingStore.acmgRating.pm6
    acmgRatingToSubmit.value.pp1 = acmgRatingStore.acmgRating.pp1
    acmgRatingToSubmit.value.pp2 = acmgRatingStore.acmgRating.pp2
    acmgRatingToSubmit.value.pp3 = acmgRatingStore.acmgRating.pp3
    acmgRatingToSubmit.value.pp4 = acmgRatingStore.acmgRating.pp4
    acmgRatingToSubmit.value.pp5 = acmgRatingStore.acmgRating.pp5
    acmgRatingToSubmit.value.ba1 = acmgRatingStore.acmgRating.ba1
    acmgRatingToSubmit.value.bs1 = acmgRatingStore.acmgRating.bs1
    acmgRatingToSubmit.value.bs2 = acmgRatingStore.acmgRating.bs2
    acmgRatingToSubmit.value.bs3 = acmgRatingStore.acmgRating.bs3
    acmgRatingToSubmit.value.bs4 = acmgRatingStore.acmgRating.bs4
    acmgRatingToSubmit.value.bp1 = acmgRatingStore.acmgRating.bp1
    acmgRatingToSubmit.value.bp2 = acmgRatingStore.acmgRating.bp2
    acmgRatingToSubmit.value.bp3 = acmgRatingStore.acmgRating.bp3
    acmgRatingToSubmit.value.bp4 = acmgRatingStore.acmgRating.bp4
    acmgRatingToSubmit.value.bp5 = acmgRatingStore.acmgRating.bp5
    acmgRatingToSubmit.value.bp6 = acmgRatingStore.acmgRating.bp6
    acmgRatingToSubmit.value.bp7 = acmgRatingStore.acmgRating.bp7
    acmgRatingToSubmit.value.class_auto = acmgRatingStore.acmgRating.class_auto
    acmgRatingToSubmit.value.class_override =
      acmgRatingStore.acmgRating.class_override
  } else {
    unsetAcmgRating()
  }
}

const acmgRatingSubmitted = computed(() => {
  if (!acmgRatingStore.acmgRating) {
    return false
  }
  return (
    parseInt(acmgRatingToSubmit.value.pvs1) ===
      acmgRatingStore.acmgRating.pvs1 &&
    parseInt(acmgRatingToSubmit.value.ps1) === acmgRatingStore.acmgRating.ps1 &&
    parseInt(acmgRatingToSubmit.value.ps2) === acmgRatingStore.acmgRating.ps2 &&
    parseInt(acmgRatingToSubmit.value.ps3) === acmgRatingStore.acmgRating.ps3 &&
    parseInt(acmgRatingToSubmit.value.ps4) === acmgRatingStore.acmgRating.ps4 &&
    parseInt(acmgRatingToSubmit.value.pm1) === acmgRatingStore.acmgRating.pm1 &&
    parseInt(acmgRatingToSubmit.value.pm2) === acmgRatingStore.acmgRating.pm2 &&
    parseInt(acmgRatingToSubmit.value.pm3) === acmgRatingStore.acmgRating.pm3 &&
    parseInt(acmgRatingToSubmit.value.pm4) === acmgRatingStore.acmgRating.pm4 &&
    parseInt(acmgRatingToSubmit.value.pm5) === acmgRatingStore.acmgRating.pm5 &&
    parseInt(acmgRatingToSubmit.value.pm6) === acmgRatingStore.acmgRating.pm6 &&
    parseInt(acmgRatingToSubmit.value.pp1) === acmgRatingStore.acmgRating.pp1 &&
    parseInt(acmgRatingToSubmit.value.pp2) === acmgRatingStore.acmgRating.pp2 &&
    parseInt(acmgRatingToSubmit.value.pp3) === acmgRatingStore.acmgRating.pp3 &&
    parseInt(acmgRatingToSubmit.value.pp4) === acmgRatingStore.acmgRating.pp4 &&
    parseInt(acmgRatingToSubmit.value.pp5) === acmgRatingStore.acmgRating.pp5 &&
    parseInt(acmgRatingToSubmit.value.ba1) === acmgRatingStore.acmgRating.ba1 &&
    parseInt(acmgRatingToSubmit.value.bs1) === acmgRatingStore.acmgRating.bs1 &&
    parseInt(acmgRatingToSubmit.value.bs2) === acmgRatingStore.acmgRating.bs2 &&
    parseInt(acmgRatingToSubmit.value.bs3) === acmgRatingStore.acmgRating.bs3 &&
    parseInt(acmgRatingToSubmit.value.bs4) === acmgRatingStore.acmgRating.bs4 &&
    parseInt(acmgRatingToSubmit.value.bp1) === acmgRatingStore.acmgRating.bp1 &&
    parseInt(acmgRatingToSubmit.value.bp2) === acmgRatingStore.acmgRating.bp2 &&
    parseInt(acmgRatingToSubmit.value.bp3) === acmgRatingStore.acmgRating.bp3 &&
    parseInt(acmgRatingToSubmit.value.bp4) === acmgRatingStore.acmgRating.bp4 &&
    parseInt(acmgRatingToSubmit.value.bp5) === acmgRatingStore.acmgRating.bp5 &&
    parseInt(acmgRatingToSubmit.value.bp6) === acmgRatingStore.acmgRating.bp6 &&
    parseInt(acmgRatingToSubmit.value.bp7) === acmgRatingStore.acmgRating.bp7 &&
    acmgRatingToSubmit.value.class_override ===
      acmgRatingStore.acmgRating.class_override
  )
})

const calculateAcmgRating = computed(() => {
  const pvs = acmgRatingToSubmit.value.pvs1
  const ps =
    acmgRatingToSubmit.value.ps1 +
    acmgRatingToSubmit.value.ps2 +
    acmgRatingToSubmit.value.ps3 +
    acmgRatingToSubmit.value.ps4
  const pm =
    acmgRatingToSubmit.value.pm1 +
    acmgRatingToSubmit.value.pm2 +
    acmgRatingToSubmit.value.pm3 +
    acmgRatingToSubmit.value.pm4 +
    acmgRatingToSubmit.value.pm5 +
    acmgRatingToSubmit.value.pm6
  const pp =
    acmgRatingToSubmit.value.pp1 +
    acmgRatingToSubmit.value.pp2 +
    acmgRatingToSubmit.value.pp3 +
    acmgRatingToSubmit.value.pp4 +
    acmgRatingToSubmit.value.pp5
  const ba = acmgRatingToSubmit.value.ba1
  const bs =
    acmgRatingToSubmit.value.bs1 +
    acmgRatingToSubmit.value.bs2 +
    acmgRatingToSubmit.value.bs3 +
    acmgRatingToSubmit.value.bs4
  const bp =
    acmgRatingToSubmit.value.bp1 +
    acmgRatingToSubmit.value.bp2 +
    acmgRatingToSubmit.value.bp3 +
    acmgRatingToSubmit.value.bp4 +
    acmgRatingToSubmit.value.bp5 +
    acmgRatingToSubmit.value.bp6 +
    acmgRatingToSubmit.value.bp7
  const isPathogenic =
    (pvs === 1 && (ps >= 1 || pm >= 2 || (pm === 1 && pp === 1) || pp >= 2)) ||
    ps >= 2 ||
    (ps === 1 && (pm >= 3 || (pm >= 2 && pp >= 2) || (pm === 1 && pp >= 4)))
  const isLikelyPathogenic =
    (pvs === 1 && pm === 1) ||
    (ps === 1 && pm >= 1 && pm <= 2) ||
    (ps === 1 && pp >= 2) ||
    pm >= 3 ||
    (pm === 2 && pp >= 2) ||
    (pm === 1 && pp >= 4)
  const isLikelyBenign = (bs >= 1 && bp >= 1) || bp >= 2
  const isBenign = ba > 0 || bs >= 2
  const isConflicting =
    (isPathogenic || isLikelyPathogenic) && (isBenign || isLikelyBenign)
  acmgRatingToSubmit.value.class_auto = 3
  if (isPathogenic) {
    acmgRatingToSubmit.value.class_auto = 5
  } else if (isLikelyPathogenic) {
    acmgRatingToSubmit.value.class_auto = 4
  } else if (isBenign) {
    acmgRatingToSubmit.value.class_auto = 1
  } else if (isLikelyBenign) {
    acmgRatingToSubmit.value.class_auto = 2
  }
  if (isConflicting) {
    acmgRatingToSubmit.value.class_auto = 3
    acmgRatingConflicting.value = true
  } else {
    acmgRatingConflicting.value = false
  }
  return acmgRatingToSubmit.value.class_auto
})

const convertEmptyToNull = () => {
  if (acmgRatingToSubmit.value.class_override === '') {
    acmgRatingToSubmit.value.class_override = null
  }
}

const onSubmitAcmgRating = async () => {
  const acmgRatingToSubmitNoAuto = copy(acmgRatingToSubmit.value)
  delete acmgRatingToSubmitNoAuto['class_auto']
  const acmgRatingToSubmitEmpty = isEqual(
    acmgRatingToSubmitNoAuto,
    emptyAcmgRatingTemplate,
  )
  if (acmgRatingStore.acmgRating && acmgRatingToSubmitEmpty) {
    // IS not empty but SHOULD be empty, so delete the ACMG rating
    await acmgRatingStore.deleteAcmgRating()
  } else if (!acmgRatingStore.acmgRating && acmgRatingToSubmitEmpty) {
    // IS empty and SHOULD be empty, so no update needed
    acmgRatingToSubmit.value = copy(emptyAcmgRatingTemplate)
  } else if (acmgRatingStore.acmgRating && !acmgRatingToSubmitEmpty) {
    // IS not empty and SHOULD not be empty, so update the ACMG rating
    await acmgRatingStore.updateAcmgRating(acmgRatingToSubmit.value)
  } else if (!acmgRatingStore.acmgRating && !acmgRatingToSubmitEmpty) {
    // IS empty but SHOULD not be empty, so create the ACMG rating
    await acmgRatingStore.createAcmgRating(
      variantDetailsStore.smallVariant,
      acmgRatingToSubmit.value,
    )
  }
}

watch(
  () => [props.smallVariant, acmgRatingStore.storeState.state],
  async () => {
    if (
      props.smallVariant &&
      acmgRatingStore.storeState.state === State.Active
    ) {
      await acmgRatingStore.retrieveAcmgRating(props.smallVariant)
      resetAcmgRating()
    }
  },
)
onMounted(async () => {
  if (props.smallVariant) {
    await acmgRatingStore.retrieveAcmgRating(props.smallVariant)
    resetAcmgRating()
  }
})
</script>

<template>
  <div class="row p-2">
    <div class="col px-0">
      <div class="row">
        <div class="col px-0">
          <h6>Pathogenic</h6>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong
            style="font-variant: small-caps"
            class="text-small text-muted text-capitalize"
          >
            Very Strong Evidence
          </strong>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon, single or multi-exon deletion) in a gene where LOF is a known mechanism of disease"
          >
            <input
              class="form-check-input"
              id="acmg-pvs1"
              type="checkbox"
              name="pvs1"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pvs1"
            />
            <label for="acmg-pvs1" class="m-0">
              <strong class="pr-2">PVS1</strong>
              <span class="text-muted">null variant</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong
            style="font-variant: small-caps"
            class="text-small text-muted text-capitalize"
          >
            Strong Evidence
          </strong>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Same amino acid change as a previously established pathogenic variant regardless of nucleotide change"
          >
            <input
              class="form-check-input"
              id="acmg-ps1"
              type="checkbox"
              name="ps1"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.ps1"
            />
            <label for="acmg-ps1" class="m-0">
              <strong class="pr-2">PS1</strong>
              <span class="text-muted">literature: this AA exchange</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="De novo (both maternity and paternity confirmed) in a patient with the disease and no family history"
          >
            <input
              class="form-check-input"
              id="acmg-ps2"
              type="checkbox"
              name="ps2"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.ps2"
            />
            <label for="acmg-ps2" class="m-0">
              <strong class="pr-2">PS2</strong>
              <span class="text-muted"><u>confirmed</u> de novo</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or gene product"
          >
            <input
              class="form-check-input"
              id="acmg-ps3"
              type="checkbox"
              name="ps3"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.ps3"
            />
            <label for="acmg-ps3" class="m-0">
              <strong class="pr-2">PS3</strong>
              <span class="text-muted">supported by functional studies</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="The prevalence of the variant in affected individuals is significantly increased compared with the prevalence in controls"
          >
            <input
              class="form-check-input"
              id="acmg-ps4"
              type="checkbox"
              name="ps4"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.ps4"
            />
            <label for="acmg-ps4" class="m-0">
              <strong class="pr-2">PS4</strong>
              <span class="text-muted"
                >prevalence in disease &gt; controls</span
              >
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong
            style="font-variant: small-caps"
            class="text-small text-muted text-capitalize"
          >
            Moderate Evidence
          </strong>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Located in a mutational hot spot and/or critical and well-established functional domain (e.g., active site of an enzyme) without benign variation"
          >
            <input
              class="form-check-input"
              id="acmg-pm1"
              type="checkbox"
              name="pm1"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pm1"
            />
            <label for="acmg-pm1" class="m-0">
              <strong class="pr-2">PM1</strong>
              <span class="text-muted">variant in hotspot (missense)</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation Consortium"
          >
            <input
              class="form-check-input"
              id="acmg-pm2"
              type="checkbox"
              name="pm2"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pm2"
            />
            <label for="acmg-pm2" class="m-0">
              <strong class="pr-2">PM2</strong>
              <span class="text-muted">rare; &lt; 1:20.000 in ExAC</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="For recessive disorders, detected in trans with a pathogenic variant"
          >
            <input
              class="form-check-input pm"
              id="acmg-pm3"
              type="checkbox"
              name="pm3"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pm3"
            />
            <label for="acmg-pm3" class="m-0">
              <strong class="pr-2">PM3</strong>
              <span class="text-muted"
                >AR: <i>trans</i> with known pathogenic</span
              >
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Protein length changes as a result of in-frame deletions/insertions in a nonrepeat region or stop-loss variants"
          >
            <input
              class="form-check-input"
              id="acmg-pm4"
              type="checkbox"
              name="pm4"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pm4"
            />
            <label for="acmg-pm4" class="m-0">
              <strong class="pr-2">PM4</strong>
              <span class="text-muted">protein length change</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Novel missense change at an amino acid residue where a different missense change determined to be pathogenic has been seen before"
          >
            <input
              class="form-check-input"
              id="acmg-pm5"
              type="checkbox"
              name="pm5"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pm5"
            />
            <label for="acmg-pm5" class="m-0">
              <strong class="pr-2">PM5</strong>
              <span class="text-muted">literature: AA exchange same pos</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Assumed de novo, but without confirmation of paternity and maternity"
          >
            <input
              class="form-check-input"
              id="acmg-pm6"
              type="checkbox"
              name="pm6"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pm6"
            />
            <label for="acmg-pm6" class="m-0">
              <strong class="pr-2">PM6</strong>
              <span class="text-muted"><u>assumed</u> de novo</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong
            style="font-variant: small-caps"
            class="text-small text-muted text-capitalize"
          >
            Supporting Evidence
          </strong>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Cosegregation with disease in multiple affected family members in a gene definitively known to cause the disease"
          >
            <input
              class="form-check-input"
              id="acmg-pp1"
              type="checkbox"
              name="pp1"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pp1"
            />
            <label for="acmg-pp1" class="m-0">
              <strong class="pr-2">PP1</strong>
              <span class="text-muted">cosegregates in family</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Missense variant in a gene that has a low rate of benign missense variation and in which missense variants are a common mechanism of disease"
          >
            <input
              class="form-check-input"
              id="acmg-pp2"
              type="checkbox"
              name="pp2"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pp2"
            />
            <label for="acmg-pp2" class="m-0">
              <strong class="pr-2">PP2</strong>
              <span class="text-muted">few missense in gene</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Multiple lines of computational evidence support a deleterious effect on the gene or gene product (conservation, evolutionary, splicing impact, etc.)"
          >
            <input
              class="form-check-input"
              id="acmg-pp3"
              type="checkbox"
              name="pp3"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pp3"
            />
            <label for="acmg-pp3" class="m-0">
              <strong class="pr-2">PP3</strong>
              <span class="text-muted">predicted pathogenic &geq; 2</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Patient's phenotype or family history is highly specific for a disease with a single genetic etiology"
          >
            <input
              class="form-check-input"
              id="acmg-pp4"
              type="checkbox"
              name="pp4"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pp4"
            />
            <label for="acmg-pp4" class="m-0">
              <strong class="pr-2">PP4</strong>
              <span class="text-muted">phenotype/pedigree match gene</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory
to perform an independent evaluation"
          >
            <input
              class="form-check-input"
              id="acmg-pp5"
              type="checkbox"
              name="pp5"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.pp5"
            />
            <label for="acmg-pp5" class="m-0">
              <strong class="pr-2">PP5</strong>
              <span class="text-muted">reliable source: pathogenic</span>
            </label>
          </div>
        </div>
      </div>
    </div>
    <div class="col px-0">
      <div class="row">
        <div class="col px-0"><h6>Benign</h6></div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong
            style="font-variant: small-caps"
            class="text-small text-muted text-capitalize"
          >
            Standalone Evidence
          </strong>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Allele frequency is >5% in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation Consortium"
          >
            <input
              class="form-check-input"
              id="acmg-ba1"
              type="checkbox"
              name="ba1"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.ba1"
            />
            <label for="acmg-ba1" class="m-0">
              <strong class="pr-2">BA1</strong>
              <span class="text-muted">allele frequency &gt; 5%</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong
            style="font-variant: small-caps"
            class="text-small text-muted text-capitalize"
          >
            Strong Evidence
          </strong>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Allele frequency is greater than expected for disorder"
          >
            <input
              class="form-check-input"
              id="acmg-bs1"
              type="checkbox"
              name="bs1"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bs1"
            />
            <label for="acmg-bs1" class="m-0">
              <strong class="pr-2">BS1</strong>
              <span class="text-muted">disease: allele freq. too high</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or X-linked (hemizygous) disorder, with full penetrance expected at an early age"
          >
            <input
              class="form-check-input"
              id="acmg-bs2"
              type="checkbox"
              name="bs2"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bs2"
            />
            <label for="acmg-bs2" class="m-0">
              <strong class="pr-2">BS2</strong>
              <span class="text-muted">observed in healthy individual</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing"
          >
            <input
              class="form-check-input"
              id="acmg-bs3"
              type="checkbox"
              name="bs3"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bs3"
            />
            <label for="acmg-bs3" class="m-0">
              <strong class="pr-2">BS3</strong>
              <span class="text-muted">functional studies: benign</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Lack of segregation in affected members of a family"
          >
            <input
              class="form-check-input"
              id="acmg-bs4"
              type="checkbox"
              name="bs4"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bs4"
            />
            <label for="acmg-bs4" class="m-0">
              <strong class="pr-2">BS4</strong>
              <span class="text-muted">lack of segregation</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong
            style="font-variant: small-caps"
            class="text-small text-muted text-capitalize"
          >
            Supporting Evidence
          </strong>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Missense variant in a gene for which primarily truncating variants are known to cause disease"
          >
            <input
              class="form-check-input bp"
              id="acmg-bp1"
              type="checkbox"
              name="bp1"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bp1"
            />
            <label for="acmg-bp1" class="m-0">
              <strong class="pr-2">BP1</strong>
              <span class="text-muted">missense in truncation gene</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed in cis with a pathogenic variant in any inheritance pattern"
          >
            <input
              class="form-check-input"
              id="acmg-bp2"
              type="checkbox"
              name="bp2"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bp2"
            />
            <label for="acmg-bp2" class="m-0">
              <strong class="pr-2">BP2</strong>
              <span class="text-muted">other variant is causative</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="In-frame deletions/insertions in a repetitive region without a known function"
          >
            <input
              class="form-check-input"
              id="acmg-bp3"
              type="checkbox"
              name="bp3"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bp3"
            />
            <label for="acmg-bp3" class="m-0">
              <strong class="pr-2">BP3</strong>
              <span class="text-muted">in-frame indel in repeat</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Multiple lines of computational evidence suggest no impact on gene or gene product (conservation, evolutionary,
splicing impact, etc.)"
          >
            <input
              class="form-check-input"
              id="acmg-bp4"
              type="checkbox"
              name="bp4"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bp4"
            />
            <label for="acmg-bp4" class="m-0">
              <strong class="pr-2">BP4</strong>
              <span class="text-muted">prediction: benign</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Variant found in a case with an alternate molecular basis for disease"
          >
            <input
              class="form-check-input"
              id="acmg-bp5"
              type="checkbox"
              name="bp5"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bp5"
            />
            <label for="acmg-bp5" class="m-0">
              <strong class="pr-2">BP5</strong>
              <span class="text-muted">different gene in other case</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="Reputable source recently reports variant as benign, but the evidence is not available to the laboratory to perform an
independent evaluation"
          >
            <input
              class="form-check-input"
              id="acmg-bp6"
              type="checkbox"
              name="bp6"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bp6"
            />
            <label for="acmg-bp6" class="m-0">
              <strong class="pr-2">BP6</strong>
              <span class="text-muted">reputable source: benign</span>
            </label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <div
            class="form-check form-check-inline"
            title="A synonymous (silent) variant for which splicing prediction algorithms predict no impact to the splice consensus
sequence nor the creation of a new splice site AND the nucleotide is not highly conserved"
          >
            <input
              class="form-check-input"
              id="acmg-bp7"
              type="checkbox"
              name="bp7"
              true-value="1"
              false-value="0"
              v-model="acmgRatingToSubmit.bp7"
            />
            <label for="acmg-bp7" class="m-0">
              <strong class="pr-2">BP7</strong>
              <span class="text-muted">silent, no splicing/conservation</span>
            </label>
          </div>
        </div>
      </div>
    </div>
    <div class="col px-0">
      <div class="row pt-4">
        <div class="col px-0">
          <strong class="text-muted mx-1">5</strong> pathogenic
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong class="text-muted mx-1">4</strong> likely pathogenic
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong class="text-muted mx-1">3</strong> uncertain significance
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong class="text-muted mx-1">2</strong> likely benign
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong class="text-muted mx-1">1</strong> benign
        </div>
      </div>
      <div
        class="row pt-4"
        title="Automatically determined ACMG class (Richards et al., 2015)"
      >
        <div class="col-4 px-0">
          <label for="acmg-class"><strong>ACMG classification</strong></label>
        </div>
        <div class="col px-0 pb-2">
          <div
            title="ACMG rating"
            class="badge"
            style="font-size: 1.5em"
            :class="getAcmgBadge(acmgRatingToSubmit.class_auto)"
          >
            {{ calculateAcmgRating }}
          </div>
        </div>
      </div>
      <div
        class="row"
        title="Manually override the automatically determined class"
      >
        <div class="col-4 px-0">
          <label for="acmg-class-override"
            ><strong>ACMG class override</strong></label
          >
        </div>
        <div class="col px-0">
          <input
            class="form-control form-control-sm"
            id="acmg-class-override"
            type="text"
            style="width: 2em"
            @change="convertEmptyToNull(acmgRatingToSubmit.class_override)"
            v-model.number="acmgRatingToSubmit.class_override"
          />
        </div>
      </div>
      <div class="row pt-2">
        <div class="col px-0">
          <div class="btn-group ml-auto">
            <button
              type="button"
              class="btn btn-sm btn-secondary"
              @click="unsetAcmgRating()"
            >
              Clear
            </button>
            <button
              type="button"
              class="btn btn-sm btn-secondary"
              @click="resetAcmgRating()"
            >
              Reset
            </button>
            <button
              type="submit"
              class="btn btn-sm"
              :class="
                acmgRatingConflicting
                  ? 'btn-warning'
                  : acmgRatingSubmitted
                  ? 'btn-success'
                  : 'btn-primary'
              "
              @click="onSubmitAcmgRating()"
            >
              <i-fa-info-circle v-if="acmgRatingConflicting" />
              <i-fa-solid-star v-else-if="acmgRatingSubmitted" />
              <i-fa-regular-star v-else />
              Submit
            </button>
          </div>
        </div>
      </div>
      <div class="row pt-4 pb-0" v-if="acmgRatingConflicting">
        <div class="col px-0">
          <div class="alert alert-warning p-2">
            <i-fa-solid-info-circle class="mr-1" />
            <strong>Caution!</strong> Conflicting interpretation of variant.
          </div>
        </div>
      </div>
      <div class="row pt-2">
        <div class="col px-0">
          <div class="alert alert-secondary text-small text-muted p-2">
            <i-fa-solid-info-circle />
            Select all fulfilled criteria to get the classification following
            Richards <i>et al.</i> (2015). If necessary, you can also specify a
            manual override.
            <span class="badge badge-primary">Submit</span> indicates that there
            are changes not yet submitted, while
            <span class="badge badge-success">Submit</span> indicates that
            changes have been submitted or not made at all.
            <span class="badge badge-warning">Submit</span> indicates that there
            are conflicting variant interpretations. In that case, submission is
            possible, but not recommended. Press
            <span class="badge badge-secondary">Reset</span> to reset the form
            to the last submitted state. Press
            <span class="badge badge-secondary">Clear</span> and
            <span class="badge badge-primary">Submit</span> to delete ACMG
            rating.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
