<script setup>
import { useVariantDetailsStore } from '@variants/stores/variantDetails'
import { useFilterQueryStore } from '@variants/stores/filterQuery'
import { getAcmgBadge } from '@variants/helpers.js'

const detailsStore = useVariantDetailsStore()
const queryStore = useFilterQueryStore()
</script>

<template>
  <div
    class="row pt-2"
    v-if="
      !detailsStore.setAcmgCriteriaRatingMode &&
      detailsStore.acmgCriteriaRatingConflicting
    "
  >
    <div class="col px-0">
      <div class="alert alert-warning p-2">
        <i-bi-exclamation-circle />
        <strong>Caution</strong> Conflicting interpretation of variant!
      </div>
    </div>
  </div>
  <div class="row">
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pvs1"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.ps1"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.ps2"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.ps3"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.ps4"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pm1"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pm2"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pm3"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pm4"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pm5"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pm6"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pp1"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pp2"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pp3"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pp4"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.pp5"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.ba1"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bs1"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bs2"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bs3"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bs4"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bp1"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bp2"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bp3"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bp4"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bp5"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bp6"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
              @change="detailsStore.calculateAcmgCriteriaRating()"
              v-model="detailsStore.acmgCriteriaRatingToSubmit.bp7"
              :disabled="!detailsStore.setAcmgCriteriaRatingMode"
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
            :class="
              getAcmgBadge(detailsStore.acmgCriteriaRatingToSubmit.class_auto)
            "
          >
            {{
              detailsStore.acmgCriteriaRatingToSubmit.class_auto
                ? detailsStore.acmgCriteriaRatingToSubmit.class_auto
                : '-'
            }}
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
            v-model="detailsStore.acmgCriteriaRatingToSubmit.class_override"
            :disabled="!detailsStore.setAcmgCriteriaRatingMode"
          />
        </div>
      </div>
      <div class="row pt-2">
        <div class="col px-0">
          <div
            class="btn-group ml-auto"
            v-if="detailsStore.setAcmgCriteriaRatingMode"
          >
            <button
              type="button"
              class="btn btn-secondary"
              @click="detailsStore.cancelAcmgCriteriaRating()"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-danger"
              @click="detailsStore.unsetAcmgCriteriaRating()"
            >
              Clear
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              @click="
                detailsStore.submitAcmgCriteriaRating(queryStore.csrfToken)
              "
            >
              Submit
            </button>
          </div>
          <div class="btn-group ml-auto" v-else>
            <button
              type="submit"
              class="btn btn-primary"
              @click="variantDetailsStore.setAcmgCriteriaRatingMode = true"
            >
              <i-mdi-pencil />
              Edit
            </button>
          </div>
        </div>
      </div>
      <div class="row pt-4" v-if="detailsStore.setAcmgCriteriaRatingMode">
        <div class="col px-0">
          <div class="alert alert-secondary text-small text-muted p-2">
            <i-fa-solid-info-circle />
            Select all fulfilled criteria to get the classification following
            Richards <i>et al.</i> (2015). If necessary, you can also specify a
            manual override. Press
            <span class="badge badge-danger">Clear</span> and
            <span class="badge badge-primary">Submit</span> to delete ACMG
            rating.
          </div>
        </div>
      </div>
      <div
        class="row"
        v-if="
          detailsStore.setAcmgCriteriaRatingMode &&
          detailsStore.acmgCriteriaRatingConflicting
        "
      >
        <div class="col px-0">
          <div class="alert alert-warning p-2">
            <i-bi-exclamation-circle class="mr-1" />
            <strong>Caution</strong> Conflicting interpretation of variant!
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
