/*global module:false*/

module.exports = function(grunt) {
  // load grunt npm tasks
  //
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-shell');

  grunt.initConfig({
    clean: {
      pkg_build: ['build'],
      pkg: ['*.deb'],
    },
    copy: {
      cv2: {
        src: '/usr/local/lib/python2.7/site-packages/cv2.so',
        dest: './env/local/lib/python2.7/site-packages/cv2.so'
      },
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
        command: './env/bin/pip install -e .'
      },
      install_local_cvutils: {
        options: {
          stdout: true,
          failOnError: true
        },
        command: './env/bin/pip install -e ../pt-cvutils'
      },
      reinstall_local_cvutils: {
        options: {
          stdout: true,
          failOnError: true
        },
        command: './env/bin/pip install --force-reinstall -e ../pt-cvutils'
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

  grunt.registerTask('install_local_dependencies',[
    'shell:install_local_cvutils',
  ]);

  grunt.registerTask('reinstall_local_dependencies',[
    'copy:cv2',
    'shell:reinstall_local_cvutils',
  ]);

  grunt.registerTask('install',[
    'shell:create_virtual_env',
    'copy:cv2',
    'install_local_dependencies',
    'shell:install_dependencies'
  ]);

  grunt.registerTask('reinstall',[
    'reinstall_local_dependencies',
  ]);

  grunt.registerTask('test',['shell:behave_stable']);

};
