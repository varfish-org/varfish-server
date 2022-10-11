<template>
  <form id="filterForm" method="post">
    <div
      class="card"
      v-if="store.querySettings !== null && store.querySettingsPreset !== null"
    >
      <div class="card-header">
        <!--        {% include "variants/filter_form/presets.html" %}-->
      </div>
      <div class="card-header row border-bottom-1 pt-1 pr-1">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a
              class="nav-link active"
              id="genotype-tab"
              data-toggle="tab"
              href="#panel-genotype"
              role="tab"
              data-tooltip="tooltip"
              title="Require genotypes in individuals"
              >Genotype</a
            >
          </li>
          <li class="nav-item">
            <a
              class="nav-link"
              id="frequency-tab"
              data-toggle="tab"
              href="#panel-frequency"
              role="tab"
              data-tooltip="tooltip"
              title="Population frequencies and het./hom. counts"
              >Frequency</a
            >
          </li>
          <!--          <li class="nav-item d-none d-md-block">-->
          <!--            <a-->
          <!--              class="nav-link"-->
          <!--              id="prioritization-tab"-->
          <!--              data-toggle="tab"-->
          <!--              href="#panel-prioritization"-->
          <!--              role="tab"-->
          <!--              data-tooltip="tooltip"-->
          <!--              title="Configure variant prioritization"-->
          <!--              >Prioritization</a-->
          <!--            >-->
          <!--          </li>-->
          <!--          <li class="nav-item dropdown">-->
          <!--            <a-->
          <!--              class="nav-link dropdown-toggle"-->
          <!--              id="more-tab"-->
          <!--              data-toggle="dropdown"-->
          <!--              href="#"-->
          <!--              role="button"-->
          <!--              aria-haspopup="true"-->
          <!--              aria-expanded="false"-->
          <!--              >More ...</a-->
          <!--            >-->
          <!--            <div class="dropdown-menu" style="z-index: 1030">-->
          <!--              <a-->
          <!--                class="dropdown-item"-->
          <!--                id="effect-tab"-->
          <!--                data-toggle="tab"-->
          <!--                href="#panel-effect"-->
          <!--                role="tab"-->
          <!--                data-tooltip="tooltip"-->
          <!--                title="Variant types/effects, coding/non-coding transcripts"-->
          <!--                >Variants &amp; Effects</a-->
          <!--              >-->
          <!--              <a-->
          <!--                class="dropdown-item"-->
          <!--                id="quality-tab"-->
          <!--                data-toggle="tab"-->
          <!--                href="#panel-quality"-->
          <!--                role="tab"-->
          <!--                data-tooltip="tooltip"-->
          <!--                title="Quality, allelic balance, coverage"-->
          <!--                >Quality</a-->
          <!--              >-->
          <!--              <a-->
          <!--                class="dropdown-item"-->
          <!--                id="clinvar-tab"-->
          <!--                data-toggle="tab"-->
          <!--                href="#panel-clinvar"-->
          <!--                role="tab"-->
          <!--                data-tooltip="tooltip"-->
          <!--                title="Filter using Clinvar/HGMD/dbSNP membership"-->
          <!--                >Clinvar, HGMD & dbSNP</a-->
          <!--              >-->
          <!--              <a-->
          <!--                class="dropdown-item"-->
          <!--                id="blocklist-tab"-->
          <!--                data-toggle="tab"-->
          <!--                href="#panel-blocklist"-->
          <!--                role="tab"-->
          <!--                data-tooltip="tooltip"-->
          <!--                title="Allow-list and block-list genes and genomic regions"-->
          <!--                >Gene Lists &amp; Regions</a-->
          <!--              >-->
          <!--              <a-->
          <!--                class="dropdown-item"-->
          <!--                id="flags-tab"-->
          <!--                data-toggle="tab"-->
          <!--                href="#panel-flags"-->
          <!--                role="tab"-->
          <!--                data-tooltip="tooltip"-->
          <!--                title="Filter for user flags and comments"-->
          <!--                >Flags &amp; Comments</a-->
          <!--              >-->
          <!--              <a-->
          <!--                class="dropdown-item"-->
          <!--                id="export-tab"-->
          <!--                data-toggle="tab"-->
          <!--                href="#panel-export"-->
          <!--                role="tab"-->
          <!--                data-tooltip="tooltip"-->
          <!--                title="Configure downloadable file creation"-->
          <!--                data-placement="left"-->
          <!--                >Configure Downloads</a-->
          <!--              >-->
          <!--              <a-->
          <!--                class="dropdown-item"-->
          <!--                id="misc-tab"-->
          <!--                data-toggle="tab"-->
          <!--                href="#panel-misc"-->
          <!--                role="tab"-->
          <!--                data-tooltip="tooltip"-->
          <!--                title="Various settings"-->
          <!--                data-placement="left"-->
          <!--                >Miscellaneous</a-->
          <!--              >-->
          <!--              <a-->
          <!--                class="dropdown-item"-->
          <!--                id="settings-tab"-->
          <!--                data-toggle="tab"-->
          <!--                href="#panel-settings"-->
          <!--                role="tab"-->
          <!--                data-tooltip="tooltip"-->
          <!--                title="Save current filter settings"-->
          <!--                >Filter Import/Export</a-->
          <!--              >-->
          <!--            </div>-->
          <!--          </li>-->
        </ul>
      </div>

      <div class="card-body p-0">
        <div class="tab-content">
          <div
            class="tab-pane fade show active"
            id="panel-genotype"
            role="tabpanel"
            aria-labelledby="genotype-tab"
          >
            <SmallVariantFilterFormGenotypeTab />
          </div>
          <div
            class="tab-pane fade"
            id="panel-frequency"
            role="tabpanel"
            aria-labelledby="frequency-tab"
          >
            <SmallVariantFilterFormFrequencyTab />
          </div>
          <!--          <div-->
          <!--            class="tab-pane fade"-->
          <!--            id="panel-effect"-->
          <!--            role="tabpanel"-->
          <!--            aria-labelledby="effect-tab"-->
          <!--          ></div>-->
          <!--          <div-->
          <!--            class="tab-pane fade"-->
          <!--            id="panel-quality"-->
          <!--            role="tabpanel"-->
          <!--            aria-labelledby="quality-tab"-->
          <!--          ></div>-->
          <!--          <div-->
          <!--            class="tab-pane fade"-->
          <!--            id="panel-blocklist"-->
          <!--            role="tabpanel"-->
          <!--            aria-labelledby="blocklist-tab"-->
          <!--          ></div>-->
          <!--          <div-->
          <!--            class="tab-pane fade"-->
          <!--            id="panel-flags"-->
          <!--            role="tabpanel"-->
          <!--            aria-labelledby="flags-tab"-->
          <!--          ></div>-->
          <!--          <div-->
          <!--            class="tab-pane fade"-->
          <!--            id="panel-prioritization"-->
          <!--            role="tabpanel"-->
          <!--            aria-labelledby="prioritization-tab"-->
          <!--          ></div>-->
          <!--          <div-->
          <!--            class="tab-pane fade"-->
          <!--            id="panel-clinvar"-->
          <!--            role="tabpanel"-->
          <!--            aria-labelledby="clinvar-tab"-->
          <!--          ></div>-->
          <!--          <div-->
          <!--            class="tab-pane fade"-->
          <!--            id="panel-export"-->
          <!--            role="tabpanel"-->
          <!--            arial-labelledby="export-tab"-->
          <!--          ></div>-->
          <!--          <div-->
          <!--            class="tab-pane fade"-->
          <!--            id="panel-misc"-->
          <!--            role="tabpanel"-->
          <!--            arial-labelledby="misc-tab"-->
          <!--          ></div>-->
          <!--          <div-->
          <!--            class="tab-pane fade"-->
          <!--            id="panel-settings"-->
          <!--            role="tabpanel"-->
          <!--            arial-labelledby="settings-tab"-->
          <!--          ></div>-->
        </div>
      </div>

      <div class="card-footer">
        <div class="row">
          <div class="col text-left p-0">
            <div class="btn-group btn-group-toggle pr-5" data-toggle="buttons">
              <label
                class="btn btn-outline-secondary active"
                title="Select RefSeq transcripts"
                for="id_database_selector_refseq"
              >
                <input
                  v-model="store.querySettings.database"
                  type="radio"
                  value="refseq"
                  id="id_database_selector_refseq"
                  required
                />
                RefSeq
              </label>
              <label
                class="btn btn-outline-secondary"
                title="Select EnsEMBL transcripts"
                for="id_database_selector_ensembl"
              >
                <input
                  v-model="store.querySettings.database"
                  type="radio"
                  value="ensembl"
                  id="id_database_selector_ensembl"
                  required
                />
                EnsEMBL
              </label>
            </div>
          </div>
          <div class="col text-right p-0">
            <div class="btn-group">
              <button
                type="button"
                id="submitFilter"
                name="submit"
                class="btn btn-primary"
                @click="store.submitQuery()"
                title='Filter variants again with current settings, limited to "Miscellaneous / Result row limit" results and display in table below'
                :disabled="spinButtonIcon()"
              >
                <i
                  :class="{
                    iconify: !spinButtonIcon(),
                    'iconify spin': spinButtonIcon(),
                  }"
                  data-icon="mdi:refresh"
                />
                Filter &amp; Display
              </button>
              <!--              <button-->
              <!--                class="btn btn-secondary dropdown-toggle"-->
              <!--                type="button"-->
              <!--                id="filterdisplayoptions"-->
              <!--                data-toggle="dropdown"-->
              <!--                aria-haspopup="true"-->
              <!--                aria-expanded="false"-->
              <!--              >-->
              <!--                <i class="iconify" data-icon="fa-solid:ellipsis-h"></i>-->
              <!--              </button>-->
              <!--              <div-->
              <!--                class="dropdown-menu"-->
              <!--                aria-labelledby="filterdisplayoptions"-->
              <!--                style="z-index: 3000"-->
              <!--              >-->
              <!--                <button-->
              <!--                  type="submit"-->
              <!--                  name="submit"-->
              <!--                  value="download"-->
              <!--                  class="dropdown-item"-->
              <!--                  data-toggle="tooltip"-->
              <!--                  aria-haspopup="true"-->
              <!--                  aria-expanded="false"-->
              <!--                  data-html="true"-->
              <!--                  title="Create downloadable file in the background of <i><b>all</b></i> variants with current settings (ignoring result count limit)."-->
              <!--                >-->
              <!--                  <i-->
              <!--                    class="iconify"-->
              <!--                    data-icon="fa-solid:cloud-download-alt"-->
              <!--                  ></i>-->
              <!--                  Download as File-->
              <!--                </button>-->
              <!--              </div>-->
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="alert alert-info">
      <i class="iconify spin" data-icon="fa-solid:circle-notch"></i>
      <strong class="pl-2">Loading filter form ...</strong>
    </div>
    <!--    {% include "variants/_distiller_resubmit_modal.html" %}-->
    <!--    {% include "variants/_cadd_resubmit_modal.html" %}-->
    <!--    {% include "variants/_spanr_resubmit_modal.html" %}-->
  </form>
</template>

<script>
import SmallVariantFilterFormGenotypeTab from './SmallVariantFilterFormGenotypeTab.vue'
import SmallVariantFilterFormFrequencyTab from './SmallVariantFilterFormFrequencyTab.vue'
import { useFilterQueryStore } from '@variants/stores/filterQuery'
import { QueryStates } from '@variants/enums'

export default {
  components: {
    SmallVariantFilterFormGenotypeTab,
    SmallVariantFilterFormFrequencyTab,
  },
  setup() {
    function spinButtonIcon() {
      return (
        this.store.queryState === QueryStates.Fetching.value ||
        this.store.queryState === QueryStates.Running.value
      )
    }

    const store = useFilterQueryStore()
    return {
      spinButtonIcon,
      store,
    }
  },
  data() {
    return { QueryStates }
  },
}
</script>

<style scoped>
.spin {
  animation-name: spin;
  animation-duration: 2000ms;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
