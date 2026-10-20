@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

if "%JAVA_HOME%"=="" (
    if exist "%USERPROFILE%\.antigravity\extensions\redhat.java-1.55.0-win32-x64\jre\21.0.11-win32-x86_64\bin\java.exe" (
        set "JAVA_HOME=%USERPROFILE%\.antigravity\extensions\redhat.java-1.55.0-win32-x64\jre\21.0.11-win32-x86_64"
    ) else if exist "%USERPROFILE%\.antigravity-ide\extensions\redhat.java-1.58.0-win32-x64\jre\25.0.4.1-win32-x86_64\bin\java.exe" (
        set "JAVA_HOME=%USERPROFILE%\.antigravity-ide\extensions\redhat.java-1.58.0-win32-x64\jre\25.0.4.1-win32-x86_64"
    )
)

set "PATH=%JAVA_HOME%\bin;%PATH%"

if exist "%SCRIPT_DIR%.tools\apache-maven-3.9.6\bin\mvn.cmd" (
    "%SCRIPT_DIR%.tools\apache-maven-3.9.6\bin\mvn.cmd" %*
) else (
    echo Error: Maven not found in .tools/apache-maven-3.9.6. Please install Maven or run setup.
    exit /b 1
)
