import { FunctionalComponent, SVGAttributes, defineComponent, h } from 'vue'

import IconCircle from '~icons/bi/circle'
import IconCircleFill from '~icons/bi/circle-fill'
import IconDiamond from '~icons/bi/diamond'
import IconDiamondFill from '~icons/bi/diamond-fill'
import IconSquare from '~icons/bi/square'
import IconSquareFill from '~icons/bi/square-fill'

import { Affected, SexAssignedAtBirth } from './types'

type IconFC = FunctionalComponent<SVGAttributes>

const ICONS: Record<SexAssignedAtBirth, [IconFC, IconFC]> = {
  [SexAssignedAtBirth.MALE]: [IconSquare, IconSquareFill],
  [SexAssignedAtBirth.FEMALE]: [IconCircle, IconCircleFill],
  [SexAssignedAtBirth.UNDEFINED]: [IconDiamond, IconDiamondFill],
}

export default defineComponent<{ sex: SexAssignedAtBirth; affected: Affected }>(
  ({ sex, affected }) => {
    return () =>
      h(ICONS[sex][affected == Affected.UNAFFECTED ? 0 : 1], {
        style: {
          'font-size': '0.6em',
          ...(affected == Affected.UNDEFINED ? { color: 'gray' } : {}),
        },
      })
  },
  // eslint-disable-next-line vue/require-prop-types
  { props: ['sex', 'affected'] },
)
