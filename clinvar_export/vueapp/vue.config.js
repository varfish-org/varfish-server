const DEPLOYMENT_PATH = '/static/'

module.exports = {
  publicPath:
    process.env.NODE_ENV === 'production'
      ? DEPLOYMENT_PATH
      : 'http://localhost:8080/',
  outputDir: './dist/',
  assetsDir: 'varfish-vue/',
  devServer: {
    allowedHosts: 'all',
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },
}
