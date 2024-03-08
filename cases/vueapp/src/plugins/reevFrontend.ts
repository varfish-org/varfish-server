import { urlConfig } from '@bihealth/reev-frontend-lib/lib/urlConfig'

export function setupBackendUrls() {
  urlConfig.baseUrlAnnonars = '/proxy/varfish/annonars'
  urlConfig.baseUrlMehari = '/proxy/varfish/mehari'
  urlConfig.baseUrlViguno = '/proxy/varfish/viguno'
  urlConfig.baseUrlNginx = '/proxy/varfish/nginx/'
  urlConfig.baseUrlPubtator = '/proxy/remote/pubtator3-api'
  urlConfig.baseUrlVariantValidator = '/proxy/variantvalidator'

  // urlConfig.baseUrlCadaPrio = '/internal/proxy/cada-prio'
  // urlConfig.baseUrlDotty = '/internal/proxy/dotty'
}
