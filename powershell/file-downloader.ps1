<#
This script does the following:
1. collects the command line parameters
2. gets a list of files in the specified bucket/folder
3. for each object, copy it to the destFolder
  
  downloader.ps1 -bucketName SOMEBUCKET -destFolder "D:\DTU" -customerFolder "CustomerName(must be same as Username)"
#>

param (
    [string]$destFolder = $(throw "-destFolder is required!"),
    [string]$bucketName = $(throw "-bucketName is required!"),
    [string]$customerFolder = $(throw "-customerFolder is required!")
)

Import-Module AWSPowerShell

$objects = Get-S3Object -bucketName $bucketName -keyprefix $customerFolder

foreach($file in $objects) {
    $localFileName = $file.Key -replace $customerFolder, ''
    $localFilePath = Join-Path $destFolder $localFileName
    Copy-S3Object -BucketName $bucketName -Key $file.key -LocalFile $localFilePath
}
