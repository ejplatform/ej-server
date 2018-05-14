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
      ]
    })
  ],
  collections: [
    { name: '@ionic/core' },
    { name: 'ionicons' }
  ],
  bundles: [
    { components: ['ion-card', 'ion-card-header', 'ion-card-content'] },
    // { components: ['ion-button', 'ion-buttons', 'ion-icon'] },

  ]
};

exports.devServer = {
  root: 'www',
  watchGlob: '**/**'
}
