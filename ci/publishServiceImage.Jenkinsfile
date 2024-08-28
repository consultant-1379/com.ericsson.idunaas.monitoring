#!/usr/bin/env groovy

def bob = "bob/bob -r \${WORKSPACE}/ci/ruleset2.0.yaml"

pipeline {
    agent {
        node {
            label SLAVE
        }
    }
    parameters {
        string(
            name: 'FUNCTIONAL_USER_SECRET',
            defaultValue: '3079dee4-a7d0-4a8e-b03e-7615bad7d6ec',
            description: 'Jenkins secret ID for ARM Registry Credentials'
        )
    }
    environment {
        CHANGE_TYPE = sh "git log -1 --pretty=%B | head -1 | awk '{print $NF}'"
    }

    stages {
        stage('Prepare workspace') {
            steps {
                sh 'git clean -xdff'
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive'
            }
        }
        stage('Bump EICaaS monitoring version') {
            steps {
                sh "${bob} bump-service-version:bump-version-file"
                sh "${bob} bump-service-version:expose-version-in-artifactproperties"
                script {
                    env.IMAGE_VERSION = readFile('artifact.properties').trim()
                }
            }
        }
        stage('Build EICaaS monitoring image') {
            steps {
                sh "${bob} build-monitoring"
            }
        }
        stage('Publish EIAPaaS monitoring image') {
            steps {
                sh "${bob} publish-monitoring"
            }
        }
        stage('Package EICaaS helm chart') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]){
                sh "${bob} Publish-helm-chart"
                }
            }
        }
        stage('Push changes to version file') {
            steps {
                sh "${bob} push-changes-to-version-file"
            }
        }
        stage('Archive artifact.properties') {
            steps {
                archiveArtifacts artifacts: 'artifact.properties', onlyIfSuccessful: true
            }
        }
    }
}

