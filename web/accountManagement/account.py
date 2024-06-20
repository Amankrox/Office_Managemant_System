import json
import sys
from datetime import datetime, timedelta

import tornado.web
from bson import ObjectId
from build_config import CONFIG
from util.conn_util import MongoMixin
from util.log_util import Log
from util.time_util import timeNow
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1, JWT_ENCODE_1
from helper.decorators import all_origin

class AccountHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('OPTIONS', 'POST')

    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]

    company = MongoMixin.userDb[
        CONFIG['database'][0]['table'][13]['name']
    ]

    branch = MongoMixin.userDb[
        CONFIG['database'][0]['table'][14]['name']
    ]

    account =MongoMixin.userDb[
        CONFIG['database'][0]['table'][21]['name']
    ]
    payScale = MongoMixin.userDb[
        CONFIG['database'][0]['table'][17]['name']
    ]
    attendance=MongoMixin.userDb[
        CONFIG['database'][0]['table'][18]['name']
    ]

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

            user_id = payload.get('userId')
            company_id= payload.get('companyId')
            # find branch_id using user_id

            userQ = self.user.find({'_id': ObjectId(user_id)})

            user = []
            async for i in userQ:
                user.append(i)
            if user is None:
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
            # print("************************")
            try:
                empUserId=self.request.arguments.get('empUserId')
            except:
                code=4020
                message='enter valid emp id'
                status=False
                raise Exception

            # print("************************",empUserId)
            try:
                payId=self.request.arguments.get('payId')
            except:
                code=4021
                message='enter valid payGrade'
                status=False
                raise Exception
            # try:
            #     startDate=self.request.arguments.get('statDate')
            # except:
            #     code=4022
            #     message='enter valid startDate'
            #     status=False
            #     raise Exception
            # try:
            #     endDate=self.request.arguments.get('endDate')
            # except:
            #     code=4023
            #     message='enter valid endDate'
            #     status=False
            #     raise Exception
            try:
                emp_user =await self.user.find_one({'_id': ObjectId(user_id)})
                # print('*************',emp_user)
            except:
                code=4020
                message='Internal Server error please contact admin.'
                status=False
                raise Exception
            
            # userEmp = []
            # print('***********************',userEmp)
            # for i in emp_user:
            #     userEmp.append(i)

            if not emp_user:
                message='user not found'
                code=4006
                status=False
                raise Exception
            
            branch_id=emp_user['branchId']

            # print('******************',branch_id)

            paySlipQ = self.payScale.aggregate(
                [
                    {
                        '$match': {
                            '_id': ObjectId(payId)
                        }
                    }, {
                        '$project': {
                            '_id': {
                                '$toString': '$_id'
                            }, 
                            'payGrade': 1, 
                            'performanceBonus': 1, 
                            'baseSalary': 1, 
                            'signingBonus': 1, 
                            'annualBonus': 1
                        }
                    }
                ]
            )

            # print('****************',paySlipQ)

            paySlip =  []
            async for i in paySlipQ:
                paySlip.append(i)

            # print("***********************",paySlip) 
             
            if not paySlip:
                message='payslip not found'
                code=4007
                status=False
                raise Exception
            
            base_salary = paySlip[0]['baseSalary']
            performance_bonous = paySlip[0]['performanceBonus']
            signing_bonous = paySlip[0]['signingBonus']


            # presentDayQ = self.attendance.aggregate(

            #     [
            #         {
            #             '$match': {
            #                 'user_id': ObjectId('6668259eb27f0e68666fa3ba'), 
            #                 'is_absent': False, 
            #                 'date': {
            #                     '$gte': '2024-06-01', 
            #                     '$lte': '2024-06-30'
            #                 }
            #             }
            #         }, {
            #             '$count': 'presentDay'
            #         }
            #     ]
            # ) 
            # print("*************************",presentDayQ) 
            # presentDay1=[]
            # print("******************************",presentDay1)
            # for i in presentDayQ:
            #     presentDay1.append(i)

            # NoOfDayPresent=presentDay1[0]['presentDay']
            # # print("***************************",NoOfDayPresent)
            # print("***************")

            

            # absentDay = self.attendance.aggregate(
                # [
                #     {
                #         '$match': {
                #             'user_id': ObjectId(empUserId), 
                #             'is_absent': True,
                #             'date': {
                #                 '$gte': startDate, 
                #                 '$lte': endDate
                #             }
                #         }
                #     }, {
                #         '$count': 'absentDay'
                #     }
                # ]
            # ) 

            # leave = self.attendance.aggregate(
            #     [
            #         {
            #             '$match': {
            #                 'user_id': ObjectId(empUserId), 
            #                 'leave': False, 
            #                 'date': {
            #                     '$gte': startDate, 
            #                     '$lte': endDate
            #                 }
            #             }
            #         }, {
            #             '$count': 'leave'
            #         }
            #     ]
            # )
            # isLate=self.attendance.aggregate(
            #     [
            #         {
            #             '$match': {
            #                 'user_id': ObjectId(empUserId), 
            #                 'is_late': True, 
            #                 'date': {
            #                     '$gte': startDate, 
            #                     '$lte': endDate
            #                 }
            #             }
            #         }, {
            #             '$count': 'isLate'
            #         }
            #     ]
            # )

            # dailySalary = base_salary / 30  
            # totalPresent = presentDay1 - absentDay - leave
            # finalSalary= ((dailySalary * totalPresent)+ performance_bonous+signing_bonous)

            # # If late more than 3 days, deduct one day's salary
            # if isLate > 3:
            #     finalSalary -= dailySalary
            

            data={
                'companyId':ObjectId(company_id),
                'branchId':ObjectId(branch_id),
                'userId':ObjectId(empUserId),
                'createdBy':ObjectId(user_id),
                'payGrade':payId,
                'baseSalary':base_salary,
                # 'finalSalary':finalSalary,
                'performanceBounous':performance_bonous,
                'singingBonous':signing_bonous,
                'createdAt':datetime.now(),
                'isActive':True
            }
            try:
                await self.account.insert_one(data)
                code = 200
                status = True
                message = 'paylip added succesfully'

            except Exception as e:
                code = 43315
                status =False
                message = 'faild to add payslip'
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
