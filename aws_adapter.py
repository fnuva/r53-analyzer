import boto3
import logging
#
#  Ids:[id1,id2,id3]
#  result: [{id1:'service-a',id2:'service-b'}]
#
def get_instance_service_name(ec2_client,Ids,tag_name):
    response = ec2_client.describe_instances(InstanceIds=Ids)
    result = dict({})
    for id in Ids:
        for reservations in response['Reservations']:
            for instance in reservations['Instances']:
                if id == instance['InstanceId']:
                    for tag in instance['Tags']:
                        if tag['Key'] ==tag_name:
                            result[id] = tag['Value']
                            break
                    break
    return result
#
# hosted_zone_id = ZONE1245
# dns_names = ['service-a.myinternal.service','service-b.myinternal.service']
#
# result = {'service-a.myinternal.service':'elb-1234.amazonaws.com','service-b.myinternal.service':'elb-2345.amazonaws.com'}
#
def get_r53_record_origins_service_name(r53_client,hosted_zone_name,dns_names):
    zone_response = r53_client.list_hosted_zones()
    hosted_zone_id = None
    while True:
        for zone in zone_response['HostedZones']:
            if zone['Name'] == hosted_zone_name+'.':
                hosted_zone_id = zone['Id']
                break
        if not zone_response['IsTruncated'] or hosted_zone_id is not None:
            break
        zone_response = r53_client.list_hosted_zones(marker = zone_response['NextMarker'])
    if hosted_zone_id is None:
        raise Exception("could not found hostedzone "+hosted_zone_name) 

    logger = logging.getLogger("r53_api")
    logger.info('hosted_zone_id:'+hosted_zone_id)
    
    record_set_result = r53_client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
    results = dict({})
    for dns in dns_names:
        for record in record_set_result['ResourceRecordSets']:
            if dns == record['Name']:
                results[dns] = record['AliasTarget']['DNSName'] if record['AliasTarget']['DNSName'] else 'unkown'
                break
    return results

#
#
# input = ['elb-1234.amazonaws.com','elb-2345.amazonaws.com']
# tag_name = 'service'
# result = {'elb-1234.amazonaws.com':'service-a','elb-2345.amazonaws.com':'service-a'}
#
def get_tag_of_alb_resources(elb_client,input,tag_name):
    response = elb_client.describe_load_balancers()
    alb_arn_map = dict({})
    alb_arns=[]
    for lb in response['LoadBalancers']:
        alb_name = lb['DNSName']+'.'
        if alb_name in input:
            alb_arn_map[lb['LoadBalancerArn']] = alb_name
            alb_arns.append(lb['LoadBalancerArn'])
    response = elb_client.describe_tags(ResourceArns=alb_arns)
    result = dict({})
    for desc in response['TagDescriptions']:
        for tag in desc['Tags']:
            if tag['Key'] == tag_name:
                result[alb_arn_map[desc['ResourceArn']]] = tag['Value']
                break
    return result