# Danh sách các PrivateKey cần sử dụng
$privateKeys = @(
    "112d7241c7c03e03575ed1f42a3258aa692951bef8e2468ac5d9f6f3df27ffd9"
)

# Chuỗi thông báo cần kiểm tra
$checkMessage = 'level=INFO msg="Next automatic check should be in about 4 hours" component=availability-challenge-dispatcher'

# Vòng lặp để chạy từng PrivateKey
foreach ($key in $privateKeys) {
    Write-Output "Đang chạy lệnh với PrivateKey: $key"

    try {
        # Thực thi lệnh PowerShell và bắt đầu lưu đầu ra
        $process = Start-Process -FilePath "powershell.exe" `
            -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"try { Invoke-WebRequest -Uri 'https://console.icn.global/downloads/install/start.ps1' -OutFile '.\start.ps1' -UseBasicParsing; & '.\start.ps1' -PrivateKey '$key' } finally { Remove-Item .\start.ps1 -ErrorAction SilentlyContinue }`"" `
            -NoNewWindow -PassThru -RedirectStandardOutput .\output.log -RedirectStandardError .\error.log

        # Theo dõi file log để kiểm tra thông báo
        while ($true) {
            Start-Sleep -Seconds 5  # Kiểm tra sau mỗi 5 giây
            $output = Get-Content .\output.log -Tail 50

            if ($output -like "*$checkMessage*") {
                Write-Output "Đã nhận được thông báo cần thiết với PrivateKey: $key"

                # Gửi tín hiệu Ctrl+C để dừng tiến trình
                Stop-Process -Id $process.Id -Force
                break
            }
        }
    } catch {
        Write-Error "Lỗi khi thực thi với PrivateKey $privateKey : $_"
    }

    Write-Output "Chuyển sang PrivateKey tiếp theo..."
}

Write-Output "Hoàn thành tất cả các PrivateKey."