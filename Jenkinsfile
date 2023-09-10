pipeline {
    agent none
    stages {
        stage('build-all') {
            parallel {
                stage('linux-build') {
                    agent {label 'linux-node'}
                    steps {
                        sh "pip3 install --upgrade pip"
                        sh "pip3 install virtualenv"
                        sh "python3 -m virtualenv venv"
                        sh "venv/bin/pip install pyinstaller requests"
                        sh "pwd"
                        sh "venv/bin/pyinstaller --onefile --noconsole src/network_health.py --name network_health"
                        sh "mkdir linux_x86/"
                        sh "cp dist/network_health linux_x86/"
                        archiveArtifacts artifacts: 'linux_x86/*', fingerprint: true
                        sh "rm -rf dist"
                        sh "rm -rf linux_x86"
                        sh "rm -rf build"
                        sh "rm *.spec"
                        sh "rm -rf venv"
                    }
                }
                stage('windows-build') {
                    agent {label 'windows-node'} 
                    steps {
                        powershell "C:/Users/jenkins/AppData/Local/Programs/Python/Python311/python.exe --version"
                        powershell "C:/Users/jenkins/AppData/Local/Programs/Python/Python311/python.exe -m pip install --upgrade pip"
                        powershell "C:/Users/jenkins/AppData/Local/Programs/Python/Python311/python.exe -m pip install virtualenv"
                        powershell "C:/Users/jenkins/AppData/Local/Programs/Python/Python311/python.exe -m virtualenv venv"
                        powershell "venv/Scripts/python.exe -m pip install --upgrade pip"
                        powershell "venv/Scripts/python.exe -m pip install requests pyinstaller"
                        powershell "venv/Scripts/pyinstaller.exe --onefile --noconsole src/network_health.py --name network_health.exe"
                        powershell "New-Item -Name 'windows_x86' -ItemType 'directory'"
                        powershell "Copy-Item dist/network_health.exe windows_x86"
                        archiveArtifacts artifacts: 'windows_x86/*', fingerprint: true
                        powershell "Remove-Item -Recurse dist"
                        powershell "Remove-Item -Recurse windows_x86"
                        powershell "Remove-Item -Recurse build"
                        powershell "Remove-Item *.spec"
                        powershell "Remove-Item -Recurse venv"
                    }
                }
                stage('mac-build') {
                    agent {label 'mac-node'}
                    steps {
                        sh "pip3 install --upgrade pip"
                        sh "pip3 install virtualenv"
                        sh "python3 -m virtualenv venv"
                        sh "venv/bin/pip install pyinstaller requests"
                        sh "pwd"
                        sh "venv/bin/pyinstaller --onefile --noconsole src/network_health.py --name network_health"
                        sh "mkdir macos_x86/"
                        sh "cp dist/network_health macos_x86/"
                        archiveArtifacts artifacts: 'macos_x86/*', fingerprint: true
                        sh "rm -rf dist"
                        sh "rm -rf macos_x86"
                        sh "rm -rf build"
                        sh "rm *.spec"
                        sh "rm -rf venv"
                    }
                }
            }
        }
    }
}