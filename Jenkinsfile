pipeline {
    agent any

    environment {
        EC2_HOST = '51.21.194.2'                          // ✅ NOUVELLE IP EC2
        EC2_USER = 'ubuntu'                               // Utilisateur Ubuntu
        APP_NAME = 'vehicule_price_api'                   // Nom du container / app
        GITHUB_REPO = 'https://github.com/sloffer47/MLops_vehicule_price.git'
        SSH_CREDENTIALS = 'server_key1'                   // ⚙️ Nom du credential (server_key1)
        DOCKER_IMAGE = 'vehicule-price-api:latest'        // Nom de l'image Docker
        APP_PORT = '8000'                                 // Port FastAPI
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
                echo '🔎 Vérification des fichiers du projet...'
                sh 'ls -la'
                sh 'cat Dockerfile || echo "⚠️ Dockerfile manquant !"'
            }
        }

        stage('🔑 Test SSH Connection to EC2') {
            steps {
                echo '🔐 Test de connexion SSH au serveur EC2...'
                sshagent([SSH_CREDENTIALS]) {
                    sh 'ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} "echo ✅ Connexion SSH réussie au serveur 51.21.194.2"'
                }
            }
        }

        stage('🚀 Deploy to EC2 Server') {
            steps {
                echo '🚢 Déploiement du container sur EC2 (51.21.194.2)...'
                sshagent(credentials: [SSH_CREDENTIALS]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} "bash -c '
                            echo \\"🧹 Nettoyage des anciens containers...\\"
                            docker stop ${APP_NAME} 2>/dev/null || true
                            docker rm ${APP_NAME} 2>/dev/null || true
                            docker rmi ${DOCKER_IMAGE} 2>/dev/null || true

                            echo \\"📥 Mise à jour du code source depuis GitHub...\\"
                            if [ -d \\\"${APP_NAME}\\\" ]; then
                                cd ${APP_NAME}
                                git pull origin main
                                cd ..
                            else
                                git clone ${GITHUB_REPO}
                            fi

                            echo \\"🔨 Construction de l'image Docker...\\"
                            cd ${APP_NAME}
                            docker build -t ${DOCKER_IMAGE} .

                            echo \\"🚀 Lancement du container sur le port ${APP_PORT}...\\"
                            docker run -d --name ${APP_NAME} -p ${APP_PORT}:${APP_PORT} --restart unless-stopped ${DOCKER_IMAGE}

                            echo \\"✅ Container déployé avec succès !\\"
                            docker ps | grep ${APP_NAME} || (echo \\"❌ Erreur de déploiement !\\" && exit 1)

                            echo \\"🧹 Nettoyage des images Docker inutiles...\\"
                            docker image prune -f
                        '"
                    """
                }
            }
        }

        stage('🏥 Health Check') {
            steps {
                echo '💊 Vérification de la santé de l’API...'
                script {
                    sleep(10)
                    try {
                        def response = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://${EC2_HOST}:${APP_PORT}/health",
                            returnStdout: true
                        ).trim()
                        if (response == '200') {
                            echo "✅ SUCCESS: API accessible et opérationnelle !"
                            echo "📖 Documentation Swagger: http://${EC2_HOST}:${APP_PORT}/docs"
                        } else {
                            echo "⚠️ WARNING: Code de réponse HTTP: ${response}"
                        }
                    } catch (Exception e) {
                        echo "⚠️ Impossible de tester l’API - Vérifiez le Security Group AWS (port ${APP_PORT})"
                    }
                }
            }
        }
    }

    post {
        success {
            echo """
            🎉🎉🎉 DÉPLOIEMENT RÉUSSI 🎉🎉🎉

            🚗 Votre API MLOps de prédiction de prix de véhicules est accessible :
            🌐 Swagger UI: http://51.21.194.2:8000/docs
            🏥 Health Check: http://51.21.194.2:8000/health
            🔮 Prédiction: http://51.21.194.2:8000/predict

            🔍 Commandes utiles :
            ssh -i server_key1.pem ubuntu@51.21.194.2
            docker logs vehicule_price_api
            docker ps
            curl http://51.21.194.2:8000/health
            """
        }

        failure {
            echo """
            ❌ DÉPLOIEMENT ÉCHOUÉ ❌

            🔍 Vérifiez les logs pour identifier le problème :
            ssh -i server_key1.pem ubuntu@51.21.194.2
            docker logs vehicule_price_api
            docker ps -a

            ⚙️ Vérifiez aussi :
            - Le Security Group AWS (port 8000 ouvert ?)
            - Docker est installé sur EC2 ?
            - Les credentials SSH dans Jenkins sont corrects ?
            """
        }

        always {
            echo '🏁 Pipeline terminé.'
        }
    }
}
