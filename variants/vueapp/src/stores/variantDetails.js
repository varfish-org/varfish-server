import { EditCommentModes, VariantValidatorStates } from '@variants/enums'
import { defineStore } from 'pinia'

const emptyFlagsTemplate = {
  flag_bookmarked: false,
  flag_for_validation: false,
  flag_candidate: false,
  flag_final_causative: false,
  flag_no_disease_association: false,
  flag_segregates: false,
  flag_doesnt_segregate: false,
  flag_visual: 'empty',
  flag_molecular: 'empty',
  flag_validation: 'empty',
  flag_phenotype_match: 'empty',
  flag_summary: 'empty',
}

const initialFlagsTemplate = { ...emptyFlagsTemplate, flag_bookmarked: true }

const emptyAcmgCriteriaRatingTemplate = {
  pvs1: 0,
  ps1: 0,
  ps2: 0,
  ps3: 0,
  ps4: 0,
  pm1: 0,
  pm2: 0,
  pm3: 0,
  pm4: 0,
  pm5: 0,
  pm6: 0,
  pp1: 0,
  pp2: 0,
  pp3: 0,
  pp4: 0,
  pp5: 0,
  ba1: 0,
  bs1: 0,
  bs2: 0,
  bs3: 0,
  bs4: 0,
  bp1: 0,
  bp2: 0,
  bp3: 0,
  bp4: 0,
  bp5: 0,
  bp6: 0,
  bp7: 0,
  class_override: null,
}

export const useVariantDetailsStore = defineStore({
  id: 'useVariantDetailsStore',
  state: () => ({
    fetched: false,
    geneId: null,
    smallVariant: null,
    comments: null,
    flags: null,
    clinvar: null,
    knowngeneaa: null,
    effectDetails: null,
    extraAnnos: null,
    populations: null,
    popFreqs: null,
    inhouseFreq: null,
    mitochondrialFreqs: null,
    gene: null,
    ncbiSummary: null,
    ncbiGeneRifs: null,
    variantValidatorResults: null,
    beaconAddress: null,
    commentToSubmit: '',
    setFlagsMode: false,
    editCommentMode: EditCommentModes.Off,
    editCommentUuid: '',
    editCommentIndex: null,
    flagsToSubmit: { ...initialFlagsTemplate },
    acmgCriteriaRatingToSubmit: { ...emptyAcmgCriteriaRatingTemplate },
    setAcmgCriteriaRatingMode: false,
    acmgCriteriaRatingConflicting: false,
    variantValidatorState: VariantValidatorStates.Initial,
    gridRow: null,
    gridApi: null,
    queryDetails: null,
  }),
  actions: {
    async fetchVariantDetails(
      { gridRow, gridApi, smallVariant },
      previousQueryDetails
    ) {
      this.previousQueryDetails = previousQueryDetails
      this.gridRow = gridRow
      this.gridApi = gridApi
      this.smallVariant = smallVariant
      this.variantValidatorResults = null
      this.beaconAddress = null
      this.fetched = false
      this.commentToSubmit = ''
      this.setFlagsMode = false
      this.setAcmgCriteriaRatingMode = false
      this.editCommentMode = EditCommentModes.Off
      this.editCommentUuid = ''
      this.variantValidatorState = VariantValidatorStates.Initial
      const res = await fetch(
        `/variants/ajax/small-variant-details/${this.smallVariant.case_uuid}/${this.smallVariant.release}-${this.smallVariant.chromosome}-${this.smallVariant.start}-${this.smallVariant.end}-${this.smallVariant.reference}-${this.smallVariant.alternative}/${this.previousQueryDetails.query_settings.database_select}/${this.smallVariant.gene_id}/`
      )
      if (res.ok) {
        const resJson = await res.json()
        this.fetched = true
        this.flags = resJson.flags
        this.comments = resJson.comments
        this.gene = resJson.gene
        this.ncbiGeneRifs = resJson.ncbi_gene_rifs
        this.ncbiSummary = resJson.ncbi_summary
        this.clinvar = resJson.clinvar
        this.populations = resJson.populations
        this.popFreqs = resJson.pop_freqs
        this.inhouseFreq = resJson.inhouse_freq
        this.mitochondrialFreqs = resJson.mitochondrial_freqs
        this.knownGeneAa = resJson.knowngeneaa
        this.extraAnnos = resJson.extra_annos
        this.effectDetails = resJson.effect_details
        this.acmgCriteriaRating = resJson.acmg_rating
        this.resetFlags()
        this.resetAcmgCriteriaRating()
      }
    },
    async submitComment(csrfToken) {
      let url, payload, httpMethod
      if (
        this.editCommentMode === EditCommentModes.Edit &&
        this.editCommentUuid
      ) {
        url = `/variants/ajax/small-variant-comment/update/${this.editCommentUuid}/`
        payload = { text: this.commentToSubmit }
        httpMethod = 'PATCH'
      } else {
        url = `/variants/ajax/small-variant-comment/create/${this.smallVariant.case_uuid}/`
        payload = {
          release: this.smallVariant.release,
          chromosome: this.smallVariant.chromosome,
          start: this.smallVariant.start,
          end: this.smallVariant.end,
          bin: this.smallVariant.bin,
          reference: this.smallVariant.reference,
          alternative: this.smallVariant.alternative,
          text: this.commentToSubmit,
        }
        httpMethod = 'POST'
      }
      const res = await fetch(url, {
        method: httpMethod,
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(payload),
      })
      if (res.ok) {
        const resJson = await res.json()
        if (this.editCommentMode === EditCommentModes.Edit) {
          this.comments[this.editCommentIndex] = resJson
          this.unsetEditComment()
        } else {
          this.comments.push(resJson)
          this.smallVariant.comment_count = this.comments.length
          this.commentToSubmit = ''
        }
        // TODO remove after solving issue with reactive aggrid
        // setTimeout(function() { this.gridApi.redrawRows({ rows: [this.gridRow] }); }, 0)
        try {
          this.gridApi.redrawRows({ rows: [this.gridRow] })
        } catch (error) {
          // noop
        }
      }
    },
    async deleteComment(csrfToken) {
      if (this.editCommentMode === EditCommentModes.Delete) {
        const res = await fetch(
          `/variants/ajax/small-variant-comment/delete/${this.editCommentUuid}/`,
          {
            method: 'DELETE',
            credentials: 'same-origin',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken,
            },
          }
        )
        if (res.ok) {
          this.comments.splice(this.editCommentIndex, 1)
          this.smallVariant.comment_count = this.comments.length
          this.unsetEditComment()
          // TODO remove after solving issue with reactive aggrid
          // setTimeout(function() { this.gridApi.redrawRows({ rows: [this.gridRow] }); }, 0)
          try {
            this.gridApi.redrawRows({ rows: [this.gridRow] })
          } catch (error) {
            // noop
          }
        }
      }
    },
    async submitFlags(csrfToken) {
      let url, payload, httpMethod
      const flagsEmpty =
        JSON.stringify(this.flagsToSubmit) ===
        JSON.stringify(emptyFlagsTemplate)
      if (!this.flags && flagsEmpty) {
        this.setFlagsMode = false
        this.flagsToSubmit = { ...initialFlagsTemplate }
        return
      }
      if (this.flags && flagsEmpty) {
        url = `/variants/ajax/small-variant-flags/delete/${this.flags.sodar_uuid}/`
        httpMethod = 'DELETE'
      } else if (this.flags && !flagsEmpty) {
        url = `/variants/ajax/small-variant-flags/update/${this.flags.sodar_uuid}/`
        payload = {
          body: JSON.stringify({
            ...this.flagsToSubmit,
          }),
        }
        httpMethod = 'PATCH'
      } else {
        url = `/variants/ajax/small-variant-flags/create/${this.smallVariant.case_uuid}/`
        payload = {
          body: JSON.stringify({
            release: this.smallVariant.release,
            chromosome: this.smallVariant.chromosome,
            start: this.smallVariant.start,
            end: this.smallVariant.end,
            bin: this.smallVariant.bin,
            reference: this.smallVariant.reference,
            alternative: this.smallVariant.alternative,
            ...this.flagsToSubmit,
          }),
        }
        httpMethod = 'POST'
      }
      const res = await fetch(url, {
        method: httpMethod,
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        ...payload,
      })
      if (res.ok) {
        if (httpMethod === 'DELETE') {
          this.smallVariant.flag_count = 0
          this.flags = null
          this.flagsToSubmit = { ...initialFlagsTemplate }
        } else {
          if (httpMethod === 'POST') {
            this.smallVariant.flag_count = 1
          }
          this.flags = await res.json()
          this.smallVariant.flag_bookmarked = this.flags.flag_bookmarked
          this.smallVariant.flag_for_validation = this.flags.flag_for_validation
          this.smallVariant.flag_candidate = this.flags.flag_candidate
          this.smallVariant.flag_final_causative =
            this.flags.flag_final_causative
          this.smallVariant.flag_no_disease_association =
            this.flags.flag_no_disease_association
          this.smallVariant.flag_segregates = this.flags.flag_segregates
          this.smallVariant.flag_doesnt_segregate =
            this.flags.flag_doesnt_segregate
          this.smallVariant.flag_visual = this.flags.flag_visual
          this.smallVariant.flag_molecular = this.flags.flag_molecular
          this.smallVariant.flag_validation = this.flags.flag_validation
          this.smallVariant.flag_phenotype_match =
            this.flags.flag_phenotype_match
          this.smallVariant.flag_summary = this.flags.flag_summary
        }
        // Todo: Redrawing shouldn't be required as the data is updated.
        // Todo: However, only the first change is reacted to, not the subsequent changes.
        // setTimeout(function() { this.gridApi.redrawRows({ rows: [this.gridRow] }); }, 0)
        try {
          this.gridApi.redrawRows({ rows: [this.gridRow] })
        } catch (error) {
          // noop
        }
      }
      this.setFlagsMode = false
    },
    async submitAcmgCriteriaRating(csrfToken) {
      let url, payload, httpMethod
      const acmgCriteriaRatingToSubmitNoAuto = {
        ...this.acmgCriteriaRatingToSubmit,
      }
      delete acmgCriteriaRatingToSubmitNoAuto['class_auto']
      const acmgCriteriaRatingEmpty =
        JSON.stringify(acmgCriteriaRatingToSubmitNoAuto) ===
        JSON.stringify(emptyAcmgCriteriaRatingTemplate)
      if (!this.acmgCriteriaRating && acmgCriteriaRatingEmpty) {
        this.setAcmgCriteriaRatingMode = false
        this.acmgCriteriaRatingToSubmit = {
          ...emptyAcmgCriteriaRatingTemplate,
        }
        return
      }
      if (this.acmgCriteriaRating && acmgCriteriaRatingEmpty) {
        url = `/variants/ajax/acmg-criteria-rating/delete/${this.acmgCriteriaRating.sodar_uuid}/`
        httpMethod = 'DELETE'
      } else if (this.acmgCriteriaRating && !acmgCriteriaRatingEmpty) {
        url = `/variants/ajax/acmg-criteria-rating/update/${this.acmgCriteriaRating.sodar_uuid}/`
        payload = {
          body: JSON.stringify({
            ...this.acmgCriteriaRatingToSubmit,
          }),
        }
        httpMethod = 'PATCH'
      } else {
        url = `/variants/ajax/acmg-criteria-rating/create/${this.smallVariant.case_uuid}/`
        payload = {
          body: JSON.stringify({
            release: this.smallVariant.release,
            chromosome: this.smallVariant.chromosome,
            start: this.smallVariant.start,
            end: this.smallVariant.end,
            bin: this.smallVariant.bin,
            reference: this.smallVariant.reference,
            alternative: this.smallVariant.alternative,
            ...this.acmgCriteriaRatingToSubmit,
          }),
        }
        httpMethod = 'POST'
      }
      const res = await fetch(url, {
        method: httpMethod,
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        ...payload,
      })
      if (res.ok) {
        if (httpMethod === 'DELETE') {
          this.smallVariant.acmg_class_auto = null
          this.smallVariant.acmg_class_override = null
          this.acmgCriteriaRating = null
          this.acmgCriteriaRatingToSubmit = {
            ...emptyAcmgCriteriaRatingTemplate,
          }
        } else {
          this.acmgCriteriaRating = await res.json()
          this.smallVariant.acmg_class_auto = this.acmgCriteriaRating.class_auto
          this.smallVariant.acmg_class_override =
            this.acmgCriteriaRating.class_override
        }
        // Todo: Redrawing shouldn't be required as the data is updated.
        // Todo: However, only the first change is reacted to, not the subsequent changes.
        // setTimeout(function() { this.gridApi.redrawRows({ rows: [this.gridRow] }); }, 0)
        try {
          this.gridApi.redrawRows({ rows: [this.gridRow] })
        } catch (error) {
          // noop
        }
      }
      this.setAcmgCriteriaRatingMode = false
    },
    setDeleteComment(commentUuid, index) {
      this.editCommentMode = EditCommentModes.Delete
      this.editCommentUuid = commentUuid
      this.editCommentIndex = index
    },
    setEditComment(commentUuid, text, index) {
      this.editCommentMode = EditCommentModes.Edit
      this.editCommentUuid = commentUuid
      this.commentToSubmit = text
      this.editCommentIndex = index
    },
    unsetEditComment() {
      this.editCommentMode = EditCommentModes.Off
      this.editCommentUuid = ''
      this.commentToSubmit = ''
      this.editCommentIndex = null
    },
    unsetFlags() {
      this.flagsToSubmit = { ...emptyFlagsTemplate }
    },
    resetFlags() {
      if (this.flags) {
        this.flagsToSubmit.flag_bookmarked = this.flags.flag_bookmarked
        this.flagsToSubmit.flag_for_validation = this.flags.flag_for_validation
        this.flagsToSubmit.flag_candidate = this.flags.flag_candidate
        this.flagsToSubmit.flag_final_causative =
          this.flags.flag_final_causative
        this.flagsToSubmit.flag_no_disease_association =
          this.flags.flag_no_disease_association
        this.flagsToSubmit.flag_segregates = this.flags.flag_segregates
        this.flagsToSubmit.flag_doesnt_segregate =
          this.flags.flag_doesnt_segregate
        this.flagsToSubmit.flag_visual = this.flags.flag_visual
        this.flagsToSubmit.flag_molecular = this.flags.flag_molecular
        this.flagsToSubmit.flag_validation = this.flags.flag_validation
        this.flagsToSubmit.flag_phenotype_match =
          this.flags.flag_phenotype_match
        this.flagsToSubmit.flag_summary = this.flags.flag_summary
      } else {
        this.flagsToSubmit = { ...initialFlagsTemplate }
      }
    },
    cancelFlags() {
      this.resetFlags()
      this.setFlagsMode = false
    },
    unsetAcmgCriteriaRating() {
      this.acmgCriteriaRatingToSubmit = { ...emptyAcmgCriteriaRatingTemplate }
      this.calculateAcmgCriteriaRating()
    },
    resetAcmgCriteriaRating() {
      if (this.acmgCriteriaRating) {
        this.acmgCriteriaRatingToSubmit.pvs1 = this.acmgCriteriaRating.pvs1
        this.acmgCriteriaRatingToSubmit.ps1 = this.acmgCriteriaRating.ps1
        this.acmgCriteriaRatingToSubmit.ps2 = this.acmgCriteriaRating.ps2
        this.acmgCriteriaRatingToSubmit.ps3 = this.acmgCriteriaRating.ps3
        this.acmgCriteriaRatingToSubmit.ps4 = this.acmgCriteriaRating.ps4
        this.acmgCriteriaRatingToSubmit.pm1 = this.acmgCriteriaRating.pm1
        this.acmgCriteriaRatingToSubmit.pm2 = this.acmgCriteriaRating.pm2
        this.acmgCriteriaRatingToSubmit.pm3 = this.acmgCriteriaRating.pm3
        this.acmgCriteriaRatingToSubmit.pm4 = this.acmgCriteriaRating.pm4
        this.acmgCriteriaRatingToSubmit.pm5 = this.acmgCriteriaRating.pm5
        this.acmgCriteriaRatingToSubmit.pm6 = this.acmgCriteriaRating.pm6
        this.acmgCriteriaRatingToSubmit.pp1 = this.acmgCriteriaRating.pp1
        this.acmgCriteriaRatingToSubmit.pp2 = this.acmgCriteriaRating.pp2
        this.acmgCriteriaRatingToSubmit.pp3 = this.acmgCriteriaRating.pp3
        this.acmgCriteriaRatingToSubmit.pp4 = this.acmgCriteriaRating.pp4
        this.acmgCriteriaRatingToSubmit.pp5 = this.acmgCriteriaRating.pp5
        this.acmgCriteriaRatingToSubmit.ba1 = this.acmgCriteriaRating.ba1
        this.acmgCriteriaRatingToSubmit.bs1 = this.acmgCriteriaRating.bs1
        this.acmgCriteriaRatingToSubmit.bs2 = this.acmgCriteriaRating.bs2
        this.acmgCriteriaRatingToSubmit.bs3 = this.acmgCriteriaRating.bs3
        this.acmgCriteriaRatingToSubmit.bs4 = this.acmgCriteriaRating.bs4
        this.acmgCriteriaRatingToSubmit.bp1 = this.acmgCriteriaRating.bp1
        this.acmgCriteriaRatingToSubmit.bp2 = this.acmgCriteriaRating.bp2
        this.acmgCriteriaRatingToSubmit.bp3 = this.acmgCriteriaRating.bp3
        this.acmgCriteriaRatingToSubmit.bp4 = this.acmgCriteriaRating.bp4
        this.acmgCriteriaRatingToSubmit.bp5 = this.acmgCriteriaRating.bp5
        this.acmgCriteriaRatingToSubmit.bp6 = this.acmgCriteriaRating.bp6
        this.acmgCriteriaRatingToSubmit.bp7 = this.acmgCriteriaRating.bp7
        this.acmgCriteriaRatingToSubmit.class_auto =
          this.acmgCriteriaRating.class_auto
        this.acmgCriteriaRatingToSubmit.class_override =
          this.acmgCriteriaRating.class_override
        this.calculateAcmgCriteriaRating()
      } else {
        this.unsetAcmgCriteriaRating()
      }
    },
    cancelAcmgCriteriaRating() {
      this.resetAcmgCriteriaRating()
      this.setAcmgCriteriaRatingMode = false
    },
    calculateAcmgCriteriaRating() {
      const pvs = this.acmgCriteriaRatingToSubmit.pvs1
      const ps =
        this.acmgCriteriaRatingToSubmit.ps1 +
        this.acmgCriteriaRatingToSubmit.ps2 +
        this.acmgCriteriaRatingToSubmit.ps3 +
        this.acmgCriteriaRatingToSubmit.ps4
      const pm =
        this.acmgCriteriaRatingToSubmit.pm1 +
        this.acmgCriteriaRatingToSubmit.pm2 +
        this.acmgCriteriaRatingToSubmit.pm3 +
        this.acmgCriteriaRatingToSubmit.pm4 +
        this.acmgCriteriaRatingToSubmit.pm5 +
        this.acmgCriteriaRatingToSubmit.pm6
      const pp =
        this.acmgCriteriaRatingToSubmit.pp1 +
        this.acmgCriteriaRatingToSubmit.pp2 +
        this.acmgCriteriaRatingToSubmit.pp3 +
        this.acmgCriteriaRatingToSubmit.pp4 +
        this.acmgCriteriaRatingToSubmit.pp5
      const ba = this.acmgCriteriaRatingToSubmit.ba1
      const bs =
        this.acmgCriteriaRatingToSubmit.bs1 +
        this.acmgCriteriaRatingToSubmit.bs2 +
        this.acmgCriteriaRatingToSubmit.bs3 +
        this.acmgCriteriaRatingToSubmit.bs4
      const bp =
        this.acmgCriteriaRatingToSubmit.bp1 +
        this.acmgCriteriaRatingToSubmit.bp2 +
        this.acmgCriteriaRatingToSubmit.bp3 +
        this.acmgCriteriaRatingToSubmit.bp4 +
        this.acmgCriteriaRatingToSubmit.bp5 +
        this.acmgCriteriaRatingToSubmit.bp6 +
        this.acmgCriteriaRatingToSubmit.bp7
      const isPathogenic =
        (pvs === 1 &&
          (ps >= 1 || pm >= 2 || (pm === 1 && pp === 1) || pp >= 2)) ||
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
      this.acmgCriteriaRatingToSubmit.class_auto = 3
      if (isPathogenic) {
        this.acmgCriteriaRatingToSubmit.class_auto = 5
      } else if (isLikelyPathogenic) {
        this.acmgCriteriaRatingToSubmit.class_auto = 4
      } else if (isBenign) {
        this.acmgCriteriaRatingToSubmit.class_auto = 1
      } else if (isLikelyBenign) {
        this.acmgCriteriaRatingToSubmit.class_auto = 2
      }
      if (isConflicting) {
        this.acmgCriteriaRatingToSubmit.class_auto = 3
        this.acmgCriteriaRatingConflicting = true
      } else {
        this.acmgCriteriaRatingConflicting = false
      }
    },
  },
})
