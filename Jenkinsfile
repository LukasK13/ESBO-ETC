pipeline {
    agent {
        dockerfile {
          filename "Dockerfile"
          args "-u root" //needed to get around permission issues
        }
    }
    environment {
        SPHINX_DIR  = 'docs'
        BUILD_DIR   = 'build/html'
        SOURCE_DIR  = 'source'
        DEPLOY_HOST = 'deployer@www.example.com:/path/to/docs/'
    }
    stages {
        stage('Install Dependencies') {
            steps {
                // virtualenv may not be necessary with root,
                // but I still think it's a good idea.
                sh '''
                   virtualenv pyenv
                   . pyenv/bin/activate
                   pip3 install -r requirements.txt
                '''
            }
        }
        stage('Build') {
            steps {
                // clear out old files
                sh 'rm -rf ${BUILD_DIR}'
                sh 'rm -f ${SPHINX_DIR}/sphinx-build.log'
                sh 'ls ${WORKSPACE}'
                sh '''
                   ${WORKSPACE}/pyenv/bin/sphinx-build \
                   -q -w ${SPHINX_DIR}/sphinx-build.log \
                   -b html \
                   -d ${SPHINX_DIR}/${BUILD_DIR}/doctrees ${SPHINX_DIR}/${SOURCE_DIR} ${SPHINX_DIR}/${BUILD_DIR}
                '''
                archiveArtifacts 'docs/build/html'
            }
            post {
                failure {
                    sh 'cat ${SPHINX_DIR}/sphinx-build.log'
                }
            }
        }
/*
        stage('Deploy') {
            steps {
                sshagent(credentials: ['deployer']) {
                   sh '''#!/bin/bash
                      rm -f ${SPHINX_DIR}/rsync.log
                      RSYNCOPT=(-aze 'ssh -o StrictHostKeyChecking=no')
                      rsync "${RSYNCOPT[@]}" \
                      --exclude-from=${SPHINX_DIR}/rsync-exclude.txt \
                      --log-file=${SPHINX_DIR}/rsync.log \
                      --delete \
                      ${BUILD_DIR}/ ${DEPLOY_HOST}
                    '''
                }
            }
            post {
                failure {
                    sh 'cat ${SPHINX_DIR}/rsync.log'
                }
            }
        }
*/
    }
}