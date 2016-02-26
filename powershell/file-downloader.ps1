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