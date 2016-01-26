param (
    [string]$region = $(throw "-region is required"),
    [string]$device = $(throw "-device is required.")
 )

Import-Module AWSPowerShell
Set-DefaultAWSRegion -Region $region

$disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='${device}:'"
$PercentFree = [Math]::round((($disk.freespace/$disk.size) * 100))

$InstanceId = invoke-restmethod -uri http://169.254.169.254/latest/meta-data/instance-id
$dimensions = New-Object System.Collections.Generic.List``1[Amazon.CloudWatch.Model.Dimension]
$dimension1 = New-Object -TypeName Amazon.CloudWatch.Model.Dimension
$dimension1.Name = "InstanceId"
$dimension1.Value = $InstanceId
$dimension2 = New-Object -TypeName Amazon.CloudWatch.Model.Dimension
$dimension2.Name = "VolumeId"
$dimension2.Value = ${device}
$dimensions.Add($dimension1)
$dimensions.Add($dimension2)

$dat = New-Object Amazon.CloudWatch.Model.MetricDatum
$dat.Timestamp = (Get-Date).ToUniversalTime() 
$dat.MetricName = "DiskFreePercent"
$dat.Unit = "Percent"
$dat.Value = $PercentFree
$dat.Dimensions = $dimensions
Write-CWMetricData -Namespace "Disk Metrics" -MetricData $dat