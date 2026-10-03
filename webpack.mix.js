const mix = require('laravel-mix');

// Minimal build config: compile main JS and SCSS into static/build
mix.setPublicPath('static/build')
   .js('static/index/index.js', 'js')
   .sass('static/src/scss/main.scss', 'css')
   .options({ processCssUrls: false })
   .disableNotifications();

// When running in production, version files
if (mix.inProduction()) {
  mix.version();
}
