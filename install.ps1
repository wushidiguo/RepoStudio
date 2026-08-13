<#
RepoStudio - one-click installer for the `repo-to-video` Codex skill.

Default behavior:
  1. Copies skills/repo-to-video into $CODEX_HOME\skills (or ~\.codex\skills).
  2. Checks prerequisites and prints a status table.

Optional flags:
  -InstallDeps       Install missing core prerequisites via winget (git, node,
                     python, ffmpeg, gh) where available.
  -InstallTts        pip install edge-tts (CPU fallback TTS).
  -InstallRenderDeps npm install the bundled Remotion template.
  -InstallAnalysis   Install codebase-memory-mcp (deep code analysis MCP).
  -Full              Same as all of the above.

Examples:
  .\install.ps1
  .\install.ps1 -Full
  .\install.ps1 -Target "$HOME\.agents\skills"
#>
[CmdletBinding()]
param(
    [string]$SkillName = 'repo-to-video',
    [string]$Source = '',
    [string]$Target = '',
    [switch]$InstallDeps,
    [switch]$InstallTts,
    [switch]$InstallRenderDeps,
    [switch]$InstallAnalysis,
    [switch]$Full
)

$ErrorActionPreference = 'Stop'

if (-not $Source) {
    $scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
    $Source = Join-Path $scriptRoot 'skills'
}

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-Command([string]$Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) { return $false }
    try {
        $out = & $cmd.Source --version 2>&1 | Select-Object -First 1
        return -not [string]::IsNullOrWhiteSpace("$out")
    } catch {
        return $false
    }
}

if (-not $Target) {
    $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
    $Target = Join-Path $codexHome 'skills'
}

$srcDir = Join-Path $Source $SkillName
$dstDir = Join-Path $Target $SkillName

if (-not (Test-Path -LiteralPath $srcDir)) {
    Write-Error "Skill source not found: $srcDir"
    exit 1
}

Write-Step "Installing skill '$SkillName' into $Target"
New-Item -ItemType Directory -Force -Path $Target | Out-Null

if (Test-Path -LiteralPath $dstDir) {
    $resolved = (Resolve-Path -LiteralPath $dstDir).Path
    $resolvedTarget = (Resolve-Path -LiteralPath $Target).Path
    if (-not $resolved.StartsWith($resolvedTarget, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Error "Refusing to remove path outside target: $resolved"
        exit 1
    }
    Write-Step "Replacing existing skill at $dstDir"
    Remove-Item -LiteralPath $dstDir -Recurse -Force
}

Copy-Item -LiteralPath $srcDir -Destination $dstDir -Recurse -Force
Write-Host "    Copied -> $dstDir" -ForegroundColor Green

$prereqs = @(
    @{ Name = 'git';           Needed = $true },
    @{ Name = 'node';          Needed = $true },
    @{ Name = 'npm';           Needed = $true },
    @{ Name = 'python';        Needed = $true },
    @{ Name = 'ffmpeg';        Needed = $true },
    @{ Name = 'gh';            Needed = $false },
    @{ Name = 'codebase-memory-mcp'; Needed = $false }
)

Write-Step "Checking prerequisites"
$missing = @()
foreach ($p in $prereqs) {
    $ok = Test-Command $p.Name
    $status = if ($ok) { 'OK' } else { 'MISSING' }
    Write-Host ("    {0,-22} {1}" -f $p.Name, $status)
    if (-not $ok) {
        if ($p.Needed) { $missing += $p.Name }
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing required tools: $($missing -join ', ')" -ForegroundColor Yellow
    Write-Host "Re-run with -InstallDeps (winget) or install them manually." -ForegroundColor Yellow
}

if ($Full -or $InstallDeps) {
    Write-Step "Installing missing core tools via winget"
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        Write-Host "    winget not available; install tools manually." -ForegroundColor Yellow
    } else {
        $wingetPackages = @(
            @{ Name = 'git';    Id = 'Git.Git' },
            @{ Name = 'node';   Id = 'OpenJS.NodeJS.LTS' },
            @{ Name = 'python'; Id = 'Python.Python.3.12' },
            @{ Name = 'ffmpeg'; Id = 'Gyan.FFmpeg' },
            @{ Name = 'gh';     Id = 'GitHub.cli' }
        )
        foreach ($pkg in $wingetPackages) {
            if (-not (Test-Command $pkg.Name)) {
                Write-Host "    winget install $($pkg.Id)"
                & $winget.Source install --id $pkg.Id -e --accept-package-agreements --accept-source-agreements --silent | Out-Null
            }
        }
    }
}

if ($Full -or $InstallTts) {
    Write-Step "Installing edge-tts (CPU TTS fallback)"
    python -m pip install --upgrade edge-tts
}

if ($Full -or $InstallRenderDeps) {
    Write-Step "Installing Remotion template dependencies (first render is then offline-fast)"
    Push-Location (Join-Path $dstDir 'assets\remotion-template')
    try {
        npm install
    } finally {
        Pop-Location
    }
}

if ($Full -or $InstallAnalysis) {
    Write-Step "Installing codebase-memory-mcp"
    $installer = Join-Path $env:TEMP 'cbm-install.ps1'
    Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.ps1' -OutFile $installer
    Unblock-File $installer
    & $installer
}

Write-Step "Install complete"
Write-Host @"

  Skill installed at: $dstDir

  Next steps:
  1. Restart your Codex session so the skill is discovered.
  2. Ask:
       Use `$repo-to-video` to turn https://github.com/owner/repo into a 2-minute explainer video.

  Optional extras (per video job, on demand):
    - Deep analysis: codebase-memory-mcp (installed with -InstallAnalysis)
    - Best TTS:      Qwen3-TTS (needs GPU) - see skills/repo-to-video/references/tts.md
    - Diagrams:      codex plugin marketplace add cathrynlavery/diagram-design
"@ -ForegroundColor Green

exit 0
