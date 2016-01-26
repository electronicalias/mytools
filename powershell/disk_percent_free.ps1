﻿
param (
    [string]$region = $(throw "-region is required")
 )

Import-Module AWSPowerShell
Set-DefaultAWSRegion -Region $region

$InstanceId = invoke-restmethod -uri http://169.254.169.254/latest/meta-data/instance-id
$disks = Get-WmiObject Win32_LogicalDisk
$topicARN = "arn:aws:sns:sa-east-1:427696001268:disk"


foreach ($disk in $disks) {
    $dimensions = New-Object System.Collections.Generic.List``1[Amazon.CloudWatch.Model.Dimension]
    $PercentFree = [Math]::round((($disk.freespace/$disk.size) * 100))
    $dimension1 = New-Object -TypeName Amazon.CloudWatch.Model.Dimension
    $dimension1.Name = "InstanceId"
    $dimension1.Value = $InstanceId
    $dimension2 = New-Object -TypeName Amazon.CloudWatch.Model.Dimension
    $dimension2.Name = "VolumeId"
    $dimension2.Value = $disk.deviceid
    $dimensions.Add($dimension1)
    $dimensions.Add($dimension2)

    $dat = New-Object Amazon.CloudWatch.Model.MetricDatum
    $dat.Timestamp = (Get-Date).ToUniversalTime() 
    $dat.MetricName = "DiskFreePercent"
    $dat.Unit = "Percent"
    $dat.Value = $PercentFree
    $dat.Dimensions = $dimensions
    Write-CWMetricData -Namespace "Disk Metrics" -MetricData $dat
    
    Write-CWMetricAlarm -AlarmName "Disk % Free" `
                    -AlarmDescription "Alarm when the disk percent used is above 80%" `
                    -Namespace "Disk Metrics" `
                    -MetricName DiskFreePercent `
                    -Dimensions @{ Name="InstanceId"; Value="${InstanceId}" } `
                    -AlarmActions $topicARN `
                    -ComparisonOperator LessThanOrEqualToThreshold `
                    -EvaluationPeriods 1 `
                    -Period 21600 `
                    -Statistic Average `
                    -Threshold 20

}