<#
This will collect the AccessKey and SecretKey from the role that is selected on the command line.
#>

$AccessKey = ((Invoke-webrequest http://169.254.169.254/latest/meta-data/iam/security-credentials/sftp-role/ -UseBasicParsing -DisableKeepAlive).content.trim() | ConvertFrom-Json).AccessKeyId.trim()
$SecretKey = ((Invoke-webrequest http://169.254.169.254/latest/meta-data/iam/security-credentials/sftp-role/ -UseBasicParsing -DisableKeepAlive).content.trim() | ConvertFrom-Json).SecretAccessKey.trim()
Set-AWSCredentials -AccessKey $AccessKey -SecretKey $SecretKey -StoreAs S3Profile
