param([string]$OutputDirectory = (Join-Path $PSScriptRoot '..\outputs'))
$ErrorActionPreference = 'Stop'
$resolvedOutput = (Resolve-Path -LiteralPath $OutputDirectory).Path
$word = New-Object -ComObject Word.Application
try {
    $word.DisplayAlerts = 0
    foreach ($file in Get-ChildItem -LiteralPath $resolvedOutput -Filter '*.docx') {
        $document = $word.Documents.Open($file.FullName, $false, $false)
        try {
            $document.Repaginate()
            $document.Fields.Update() | Out-Null
            $document.Save()
            $pdfPath = [System.IO.Path]::ChangeExtension($file.FullName, '.pdf')
            # Export document headings as PDF bookmarks, preserve accessibility.
            $document.ExportAsFixedFormat($pdfPath, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
            Write-Output $pdfPath
        } finally {
            $document.Close(0)
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($document) | Out-Null
        }
    }
} finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
