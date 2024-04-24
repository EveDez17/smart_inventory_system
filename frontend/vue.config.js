const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
  outputDir: 'dist',   // Outputs to 'frontend/dist'
  assetsDir: 'static', // Puts compiled assets in 'frontend/dist/static'
  transpileDependencies: true
});


