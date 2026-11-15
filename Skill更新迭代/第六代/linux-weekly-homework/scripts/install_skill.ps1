param([string]$DestinationRoot)
$ErrorActionPreference = 'Stop'
$taskSource = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not $DestinationRoot) {
    $taskCodexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
    $DestinationRoot = Join-Path $taskCodexRoot 'skills'
}
$taskDeployRoot = [System.IO.Path]::GetFullPath($DestinationRoot)
$taskDestination = [System.IO.Path]::GetFullPath((Join-Path $taskDeployRoot 'linux-weekly-homework'))
if ($taskDestination -eq $taskSource) { throw 'Source and deployed skill are the same path.' }
$taskText = Get-Content -LiteralPath (Join-Path $taskSource 'SKILL.md') -Raw -Encoding UTF8
if ($taskText -notmatch '(?m)^name: linux-weekly-homework\s*$') { throw 'Unexpected skill identity.' }
# Stage and validate before replacing an existing deployment. All moves stay
# within the explicitly resolved deployment root; an old version is retained.
$taskId = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$taskStage = Join-Path $taskDeployRoot ('.linux-weekly-homework-stage-' + $taskId)
$taskArchiveRoot = Join-Path (Split-Path $taskDeployRoot -Parent) 'skill-deployment-backups'
$taskBackup = Join-Path $taskArchiveRoot ('linux-weekly-homework-' + $taskId)
foreach ($taskTarget in @($taskStage, $taskDestination)) {
    $taskResolved = [System.IO.Path]::GetFullPath($taskTarget)
    if (-not $taskResolved.StartsWith($taskDeployRoot.TrimEnd('\','/') + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Deployment path escaped its root.'
    }
}
if (-not ([System.IO.Path]::GetFullPath($taskBackup)).StartsWith(([System.IO.Path]::GetFullPath($taskArchiveRoot)).TrimEnd('\','/') + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Backup path escaped its root.'
}
New-Item -ItemType Directory -Path $taskDeployRoot -Force | Out-Null
Copy-Item -LiteralPath $taskSource -Destination $taskStage -Recurse
$taskFiles = Get-ChildItem -LiteralPath $taskSource -Recurse -File
foreach ($taskFile in $taskFiles) {
    $taskRelative = $taskFile.FullName.Substring($taskSource.Length + 1)
    $taskStagedFile = Join-Path $taskStage $taskRelative
    if ((Get-FileHash -LiteralPath $taskFile.FullName -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $taskStagedFile -Algorithm SHA256).Hash) {
        throw ('Staging verification failed: ' + $taskRelative)
    }
}
if (Test-Path -LiteralPath $taskDestination) {
    New-Item -ItemType Directory -Path $taskArchiveRoot -Force | Out-Null
    Move-Item -LiteralPath $taskDestination -Destination $taskBackup
}
try {
    Move-Item -LiteralPath $taskStage -Destination $taskDestination
} catch {
    if ((Test-Path -LiteralPath $taskBackup) -and -not (Test-Path -LiteralPath $taskDestination)) {
        Move-Item -LiteralPath $taskBackup -Destination $taskDestination
    }
    throw
}
foreach ($taskFile in $taskFiles) {
    $taskRelative = $taskFile.FullName.Substring($taskSource.Length + 1)
    if ((Get-FileHash -LiteralPath $taskFile.FullName -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath (Join-Path $taskDestination $taskRelative) -Algorithm SHA256).Hash) {
        throw ('Deployed file verification failed: ' + $taskRelative)
    }
}
Write-Output ('Installed: ' + $taskDestination)
Write-Output ('Verified SHA-256 for ' + $taskFiles.Count + ' files.')
if (Test-Path -LiteralPath $taskBackup) { Write-Output ('Previous deployment retained: ' + $taskBackup) }
