import { NavItem } from './types'

/** Sections in the navigation. */
export const SECTIONS: { [key: string]: NavItem[] } = {
  TOP: [{ id: 'gene-list', title: 'List' }],
  GENE: [
    { id: 'gene-overview', title: 'Overview' },
    { id: 'gene-pathogenicity', title: 'Pathogenicity' },
    { id: 'gene-conditions', title: 'Conditions' },
    { id: 'gene-expression', title: 'Expression' },
    { id: 'gene-clinvar', title: 'ClinVar' },
    { id: 'gene-literature', title: 'Literature' },
  ],
  STRUCVAR: [
    { id: 'strucvar-calldetails', title: 'Call Details' },
    { id: 'strucvar-clinvar', title: 'ClinVar' },
    { id: 'strucvar-tools', title: 'Tools' },
    { id: 'strucvar-flags', title: 'Flags' },
    { id: 'strucvar-comments', title: 'Comments' },
    { id: 'strucvar-genomebrowser', title: 'Genome Browser' },
  ],
}
