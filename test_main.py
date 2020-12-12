from analyzer import *
import json
# enrich data about service names
#  expected input is 
# [[{'field': 'query_name', 'value': 'service-d.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06a0adb92a71a152d'}, {'field': '@ptr', 'value': 'ClsKIgoeNDk1MTc5MzA4MzcxOi9hd3Mvcm91dGU1My9sb2dzEAISNRoYAgX8TRDsAAAAACDKNZ0ABfxqEWAAAADCIAEoqI2X/+EuMOi2nv/hLjgFQM0QSJwqULcgEAQYAQ=='}],
#  [{'field': 'query_name', 'value': 'service-d.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06766c1dd0d299dff'}, {'field': '@ptr', 'value': 'ClsKIgoeNDk1MTc5MzA4MzcxOi9hd3Mvcm91dGU1My9sb2dzEAQSNRoYAgX7XrrgAAAAAKO1S5MABfxqEuAAAAQCIAEoqI2X/+EuMNC+nv/hLjgeQKJgSMQ3UNstEBQYAQ=='}]
#  ]
#  By instanceIds, service tag will be found and added into data.
#  expected result is
#
#  [{'dns':'service-d.internal.myservice', 'from':'service-a'},{'dns':'service-d.internal.myservice', 'from':'service-b'}]
#  
#
#
def test_enrich_data_with_sender():
    input = [[{'field': 'query_name', 'value': 'service-d.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06a0adb92a71a152d'}, {'field': '@ptr', 'value': 'ClsKIgoeNDk1MTc5MzA4MzcxOi9hd3Mvcm91dGU1My9sb2dzEAISNRoYAgX8TRDsAAAAACDKNZ0ABfxqEWAAAADCIAEoqI2X/+EuMOi2nv/hLjgFQM0QSJwqULcgEAQYAQ=='}],
             [{'field': 'query_name', 'value': 'service-d.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06766c1dd0d299dff'}, {'field': '@ptr', 'value': 'ClsKIgoeNDk1MTc5MzA4MzcxOi9hd3Mvcm91dGU1My9sb2dzEAQSNRoYAgX7XrrgAAAAAKO1S5MABfxqEuAAAAQCIAEoqI2X/+EuMNC+nv/hLjgeQKJgSMQ3UNstEBQYAQ=='}]
            ]
    instance_service_map={'i-06a0adb92a71a152d':'service-a','i-06766c1dd0d299dff':'service-b'}
    output = enrich_data_with_sender(input,instance_service_map)
    expected_results = [{'dns':'service-d.internal.myservice.', 'from':'service-a'},{'dns':'service-d.internal.myservice.', 'from':'service-b'}]
    assert output == expected_results

def test_enrich_data_with_receiver():
    input = [[{'field': 'query_name', 'value': 'service-d.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06a0adb92a71a152d'}, {'field': '@ptr', 'value': 'ClsKIgoeNDk1MTc5MzA4MzcxOi9hd3Mvcm91dGU1My9sb2dzEAISNRoYAgX8TRDsAAAAACDKNZ0ABfxqEWAAAADCIAEoqI2X/+EuMOi2nv/hLjgFQM0QSJwqULcgEAQYAQ=='}],
             [{'field': 'query_name', 'value': 'service-d.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06766c1dd0d299dff'}, {'field': '@ptr', 'value': 'ClsKIgoeNDk1MTc5MzA4MzcxOi9hd3Mvcm91dGU1My9sb2dzEAQSNRoYAgX7XrrgAAAAAKO1S5MABfxqEuAAAAQCIAEoqI2X/+EuMNC+nv/hLjgeQKJgSMQ3UNstEBQYAQ=='}]
            ]
    r53_dns_map = {'service-a.internal.myservice.':'elb-1234.amazonaws.com','service-d.internal.myservice.':'elb-2345.amazonaws.com'}
    alb_service_map = {'elb-1234.amazonaws.com':'service-a','elb-2345.amazonaws.com':'service-d'}
    expected_results = [{'dns':'service-d.internal.myservice.', 'to':'service-d'},{'dns':'service-d.internal.myservice.', 'to':'service-d'}]
    result = enrich_data_with_receiver(input,r53_dns_map,alb_service_map)
    assert result == expected_results



