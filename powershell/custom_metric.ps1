$disk = Get-WmiObject Win32_LogicalDisk -ComputerName remotecomputer -Filter "DeviceID='C:'" |
Foreach-Object {$_.Size,$_.FreeSpace}

$dat = New-Object Amazon.CloudWatch.Model.MetricDatum
$dat.Timestamp = (Get-Date).ToUniversalTime() 
$dat.MetricName = "DiskFreeSpace"
$dat.Unit = "Count"
$dat.Value = $FreeSpace
Write-CWMetricData -Namespace "Disk Metrics" -MetricData $dat