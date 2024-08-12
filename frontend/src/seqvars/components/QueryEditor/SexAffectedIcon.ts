import { FunctionalComponent, SVGAttributes, defineComponent, h } from 'vue'

import IconCircle from '~icons/bi/circle'
import IconCircleFill from '~icons/bi/circle-fill'
import IconDiamond from '~icons/bi/diamond'
import IconDiamondFill from '~icons/bi/diamond-fill'
import IconSquare from '~icons/bi/square'
import IconSquareFill from '~icons/bi/square-fill'

import { Sex } from '@/cases/stores/caseDetails'

type IconFC = FunctionalComponent<SVGAttributes>

const ICONS: Record<Sex, [IconFC, IconFC]> = {
  ['male']: [IconSquare, IconSquareFill],
  ['female']: [IconCircle, IconCircleFill],
  ['unknown']: [IconDiamond, IconDiamondFill],
  ['other']: [IconDiamond, IconDiamondFill],
}

export default defineComponent<{ sex?: Sex; affected?: boolean }>(
  ({ sex, affected }) => {
    return () =>
      h(ICONS[sex ?? 'unknown'][affected !== true ? 0 : 1], {
        style: {
          'font-size': '0.6em',
          ...(['unknown', 'other'].includes(sex ?? 'unknown')
            ? { color: 'gray' }
            : {}),
        },
      })
  },
  // eslint-disable-next-line vue/require-prop-types
  { props: ['sex', 'affected'] },
)
