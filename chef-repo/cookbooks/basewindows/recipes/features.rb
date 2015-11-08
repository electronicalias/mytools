#Check the features and their current state
powershell_script 'installed_features' do
code <<-EOH
  dism /online /get-features /format:table > c://chef//features.txt
EOH
end

cookbook_file 'C:\Scripts\service-check.ps1' do
  source 'service-check.ps1'
end