<#
This script does the following:
1. Create a variable containing directories that are specified by the $rootFolder
2. For each entry as $i.Name that isn't 'Administrator' or 'test', set $localPath
3. For each item in each $localPath set $localFile
4. Upload $localFile to the bucket specified by the argument passed when using the script as follows:

  Example Usage:
  Copy all files from each folder contained in E:\Some\Root\Folder where the contents would be many folders, then inside
  each of the variable folders, copy all the items from the upload folder. Match the variable folders under the root to the
  key name being used. So for example:
  
  Source File:
  E:\Some\Root\Folder\unique_folder_name\upload\filename.txt
  
  Destination Ojbect
  s3://bucketname/unique_folder_name/filename.txt
  
  file-uploader.ps1 -bucketName SOMEBUCKET -rootFolder "E:\Some\Root\Folder" -uploadFolder "upload"
#>
Import-Module AWSPowerShell

param (
    [string]$bucketName = $(throw "-bucketName is required in order to copy the files to the destination bucket"),
    [string]$rootFolder = $(throw "-rootFolder is required so that the script can find all folders with in the root to generate a list"),
    [string]$uploadFolder = $(throw "-uploadFolder is required and should be specified as the folder that contains the source files"),
)

foreach ($i in Get-ChildItem $rootFolder)
{ 
    if($i.Name -ne "test" -and $i.Name -ne "Administrator")
    {
        $localPath = "$rootFolder\$i\$uploadFolder"
        foreach($item in Get-ChildItem $localPath)
        {
            $localfile = "$localPath\$item"
            Write-S3Object -BucketName $bucketName -File $localFile -Key "$i/$item"
        }
    }
}
