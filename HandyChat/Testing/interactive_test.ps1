# Interactive API Testing

$BaseUrl = "http://localhost:5000"

function Show-Menu {
    Clear-Host
    Write-Host "🤖 Find My PE Class - API Testing Console" -ForegroundColor Cyan
    Write-Host "==========================================`n"
    Write-Host "1. Test Home Endpoint"
    Write-Host "2. List All Routes" 
    Write-Host "3. Get Available Sports"
    Write-Host "4. Ask a Question"
    Write-Host "5. Bulk Test Questions"
    Write-Host "6. Exit`n"
}

function Test-Question {
    $question = Read-Host "Enter your question"
    if (-not $question) { return }
    
    Write-Host "`nSending question: '$question'" -ForegroundColor Yellow
    
    $body = @{question = $question} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$BaseUrl/api/chat/ask" -Method Post -Body $body -ContentType "application/json"
    
    Write-Host "🤖 Response: " -NoNewline -ForegroundColor Green
    Write-Host $response.response -ForegroundColor White
    Write-Host "Status: $($response.status)`n" -ForegroundColor Gray
    
    Read-Host "Press Enter to continue"
}

function Bulk-Test {
    $questions = @(
        "basketball today",
        "swimming class location",
        "where is tennis",
        "badminton time"
    )
    
    Write-Host "`nRunning bulk test with $($questions.Count) questions...`n" -ForegroundColor Yellow
    
    foreach ($q in $questions) {
        Write-Host "Q: $q" -ForegroundColor Cyan
        $body = @{question = $q} | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/chat/ask" -Method Post -Body $body -ContentType "application/json"
        Write-Host "A: $($response.response)" -ForegroundColor Green
        Write-Host "---"
        Start-Sleep -Milliseconds 500  # Small delay between requests
    }
    
    Read-Host "`nBulk test complete. Press Enter to continue"
}

# Main interactive loop
do {
    Show-Menu
    $choice = Read-Host "Select an option (1-6)"
    
    switch ($choice) {
        '1' { 
            Write-Host "`nTesting Home Endpoint..." -ForegroundColor Yellow
            $response = Invoke-RestMethod -Uri "$BaseUrl/" -Method Get
            $response | Format-List
            Read-Host "Press Enter to continue"
        }
        '2' { 
            Write-Host "`nGetting All Routes..." -ForegroundColor Yellow
            $response = Invoke-RestMethod -Uri "$BaseUrl/routes" -Method Get
            Write-Host "Available Routes:" -ForegroundColor Green
            $response.routes | ForEach-Object { Write-Host "  $($_.methods) -> $($_.path)" }
            Read-Host "Press Enter to continue"
        }
        '3' { 
            Write-Host "`nGetting Available Sports..." -ForegroundColor Yellow
            $response = Invoke-RestMethod -Uri "$BaseUrl/api/chat/sports" -Method Get
            Write-Host "Available Sports: $($response.sports -join ', ')" -ForegroundColor Green
            Read-Host "Press Enter to continue"
        }
        '4' { Test-Question }
        '5' { Bulk-Test }
        '6' { Write-Host "Goodbye! 👋" -ForegroundColor Cyan; break }
        default { Write-Host "Invalid option. Please try again." -ForegroundColor Red; Start-Sleep -Seconds 2 }
    }
} while ($choice -ne '6')