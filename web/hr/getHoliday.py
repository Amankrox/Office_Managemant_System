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
class GetHolidayListHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('OPTIONS', 'GET')

    holiday = MongoMixin.userDb[
        CONFIG['database'][0]['table'][20]['name']
    ]
    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]
    def options(self):
        code = 4100
        status = False
        message = ''
        result = []

    async def get(self):
        code = 4100
        status = False
        message = ''
        result = []

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
            userQ= self.user.find(
                {
                    '_id':ObjectId(user_id)
                },
                limit=1
            )

            user=[]
            async for i in userQ:
                user.append(i)

            # print('*****************',user)
            if not user:
                message='user not found'
                code=4005
                status=False
                raise Exception
            branch_id=user[0]['branchId']
            print("*******",branch_id)

            try:
                print("11111111")
                holidayQ= self.holiday.aggregate(
                    [
                        {
                            '$match': {
                                'branchId': ObjectId('66681d79a3c4ba4888ad4965'), 
                                'comapnyId': ObjectId('66681a63ed55f1052413d85c')
                            }
                        }, {
                            '$project': {
                                'title': 1, 
                                'date': 1, 
                                '_id': 0
                            }
                        }
                    ]
                )
                print("222222222")

                holidays=[]
                async for i in holidayQ:
                    holidays.append(i)
                code=200
                status:True
                message='this is your holidays list'
                result= holidays
                print('pppppppppppppppppppppppp',holidays)

            except Exception as e:
                code =400
                status=False
                message='Failed to fetch the list of holiday'
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
    


   