$disk = Get-WmiObject Win32_LogicalDisk -ComputerName remotecomputer -Filter "DeviceID='C:'" |
Foreach-Object {$_.Size,$_.FreeSpace}