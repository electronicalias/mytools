python stacker.py \
-azs a b c \
-nzs \
    name=public,subnets=3,internet=true \
    name=private,subnets=3,internet=false \
--vpc-cidr 10.3.0.0/18 \
--project-name production \
--company-name ${3} \
--region-name ${1} \
--stack-name ${2}
