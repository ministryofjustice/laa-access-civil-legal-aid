const fs = require('node:fs');

const gulp= require("gulp")
const sass = require('gulp-sass')(require('sass'));
const minify = require('gulp-minify');
var concat = require('gulp-concat');


const STYLES_PATHS = ["app/static/src/**/*.scss"]
const SCRIPTS_PATHS = ["app/static/src/**/*.js", "node_modules/govuk-frontend/dist/govuk/govuk-frontend.min.js"]
const ASSETS_PATH = ["node_modules/govuk-frontend/dist/govuk/assets/**/*"]
const DST_PATH = "app/static/dist"

function clean(cb) {
    const dir = DST_PATH
    fs.rmSync(dir, { recursive: true, force: true }, err => {
      if (err) {
        throw err;
      }
      console.log(`${dir} is deleted!`);
    });
    cb();
}
function create(cb) {
    const dir = DST_PATH;
    try {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir);
        console.log(`${dir} is created!`);
      }
    } catch (err) {
      console.error(err);
    }
    cb()
}
function buildStyles(cb){
    return gulp.src(STYLES_PATHS)
        .pipe(sass({outputStyle: "compressed"}).on('error', sass.logError))
        .pipe(minify())
        .pipe(concat("styles.css"))
        .pipe(gulp.dest(DST_PATH));
    cb();
}

function buildsSripts(cb){
    return gulp.src(SCRIPTS_PATHS)
        .pipe(concat("scripts.js"))
        .pipe(gulp.dest(DST_PATH));
    cb();
}

function buildImages(cb) {
    return gulp.src(ASSETS_PATH)
        .pipe(gulp.dest(DST_PATH));
    cb();
}

exports.default = gulp.series(clean, create, buildStyles, buildsSripts, buildImages);