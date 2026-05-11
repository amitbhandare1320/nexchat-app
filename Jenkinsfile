pipeline {
    agent any

    environment {
        EC2_HOST = '13.202.37.196'
        EC2_USER = 'ubuntu'
        APP_DIR  = '/opt/nexchat'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== Getting code from GitHub ==='
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '=== Building Docker image ==='
                sh 'docker build -t nexchat-app:latest .'
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo '=== Deploying to EC2 ==='
                sshagent(['nexchat-ec2-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} "
                            cd ${APP_DIR} &&
                            git pull origin main &&
                            docker compose up -d --build &&
                            docker compose ps
                        "
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                echo '=== Checking app is running ==='
                sh 'sleep 10 && curl -s -o /dev/null -w "%{http_code}" http://${EC2_HOST} || echo "Check manually"'
            }
        }
    }

    post {
        success { echo '✅ NexChat deployed successfully!' }
        failure { echo '❌ Deployment failed! Check logs.' }
    }
}
