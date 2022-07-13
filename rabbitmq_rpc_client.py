#!/usr/bin/python3

import threading
from time import sleep
import amqpstorm
from amqpstorm import Message


class RpcClient(object):
    """Asynchronous Rpc client."""

    def __init__(self, cfg_params, my_logger):

        self.queue = {}
        self.primary_host = cfg_params.get('RabbitMQ').get('primary_host')
        self.backup_host = cfg_params.get('RabbitMQ').get('backup_host')
        self.username = cfg_params.get('RabbitMQ').get('username')
        self.password = cfg_params.get('RabbitMQ').get('password')
        self.channel = None
        self.connection = None
        self.callback_queue = None              
        self.rpc_queue = cfg_params.get('RabbitMQ').get('rpc_queue')
        self.max_retries = int(cfg_params.get('RabbitMQ').get('max_retries'))
        self.max_retries_per_server = int(cfg_params.get('RabbitMQ').get('max_retries_per_server'))
        self.vhost = cfg_params.get('RabbitMQ').get('vhost')
        self.msg_ttl = int(cfg_params.get('RabbitMQ').get('message_ttl'))
        self.my_logger = my_logger
        self.create_connection()

    def create_connection(self):

        attempts = 0
        while True:
            attempts += 1
            try:

                if (attempts % 2) == 1:
                    l_hostname = self.primary_host
                else:
                    l_hostname = self.backup_host

                self.connection = amqpstorm.Connection(hostname=l_hostname, username=self.username,
                                                       password=self.password, virtual_host=self.vhost)
                self.start()

                break

            except amqpstorm.AMQPConnectionError as e:
                self.my_logger.exception(e)
                if self.max_retries and attempts > self.max_retries:
                    break
                sleep(min(attempts * 2, 30))
            except KeyboardInterrupt:
                break

    def start(self):

        if not self.connection:
            self.create_connection()

        attempts = 0
        while True:
            attempts += 1
            try:
                self.channel = self.connection.channel()
                self.channel.queue.declare(self.rpc_queue, arguments={'x-message-ttl': int(self.msg_ttl)})
                result = self.channel.queue.declare(exclusive=True,arguments={'x-message-ttl': int(self.msg_ttl)})                
                #result = self.channel.queue.declare(arguments={'x-message-ttl': int(self.msg_ttl)})
                self.my_logger.info(f' RabbitMQ Num of messages in Queue on startup {result}')
                self.callback_queue = result['queue']
                self.channel.basic.consume(self._on_response, no_ack=False, queue=self.callback_queue)
                self._create_process_thread()
                break


            except amqpstorm.AMQPChannelError as e:
                self.my_logger.exception(f' RabbitMQ AMQPChannelError:  {e}')
                if self.max_retries and attempts > self.max_retries:
                    break
                sleep(min(attempts * 2, 30))
            except KeyboardInterrupt:
                self.my_logger.info(f' KeyboardInterrupt')
                break

    def _create_process_thread(self):
        thread = threading.Thread(target=self._process_data_events)
        thread.setDaemon(True)
        thread.start()
        self.my_logger.info(f' Thread identity {threading.get_ident()}')

    
    def _process_data_events(self):
        try:
            self.channel.start_consuming()
        except amqpstorm.AMQPConnectionError as e:
            self.my_logger.info(f' process date event exception {e}')
            self.create_connection()

    def _on_response(self, message):

        try:

            self.queue[message.correlation_id] = message.body
            self.my_logger.info(f'message response :  {message.body}')

        except Exception as e:
            self.my_logger.exception(e)

    def send_request(self, payload):
        # Create the Message object.
        self.my_logger.info(f'request from GVP :  {payload}')
        properties = {'content_type': 'application/json'}
        message = Message.create(self.channel, payload, properties)
        message.reply_to = self.callback_queue
        self.queue[message.correlation_id] = None
        message.publish(routing_key=self.rpc_queue)
        return message.correlation_id
