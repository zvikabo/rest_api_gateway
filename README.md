# rest_api_gateway
Flask Rest API GW using RPC RabbitMq


1.	General
Deploying Rest Api Gateway using python- Flak to serve Pay Per View orders that running on legacy Billing system (using Win socket protocol)

2.	Architecture
  2.1	The rest api gateway application deployed on Production on 2 servers:
  •	Kfs-app-lnx
  •	Bs-app-lnx

  2.2	The deployment on each server is as describe below:

![image](https://user-images.githubusercontent.com/56754883/227587818-9b63a434-30d8-4cce-9df4-e9d73ba577c0.png)


  For more details, browse to the following link:
  https://medium.com/@yekabotep/deploy-flask-app-in-nginx-using-uwsgi-with-architectural-explanation-2e24a41c030a

  2.3	Nginx , rest-app-gateway and PPV application run as a service/deamon :

![image](https://user-images.githubusercontent.com/56754883/227587869-157bcaf2-3cc2-4555-890b-94352c9c6796.png)

  Reset the service:
  As root user type:
  service <service_name> < start, stop, restart, try-restart, reload, force-reload, status>
  For example: 	service rest-api-gateway restart 
      service PPV_SRV stop
      service rh-nginx118-nginx status

  We care only for the following services/daemons :
  •	rest-api-gateway         install on : /GCTI/RestRPC/rest_api_gateway
  •	PPV-SRV	           install on : /GCTI/RestRPC/PPV_SRV
  •	rh-nginx118-nginx      
  install on /opt/rh/rh-nginx118/register.content/etc/opt/rh/rh-nginx118/nginx

3.	PPV application:
  In order to implement PPV protocol from a mcp session we uses RabbitMQ with RPC (Remote Procedure Call) design pattern base on AdvanceMessageQueueProtocol, meaning in sync way:
  ![image](https://user-images.githubusercontent.com/56754883/227587732-68c7fcdd-5bf3-4061-9eaf-00f67824a51b.png)



  1.	Rest request from MCP (post)
  2.	Request to rpc queue (including where to send the response ) response with unique id.
  3.	PPV_SRV that registered to the queue notify the message – prepare the request and open win socket to wizard port.(4)
  4.	Stream the data to wizard
  5.	Get response from wizard
  6.	Reply to the callback queue
  7.	Rest api gateway application got response and replay to mcp request(8).


4.	CFG File:
    Rest_api_gateway.cfg
   ![image](https://user-images.githubusercontent.com/56754883/227589125-611c7091-74a0-40f6-846e-a246e6b15fe3.png)
    ![image](https://user-images.githubusercontent.com/56754883/227589242-b5383cdd-7f0c-4f00-aa67-74580cf57e40.png)
    ![image](https://user-images.githubusercontent.com/56754883/227589339-500dc503-ad5b-45ed-a43e-b2680a24dde5.png)
    ![image](https://user-images.githubusercontent.com/56754883/227589426-530f4e10-4c9e-48d1-be96-3bc98370fb41.png)


Log file:
PPV_SRV.log
EV:
INFO:/GCTI_Log/RestRPC/ppv_srv.log | Wizard line number 016 '' | (2022-06-14 23:33:50 |  PPV_SRV.py  |  51)
INFO:/GCTI_Log/RestRPC/ppv_srv.log |  GVP request : {'connid': '012703395c597610', 'EV': '262193'} '' | (2022-06-14 23:33:50 |  PPV_SRV.py  |  57)
INFO:/GCTI_Log/RestRPC/ppv_srv.log |  sending message to wizard : A016EV262193               '' | (2022-06-14 23:33:50 |  PPV_SRV.py  |  114)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | request to sent A016EV262193               '' | (2022-06-14 23:33:50 |  PPV_SRV.py  |  205)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | chunkb'H016OK\r' '' | (2022-06-14 23:33:50 |  PPV_SRV.py  |  124)
INFO:/GCTI_Log/RestRPC/ppv_srv.log |  response : H016OK  '' | (2022-06-14 23:33:50 |  PPV_SRV.py  |  129)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | wizard response : OK  '' | (2022-06-14 23:33:50 |  PPV_SRV.py  |  207)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | wizard close socket '' | (2022-06-14 23:33:50 |  PPV_SRV.py  |  209)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | response   OK  '' | (2022-06-14 23:33:50 |  PPV_SRV.py  |  217)

EN:
INFO:/GCTI_Log/RestRPC/ppv_srv.log | Wizard line number 016 '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  51)
INFO:/GCTI_Log/RestRPC/ppv_srv.log |  GVP request : {'connid': '012703395c597610', 'EN': '85165320'} '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  57)
INFO:/GCTI_Log/RestRPC/ppv_srv.log |  sending message to wizard : A016EN85165320             '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  114)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | request to sent A016EN85165320             '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  205)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | chunkb'H016OK\r' '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  124)
INFO:/GCTI_Log/RestRPC/ppv_srv.log |  response : H016OK  '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  129)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | wizard response : OK  '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  207)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | wizard close socket '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  209)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | response   OK  '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  217)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | Wizard line number 016 '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  51)

UP:
INFO:/GCTI_Log/RestRPC/ppv_srv.log |  GVP request : {'connid': '012703395c597610', 'CONFIRM': 'UP'} '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  57)
INFO:/GCTI_Log/RestRPC/ppv_srv.log |  sending message to wizard : A016UP '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  114)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | request to sent A016UP '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  205)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | chunkb'H016OK\r' '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  124)
INFO:/GCTI_Log/RestRPC/ppv_srv.log |  response : H016OK  '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  129)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | wizard response : OK  '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  207)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | wizard close socket '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  209)
INFO:/GCTI_Log/RestRPC/ppv_srv.log | response   OK  '' | (2022-06-14 23:34:03 |  PPV_SRV.py  |  217)







Rest_api_gateway.log
EV:
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Original Rest GET request from GVP  : {'content': "{'connid':'0127032d64a94732','EV':'1569885'}"} '' | (2022-05-30 22:09:31 |  rest_api_gateway.py  |  69)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Rest GET request from GVP  : {'connid':'0127032d64a94732','EV':'1569885'} '' | (2022-05-30 22:09:31 |  rest_api_gateway.py  |  71)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log | request from GVP :  {'connid':'0127032d64a94732','EV':'1569885'} '' | (2022-05-30 22:09:31 |  rabbitmq_rpc_client.py  |  111)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Message sent to RabbitMQ : {'queue': {'aad1fdc9-c462-465e-96d9-d4257f47193e': 'OK\r', 'da34c44a-23ab-42dd-a628-62c4c72ccce5': 'OK\r', 'f477ff06-28dd-4855-9fb7-c95dd6d62509': None}, 'primary_host': 'bs-gax', 'backup_host': 'kfs-gax', 'username': 'ppv', 'password': 'ppv', 'channel': <amqpstorm.channel.Channel object at 0x7f7299baf948>, 'connection': <amqpstorm.connection.Connection object at 0x7f72998ce288>, 'callback_queue': 'amq.gen-kchdUVY0htyY15pv4KyZSg', 'rpc_queue': 'prod.ppv.bs', 'max_retries': 2000, 'max_retries_per_server': 2, 'vhost': '/ppv', 'msg_ttl': 30000, 'my_logger': <Logger /GCTI_Log/RestRPC/rest_api_gateway.log (DEBUG)>} '' | (2022-05-30 22:09:31 |  rest_api_gateway.py  |  73)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log | message response :  OK  '' | (2022-05-30 22:09:31 |  rabbitmq_rpc_client.py  |  104)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Return PPV response to GVP client : OK  '' | (2022-05-30 22:09:31 |  rest_api_gateway.py  |  86)
EN:
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Original Rest GET request from GVP  : {'content': "{'connid':'0127032d64a94732','EN':'84880185'}"} '' | (2022-05-30 22:09:48 |  rest_api_gateway.py  |  69)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Rest GET request from GVP  : {'connid':'0127032d64a94732','EN':'84880185'} '' | (2022-05-30 22:09:48 |  rest_api_gateway.py  |  71)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log | request from GVP :  {'connid':'0127032d64a94732','EN':'84880185'} '' | (2022-05-30 22:09:48 |  rabbitmq_rpc_client.py  |  111)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Message sent to RabbitMQ : {'queue': {'b3fced41-a4eb-475f-a064-fa4d07886181': 'OK\r', '4ad8dedf-0c89-48bb-8e2f-6cda07c2acc3': None}, 'primary_host': 'bs-gax', 'backup_host': 'kfs-gax', 'username': 'ppv', 'password': 'ppv', 'channel': <amqpstorm.channel.Channel object at 0x7f7299baf948>, 'connection': <amqpstorm.connection.Connection object at 0x7f72998ce288>, 'callback_queue': 'amq.gen-JaUnUkl9Knk7PGFD_QFr9w', 'rpc_queue': 'prod.ppv.bs', 'max_retries': 2000, 'max_retries_per_server': 2, 'vhost': '/ppv', 'msg_ttl': 30000, 'my_logger': <Logger /GCTI_Log/RestRPC/rest_api_gateway.log (DEBUG)>} '' | (2022-05-30 22:09:48 |  rest_api_gateway.py  |  73)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log | message response :  OK  '' | (2022-05-30 22:09:48 |  rabbitmq_rpc_client.py  |  104)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Return PPV response to GVP client : OK  '' | (2022-05-30 22:09:48 |  rest_api_gateway.py  |  86)
UP:
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Original Rest GET request from GVP  : {'content': "{'connid':'0127032d64a94732','CONFIRM':'UP'}"} '' | (2022-05-30 22:09:48 |  rest_api_gateway.py  |  69)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Rest GET request from GVP  : {'connid':'0127032d64a94732','CONFIRM':'UP'} '' | (2022-05-30 22:09:48 |  rest_api_gateway.py  |  71)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log | request from GVP :  {'connid':'0127032d64a94732','CONFIRM':'UP'} '' | (2022-05-30 22:09:48 |  rabbitmq_rpc_client.py  |  111)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Message sent to RabbitMQ : {'queue': {'b3fced41-a4eb-475f-a064-fa4d07886181': 'OK\r', '4ad8dedf-0c89-48bb-8e2f-6cda07c2acc3': 'OK\r', '8c8bafab-3de2-462f-ad7e-f157865ad723': None}, 'primary_host': 'bs-gax', 'backup_host': 'kfs-gax', 'username': 'ppv', 'password': 'ppv', 'channel': <amqpstorm.channel.Channel object at 0x7f7299baf948>, 'connection': <amqpstorm.connection.Connection object at 0x7f72998ce288>, 'callback_queue': 'amq.gen-JaUnUkl9Knk7PGFD_QFr9w', 'rpc_queue': 'prod.ppv.bs', 'max_retries': 2000, 'max_retries_per_server': 2, 'vhost': '/ppv', 'msg_ttl': 30000, 'my_logger': <Logger /GCTI_Log/RestRPC/rest_api_gateway.log (DEBUG)>} '' | (2022-05-30 22:09:48 |  rest_api_gateway.py  |  73)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log | message response :  OK  '' | (2022-05-30 22:09:48 |  rabbitmq_rpc_client.py  |  104)
INFO:/GCTI_Log/RestRPC/rest_api_gateway.log |  Return PPV response to GVP client : OK  '' | (2022-05-30 22:09:48 |  rest_api_gateway.py  |  86)
 


Test client:
Each machine has a test client on /GCTI/RestRPC/PPV_SRV:

[yescti@KFS-APP-LNX PPV_SRV]$ ./test_client.py
send time    :  2022-06-15 14:05:31.608771
{'connid': '0128031c21578752', 'EV': '553403'}
Send time time :  2022-06-15 14:05:31.608838
{"callresult":"OK"}

response time :  2022-06-15 14:05:31.924137
Time left =  0:00:00.315299
None
 
RabbitMQ managemt:

http://kfs-gax:15672  /    http://bs-gax:15672
User : yescti
Password: xxxxxxxx

Admin-users:
 
 ![image](https://user-images.githubusercontent.com/56754883/227588082-ea655784-3f6b-4a5a-8ca0-127bd7d35a43.png)
![image](https://user-images.githubusercontent.com/56754883/227588213-09f72679-9222-4e6e-957c-a53b8bc144db.png)
![image](https://user-images.githubusercontent.com/56754883/227588251-7771a89d-8537-4990-b01a-ffd99edc4d92.png)
![image](https://user-images.githubusercontent.com/56754883/227588279-02671d6d-bac2-4073-b882-2024e54d6b58.png)
![image](https://user-images.githubusercontent.com/56754883/227588310-784a2123-627d-4f9e-beaa-fa49e12e0036.png)

 
Cluster nodes:
 
 
