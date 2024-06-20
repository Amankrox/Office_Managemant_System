from asyncio import log
import json
import sys
from datetime import date, datetime, timedelta

import tornado.web
from bson import ObjectId
from build_config import CONFIG
from lib.fernet_crypto import FN_DECRYPT
from util.conn_util import MongoMixin
from util.log_util import Log
from util.time_util import timeNow
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1, JWT_ENCODE_1
from helper.decorators import all_origin

class LeaveApprovalHandler(tornado.web.RequestHandler,MongoMixin):
    SUPPORTED_METHODS=('OPTIONS','PUT')

    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]
    holiday=MongoMixin.userDb[
        CONFIG['database'][0]['table'][20]['name']
    ]
    leave=MongoMixin.userDb[
        CONFIG['database'][0]['table'][22]['name']
    ]

    #if there is same for all handlers
    def options(self):
        code =4100
        status=False
        message=''
        result=[]
    async def put(self):
        code =4100
        status=False
        message=''
        result=[]

        try:
            try:
                token = self.request.headers.get('Authorization')
                if token:
                    token = token.replace('Bearer ', '')
                else:
                    code = 4211
                    message = 'Invalid - [ Authorization ]'
                    status = False
                    raise Exception

                # Decode the token
                payload = JWT_DECODE_1(token)
                if payload is None:
                    code = 4212
                    message = 'Invalid - [ Authorization ]'
                    status = False
                    raise Exception
            except Exception as e:
                Log.i(e)
                code = 4334
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception

            user_id = payload.get('userId')
            company_id = payload.get('companyId')
            role = payload.get('userRole')
            print(role)

            if role not in ['branchManager', 'HR-1', 'HR-2', 'HR-3']:
                code=4003
                message='You are not Authorized to use this'
                status=False
                raise Exception

            # converting the body into json
            print('**********')
            try:
                self.request.arguments=json.loads(self.request.body)

            except Exception as e:
                code=4004      
                message='Expected request type json'
                status=False
                raise Exception
            # print('**********')
            leave_id = self.request.arguments.get('leaveId')
            print('**************',leave_id)

            if not leave_id:
                code = 4006
                message = 'Missing leaveId in request'
                raise Exception
            
            empUserId= self.request.arguments.get('empUserId')
            if not empUserId:
                code = 4007
                message = 'Missing empUserId in request'
                raise Exception


            # Check user existence
            user_query = self.user.find({'_id': ObjectId(empUserId)}, limit=1)
            user = []
            async for i in user_query:

                user.append(i)

            if not user:
                code = 4005
                message = 'User not found'
                raise Exception

            # branch_id = user[0]['branchId']

            # Check if the leave request exists
            leave_query = self.leave.find({'_id': ObjectId(leave_id)}, limit=1)
            leave_request = []
            async for leave in leave_query:
                leave_request.append(leave)

            print(leave_query)

            if not leave_request:
                code = 4007
                message = 'Leave request not found'
                raise Exception

            # Approve the leave
            update_result = await self.leave.update_one(
                {'_id': ObjectId(leave_id)},
                {'$set': {'isApproved': True}}
            )

            if update_result.modified_count == 0:
                code = 4008
                message = 'Failed to approve leave'
                raise Exception

            code = 2000
            status = True
            message = 'Leave approved successfully'
            result = {'leaveId': leave_id}
 #writ the logic to modify theapprove the holiday


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
    


   