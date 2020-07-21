pipeline {
    agent none
    environment {
        SPHINX_DIR  = 'docs'
        BUILD_DIR   = 'build/html'
        SOURCE_DIR  = 'source'
    }
    stages {
        stage('Test') {
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
                sh '''
                   export PYTHONPATH=`pwd`
                   cd tests
                   ../pyenv/bin/python3 -m unittest discover .
                '''
            }
        }

        stage('Build Docs') {
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
                sh '''
                   pyenv/bin/sphinx-build \
                   -w ${SPHINX_DIR}/sphinx-build.log \
                   -b html ${SPHINX_DIR}/${SOURCE_DIR} ${SPHINX_DIR}/${BUILD_DIR}
                '''
                stash includes: 'docs/build/html/**/*.*', name: 'html'
            }
            post {
                failure {
                    sh 'cat ${SPHINX_DIR}/sphinx-build.log'
                }
            }
        }
        stage('Deploy') {
            agent {
                label 'lunjaserv'
            }
            steps {
                unstash 'html'
                sh 'rm -rf /opt/esbo-etc/html/*'
                sh 'cp -rf docs/build/html /opt/esbo-etc/'
            }
        }
    }
}