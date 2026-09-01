[CmdletBinding()]
param(
    [ValidateSet('DryRun', 'Apply')]
    [string]$Mode = 'DryRun',
    [switch]$Update,
    [switch]$Replace,
    [string]$Target
)

$ErrorActionPreference = 'Stop'
$publicRepository = Split-Path -Parent $PSScriptRoot
$repositoriesRoot = Split-Path -Parent $publicRepository
$privateRepository = Join-Path $repositoriesRoot 'private'
$codexHomePath = if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) { Join-Path $env:USERPROFILE '.codex' } else { $env:CODEX_HOME }
$targetSkills = if ([string]::IsNullOrWhiteSpace($Target)) { Join-Path $codexHomePath 'skills' } else { $Target }

foreach ($repository in @($publicRepository, $privateRepository)) {
    if (-not (Test-Path -LiteralPath (Join-Path $repository '.git'))) {
        throw "Expected a Git repository at $repository. Clone public and private as sibling folders."
    }
    if ($Update) {
        $changes = @(git -C $repository status --porcelain)
        if ($changes.Count -gt 0) {
            throw "Refusing to update $repository because it has local changes. Commit, stash, or resolve them first."
        }
        & git -C $repository pull --ff-only
        if ($LASTEXITCODE -ne 0) { throw "Unable to fast-forward $repository." }
    }
}

$sourceSkills = @()
foreach ($repository in @($publicRepository, $privateRepository)) {
    $skillsDirectory = Join-Path $repository 'skills'
    if (Test-Path -LiteralPath $skillsDirectory) {
        $sourceSkills += Get-ChildItem -LiteralPath $skillsDirectory -Directory | ForEach-Object {
            [pscustomobject]@{ Name = $_.Name; Path = $_.FullName; Repository = $repository }
        }
    }
}

$duplicates = $sourceSkills | Group-Object Name | Where-Object Count -gt 1
if ($duplicates) {
    $names = ($duplicates | ForEach-Object Name) -join ', '
    throw "A skill exists in both repositories: $names. Keep each skill in exactly one source repository."
}

function Get-TreeFingerprint([string]$Path) {
    $files = Get-ChildItem -LiteralPath $Path -Recurse -File | Sort-Object FullName
    return ($files | ForEach-Object {
        $relative = $_.FullName.Substring($Path.Length).TrimStart('\', '/')
        "$relative $((Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash)"
    }) -join "`n"
}

if ($Mode -eq 'Apply' -and -not (Test-Path -LiteralPath $targetSkills)) {
    New-Item -ItemType Directory -Path $targetSkills -Force | Out-Null
}

$conflicts = @()
foreach ($source in $sourceSkills | Sort-Object Name) {
    $destination = Join-Path $targetSkills $source.Name
    if (-not (Test-Path -LiteralPath $destination)) {
        Write-Output "INSTALL $($source.Name) from $($source.Repository)"
        if ($Mode -eq 'Apply') { Copy-Item -LiteralPath $source.Path -Destination $destination -Recurse }
        continue
    }

    if ((Get-TreeFingerprint $source.Path) -eq (Get-TreeFingerprint $destination)) {
        Write-Output "UNCHANGED $($source.Name)"
        continue
    }

    if (-not $Replace) {
        $conflicts += $source.Name
        Write-Output "CONFLICT $($source.Name): local copy differs"
        continue
    }

    Write-Output "REPLACE $($source.Name) from $($source.Repository)"
    if ($Mode -eq 'Apply') {
        Remove-Item -LiteralPath $destination -Recurse -Force
        Copy-Item -LiteralPath $source.Path -Destination $destination -Recurse
    }
}

if ($conflicts.Count -gt 0) {
    throw "Local skill conflicts require review: $($conflicts -join ', '). Re-run with -Replace only when replacement is intended."
}

Write-Output "Skill sync completed: $Mode -> $targetSkills"
