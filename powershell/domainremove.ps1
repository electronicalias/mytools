param (
    [string]$username = $(throw "-username is required"),
    [string]$password = $(throw "-password is required")
    )

$passString = $password | ConvertTo-SecureString -asPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential("$username",$passString)


Remove-Computer -UnjoinDomainCredential $credential -Force