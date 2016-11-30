/*global module:false*/

module.exports = function(grunt) {
  // load grunt npm tasks
  //
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-shell');

  grunt.initConfig({
    clean: {
      pkg_build: ['build'],
      pkg: ['*.deb'],
    },
    shell: {
      build_package: {
        options: {
          stdout: true,
          failOnError: true
        },
        command: './bin/build-deb.sh'
      },
      create_virtual_env: {
        options: {
          stdout: true,
          failOnError: true
        },
        command: 'virtualenv --no-site-packages env'
      },
      install_dependencies: {
        options: {
          stdout: true,
          failOnError: true
        },
        command: './env/bin/pip install -e portal/'
      },
      install_testing_dependencies: {
        options: {
          stdout: true,
          failOnError: true
        },
        command: './env/bin/pip install behave'
      },
      behave_stable: {
        options: {
          stdout: true,
          stderr: true
        },
        command: './env/bin/behave ./tests/features/'
      },
    }
  });

  // build targets

  grunt.registerTask('package',[
    'clean:pkg-build',
    'shell:build_package'
  ]);

  grunt.registerTask('install',[
  ]);

  grunt.registerTask('deploy',['package', 'shell:deploy_vagrant']);

};
