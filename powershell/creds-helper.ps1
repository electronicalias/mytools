<#
Designed as a credential helper which can be used/called as a program that will output the results
and allow a script downflow to use the credentials
#>

param (
    [string]$region = $(throw "-region is required"),
    [string]$accKey = $(throw "-accKey is required"),
    [string]$secKey = $(throw "-secKey is required"),
    [string]$roleArn = $(throw "-roleArn is required"),
    [string]$roleName = $(throw "-roleName is required")
 )

Import-Module AWSPowerShell
Set-AWSCredentials -AccessKey $accKey -SecretKey $secKey -StoreAs tempProfile
Initialize-AWSDefaults -ProfileName tempProfile -Region $region

$Creds = (Use-STSRole -RoleArn $roleArn -RoleSessionName $roleName).Credentials
[Environment]::SetEnvironmentVariable("Creds", $Creds, "Machine")

Clear-AWSCredentials -StoredCredentials tempProfile
