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

class AddHolidayHandler(tornado.web.RequestHandler,MongoMixin):
    SUPPORTED_METHODS=('OPTIONS','POST')

    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]
    holiday=MongoMixin.userDb[
        CONFIG['database'][0]['table'][20]['name']
    ]

    #if there is same for all handlers
    def options(self):
        code =4100
        status=False
        message=''
        result=[]
    async def post(self):
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

            if role != 'branchManager':
                code=4003
                message='You are not Authorized to use this'
                status=False
                raise Exception
            #converting the body into json
            try:
                self.request.arguments=json.loads(self.request.body)

            except Exception as e:
                code=4004      
                message='Expected request type json'
                status=False
                raise Exception
            
            userQ= self.user.find(
                {
                    '_id':ObjectId(user_id)
                },
                limit=1
            )

            user=[]
            async for i in userQ:
                user.append(i)

            print('*****************',user)
            if not user:
                message='user not found'
                code=4005
                status=False
                raise Exception
            branch_id=user[0]['branchId']
            print("breach _id is",branch_id)
            
         
            title=self.request.arguments.get('title')
            print("your title is :--------------",title)
            
            if title is None or not title or  not isinstance(title,str):
                print("***********",title)
                code = 4332
                message = 'Please Enter Valid Title.'
                status = False
                raise Exception
           
            print('***********',title)

            holidayDate=self.request.arguments.get('holidayDate')
            holidayDate = datetime.strptime(holidayDate, '%Y-%m-%d').date()
            if holidayDate is None or not holidayDate:
                code = 4333
                message ='plz enter the valid date in the format of YYYY-MM-DD.',
                status = False
                raise Exception
            
            print('*************',holidayDate)

             #wirte code here
            data={
                'comapnyId':ObjectId(company_id),
                'branchId':ObjectId(branch_id),
                'userId':ObjectId(user_id),
                'title':title,
                'date':holidayDate.strftime('%Y-%m-%d'),
                'currentYear':datetime.now().year,
                'isActive':True,
                'isDeleted':False
                 
             }
            print("*&*&*&*&*&*&*&*&*&**&*&*&*&*&*&*&*&*&*&*&*&*&*&")
            
            try:
                await self.holiday.insert_one(data)
                code = 200
                status = True
                message = 'Holiday added successfully'

            except Exception as e:
                code = 43315
                status =False
                message = 'faild to add holiday'
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
    


   