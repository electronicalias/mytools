python stacker.py \
-azs a b c \
-nzs \
    name=public,subnets=3,internet=true \
--vpc-cidr 10.0.0.0/16 \
--project-name Poc \
--company-name "TravelRepublic"

