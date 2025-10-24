pipeline {
    agent any

    environment {
        EC2_HOST = '51.21.194.2'
        EC2_USER = 'ubuntu'
        APP_NAME = 'vehicule_price_api'
        GITHUB_REPO = 'https://github.com/sloffer47/MLops_vehicule_price.git'
        SSH_CREDENTIALS = 'server_key1'
        DOCKER_IMAGE = 'vehicule-price-api:latest'
        APP_PORT = '8000'
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
                    sh "ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} 'echo ✅ Connexion SSH réussie'"
                }
            }
        }

        stage('🧹 Nettoyage préventif EC2') {
            steps {
                echo '🗑️ Libération d\'espace disque sur EC2...'
                sshagent(credentials: [SSH_CREDENTIALS]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << 'ENDSSH'
                            echo "📊 Espace disque AVANT nettoyage :"
                            df -h /
                            
                            echo "🧹 Nettoyage Docker agressif..."
                            docker system prune -a --volumes -f || true
                            
                            echo "🗑️ Suppression anciens builds..."
                            rm -rf ~/MLops_vehicule_price 2>/dev/null || true
                            
                            echo "📊 Espace disque APRÈS nettoyage :"
                            df -h /
ENDSSH
                    """
                }
            }
        }

        stage('🚀 Deploy to EC2 Server') {
            steps {
                echo "🚢 Déploiement du container sur EC2 (${EC2_HOST})..."
                sshagent(credentials: [SSH_CREDENTIALS]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << 'ENDSSH'
                            echo "🛑 Arrêt des anciens containers..."
                            docker stop vehicule_price_api 2>/dev/null || true
                            docker rm vehicule_price_api 2>/dev/null || true

                            echo "📥 Clone du code depuis GitHub..."
                            cd ~ || exit 1
                            git clone https://github.com/sloffer47/MLops_vehicule_price.git
                            cd MLops_vehicule_price || exit 1

                            echo "🔨 Construction de l'image Docker..."
                            docker build --no-cache -t vehicule-price-api:latest . || exit 1

                            echo "🚀 Lancement du container..."
                            docker run -d --name vehicule_price_api -p 8000:8000 --restart unless-stopped vehicule-price-api:latest

                            echo "✅ Déploiement terminé !"
                            docker ps | grep vehicule_price_api || (echo "❌ Container introuvable" && exit 1)
ENDSSH
                    """
                }
            }
        }

        stage('🏥 Health Check') {
            steps {
                echo '💊 Vérification de la santé de l\'API...'
                script {
                    sleep(10)
                    try {
                        def response = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://${EC2_HOST}:${APP_PORT}/health || echo '000'",
                            returnStdout: true
                        ).trim()
                        
                        if (response == '200') {
                            echo "✅ SUCCESS: API accessible et opérationnelle !"
                            echo "📖 Documentation Swagger: http://${EC2_HOST}:${APP_PORT}/docs"
                        } else {
                            echo "⚠️ WARNING: Code de réponse HTTP: ${response}"
                        }
                    } catch (Exception e) {
                        echo "⚠️ Impossible de tester l'API - Vérifiez le Security Group AWS (port ${APP_PORT}) ou les logs Docker sur EC2."
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
            🌐 Swagger UI: http://${EC2_HOST}:${APP_PORT}/docs
            🏥 Health Check: http://${EC2_HOST}:${APP_PORT}/health
            🔮 Prédiction: http://${EC2_HOST}:${APP_PORT}/predict

            🔍 Commandes utiles :
            ssh -i server_key1.pem ubuntu@${EC2_HOST}
            docker logs ${APP_NAME}
            """
        }

        failure {
            echo """
            ❌ DÉPLOIEMENT ÉCHOUÉ ❌

            🔍 Vérifiez les logs pour identifier le problème :
            ssh -i server_key1.pem ubuntu@${EC2_HOST}
            docker logs ${APP_NAME}
            docker ps -a

            ⚙️ Vérifiez aussi :
            - Le Security Group AWS (port ${APP_PORT} ouvert ?)
            - Docker est installé sur EC2 ?
            - Les credentials SSH dans Jenkins sont corrects ?
            """
        }

        always {
            echo '🏁 Pipeline terminé.'
        }
    }
}
