const sass = require('@stencil/sass');

exports.config = {
  namespace: 'ejconversation',
  outputTargets:[
    { 
      type: 'dist' 
    },
    { 
      type: 'www',
      serviceWorker: false
    }
  ],
  plugins: [
    sass({
      injectGlobalPaths: [
        'src/global/variables.scss',
        // 'src/global/mixins.scss'
      ]
    })
  ]
};

exports.devServer = {
  root: 'www',
  watchGlob: '**/**'
}
