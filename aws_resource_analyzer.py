class ResourceAnalyzerInterface:
    """
        data : [[{'field': 'query_name', 'value': 'service-d.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06a0adb92a71a152d'}, {'field': '@ptr', 'value': 'ClsKIgoeNDk1MTc5MzA4MzcxOi9hd3Mvcm91dGU1My9sb2dzEAISNRoYAgX8TRDsAAAAACDKNZ0ABfxqEWAAAADCIAEoqI2X/+EuMOi2nv/hLjgFQM0QSJwqULcgEAQYAQ=='}],
                [{'field': 'query_name', 'value': 'service-d.internal.myservice.'}, {'field': 'srcids.instance', 'value': 'i-06766c1dd0d299dff'}, {'field': '@ptr', 'value': 'ClsKIgoeNDk1MTc5MzA4MzcxOi9hd3Mvcm91dGU1My9sb2dzEAQSNRoYAgX7XrrgAAAAAKO1S5MABfxqEuAAAAQCIAEoqI2X/+EuMNC+nv/hLjgeQKJgSMQ3UNstEBQYAQ=='}]
               ]
         we expect the method to gather resource related information and keep them in class fields
    """
    def gather_data_from_logs(self, data: dict):
        pass
    """
       we will enrich the data gathered. For example, 
       * we can find service tags in ec2 instances
       * we can find alb names from r53 record and get service tags
    """
    def enrich_gathered_data_to_logs(self):
        pass
