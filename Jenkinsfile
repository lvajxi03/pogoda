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
                lock(resource: 'weather-dev') {
                    configFileProvider([
                        configFile(fileId: 'pogoda-dev-specifics', variable: 'CONNECTION_FILE')
                    ]) {
                        sh '''
                           ansible-playbook \
                             -i deploy/inventory/dev.yml \
                             -i "$CONNECTION_FILE" \
                             deploy/playbook.yml
                           '''
                    }
                }
            }
        }

        stage('Deploy int') {
            when {
                expression { env.CHANGED_ENVS?.split(" ")?.contains("int") }
            }
            steps {
                lock(resource: 'weather-int') {
                    configFileProvider([
                        configFile(fileId: 'pogoda-int-specifics', variable: 'CONNECTION_FILE')
                    ]) {
                        sh '''
                           ansible-playbook \
                             -i deploy/inventory/int.yml \
                             -i "$CONNECTION_FILE" \
                             deploy/playbook.yml
                           '''
                    }
                }
            }
        }

        stage('Deploy prod') {
            when {
                expression { env.CHANGED_ENVS?.split(" ")?.contains("prod") }
            }
            steps {
                lock(resource: 'weather-prod') {
                    configFileProvider([
                        configFile(fileId: 'pogoda-prod-specifics', variable: 'CONNECTION_FILE')
                    ]) {
                        sh '''
                           ansible-playbook \
                             -i deploy/inventory/prod.yml \
                             -i "$CONNECTION_FILE" \
                             deploy/playbook.yml
                           '''
                    }
                }
            }
        }
    }
}

