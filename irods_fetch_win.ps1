# exec url: Invoke-Command -ScriptBlock ([Scriptblock]::Create((iwr "https://raw.githubusercontent.com/cemcof/cemcof.github.io/main/irods_fetch_win.ps1").Content)) -ArgumentList ($args + @('someargument'))

Write-Host "Welcome to irods_win_fetcher.ps1"
Write-Host $args
exit 

# Ensure python is installed and available
if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed. Please install python3 on your computer."
    exit
} 

# Ensure python-irodsclient is installed and available
python3 -c "import irods" 2>$null

if (-not ($?)) {
    Write-Host "irods python module is not installed. Installing irods..."
    python3 -m pip install python-irodsclient
    Write-Host "irods module has been successfully installed."
}

# Download and invoke the downloader script 
$scriptUrl = "https://raw.githubusercontent.com/cemcof/cemcof.github.io/main/irods_fetch.py"
$pythonScript = (Invoke-WebRequest -Uri $scriptUrl).Content
# Write-Host $pythonScript
exit
$pythonScript | python3 - 


# Or rather save it to tempfile first? 
# $scriptTempPath = [System.IO.Path]::GetTempFileName() + ".py"
# $pythonScript | Set-Content -Path $scriptTempPath
# python3 $scriptTempPath
# Remove-Item -Path $scriptTempPath -Force