pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    environment {
        PYTHON          = 'python3'
        VENV_DIR        = '.venv'
        TEST_RESULTS_DIR = 'test-results'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set Up Python Environment') {
            steps {
                sh '''
                    ${PYTHON} -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    else
                        pip install streamlit pandas
                    fi
                    pip install pytest pytest-cov
                '''
            }
        }

        stage('Run Streamlit AppTest Suite') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    mkdir -p ${TEST_RESULTS_DIR}
                    pytest tests/ \
                        --junitxml=${TEST_RESULTS_DIR}/apptest-results.xml \
                        --cov=. \
                        --cov-report=xml:${TEST_RESULTS_DIR}/coverage.xml \
                        --cov-report=term \
                        -v
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: "${TEST_RESULTS_DIR}/apptest-results.xml"
            archiveArtifacts artifacts: "${TEST_RESULTS_DIR}/**", allowEmptyArchive: true
        }
        success {
            echo '✅ AppTest suite passed.'
        }
        failure {
            echo '❌ AppTest suite failed — check the JUnit report for details.'
        }
        cleanup {
            sh 'rm -rf ${VENV_DIR}'
        }
    }
}