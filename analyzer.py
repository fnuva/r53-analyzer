from __future__ import print_function
import boto3
import time
from aws_adapter import *
import logging
import re
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import plotly.express as px
import dash_style

logger = logging.basicConfig(level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# run query agains cloudwatch and wait for metrics to return
#  expected result is 
# [[{'field': 'query_name', 'value': 'service-d.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06a0adb92a71a152d'}, {'field': '@ptr', 'value': 'ClsKIgoeNDk1MTc5MzA4MzcxOi9hd3Mvcm91dGU1My9sb2dzEAISNRoYAgX8TRDsAAAAACDKNZ0ABfxqEWAAAADCIAEoqI2X/+EuMOi2nv/hLjgFQM0QSJwqULcgEAQYAQ=='}],
#  [{'field': 'query_name', 'value': 'service-d.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06766c1dd0d299dff'}, {'field': '@ptr', 'value': 'ClsKIgoeNDk1MTc5MzA4MzcxOi9hd3Mvcm91dGU1My9sb2dzEAQSNRoYAgX7XrrgAAAAAKO1S5MABfxqEuAAAAQCIAEoqI2X/+EuMNC+nv/hLjgeQKJgSMQ3UNstEBQYAQ=='}]
#  ]
#
def run_query(dns_prefix,cloudwatch_log_group):
  logger = logging.getLogger("cloudwatch-query")
  client = boto3.client('logs',region_name='eu-central-1')
  current_time = int(time.time())
  queryString = "fields query_name, srcids.instance | filter query_name like /(?i)"+re.escape(dns_prefix)+"/ | sort @timestamp desc | limit 20"
  response = client.start_query(
    logGroupName=cloudwatch_log_group,
    startTime=current_time - 900,
    endTime=current_time,
    queryString=queryString,
    limit=123
  )
  logger.info("running the cloudwatch query "+queryString)
  result = client.get_query_results(queryId=response['queryId'])
  logger.info("waiting for cloudwatch the query to finish")

  while result['status'] == 'Running':
    result = client.get_query_results(queryId=response['queryId'])
    time.sleep(1)
  return result

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
def enrich_data_with_sender(data,instance_service_map):
  results = []
  for dat in data:
      result = dict({})
      for da in dat:
        if da['field'] == 'srcids.instance':
          result['from'] = instance_service_map[da['value']] if instance_service_map[da['value']] else 'unknown'
        elif da['field'] == 'query_name':
          result['dns'] = da['value'] if da['value'] else 'unknown'
      results.append(result)
  return results
  
# enrich data about service names
#  expected input is 
# r53_dns_map = {u'service-d.internal.myservice.': 'internal-service-d-alb-283416937.eu-central-1.elb.amazonaws.com.', u'service-a.internal.myservice.': 'internal-service-a-alb-1063055395.eu-central-1.elb.amazonaws.com.'}
# alb_service_map = {'internal-service-a-alb-1063055395.eu-central-1.elb.amazonaws.com.': 'service-a', 'internal-service-d-alb-283416937.eu-central-1.elb.amazonaws.com.': 'service-d'}
#  
#  By R53 private hostedzone, we identify alb names and find service name by service tags in alb.
#
#  result = [{'to': 'service-d', 'from': u'service-d.internal.myservice.'}, {'to': 'service-a', 'from': u'service-a.internal.myservice.'}]
#
#
def enrich_data_with_receiver(r53_dns_map,alb_service_map):
  result = dict({})
  for r53Key in r53_dns_map.keys():
    result[r53Key] = alb_service_map[r53_dns_map[r53Key]]
  return result
#
#
#
# data_sender: #  {'i-06766c1dd0d299dff':'service-a','i-067661230d299dff':'service-b'}
# data_receiver: {'service-d.internal.myservice':'service-d'}
# 
# merge data and generate all graph information 
#  
# result: [{'data':{'id':'service-a'}},{'data':{'id':'service-d'}},{'data':{'id':'service-b'}},{'data':{'source':'service-a','targetto':'service-d'}},{'data':{'source':'service-b','target':'service-d'}}]
#
def merge_all_data(data,data_sender,data_receiver):
  results = []
  edges = []
  nodes_ = set()
  nodes_.update(data_sender.values(),data_receiver.values())
  
  for dat in data['results']:
    edge = dict({})
    for da in dat:
      if da['field'] == 'srcids.instance':
        if da['value'] in data_sender:
          edge['source'] = data_sender[da['value']]
        else:
          edge['source'] = 'unkown'
          nodes_.update(['unkown'])
      elif da['field'] == 'query_name':
        if da['value'] in data_receiver:
          edge['target'] = data_receiver[da['value']]  
        else: 
          edge['target'] = 'unkown'
          nodes_.update(['unkown'])
    if edge not in edges:
      edges.append(edge)
  for node in nodes_:
    results.append({'data':{'id':node}})
  
  for edge in edges:
    edge['id'] = edge['source']+edge['target']
    results.append({'data':edge})
  return results

def get_data_from_query(data):
  logger = logging.getLogger("gathering resource and dns data from query results")
  logger.info("gathering dns and in")
  instance_ids =[]
  dns = []
  for dat in data['results']:
    for da in dat:
      if da['field'] == 'srcids.instance' and  da['value'] not in instance_ids:
        instance_ids.append(da['value'])
      elif da['field'] == 'query_name' and da['value'] not in dns:
        dns.append(da['value'])
        
  return dict({'instance_ids':instance_ids,'dns':dns})

def plot(result):
  app = dash.Dash(__name__)
  app.layout = html.Div([
      cyto.Cytoscape(
          id='cytoscape-styling-9',
          elements=result,
          layout={'name': 'breadthfirst'},
          style={'width': '800px', 'height': '800px'},
          stylesheet = dash_style.stylesheet
      )
  ])
  app.run_server(debug=True)



if __name__ == "__main__":
    SERVICE_TAG_KEY = "Service"
    REGION='eu-central-1'
    HOSTED_ZONE_NAME = 'internal.myservice'
    CLOUDWATCH_LOG_GROUP = '/aws/route53/logs'
    BUCKET_NAME="graph-plotter"

    data = run_query(HOSTED_ZONE_NAME,CLOUDWATCH_LOG_GROUP)
    data_generated = get_data_from_query(data)
    sender_info = get_instance_service_name(boto3.client('ec2',region_name=REGION),data_generated["instance_ids"],SERVICE_TAG_KEY)
    print(sender_info)
    receiver_r53_info = get_r53_record_origins_service_name(boto3.client('route53'),HOSTED_ZONE_NAME,data_generated["dns"])
    receiver_alb_info = get_tag_of_alb_resources(boto3.client('elbv2',region_name=REGION),receiver_r53_info.values(),SERVICE_TAG_KEY)
    receiver_info = enrich_data_with_receiver(receiver_r53_info,receiver_alb_info)
    print(receiver_info)
    result = merge_all_data(data,sender_info,receiver_info)
    print(result)
    plot(result)