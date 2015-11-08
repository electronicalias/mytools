# Requries the .\features.txt to exist

$content = Get-Content .\features.txt
$feature = $args[0]

function grep($f) {
	foreach($_ in $content){
	  $data = $_.split("|")
	  %{if($($data[0]) -match $f) {return "$($data[1])"}}
    }
}

grep $feature

# Usage is:
# grep feature-name-for-windows
#
#
# for a full list of features use:
# dism /online /get-features