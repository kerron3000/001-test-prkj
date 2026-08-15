pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    environment {
        VENV_DIR          = '.venv'
        TEST_RESULTS_DIR  = 'test-results'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify Python') {
            steps {
                bat 'python --version'
            }
        }

        stage('Set Up Python Environment') {
            steps {
                bat '''
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    if exist requirements.txt (
                        pip install -r requirements.txt
                    ) else (
                        pip install streamlit pandas
                    )
                    pip install pytest pytest-cov
                '''
            }
        }

        stage('Run Streamlit AppTest Suite') {
            steps {
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    if not exist %TEST_RESULTS_DIR% mkdir %TEST_RESULTS_DIR%
                    pytest tests/ ^
                        --junitxml=%TEST_RESULTS_DIR%\\apptest-results.xml ^
                        --cov=. ^
                        --cov-report=xml:%TEST_RESULTS_DIR%\\coverage.xml ^
                        --cov-report=term ^
                        -v
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: "${TEST_RESULTS_DIR}\\apptest-results.xml"
            archiveArtifacts artifacts: "${TEST_RESULTS_DIR}\\**", allowEmptyArchive: true
        }
        success {
            echo 'AppTest suite passed.'
        }
        failure {
            echo 'AppTest suite failed - check the JUnit report for details.'
        }
        cleanup {
            bat 'rmdir /S /Q %VENV_DIR% 2>nul || exit 0'
        }
    }
}