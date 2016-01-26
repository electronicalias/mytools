param (
    [string]$region = $(throw "-region is required"),
    [string]$disk = $(throw "-disk is required.")
 )

Import-Module AWSPowerShell
Set-DefaultAWSRegion -Region sa-east-1

$disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
$PercentFree = [Math]::round((($disk.freespace/$disk.size) * 100))

$InstanceId = invoke-restmethod -uri http://169.254.169.254/latest/meta-data/instance-id
$dimensions = New-Object System.Collections.Generic.List``1[Amazon.CloudWatch.Model.Dimension]
$dimension = New-Object -TypeName Amazon.CloudWatch.Model.Dimension
$dimension.Name = "InstanceId"
$dimension.Value = $InstanceId
$dimensions.Add($dimension)

$dat = New-Object Amazon.CloudWatch.Model.MetricDatum
$dat.Timestamp = (Get-Date).ToUniversalTime() 
$dat.MetricName = "DiskFreePercent"
$dat.Unit = "Percent"
$dat.Value = $PercentFree
$dat.Dimensions = $dimensions
Write-CWMetricData -Namespace "Disk Metrics" -MetricData $dat