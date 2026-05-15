$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Desktop = [Environment]::GetFolderPath("Desktop")
$Shell = New-Object -ComObject WScript.Shell

function New-KomchiShortcut($Name, $Target, $Description, $IconIndex) {
    $ShortcutPath = Join-Path $Desktop "$Name.lnk"
    $Shortcut = $Shell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = Join-Path $Root $Target
    $Shortcut.WorkingDirectory = $Root
    $Shortcut.Description = $Description
    $Shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,$IconIndex"
    $Shortcut.Save()
    Write-Host "Created: $ShortcutPath"
}

New-KomchiShortcut "Komchi Creator App" "start_komchi_app.bat" "Komchi creator dashboard" 167
New-KomchiShortcut "Komchi ROOM Draft" "start_room_draft_assistant.bat" "Rakuten ROOM draft assistant" 44
New-KomchiShortcut "Komchi Photo Dance" "start_photo_dance_creator.bat" "Photo dance short creator" 135
New-KomchiShortcut "Komchi Short Stock" "start_short_stock_creator.bat" "YouTube Shorts stock creator" 138

Write-Host "Desktop shortcuts installed."
