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
    r53_dns_map = {'service-a.internal.myservice.':'elb-1234.amazonaws.com','service-d.internal.myservice.':'elb-2345.amazonaws.com'}
    alb_service_map = {'elb-1234.amazonaws.com':'service-a','elb-2345.amazonaws.com':'service-d'}
    expected_results = {'service-a.internal.myservice.':'service-a','service-d.internal.myservice.':'service-d'}
    result = enrich_data_with_receiver(r53_dns_map,alb_service_map)
    print(result)
    print(expected_results)
    assert result == expected_results

def test_merge_all_data():
    data = {'results':[[{'field': 'query_name', 'value': 'service-d.internal.myservice.'},{'field': 'srcids.instance', 'value': 'i-06a0adb92a71a152d'}, {'field': '@ptr', 'value': '124'}],
            [{'field': 'query_name', 'value': 'service-c.internal.myservice.'},{'field': 'srcids.instance', 'value': 'i-06766c1dd0d299dff'}, {'field': '@ptr', 'value': '124'}],
             [{'field': 'query_name', 'value': 'service-c.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06unkown0d299dff'}, {'field': '@ptr', 'value': '245'}]
            ]}
    data_sender = {'i-06a0adb92a71a152d':'service-a','i-06766c1dd0d299dff':'service-b'}
    data_receiver = {'service-d.internal.myservice.':'service-d','service-c.internal.myservice.':'service-c'}
    expected_results = [{'data': {'id': 'unkown'}}, {'data': {'id': 'service-a'}}, {'data': {'id': 'service-c'}}, {'data': {'id': 'service-d'}}, {'data': {'id': 'service-b'}}, {'data': {'target': 'service-d', 'source': 'service-a', 'id': 'service-aservice-d'}}, {'data': {'target': 'service-c', 'source': 'service-b', 'id': 'service-bservice-c'}}, {'data': {'target': 'service-c', 'source': 'unkown', 'id': 'unkownservice-c'}}]
    result = merge_all_data(data,data_sender,data_receiver)
    print(result)
    print(expected_results)
    for ex_result in expected_results:
        assert ex_result in result
    assert len(result) == len(expected_results)

