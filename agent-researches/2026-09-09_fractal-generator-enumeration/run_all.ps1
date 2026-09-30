$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    foreach ($scriptName in @('research.mjs','coupled.mjs','global.mjs','verify.mjs','build_report.mjs')) {
        & node $scriptName
        if ($LASTEXITCODE -ne 0) { throw "Failed: $scriptName" }
    }
    foreach ($caseArgs in @(@(0,0,0),@(68,0,0),@(0,0,1),@(68,0,2))) {
        & node inspect.mjs @caseArgs
        if ($LASTEXITCODE -ne 0) { throw 'Case export failed' }
    }
    & node archive.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Archive manifest failed' }
} finally {
    Pop-Location
}

