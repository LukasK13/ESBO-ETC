pipeline {
    agent none
    environment {
        SPHINX_DIR  = 'docs'
        BUILD_DIR   = 'build/html'
        SOURCE_DIR  = 'source'
        DEPLOY_HOST = 'deployer@www.example.com:/path/to/docs/'
    }
    stages {
        stage('Build') {
            agent {
                dockerfile {
                  filename "Dockerfile"
                  args "-u root" //needed to get around permission issues
                }
            }
            steps {
                // Install dependencies
                sh '''
                   virtualenv pyenv
                   . pyenv/bin/activate
                   pip3 install -r requirements.txt
                '''
                // clear out old files
                sh 'rm -rf ${BUILD_DIR}'
                sh 'rm -f ${SPHINX_DIR}/sphinx-build.log'
                sh 'ls'
                sh '''
                   pyenv/bin/sphinx-build \
                   -w ${SPHINX_DIR}/sphinx-build.log \
                   -b html ${SPHINX_DIR}/${SOURCE_DIR} ${SPHINX_DIR}/${BUILD_DIR}
                '''
                stash includes: 'docs/build/html/**/*.*', name: 'html'
                // archiveArtifacts 'docs/build/html/**/*.*', onlyIfSuccessful: true
            }
            post {
                failure {
                    sh 'cat ${SPHINX_DIR}/sphinx-build.log'
                }
            }
        }
        stage('Deploy') {
            agent any
            steps {
                unstash 'html'
                sh 'ls docs/build/html'
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