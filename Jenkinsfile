pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        ENV_ORDER = "dev int prod"
    }

    stages {
        stage('Detect changed deploy configs') {
            steps {
                script {
                    sh 'git fetch --tags --force'

                    def changed = sh(
                        script: '''
                            git diff --name-only HEAD~1 HEAD \
                                | grep '^deploy/inventory/.*yaml$' \
                                | sort || true
                            ''',
                        returnStdout: true
                    ).trim()

                    if (!changed) {
                        currentBuild.description = "No deploy config changes"
                        env.CHANGED_ENVS = ""
                        return
                    }

                    def envs = []
                    changed.split("\\n").each { file ->
                        def envName = file.replace("deploy/inventory/", "").replace(".yaml", "")
                        if (["dev", "int", "prod"].contains(envName)) {
                            envs.add(envName)
                        }
                    }

                    def order = env.ENV_ORDER.split(" ")
		    echo "sorted: $envs (koniec)"
                    envs = envs.unique().sort { a, b -> order.indexOf(a) <=> order.indexOf(b) }

                    env.CHANGED_ENVS = envs.join(" ")
                    currentBuild.description = "Deploy: ${env.CHANGED_ENVS}"
                }
            }
        }

        stage('Deploy dev') {
            when {
                expression { env.CHANGED_ENVS?.split(" ")?.contains("dev") }
            }
            steps {
                configFileProvider([
                    configFile(fileId: 'pogoda-dev-specifics', targetLocation: '.jenkins_connection.yml')
                ]) {
                    sh '''
                       ansible-playbook -vvvv \
                         -i deploy/inventory/dev.yaml \
                         -i .jenkins_connection.yml \
                         deploy/pogoda.yml
                       '''
                }
            }
        }

        stage('Deploy int') {
            when {
                expression { env.CHANGED_ENVS?.split(" ")?.contains("int") }
            }
            steps {
                configFileProvider([
                    configFile(fileId: 'pogoda-int-specifics', targetLocation: '.jenkins_connection.yml')
                ]) {
                    sh '''
                       ansible-playbook \
                         -i deploy/inventory/int.yaml \
                         -i .jenkins_connection.yml \
                         deploy/pogoda.yml
                       '''
                }
            }
        }

        stage('Deploy prod') {
            when {
                expression { env.CHANGED_ENVS?.split(" ")?.contains("prod") }
            }
            steps {
                configFileProvider([
                    configFile(fileId: 'pogoda-prod-specifics', targetLocation: '.jenkins_connection.yml')
                ]) {
                    sh '''
                       ansible-playbook \
                         -i deploy/inventory/prod.yaml \
                         -i .jenkins_connection.yml \
                         deploy/pogoda.yml
                       '''
                }
            }
        }
    }
}
