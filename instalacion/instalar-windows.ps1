# Prepara un PC con Windows 10/11 para editar. Lo lanza Claude desde la carpeta del editor. Se puede repetir sin miedo.
$ErrorActionPreference = "Continue"; $ProgressPreference = "SilentlyContinue"
Set-Location (Split-Path -Parent $PSScriptRoot)
function ok($t)  { Write-Host "OK     $t" }
function mal($t) { Write-Host "FALLA  $t" }
function hay($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function refresca { $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH", "User") }
$acepta = @("-e", "--silent", "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity")
$winget = hay winget
if ($winget) { winget source update *> $null }
function instala($id) { if ($winget) { winget install --id $id @acepta | Out-Host }; refresca }
$nuevo = $false

# Git: Claude lo usa para trabajar mejor en Windows (no es imprescindible para editar)
if (-not (hay git)) { instala "Git.Git"; if (hay git) { $nuevo = $true } }
if (hay git) { ok "Git" } else { Write-Host "AVISO  Git no se pudo instalar: Claude funcionará igual, pero conviene instalarlo desde git-scm.com" }

# ffmpeg: si winget no puede, versión portátil dentro de la carpeta (herramientas\ffmpeg)
if (-not (hay ffmpeg) -and -not (Test-Path "herramientas\ffmpeg\bin\ffmpeg.exe")) {
  instala "Gyan.FFmpeg"
  if (-not (hay ffmpeg)) {
    New-Item -ItemType Directory -Force "herramientas" | Out-Null
    Invoke-WebRequest "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile "herramientas\ffmpeg.zip"
    Expand-Archive "herramientas\ffmpeg.zip" "herramientas\tmp" -Force
    Move-Item (Get-ChildItem "herramientas\tmp" -Directory | Select-Object -First 1).FullName "herramientas\ffmpeg" -Force
    Remove-Item "herramientas\ffmpeg.zip", "herramientas\tmp" -Recurse -Force -ErrorAction SilentlyContinue
  }
}
if ((hay ffmpeg) -or (Test-Path "herramientas\ffmpeg\bin\ffmpeg.exe")) { ok "ffmpeg (cortar, unir y exportar vídeo)" } else { mal "ffmpeg"; exit 3 }

# Python 3.10+ (el «python» de la Microsoft Store no vale: es un acceso directo a la tienda)
function pyok { try { $v = & python -c "import sys;print(sys.version_info[:2]>=(3,10))" 2>$null; return $v -eq "True" } catch { return $false } }
if (-not (pyok)) {
  instala "Python.Python.3.12"
  if (-not (pyok)) {
    Invoke-WebRequest "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe" -OutFile "$env:TEMP\python-instalador.exe"
    Start-Process "$env:TEMP\python-instalador.exe" -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=0" -Wait
    refresca; $nuevo = $true
  }
}
if (pyok) { ok "Python" } else { mal "Python"; exit 3 }

# Navegador para pintar los gráficos: Edge viene con Windows; si no, Chrome
$edge = Test-Path "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
$chrome = (Test-Path "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") -or (Test-Path "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe")
if (-not ($edge -or $chrome)) { instala "Google.Chrome" }
ok "navegador para pintar los gráficos"

# Python en UTF-8 (si no, las tildes y los emojis rompen los archivos en Windows)
[Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User"); $env:PYTHONUTF8 = "1"

# Entorno de Python propio del editor (no toca el resto del ordenador)
if (-not (Test-Path ".venv\Scripts\python.exe")) { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -q --upgrade pip
.\.venv\Scripts\python.exe -m pip install -q -r instalacion\requisitos.txt
if ($LASTEXITCODE -ne 0) { mal "librerías de Python"; exit 3 }
ok "librerías de Python (transcribir, recortar a la persona, dibujar)"
"brutos", "proyectos", "entregados", "referencias", "estilos", "marca" | ForEach-Object { New-Item -ItemType Directory -Force "mi-edicion\$_" | Out-Null }
New-Item -ItemType Directory -Force "recursos-descargados" | Out-Null; ok "carpeta mi-edicion"
if ($nuevo) { Write-Host "REINICIA_CLAUDE: hay programas nuevos. Cierra Claude del todo, ábrelo otra vez en esta carpeta y escribe /empezar." }
Write-Host "TODO_LISTO"
