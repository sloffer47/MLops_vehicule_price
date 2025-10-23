pipeline {
    agent any

    environment {
        EC2_HOST = '13.61.100.51'                         // ✅ Nouvelle IP EC2
        EC2_USER = 'ubuntu'                               // Utilisateur EC2 par défaut
        APP_NAME = 'vehicule_price_api'                   // Nom du container / app
        GITHUB_REPO = 'https://github.com/sloffer47/MLops_vehicule_price.git'   // ⚙️ Ton repo GitHub
        SSH_CREDENTIALS = 'serveur_ssh_key'               // ⚙️ Nom du credential Jenkins (clé SSH)
        DOCKER_IMAGE = 'vehicule-price-api:latest'        // Nom de ton image Docker locale
        APP_PORT = '8000'                                 // Port exposé par FastAPI
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
                sshagent(['serveur_ssh_key']) {
                    sh 'ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} "echo ✅ Connexion SSH OK"'
                }
            }
        }

        stage('🚀 Deploy to EC2 Server') {
            steps {
                echo '🚢 Déploiement du container sur EC2...'
                sshagent(credentials: ["${SSH_CREDENTIALS}"]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            echo "🧹 Nettoyage des anciens containers..."
                            docker stop ${APP_NAME} 2>/dev/null || true
                            docker rm ${APP_NAME} 2>/dev/null || true
                            docker rmi ${DOCKER_IMAGE} 2>/dev/null || true

                            echo "📥 Mise à jour du code source..."
                            if [ -d "${APP_NAME}" ]; then
                                cd ${APP_NAME}
                                git pull origin main
                                cd ..
                            else
                                git clone ${GITHUB_REPO}
                            fi

                            echo "🔨 Construction de l'image Docker..."
                            cd ${APP_NAME}
                            docker build -t ${DOCKER_IMAGE} .

                            echo "🚀 Lancement du container..."
                            docker run -d \\
                                --name ${APP_NAME} \\
                                -p ${APP_PORT}:${APP_PORT} \\
                                --restart unless-stopped \\
                                ${DOCKER_IMAGE}

                            echo "✅ Container déployé !"
                            docker ps | grep ${APP_NAME} || (echo "❌ Erreur de déploiement !" && exit 1)

                            echo "🧹 Nettoyage des images inutiles..."
                            docker image prune -f
                        '
                    """
                }
            }
        }

        stage('🏥 Health Check') {
            steps {
                echo '💊 Vérification de la santé du service...'
                script {
                    sleep(10)
                    try {
                        def response = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://${EC2_HOST}:${APP_PORT}/health",
                            returnStdout: true
                        ).trim()
                        if (response == '200') {
                            echo "✅ SUCCESS: API accessible à http://${EC2_HOST}:${APP_PORT}/docs"
                        } else {
                            echo "⚠️ WARNING: Réponse HTTP inattendue: ${response}"
                        }
                    } catch (Exception e) {
                        echo "⚠️ Impossible de tester l'API — vérifier le port ou le pare-feu."
                    }
                }
            }
        }
    }

    post {
        success {
            echo """
            🎉🎉🎉 DÉPLOIEMENT RÉUSSI 🎉🎉🎉

            🚗 Ton API est accessible ici :
            🌐 http://${EC2_HOST}:${APP_PORT}/docs

            🔍 Vérifie les logs du container :
            docker logs ${APP_NAME}

            📊 Conteneurs actifs :
            docker ps
            """
        }

        failure {
            echo """
            ❌ DÉPLOIEMENT ÉCHOUÉ ❌

            Vérifie les logs pour trouver le problème :
            ssh -i serveur_KEY.pem ubuntu@${EC2_HOST}
            docker logs ${APP_NAME}
            docker ps -a
            """
        }

        always {
            echo '🏁 Pipeline terminé.'
        }
    }
}
