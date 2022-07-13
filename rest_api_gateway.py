#!/usr/bin/python3
# -*- coding: utf-8 -*-

import flask
import json, requests
from flask import Flask, request, jsonify, make_response
import initialization
from time import sleep
import rabbitmq_rpc_client
# from flask_httpauth import HTTPBasicAuth
import salesforce_api as sf
import cx_Oracle as oracle
import disny_api as disny

v_cfg_file = r'/GCTI/RestRPC/rest_api_gateway/rest_api_gateway.cfg'
# v_cfg_file = r'D:\Python_Projects\RestRPC\rest_api_gateway.cfg'
cfg_params = initialization.CfgFile(v_cfg_file).get_cfg_data()
my_logger = initialization.MyLogger(cfg_params.get('Log_File').get('log_file_name')).get_logger()
my_logger.info(cfg_params)

application = Flask(__name__)
# auth = HTTPBasicAuth()
RPC_CLIENT = rabbitmq_rpc_client.RpcClient(cfg_params, my_logger)

"""
users = {
    "zvika": "bourshan",
    "zvika1": "bourshan1",
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

"""

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


@application.route('/k2view', methods=['GET'])
def k_to_view():
    if request.method == 'GET':
        v_payload = request.get_json()
        my_logger.info(f' k_to_view payload : {v_payload}')
        sf.k2view(v_payload.get('connid'), v_payload.get('consumer_id'), my_logger)
        return jsonify({"response": "Send_k2view_Request"})

@application.route('/test', methods=['GET'])
# auth.login_required
def test():
    if request.method == 'GET':
        v_payload = request.get_json()
        my_logger.info(f' test payload : {v_payload}')
        response = jsonify({"response": 'Hellowwwwww ' + v_payload.get('name')})
        return response

@application.route('/ocs/v1/colddata/createlead', methods=['POST'])
def ocs():
    if (request.method == 'POST'):
        payload = request.get_json()
        my_logger.info(f' orig payload from OCS : {request.get_json()}')
        ETag = payload.get('GSW_RECORD_HANDLE')
        my_logger.info(f'Etag : {ETag}')
        v_url_createLead = 'http://osb11dev:8011/IVR/ivrRestCons/CreateLeadInSF'

        if len(payload.get('AD_sf_lead_id')) == 0:
            rslt_leadId = sf.createLeadsf(v_url_createLead, payload, my_logger)
            my_logger.info(f'returning data from osb  : {rslt_leadId}')

            if len(rslt_leadId.get('AD_sf_lead_id')) != 0:
                response = make_response(jsonify(rslt_leadId), '200 OK')
            else:
                response = make_response('200 OK')

        response.headers['Content-Type'] = 'application/json'
        response.headers['ETag'] = ETag
        return response

@application.route('/sbc_test/extension', methods=['GET'])
def select():
    if (request.method == 'GET'):
        payload = request.get_json()
        my_logger.info(f' sbc_test : {request.get_json()}')
        extension = payload.get('extension')
        connection = pool.acquire()
        cursor = connection.cursor()
        cursor.execute("SELECT MAC_ADDRESS FROM IPPHONES_CFG WHERE EXTENSION="+extension)
        r = cursor.fetchone()
        return (r[0] if r else "Unknown extension")
"""
@application.route('/createLeadDisni', methods=['GET', 'POST'])
def LeadDisny():
    if (request.method == 'POST' or request.method == 'GET'):
        payload = (request.get_json()).get('content')
        my_logger.info(f' orig payload from IVR_Disny : {payload}')
        v_url_createLeadDisny = 'http://osb11dev:8011/IVR/ivrRestCons/SetStreamServiceAttr'
        rslt = disny.createLeadDisny(v_url_createLeadDisny, payload, my_logger)
        my_logger.info(f' returning data from osb_SetStreamServiceAttr  : {rslt}')
        
        return jsonify({"response":rslt})
"""           
@application.route('/createLeadDisni', methods=['GET', 'POST'])
def LeadDisny():
    if (request.method == 'POST' or request.method == 'GET'):
        payload = (request.get_json()).get('content')
        v_account_id = payload.split(':')[1].split(',')[0]
        v_phone = payload.split(':')[2].split('}')[0] 
        my_logger.info(f' orig payload from IVR_Disny : {payload} , {v_phone} , {v_account_id}')
        v_url_createLeadDisny = 'http://osb11prod:8011/IVR/ivrRestCons/SetStreamServiceAttr'
        rslt = disny.createLeadDisny(v_url_createLeadDisny, v_phone, v_account_id, my_logger)
        my_logger.info(f' returning data from osb_SetStreamServiceAttr  : {rslt}')
        
        return jsonify({"response":rslt})



if __name__ == '__main__':
    application.run(host="0.0.0.0",  port=8070 , debug=False)
