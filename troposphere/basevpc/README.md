BaseVPC
=======


Usage Examples
---------------
To use this tool, observe the following options:

    -azs | --availability-zones  : Required
    Specify the AZs for the region you are using, you can specify a single AZ (not recommended) or, a b c for example:
    -azs a b c

   -nzs | --network-zones' : Required
         Specify the zones you require, here you need to enter 3 bits of information, separated by comma and written as a key=value, below is an example:
         -nzs name=public,subnets=2,internet=true name=dmz,subnets=2,internet=true name=private,subnets=4,internet=false

         The command above will create 3 zones (public, dmz and private) and then create the required number of subnets in each zone, attaching them to the
         Internet Gateway if required. There is a VPC of /16, so I guess the limitation is 256 useable nets, but I could be wrong and I'm yet to have tested it.

   -vcr | --vpc-cidr : Required
         Set this as the chosen VPC CIDR, like 10.0.0.0/8 or 10.0.0.0/16 etc.. 172.26.0.0/16 if you really want, and so on. if you use smaller than 16, there may
         need to be some re-development in the math that 'splits' the resources.

   -prn | --project-name : Not tested, however the value is used to name/tag, so it's worth entering

   -con | --company-name : As above, is also used in some tagging

   -stk | --stack-type : Currently not used, will come into use when multiple VPCs are being provisioned from this single program.
