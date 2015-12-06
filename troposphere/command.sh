git pull
python poc_template.py \
  --companyName 'TravelRepublic' \
  --projectName 'PCITest' \
  --vpcCidr 172.26.0.0/16 \
  --publicSubnets 3 \
  --privateSubnets 2 \
  --dmzSubnets 2 \
  --dbSubnets 1 \
  --stackType WEB 
