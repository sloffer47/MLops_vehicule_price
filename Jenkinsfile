pipeline {
    agent any

    options {
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
    }

    environment {
        EC2_HOST = '51.21.194.2'
        EC2_USER = 'ubuntu'
        APP_NAME = 'vehicule_price_api'
        GITHUB_REPO = 'https://github.com/sloffer47/MLops_vehicule_price.git'
        SSH_CREDENTIALS = 'server_key1'
        DOCKER_IMAGE = 'vehicule-price-api:latest'
        APP_PORT = '8000'
        MAX_RETRIES = 3
    }

    stages {
        stage('🔍 Pull Code from GitHub') {
            steps {
                echo '📦 Clonage du dépôt depuis GitHub...'
                git branch: 'main', url: "${GITHUB_REPO}"
            }
        }

        stage('📁 Vérification du projet') {
            steps {
                script {
                    echo '🔎 Vérification des fichiers du projet...'
                    sh 'ls -la'
                    def dockerfileExists = fileExists 'Dockerfile'
                    if (!dockerfileExists) {
                        error "⚠️ Dockerfile manquant !"
                    }
                }
            }
        }

        stage('🔑 Test SSH Connection to EC2') {
            steps {
                echo '🔐 Test de connexion SSH au serveur EC2...'
                sshagent([SSH_CREDENTIALS]) {
                    retry(3) {
                        sh 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 ${EC2_USER}@${EC2_HOST} "echo ✅ Connexion SSH réussie au serveur ${EC2_HOST}"'
                    }
                }
            }
        }

        stage('📦 Backup') {
            steps {
                sshagent([SSH_CREDENTIALS]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} "
                            if [ -d ${APP_NAME} ]; then
                                tar -czf ${APP_NAME}_backup_\$(date +%Y%m%d_%H%M%S).tar.gz ${APP_NAME}
                            fi
                        "
                    """
                }
            }
        }

        stage('🚀 Deploy to EC2 Server') {
            steps {
                echo "🚢 Déploiement du container sur EC2 (${EC2_HOST})..."
                sshagent([SSH_CREDENTIALS]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} "
                            set -e
                            
                            echo \\"🧹 Nettoyage des anciens containers...\\"
                            docker stop ${APP_NAME} 2>/dev/null || true
                            docker rm ${APP_NAME} 2>/dev/null || true
                            docker rmi ${DOCKER_IMAGE} 2>/dev/null || true

                            echo \\"📥 Mise à jour du code source depuis GitHub...\\"
                            if [ -d ${APP_NAME} ]; then
                                cd ${APP_NAME}
                                git fetch origin
                                git reset --hard origin/main
                                cd ..
                            else
                                git clone ${GITHUB_REPO}
                            fi

                            echo \\"🔨 Construction de l'image Docker...\\"
                            cd ${APP_NAME}
                            docker build --no-cache -t ${DOCKER_IMAGE} .

                            echo \\"🚀 Lancement du container sur le port ${APP_PORT}...\\"
                            docker run -d --name ${APP_NAME} -p ${APP_PORT}:${APP_PORT} --restart unless-stopped ${DOCKER_IMAGE}

                            # Vérification que le container est bien démarré
                            if ! docker ps | grep -q ${APP_NAME}; then
                                echo \\"❌ Erreur de déploiement !\\"
                                docker logs ${APP_NAME}
                                exit 1
                            fi

                            echo \\"✅ Container déployé avec succès !\\"
                            
                            echo \\"🧹 Nettoyage des images Docker inutiles...\\"
                            docker image prune -f
                        "
                    """
                }
            }
        }

        stage('🏥 Health Check') {
            steps {
                echo '💊 Vérification de la santé de l'API...'
                script {
                    retry(3) {
                        sleep(time: 20, unit: 'SECONDS')
                        def response = sh(
                            script: """
                                curl -s -f -m 30 -o /dev/null -w '%{http_code}' http://${EC2_HOST}:${APP_PORT}/health || echo 'failed'
                            """,
                            returnStdout: true
                        ).trim()
                        
                        if (response == '200') {
                            echo "✅ SUCCESS: API accessible et opérationnelle !"
                        } else {
                            error "⚠️ Health check failed with response: ${response}"
                        }
                    }
                }
            }
        }
    }

    // ... rest of your post section remains the same ...
}