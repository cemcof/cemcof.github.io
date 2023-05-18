# exec url: Invoke-Command -ScriptBlock ([Scriptblock]::Create((iwr "https://raw.githubusercontent.com/cemcof/cemcof.github.io/main/irods_fetch_win.ps1").Content)) -ArgumentList ($args + @('someargument'))
Write-Host "Welcome to irods_win_fetcher.ps1"
Write-Host $args