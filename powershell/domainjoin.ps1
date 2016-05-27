param (
    [string]$username = $(throw "-username is required"),
    [string]$password = $(throw "-password is required"),
    [string]$domainname = $(throw "-domainname is required"),
    [string]$oustring = $(throw "-oustring is required")
    )

$passString = $password | ConvertTo-SecureString -asPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($username,$passString)

Add-Computer -domainname $domainname -OUPath $oustring -Credential $credential -passthru -Restart