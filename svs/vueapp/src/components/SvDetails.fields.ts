export type NavItem = {
  name: string
  title: string
}

export const allNavItems: NavItem[] = [
  {
    name: 'genes',
    title: 'Genes',
  },
  {
    name: 'clinvar',
    title: 'ClinVar',
  },
  {
    name: 'call-details',
    title: 'Call / Genotype',
  },
  {
    name: 'comments',
    title: 'Comments',
  },
  {
    name: 'flags',
    title: 'Flags',
  },
  {
    name: 'genome-browser',
    title: 'Genome Browser',
  },
]
