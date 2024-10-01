const esbuild = require('esbuild');
const { sassPlugin } = require('esbuild-sass-plugin');


const isProduction = process.env.NODE_ENV === 'production';

async function build() {
  try {
      await esbuild.build({
      plugins: [sassPlugin({
        quietDeps: true
      })],
      entryPoints: ["app/static/src/js/scripts.js", "app/static/src/scss/styles.scss"],
      bundle: true,
      entryNames: '[name]',
      outdir: 'app/static/dist',   // Output directory,
      minify: isProduction,
      sourcemap: !isProduction,
      external: ['/assets/*'],
    });
    console.log('Build succeeded');
  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}


(async () => {
  await build();
})();
