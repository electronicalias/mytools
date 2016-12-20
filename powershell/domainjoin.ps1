param (
    [string]$username = $(throw "-username is required"),
    [string]$password = $(throw "-password is required"),
    [string]$domainname = $(throw "-domainname is required"),
    [string]$oustring = $(throw "-oustring is required"),
    [string]$hostname = $(throw "-hostname is required"),
    [string]$groupname = $(throw "-groupname is required")
    )

$passString = $password | ConvertTo-SecureString -asPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential("$username",$passString)

Add-Computer -NewName $hostname -domainname $domainname -OUPath $oustring -Credential $credential -passthru -Verbose 

$GroupObj = [ADSI]"WinNT://./Administrators,group"
$GroupObj.Add("WinNT://$domainname/$groupname")
$GroupObj.Add("WinNT://$domainname/Operation Teams")
