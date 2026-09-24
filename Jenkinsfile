pipeline {
  agent any
  environment {
    APP_NAME = 'bloom-flower-shop'
    // Set IMAGE_REPO in Jenkins, e.g. quay.io/<user>/bloom-flower-shop
    IMAGE_REPO = credentials('bloom-image-repo')
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Build') {
      steps {
        sh 'docker build -t ${IMAGE_REPO}:${BUILD_NUMBER} .'
      }
    }
    stage('Push') {
      steps {
        sh 'docker push ${IMAGE_REPO}:${BUILD_NUMBER}'
      }
    }
    stage('Deploy Bloom') {
      steps {
        sh '''sed "s|BLOOM_IMAGE|${IMAGE_REPO}:${BUILD_NUMBER}|g" openshift/bloom-knative.yaml | oc apply -f -'''
      }
    }
  }
}
