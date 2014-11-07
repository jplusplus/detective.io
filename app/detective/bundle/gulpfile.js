var angular      = require('gulp-angular-filesort');
var coffee       = require('gulp-coffee');
var gulp         = require('gulp');
var gutil        = require('gulp-util');
var inject       = require("gulp-inject");
var less         = require('gulp-less');
var del          = require('del')
var path         = require('path');
var wiredep      = require('wiredep').stream;

gulp.task('clean', function(cb) {
  del(['.build'], cb);
});


gulp.task('less', function () {
  return gulp.src('app/css/base.less')
    .pipe(
    	less({
      	paths: [ path.join(__dirname, 'app') ]
    	})
    	.on('error', gutil.log)
    )
    .pipe(gulp.dest('.build/css/'));
});

gulp.task('coffee', function() {
  return gulp.src('app/js/**/*.coffee')
    .pipe(
    	coffee({bare: true}).on('error', gutil.log)
    )
    .pipe(gulp.dest('.build/js/'));
});

gulp.task('copy', function () {
	// Copy assets to the .build dir
  gulp.src('./app/img/**/*').pipe(gulp.dest('.build/img/'));
  gulp.src('./app/components/**/*').pipe(gulp.dest('.build/components/'));
});

gulp.task('bower', function () {
  return gulp.src('./app/templates/*.html')
  	// Inspect bower packages
    .pipe(wiredep({
    	// Excluded dependencies (must be added manually)
    	exclude: [ /angulartics/ ],
    	// Remove '../' path prefix
    	ignorePath: '../',
    	// Change tag's templates to add django filter
    	fileTypes: {
    		html: {
		      replace: {
		        js: '<script src="{% static \'{{filePath}}\' %}"></script>',
		        css: '<link rel="stylesheet" href="{% static \'{{filePath}}\' %}" />'
		    	}
    		}
    	}
   	}))
		// Template where inject bower dependencies
    .pipe(gulp.dest('./app/templates/'));
});

gulp.task('inject', ['coffee'], function() {
	// Files to inject (without workers)
	var sources = gulp.src(['js/**/*.js', '!js/workers/*'], {cwd: '.build'});
	// Preserve angular order
	sources = sources.pipe(angular())
	// Inspect template file
  gulp.src('app/templates/*.html')
  	// Inject sources from above
 		.pipe(inject(sources, {
 			addRootSlash: false,
 			// Transform the filepath
	    transform: function (filepath, file, i, length) {
	      return '<script src="{% static \'' + filepath + '\' %}"></script>';
	    }
 		}))
 		// Write into the original file
  	.pipe(gulp.dest('app/templates/'));
});


gulp.task('default', ['coffee', 'less', 'bower', 'copy']);

gulp.task('watch', ['default'], function() {
	gulp.watch('app/css/**/*.less', ['less']);
	gulp.watch('app/js/**/*.coffee', ['coffee']);
	gulp.watch('bower.json', ['bower']);
});