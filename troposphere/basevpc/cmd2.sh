python stacker.py \
-azs b c d \
-nzs \
    name=public,subnets=3,internet=true \
    name=private,subnets=3,internet=false \
    name=dmz,subnets=3,internet=true \
    name=db,subnets=3,internet=false \
--vpc-cidr 172.27.64.0/18 \
--project-name production \
--company-name ${3} \
--region-name ${1} \
--stack-name ${2}
