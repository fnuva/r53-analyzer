# r53-analyzer

This is the repository to explain how important DNS logs are. 
 - we have cloudformation template that deploy small microservices talking with each other and create r53 logs group.
 - we have python scripts that 
    * send query into cloudwatch insight,
    * analyze source and targets with 'service' tag.
    
   
   
![alt text](https://github.com/fnuva/r53-analyzer/blob/master/sample_services.png?raw=true)
