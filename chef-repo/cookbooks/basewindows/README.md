Usage: You can use this when you have a long list of Windows Features being installed to reduce the runtime on subsequent Chef runs.

Use in another recipe by doing the following:

Add the 'basewindows' cookbook as a dependency
depends         'basewindows'

Include the basewindows recipe in the current recipe for which you wish to apply it:
include_recipe 'basewindows::features'

Use the 'only_if' specification in the windows_feature resource that is being specified:
    only_if {
      status = powershell_out("Powershell -f C:\\scripts\\service-check.ps1 #{feature}").stdout.chop
      "Enabled" != status
    }


Process:

1. the recipe is called and powershell run dism to query the current status of the packages and use a table output. This is written to C:\\chef\features.txt.
2. The script that is placed in C:\\scripts\\service-check.ps1 will read this file to query the current status of a package without calling dism for each operation which causes the delay
3. To call the script you can use the only_if statement and commands above
       a) for the :install action, use "Enabled"
       b) for the :remove action, use "Disabled"

