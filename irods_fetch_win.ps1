# exec url: Invoke-Command -ScriptBlock ([Scriptblock]::Create((iwr "https://raw.githubusercontent.com/cemcof/cemcof.github.io/main/irods_fetch_win.ps1").Content)) -ArgumentList ($args + @('someargument'))

Write-Host "Welcome to irods_win_fetcher.ps1"
Write-Host $args

# Ensure python is installed and available
if (-not (Test-Path (Get-Command python3 -ErrorAction SilentlyContinue))) {
    Write-Host "Python is not installed. Installing Python..."
    # Python is not available, install it via chocolatey...
    # Check if Chocolatey is installed
    if (-not (Test-Path (Get-Command choco -ErrorAction SilentlyContinue))) {
        Write-Host "Chocolatey is necessary for installing python. Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
        Write-Host "Chocolatey has been succesfully installed."
    } 

    choco install python -y
    Write-Host "Python has been successfully installed."
} 

# Ensure python-irodsclient is installed and available
if (-not (python3 -c "import irods" 2>&1)) {
    Write-Host "irods module is not installed. Installing irods..."
    python3 -m pip install irods
    Write-Host "`e[32mirods module has been successfully installed.`e[0m"
}

# Download and invoke the downloader script 
$scriptUrl = "https://raw.githubusercontent.com/cemcof/cemcof.github.io/main/irods_fetch.py"
$pythonScript = (Invoke-WebRequest -Uri $scriptUrl).Content
python3 -c $pythonScript 

# Or rather save it to tempfile first? 
#  $scriptTempPath = [System.IO.Path]::GetTempFileName() + ".py"
#  $pythonScript | Set-Content -Path $scriptTempPath
#  python3 $scriptTempPath
#  Remove-Item -Path $scriptTempPath -Force