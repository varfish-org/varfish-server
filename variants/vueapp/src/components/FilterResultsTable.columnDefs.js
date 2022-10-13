import FilterResultsTableClinvar from '@variants/components/FilterResultsTableClinvar.vue'
import FilterResultsTableFrequency from '@variants/components/FilterResultsTableFrequency.vue'
import FilterResultsTableGeneIcons from '@variants/components/FilterResultsTableGeneIcons.vue'
import FilterResultsTableVariantIcons from '@variants/components/FilterResultsTableVariantIcons.vue'
import {
  DisplayColumns,
  DisplayConstraints,
  DisplayDetails,
  DisplayFrequencies,
} from '@variants/enums'

export function defineColumnDefs({
  displayFrequency,
  displayConstraint,
  displayDetails,
  displayColumns,
  genotypes,
}) {
  return [
    {
      field: 'selector',
      headerName: '',
      cellRenderer: () => {
        return '<input type="checkbox">'
      },
      resizable: false,
      width: 50,
      suppressSizeToFit: true,
    },
    {
      field: 'index',
      headerName: '',
      valueGetter: 'node.rowIndex + 1',
      type: 'rightAligned',
      cellRenderer: (params) => {
        return '<span class="text-muted">#' + params.value + '</span>'
      },
      resizable: false,
      width: 70,
      suppressSizeToFit: true,
    },
    {
      field: 'variant_icons',
      headerName: 'variant icons',
      cellRenderer: FilterResultsTableVariantIcons,
      resizable: false,
      width: 145,
      suppressSizeToFit: true,
    },
    {
      field: 'position',
      headerName: 'position',
      valueGetter: (params) => {
        return (
          (params.data.chromosome.startsWith('chr') ? '' : 'chr') +
          params.data.chromosome +
          ':' +
          params.data.start.toLocaleString()
        )
      },
      hide: displayDetails !== DisplayDetails.Coordinates.value,
    },
    {
      field: 'reference',
      headerName: 'ref',
      hide: displayDetails !== DisplayDetails.Coordinates.value,
    },
    {
      field: 'alternative',
      headerName: 'alt',
      hide: displayDetails !== DisplayDetails.Coordinates.value,
    },
    {
      field: 'clinvar',
      headerName: 'clinvar summary',
      hide: displayDetails !== DisplayDetails.Clinvar.value,
      cellRenderer: FilterResultsTableClinvar,
    },
    {
      field: 'exac_frequency',
      headerName: 'frequency',
      hide: displayFrequency !== DisplayFrequencies.Exac.value,
      cellRenderer: FilterResultsTableFrequency,
      sortable: true,
    },
    {
      field: 'exac_homozygous',
      headerName: '#hom',
      hide: displayFrequency !== DisplayFrequencies.Exac.value,
      sortable: true,
    },
    {
      field: 'thousand_genomes_frequency',
      headerName: 'frequency',
      hide: displayFrequency !== DisplayFrequencies.ThousandGenomes.value,
      cellRenderer: FilterResultsTableFrequency,
      sortable: true,
    },
    {
      field: 'thousand_genomes_homozygous',
      headerName: '#hom',
      hide: displayFrequency !== DisplayFrequencies.ThousandGenomes.value,
      sortable: true,
    },
    {
      field: 'gnomad_exomes_frequency',
      headerName: 'frequency',
      hide: displayFrequency !== DisplayFrequencies.GnomadExomes.value,
      cellRenderer: FilterResultsTableFrequency,
      sortable: true,
    },
    {
      field: 'gnomad_exomes_homozygous',
      headerName: '#hom',
      hide: displayFrequency !== DisplayFrequencies.GnomadExomes.value,
      sortable: true,
    },
    {
      field: 'gnomad_genomes_frequency',
      headerName: 'frequency',
      hide: displayFrequency !== DisplayFrequencies.GnomadGenomes.value,
      cellRenderer: FilterResultsTableFrequency,
      sortable: true,
    },
    {
      field: 'gnomad_genomes_homozygous',
      headerName: '#hom',
      hide: displayFrequency !== DisplayFrequencies.GnomadGenomes.value,
      sortable: true,
    },
    {
      field: 'inhouse_carriers',
      headerName: '#carriers',
      hide: displayFrequency !== DisplayFrequencies.InhouseDb.value,
      cellRenderer: FilterResultsTableFrequency,
      sortable: true,
    },
    {
      field: 'inhouse_hom_alt',
      headerName: '#hom',
      hide: displayFrequency !== DisplayFrequencies.InhouseDb.value,
      sortable: true,
    },
    {
      field: 'mtdb_frequency',
      headerName: 'frequency',
      hide: displayFrequency !== DisplayFrequencies.MtDb.value,
      valueFormatter: (params) => {
        return parseFloat(params.value).toFixed(5)
      },
      sortable: true,
    },
    {
      field: 'mtdb_count',
      headerName: '#hom',
      hide: displayFrequency !== DisplayFrequencies.MtDb.value,
      sortable: true,
    },
    {
      field: 'helixmtdb_frequency',
      headerName: 'frequency',
      hide: displayFrequency !== DisplayFrequencies.HelixMtDb.value,
      valueFormatter: (params) => {
        return parseFloat(params.value).toFixed(5)
      },
      sortable: true,
    },
    {
      field: 'helixmtdb_hom_count',
      headerName: '#hom',
      hide: displayFrequency !== DisplayFrequencies.HelixMtDb.value,
      sortable: true,
    },
    {
      field: 'mitomap_frequency',
      headerName: 'frequency',
      hide: displayFrequency !== DisplayFrequencies.Mitomap.value,
      valueFormatter: (params) => {
        return parseFloat(params.value).toFixed(5)
      },
      sortable: true,
    },
    {
      field: 'mitomap_count',
      headerName: '#hom',
      hide: displayFrequency !== DisplayFrequencies.Mitomap.value,
      sortable: true,
    },
    {
      field: 'exac_pLI',
      headerName: 'pLI',
      hide: displayConstraint !== DisplayConstraints.ExacPli.value,
      valueFormatter: (params) => {
        return parseFloat(params.value).toFixed(3)
      },
      sortable: true,
    },
    {
      field: 'exac_mis_z',
      headerName: 'Z mis',
      hide: displayConstraint !== DisplayConstraints.ExacZMis.value,
      valueFormatter: (params) => {
        return parseFloat(params.value).toFixed(3)
      },
      sortable: true,
    },
    {
      field: 'exac_syn_z',
      headerName: 'Z syn',
      hide: displayConstraint !== DisplayConstraints.ExacZSyn.value,
      valueFormatter: (params) => {
        return parseFloat(params.value).toFixed(3)
      },
      sortable: true,
    },
    {
      field: 'gnomad_loeuf',
      headerName: 'LOEUF',
      hide: displayConstraint !== DisplayConstraints.GnomadLoeuf.value,
      valueFormatter: (params) => {
        return parseFloat(params.value).toFixed(3)
      },
      sortable: true,
    },
    {
      field: 'gnomad_pLI',
      headerName: 'pLI',
      hide: displayConstraint !== DisplayConstraints.GnomadPli.value,
      valueFormatter: (params) => {
        return parseFloat(params.value).toFixed(3)
      },
      sortable: true,
    },
    {
      field: 'gnomad_mis_z',
      headerName: 'Z mis',
      hide: displayConstraint !== DisplayConstraints.GnomadZMis.value,
      sortable: true,
    },
    {
      field: 'gnomad_syn_z',
      headerName: 'Z syn',
      hide: displayConstraint !== DisplayConstraints.GnomadZSyn.value,
      sortable: true,
    },
    {
      field: 'gene',
      headerName: 'gene',
      valueGetter: (params) => {
        if (!params || !params.data) {
          return null
        } else {
          return params.data.symbol
            ? params.data.symbol
            : params.data.gene_symbol
        }
      },
      sortable: true,
      filter: 'agTextColumnFilter',
      filterParams: {
        filterOptions: ['contains'],
        caseSensitive: false,
      },
    },
    {
      field: 'gene_icons',
      headerName: 'gene icons',
      cellRenderer: FilterResultsTableGeneIcons,
    },
    {
      headerName: 'effect',
      field: 'effect_summary',
      valueGetter: (params) => {
        return [null, 'p.?', 'p.='].includes(params.data.hgvs_p)
          ? params.data.hgvs_c
          : params.data.hgvs_p
      },
      hide: !(displayColumns || []).includes(DisplayColumns.Effect.value),
    },
    {
      field: 'effect',
      valueFormatter: (params) => {
        return params.value.join(', ')
      },
      headerName: 'effect text',
      hide: !(displayColumns || []).includes(DisplayColumns.EffectText.value),
    },
    {
      field: 'hgvs_p',
      headerName: 'hgvs_p',
      hide: !(displayColumns || []).includes(
        DisplayColumns.EffectProtein.value
      ),
    },
    {
      field: 'hgvs_c',
      headerName: 'hgvs_c',
      hide: !(displayColumns || []).includes(DisplayColumns.EffectCdna.value),
    },
    {
      field: 'exon_dist',
      headerName: 'exon dist',
      hide: !(displayColumns || []).includes(
        DisplayColumns.DistanceSplicesite.value
      ),
    },
    ...genotypes,
    {
      field: 'igv',
      headerName: '',
      cellRenderer: (_params) => {
        return '<a class="btn btn-sm badge-secondary" style="font-size: 80%" :href="`http://127.0.0.1:60151/goto?locus=chr${params.data.chromosome}:${params.data.start}-${params.data.end}`">IGV</a>'
      },
    },
  ]
}
