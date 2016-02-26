<#
This will collect the AccessKey and SecretKey from the role that is specified on the command line.
#>

$role_name = $args[0]
$prof_name = $args[1]

function get_creds($RoleName, $ProfileName) {
    $AccessKey = ((Invoke-webrequest http://169.254.169.254/latest/meta-data/iam/security-credentials/$RoleName/ -UseBasicParsing -DisableKeepAlive).content.trim() | ConvertFrom-Json).AccessKeyId.trim()
    $SecretKey = ((Invoke-webrequest http://169.254.169.254/latest/meta-data/iam/security-credentials/$RoleName/ -UseBasicParsing -DisableKeepAlive).content.trim() | ConvertFrom-Json).SecretAccessKey.trim()
    Set-AWSCredentials -AccessKey $AccessKey -SecretKey $SecretKey -StoreAs $ProfileName
}

get_creds($role_name, $prof_name)
