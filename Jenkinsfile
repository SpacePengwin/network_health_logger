pipeline {
    agent none
    stages {
        parallel {
            stage('linux-build') {
                agent {label 'linux-node'}
                steps {
                    sh "pip3 install --upgrade pip"
                    sh "pip3 install virtualenv"
                    sh "python3 -m virtualenv /tmp/venv"
                    sh "/tmp/venv/bin/pip install pyinstaller requests"
                    sh "pwd"
                    sh "/tmp/venv/bin/pyinstaller --onefile --noconsole src/network_health.py --name nework_health_linux_x86"
                    archiveArtifacts artifacts: 'dist/*', fingerprint: true
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
                    powershell "venv/Scripts/pyinstaller.exe --onefile --noconsole src/network_health.py --name network_health_windows_x86.exe"
                    archiveArtifacts artifacts: 'dist/*', fingerprint: true
                }
            }
            stage('mac-build') {
                agent {label 'mac-node'}
                steps {
                    sh "rm -rf dist/"
                    sh "pip3 install --upgrade pip"
                    sh "pip3 install virtualenv"
                    sh "python3 -m virtualenv /tmp/venv"
                    sh "/tmp/venv/bin/pip install pyinstaller requests"
                    sh "pwd"
                    sh "/tmp/venv/bin/pyinstaller --onefile --noconsole src/network_health.py --name network_health_macos"
                    archiveArtifacts artifacts: 'dist/*', fingerprint: true
                }
            }
        }
    }
}