const esbuild = require('esbuild');
const { sassPlugin } = require('esbuild-sass-plugin');


const isProduction = process.env.CLA_ENVIRONMENT === 'production';

async function build(should_watch) {
    const context = {
        plugins: [sassPlugin({
            quietDeps: true
        })],
        entryPoints: ["app/static/src/js/scripts.js", "app/static/src/js/contact.js", "app/static/src/js/about-you.js", "app/static/src/js/headscripts.js", "app/static/src/scss/styles.scss", "app/static/src/js/confirmation.js"],
        bundle: true,
        entryNames: '[name]',
        outdir: 'app/static/dist',   // Output directory,
        minify: isProduction,
        sourcemap: true,
        external: ['/assets/*'],
        logLevel: 'info',
    };

    if(should_watch) {
        esbuild.context(context).then(function(ctx){
            ctx.watch();
            ctx.rebuild();
        });
    }
    else {
        esbuild.build(context);
    }
}

const should_watch = process.argv.includes("--watch");
build(should_watch);
