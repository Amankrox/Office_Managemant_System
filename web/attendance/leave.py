import json
import sys
from datetime import datetime, time, timedelta

import tornado.web
from bson import ObjectId
from build_config import CONFIG
from util.conn_util import MongoMixin
from util.log_util import Log
from util.time_util import timeNow
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1, JWT_ENCODE_1
from helper.decorators import all_origin


class LeaveHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('OPTIONS', 'GET', 'POST')

    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]
    leave=MongoMixin.userDb[
        CONFIG['database'][0]['table'][22]['name']
    ]

    def options(self):
        status = False
        code = 4100
        message = ''
        result = []

    async def post(self):
        code = 4100
        message = ''
        status = False
        result = []

        try:
            try:
                # get the token from header
                token = self.request.headers.get('Authorization')
                if token:
                    token = token.replace('Bearer ', '')
                else:
                    code = 4001
                    message = 'Invalid - [ Authorization ]'
                    status = False
                    raise Exception

                # decode the token
                payload = JWT_DECODE_1(token)
                if payload is None:
                    code = 4001
                    message = 'Invalid - [ Authorization ]'
                    status = False
                    raise Exception
            except Exception as e:
                Log.i(e)
                code = 4001
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception
            try:
                # decode json
                self.request.arguments = json.loads(self.request.body)

            except Exception as e:
                code = 4100
                status = False
                message = 'Expected Request Type JSON.'
                raise Exception

            userId = payload.get('userId')
            # print('*******************************',userId)
            companyId =payload.get('companyId')
            # print('*******************************',companyId)
            role = payload.get('role')
            # find branch_id using user_id

            userQ = await self.user.find_one({'_id': ObjectId(userId)})
            # print('*************************************',userQ)


            # userD = []
            # print('*************************************',userD)
            # for i in userQ:
            #     userD.append(i)
                
            # if userD is None:
            #     code = 4001
            #     message = 'Invalid - [ Authorization ]'
            #     status = False
            #     raise Exception
            
            branchId=userQ['branchId']
            # print("************************",branchId)
            leaveDate = self.request.arguments.get('leaveDate')
            leaveDate = datetime.strptime(leaveDate, '%Y-%m-%d').date()
            print("8888888888********************8",leaveDate )
            if leaveDate is None or not leaveDate:
                code = 400
                message = 'Enter leave date in yyyy-mm-dd'
                status = False
                raise Exception

            reason=self.request.arguments.get('reason')
            print("************************",reason)
            if reason is None or not reason or not isinstance(reason,str):
                code=401
                message='enter reason in correct format'
                status=False
                raise Exception
            leaveDate = str(leaveDate)
            print(leaveDate)
            
            #code from here:-
            data = {
                'companyId':ObjectId(companyId),
                'branchId':ObjectId(branchId),
                'userId': ObjectId(userId),
                'reason':reason,
                'leaveDate':leaveDate,
                'createdAt':timeNow(),
                'isApproved':None,
                'isActive':None,
                'isDeleted':False
            }
            try:
                # await print(data)
                await self.leave.insert_one(data)
                # await self.leave.insert_one(data)
                code=200
                status=True
                message='Applied for leave'
            
            except Exception as e:
                code = 40003
                status=False
                message ='failed to Applied for holiday'
                raise Exception

        except Exception as e:
            status = False
            if not len(message):
                template = 'Exception: {0}. Argument: {1!r}'
                code = 5010
                iMessage = template.format(type(e).__name__, e.args)
                message = 'Internal Error, Please Contact the Support Team.'
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = exc_tb.tb_frame.f_code.co_filename
                Log.w('EXC', iMessage)
                Log.d('EX2', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))

        response = {
            'code': code,
            'status': status,
            'message': message,
            'result': result
        }
        Log.d('RSP', response)
        try:
            self.write(json.loads(bdumps(response)))
            await self.finish()
            return
        except Exception as e:
            status = False
            template = 'Exception: {0}. Argument: {1!r}'
            code = 5011
            iMessage = template.format(type(e).__name__, e.args)
            message = 'Internal Error, Please Contact the Support Team.'
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename
            Log.w('EXC', iMessage)
            Log.d('EX2', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
            response = {
                'code': code,
                'status': status,
                'message': message
            }
            self.write(json.loads(bdumps(response)))
            await self.finish()
