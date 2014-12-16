var angular      = require('gulp-angular-filesort');
var coffee       = require('gulp-coffee');
var gulp         = require('gulp');
var gutil        = require('gulp-util');
var inject       = require("gulp-inject");
var less         = require('gulp-less');
var del          = require('del')
var path         = require('path');
var wiredep      = require('wiredep').stream;
var livereload   = require('gulp-livereload');

gulp.task('clean', function(cb) {
  del(['.build'], cb);
});


gulp.task('less', function () {
  return gulp.src('client/app/*/{main,embed}.less')
    .pipe(
    	less({
      	paths: [ 
          path.join(__dirname, 'client/app'),
          path.join(__dirname, 'client')
        ]
    	})
    	.on('error', gutil.log)
    )
    .pipe(gulp.dest('.build/app/'));
});

gulp.task('coffee', function() {
  return gulp.src('client/app/**/*.coffee')
    .pipe(
    	coffee({bare: true}).on('error', gutil.log)
    )
    .pipe(gulp.dest('.build/app/'));
});

gulp.task('copy', function () {
	// Copy assets to the .build dir
  gulp.src('client/img/**/*').pipe(gulp.dest('.build/img/'));
  gulp.src('client/svg/**/*').pipe(gulp.dest('.build/svg/'));
  // For painless retro compatibility we export the build dir 
  // to the same dir as before (components).
  gulp.src('client/vendors/**/*').pipe(gulp.dest('.build/components/'));
});

gulp.task('bower', function () {
  return gulp.src('client/app/*.html')
  	// Inspect bower packages
    .pipe(wiredep({
    	// Excluded dependencies (must be added manually)
    	exclude: [ /angulartics/, /jsPlumb/ ],
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
    .pipe(gulp.dest('client/app/'));
});

// THIS TASK IS NOT WORKING (YET)
// @todo: Find a way to auto inject JS file in the best order
gulp.task('inject', ['coffee'], function() {
	// Files to inject (without workers)
	var sources = gulp.src(['**/*.js', '!**/*.worker.js'], {cwd: '.build'});
	// Preserve angular order
	sources = sources.pipe(angular())
	// Inspect template file
  return gulp.src('client/app/*/*.html')
  	// Inject sources from above
 		.pipe(inject(sources, {
 			addRootSlash: false,
 			// Transform the filepath
	    transform: function (filepath, file, i, length) {
	      return '<script src="{% static \'' + filepath + '\' %}"></script>';
	    }
 		}))
 		// Write into the original file
  	.pipe(gulp.dest('client/app/'));
});


gulp.task('default', ['coffee', 'less', 'bower', 'copy']);

gulp.task('watch', ['default'], function() {
  livereload.listen({silent: true});
  gulp.watch('client/app/**/*.less', ['less']);
  gulp.watch('client/app/**/*.coffee', ['coffee']);
  gulp.watch('client/app/**/*.html').on('change', livereload.changed)
  gulp.watch('.build/**/*.css').on('change', livereload.changed)
  gulp.watch('bower.json', ['bower']);
});