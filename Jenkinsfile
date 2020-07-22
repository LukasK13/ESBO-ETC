pipeline {
    agent none
    environment {
        TEST_DIR    = 'test'
        SPHINX_DIR  = 'docs'
        BUILD_DIR   = 'build/html'
        SOURCE_DIR  = 'source'
    }
    stages {
        stage('Test') {
            agent {
                dockerfile {
                  filename "Dockerfile"
                }
            }
            steps {
                // Install dependencies
                sh '''
                   virtualenv venv
                   . venv/bin/activate
                   pip3 install -r requirements.txt
                '''
                // run tests
                sh '''
                   export PYTHONPATH=`pwd`
                   venv/bin/python3 -m unittest discover ${TEST_DIR}
                '''
            }
        }

        stage('Build Docs') {
            agent {
                dockerfile {
                  filename "Dockerfile"
                }
            }
            steps {
                // Install dependencies
                sh '''
                   virtualenv venv
                   . venv/bin/activate
                   pip3 install -r requirements.txt
                '''
                // clear out old files
                sh 'rm -rf ${BUILD_DIR}'
                sh 'rm -f ${SPHINX_DIR}/sphinx-build.log'
                // build docs
                sh '''
                   venv/bin/sphinx-build \
                   -w ${SPHINX_DIR}/sphinx-build.log \
                   -b html ${SPHINX_DIR}/${SOURCE_DIR} ${SPHINX_DIR}/${BUILD_DIR}
                '''
                // stash build result
                stash includes: 'docs/build/html/**/*.*', name: 'html'
            }
            post {
                failure {
                    sh 'cat ${SPHINX_DIR}/sphinx-build.log'
                }
            }
        }
        stage('Deploy Docs') {
            agent {
                label 'lunjaserv'
            }
            steps {
                // unstash build results from previous stage
                unstash 'html'
                // remove old files
                sh 'rm -rf /opt/esbo-etc/html/*'
                // copy new files
                sh 'cp -rf docs/build/html /opt/esbo-etc/'
            }
        }
    }
}