#!/usr/bin/python3
# -*- coding: utf-8 -*-

import flask
import json, requests
from flask import Flask, request, jsonify, make_response
import initialization
from time import sleep
import rabbitmq_rpc_client
import cx_Oracle as oracle


v_cfg_file = r'/GCTI/RestRPC/rest_api_gateway/rest_api_gateway.cfg'
cfg_params = initialization.CfgFile(v_cfg_file).get_cfg_data()
my_logger = initialization.MyLogger(cfg_params.get('Log_File').get('log_file_name')).get_logger()
my_logger.info(cfg_params)

application = Flask(__name__)

RPC_CLIENT = rabbitmq_rpc_client.RpcClient(cfg_params, my_logger)



@application.route('/api/v1/ppv', methods=['GET', 'POST'])
def ppv():
    if (request.method == 'POST' or request.method == 'GET'):
        try:
            my_logger.info(f' Original Rest GET request from GVP  : {request.get_json()}')
            ivr_msg = str(request.get_json().get('content'))
            my_logger.info(f' Rest GET request from GVP  : {ivr_msg}')
            corr_id = RPC_CLIENT.send_request(ivr_msg)
            my_logger.info(f' Message sent to RabbitMQ : {RPC_CLIENT.__dict__}')

        except Exception as e:
            my_logger.exception(e)

        time_wait = 0

        while (time_wait < int(cfg_params.get('RabbitMQ').get('timeout_waiting_for_response'))) & (
                RPC_CLIENT.queue.get(corr_id) is None):
            sleep(0.1)
            time_wait += 0.1

        if time_wait <= int(cfg_params.get('RabbitMQ').get('timeout_waiting_for_response')):
            my_logger.info(f' Return PPV response to GVP client : {RPC_CLIENT.queue.get(corr_id)}')
            call_result = (RPC_CLIENT.queue.get(corr_id))
            return jsonify({"callresult": call_result.split('\r')[0]})
        else:
            my_logger.info('f Return Timeout Error code to GVP client')
            return jsonify({"callresult": cfg_params.get('RabbitMQ').get('return_err_code_on_timeout')})


if __name__ == '__main__':
    application.run(host="0.0.0.0",  port=8070 , debug=False)
