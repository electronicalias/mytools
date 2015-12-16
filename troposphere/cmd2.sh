python stacker.py \
-azs a b c \
-nzs \
    name=public,subnets=2,internet=true \
    name=private,subnets=2,internet=false \
    name=dmz,subnets=2,internet=true \
    name=db,subnets=2,internet=false \
--vpc-cidr 172.26.0.0/16 \
--project-name SOME_NAME \
--company-name COMPANY_NAME

