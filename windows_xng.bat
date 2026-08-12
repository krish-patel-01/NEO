@echo off
:: Variables
set PORT=8080

:: Find the PID of the process using the specified port
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :%PORT%') DO (
    set PID=%%P
)

:: Kill the process if a PID is found
if defined PID (
    echo Terminating process on port %PORT% with PID %PID%...
    taskkill /F /PID %PID%
) else (
    echo No process found on port %PORT%.
)

:: Run the Docker container
docker run --rm ^
           -d -p %PORT%:8080 ^
           -v "%cd%\searxng:/etc/searxng" ^
           -e "BASE_URL=http://localhost:%PORT%/" ^
           -e "INSTANCE_NAME=my-instance" ^
           searxng/searxng
