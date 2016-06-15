param (
    [string]$username = $(throw "-username is required"),
    [string]$password = $(throw "-password is required"),
    [string]$name = $(throw "-name is required")
    )

$passString = $password | ConvertTo-SecureString -asPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential("$username",$passString)

Rename-Computer -NewName $name -DomainCredential $credential -Force -Restart