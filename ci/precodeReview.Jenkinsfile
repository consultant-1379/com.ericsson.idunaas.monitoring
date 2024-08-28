#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/ci/ruleset2.0.yaml"
def gerritReviewCommand = "ssh -p 29418 gerrit.ericsson.se gerrit review \${GIT_COMMIT}"
def verifications = [
        'Verified'  : -1,
]

pipeline {
    agent {
        label SLAVE
    }
    environment {
        CHANGED_PYTHON_FILES = sh(returnStdout: true, script: "git diff-tree --diff-filter=ACM --no-commit-id --name-only -r $GIT_COMMIT -- 'prometheus/custom_exporter/*.py'").replaceAll("\\n", " ")
        CHANGED_DOCKERFILE = sh(returnStdout: true, script: "git diff-tree --diff-filter=ACM --no-commit-id --name-only -r $GIT_COMMIT -- 'Dockerfile'").replaceAll("\\n", " ")
        CHANGE_TYPE = sh "git log -1 --pretty=%B | head -1 | awk '{print $NF}'"
    }
    stages {
        stage('Prepare workspace') {
            steps {
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive'
                sh "${bob} git-clean"
            }
        }
        stage('Bump Monitoring version') {
            steps {
                sh "${bob} bump-service-version:bump-version-file"
                sh "${bob} bump-service-version:expose-version-in-artifactproperties"
                script {
                    env.IMAGE_VERSION = readFile('artifact.properties').trim()
                }
            }
        }

        stage('Build Precode Review image') {
            steps {
                sh "${bob} build-precode-image-custom-exporter"
            }
        }
        stage('Run Pylint against prometheus custom exporter') {
            steps {
                sh "${bob} monitoring-linting"
            }
        }
        stage('Run Pylint against modified Python files') {
            when {
                expression
                    { env.CHANGED_PYTHON_FILES != null }
            }
            steps {
                script {
                    try {
                        sh "${bob} lint-changed-files"
                    } catch(error) {
                        sh "echo '++++++++++ Pylint errors detected. Please check above ++++++++++'"
                        currentBuild.result = "FAILURE"
                    }
                }
            }
        }
        stage('Run Pytest against prometheus custom exporter') {
            steps {
                sh "${bob} run-python-tests-custom-exporter"
            }
        }
    }
    post {
        always {
            sh "${bob} remove-precode-image"
        }
    }
}
