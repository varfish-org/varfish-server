<script setup>
const props = defineProps({
  smallVariant: Object,
  mitochondrialFreqs: Object,
  populations: Array,
  inhouseFreq: Object,
  popFreqs: Object,
})

/**
 * Returns whether the given position is in a homopolymer on the mitochondrial chromosome.
 *
 * @param smallVariant Small variant to check.
 * @returns {boolean} whether the position is in a mitochondrial homopolymer
 */
const checkIsVariantMtHomopolymer = (smallVariant) => {
  if (!smallVariant) {
    return false
  }
  const { chromosome, start, end } = smallVariant
  const positionCheck = (pos) => {
    return (
      (pos >= 66 && pos <= 71) ||
      (pos >= 300 && pos <= 316) ||
      (pos >= 513 && pos <= 525) ||
      (pos >= 3106 && pos <= 3107) ||
      (pos >= 12418 && pos <= 12425) ||
      (pos >= 16182 && pos <= 16194)
    )
  }
  if (chromosome === 'MT') {
    return positionCheck(start) || positionCheck(end)
  }
}

/**
 * Obtain header for mitochondrial frequencies.
 */
const getMtFrequenciesHeader = () => {
  if (props.mitochondrialFreqs) {
    return props.mitochondrialFreqs.vars.MITOMAP.map((entry) => {
      return entry[0]
    })
  } else {
    return []
  }
}

/**
 * Obtain mitochondrial frequencies.
 */
const getMtFrequencies = () => {
  if (props.mitochondrialFreqs) {
    return [
      {
        name: 'MITOMAP',
        an: props.mitochondrialFreqs.an.MITOMAP,
        isTriallelic: false,
        dloop: false,
        rows: [
          {
            title: 'AC',
            formatter: (value) => {
              return !value ? 0 : value.toLocaleString()
            },
            data: props.mitochondrialFreqs.vars.MITOMAP.map((entry) => {
              return entry[1].ac
            }),
          },
          {
            title: 'AF',
            formatter: (value) => {
              return (!value ? 0.0 : parseFloat(value)).toFixed(5)
            },
            data: props.mitochondrialFreqs.vars.MITOMAP.map((entry) => {
              return entry[1].af
            }),
          },
        ],
      },
      {
        name: 'mtDB',
        an: props.mitochondrialFreqs.an.mtDB,
        isTriallelic: false,
        dloop: props.mitochondrialFreqs.dloop,
        rows: [
          {
            title: 'AC',
            formatter: (value) => {
              return !value ? 0 : value.toLocaleString()
            },
            data: props.mitochondrialFreqs.vars.mtDB.map((entry) => {
              return entry[1].ac
            }),
          },
          {
            title: 'AF',
            formatter: (value) => {
              return (!value ? 0.0 : parseFloat(value)).toFixed(5)
            },
            data: props.mitochondrialFreqs.vars.mtDB.map((entry) => {
              return entry[1].af
            }),
          },
        ],
      },
      {
        name: 'HelixMTdb',
        an: props.mitochondrialFreqs.an.HelixMTdb,
        isTriallelic: props.mitochondrialFreqs.is_triallelic,
        dloop: false,
        rows: [
          {
            title: 'AC hom',
            formatter: (value) => {
              return !value ? 0 : value.toLocaleString()
            },
            data: props.mitochondrialFreqs.vars.HelixMTdb.map((entry) => {
              return entry[1].ac_hom
            }),
          },
          {
            title: 'AC het',
            formatter: (value) => {
              return !value ? 0 : value.toLocaleString()
            },
            data: props.mitochondrialFreqs.vars.HelixMTdb.map((entry) => {
              return entry[1].ac_het
            }),
          },
          {
            title: 'AF',
            formatter: (value) => {
              return (!value ? 0.0 : parseFloat(value)).toFixed(5)
            },
            data: props.mitochondrialFreqs.vars.HelixMTdb.map((entry) => {
              return entry[1].af
            }),
          },
        ],
      },
    ]
  }
}

const getFrequencies = () => {
  if (props.inhouseFreq && props.popFreqs && props.populations) {
    let data = {}
    for (const [name, db] of Object.entries(props.popFreqs)) {
      data[name] = [
        {
          display: true,
          colspan: null,
          rowClasses: null,
          title: 'Freq',
          titleIcon: null,
          titleClasses: 'text-center',
          formatter: (value) => {
            return (!value ? 0.0 : parseFloat(value)).toFixed(5)
          },
          data: props.populations.map((pop) => {
            if (db[pop].af) {
              return { value: db[pop].af, classes: 'text-right' }
            } else {
              return { value: null, classes: 'text-right text-muted' }
            }
          }),
        },
        {
          display: name === 'gnomAD Exomes' || name === 'gnomAD Genomes',
          rowClasses: 'text-muted',
          title: 'Ctrl',
          titleIcon: 'mdi:arrow-up-circle',
          titleClasses: 'text-center small',
          formatter: (value) => {
            return (!value ? 0.0 : parseFloat(value)).toFixed(5)
          },
          data: props.populations.map((pop) => {
            if (db[pop].controls_af) {
              return { value: db[pop].controls_af, classes: 'text-right' }
            } else {
              return { value: null, classes: 'text-right text-muted' }
            }
          }),
        },
        {
          display: true,
          colspan: null,
          rowClasses: null,
          title: 'Hom',
          titleIcon: null,
          titleClasses: 'text-center',
          formatter: (value) => {
            return !value ? 0 : value.toLocaleString()
          },
          data: props.populations.map((pop) => {
            if (db[pop].hom) {
              return { value: db[pop].hom, classes: 'text-right' }
            } else {
              return { value: null, classes: 'text-right text-muted' }
            }
          }),
        },
        {
          display: name === 'gnomAD Exomes' || name === 'gnomAD Genomes',
          colspan: null,
          rowClasses: 'text-muted',
          title: 'Ctrl',
          titleIcon: 'mdi:arrow-up-circle',
          titleClasses: 'text-center small',
          formatter: (value) => {
            return !value ? 0 : value.toLocaleString()
          },
          data: props.populations.map((pop) => {
            if (db[pop].controls_hom) {
              return { value: db[pop].controls_hom, classes: 'text-right' }
            } else {
              return { value: null, classes: 'text-right text-muted' }
            }
          }),
        },
        {
          display: true,
          colspan: null,
          rowClasses: null,
          title: 'Het',
          titleIcon: null,
          titleClasses: 'text-center',
          formatter: (value) => {
            return !value ? 0 : value.toLocaleString()
          },
          data: props.populations.map((pop) => {
            if (db[pop].het) {
              return { value: db[pop].het, classes: 'text-right' }
            } else {
              return { value: null, classes: 'text-right text-muted' }
            }
          }),
        },
        {
          display: name === 'gnomAD Exomes' || name === 'gnomAD Genomes',
          colspan: null,
          rowClasses: 'text-muted',
          title: 'Ctrl',
          titleIcon: 'mdi:arrow-up-circle',
          titleClasses: 'text-center small',
          formatter: (value) => {
            return !value ? 0 : value.toLocaleString()
          },
          data: props.populations.map((pop) => {
            if (db[pop].controls_het) {
              return { value: db[pop].controls_het, classes: 'text-right' }
            } else {
              return { value: null, classes: 'text-right text-muted' }
            }
          }),
        },
      ]
    }
    data['Inhouse'] = [
      {
        display: true,
        colspan: 9,
        rowClasses: null,
        title: 'Carriers',
        titleIcon: null,
        titleClasses: 'text-center',
        formatter: (value) => {
          return !value ? 0 : value.toLocaleString()
        },
        data: [
          {
            value: props.inhouseFreq.carriers,
            classes: 'text-right',
          },
        ],
      },
      {
        display: true,
        colspan: 9,
        rowClasses: null,
        title: 'Hom',
        titleIcon: null,
        titleClasses: 'text-center',
        formatter: (value) => {
          return !value ? 0 : value.toLocaleString()
        },
        data: [
          {
            value: props.inhouseFreq.hom,
            classes: 'text-right',
          },
        ],
      },
      {
        display: true,
        colspan: 9,
        rowClasses: null,
        title: 'Het',
        titleIcon: null,
        titleClasses: 'text-center',
        formatter: (value) => {
          return !value ? 0 : value.toLocaleString()
        },
        data: [
          {
            value: props.inhouseFreq.het,
            classes: 'text-right',
          },
        ],
      },
    ]
    return data
  }
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h4 class="card-title">
        Frequency Details
        <span
          v-if="checkIsVariantMtHomopolymer(props.smallVariant)"
          class="text-muted"
        >
          &nbsp;
          <i-bi-exclamation-circle />
          &nbsp;
          <small>Variant in homopolymeric region</small>
        </span>
      </h4>
    </div>
    <div class="table-responsive">
      <table
        v-if="props.smallVariant.chromosome === 'MT'"
        class="card-body table table-striped table-sm"
      >
        <thead>
          <tr>
            <th></th>
            <th
              v-for="vari in getMtFrequenciesHeader()"
              :key="vari"
              class="text-center"
            >
              {{ vari }}
              <span
                v-if="props.smallVariant.reference === vari"
                class="badge badge-secondary"
                >REF</span
              >
              <span
                v-else-if="props.smallVariant.alternative === vari"
                class="badge badge-info"
                >ALT</span
              >
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(data, index) in getMtFrequencies()" :key="index">
            <tr>
              <th
                :colspan="getMtFrequenciesHeader().length + 1"
                class="text-center"
              >
                {{ data.name }}
                <span class="text-muted small"
                  >AN: {{ data.an.toLocaleString() }}</span
                >
                <i-bi-exclamation-circle
                  v-if="data.isTriallelic"
                  class="text-muted"
                  title="Variant is part of a triallelic site"
                />
                <i-bi-exclamation-circle
                  v-if="data.dloop"
                  class="text-muted"
                  title="Variant is in D-loop region"
                />
              </th>
            </tr>
            <tr v-for="(row, index2) in data.rows" :key="index2">
              <th>{{ row.title }}</th>
              <td
                class="text-right"
                v-for="(value, index3) in row.data"
                :key="index3"
              >
                {{ row.formatter(value) }}
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <table v-else class="card-body table table-striped table-sm">
        <thead>
          <tr>
            <th></th>
            <th class="text-center" v-for="pop in props.populations" :key="pop">
              {{ pop }}
            </th>
          </tr>
        </thead>
        <tbody>
          <template
            v-for="(rows, name, index) in getFrequencies()"
            :key="index"
          >
            <tr>
              <th
                :colspan="props.populations ? props.populations.length + 1 : 1"
                class="text-center"
              >
                {{ name }}
              </th>
            </tr>
            <template v-for="(row, index2) in rows" :key="index2">
              <tr v-if="row.display" :class="row.rowClasses">
                <th :class="row.titleClasses">
                  <i-mdi-arrow-up-circle
                    v-if="row.titleIcon === 'mdi:arrow-up-circle'"
                  />
                </th>
                <td
                  v-for="(value, index3) in row.data"
                  :key="index3"
                  :class="value.classes"
                  :colspan="row.colspan"
                >
                  {{ row.formatter(value.value) }}
                </td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>
