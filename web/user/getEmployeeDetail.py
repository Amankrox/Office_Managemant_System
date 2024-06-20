import calendar
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

class getEmployeeDetailHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('OPTIONS', 'GET')

    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]

    company = MongoMixin.userDb[
        CONFIG['database'][0]['table'][13]['name']
    ]

    branch = MongoMixin.userDb[
        CONFIG['database'][0]['table'][14]['name']
    ]

    obBoard = MongoMixin.userDb[
        CONFIG['database'][0]['table'][16]['name']
    ]
    payScale = MongoMixin.userDb[
        CONFIG['database'][0]['table'][17]['name']
    ]

    attendance = MongoMixin.userDb[
        CONFIG['database'][0]['table'][18]['name']
    ]
    project = MongoMixin.userDb[
        CONFIG['database'][0]['table'][19]['name']
    ]
    account = MongoMixin.userDb[
        CONFIG['database'][0]['table'][21]['name']
    ]
    paySlip = MongoMixin.userDb[
        CONFIG['database'][0]['table'][23]['name']
    ]
    project = MongoMixin.userDb[
        CONFIG['database'][0]['table'][19]['name']
    ]
    assignProject=MongoMixin.userDb[
        CONFIG['database'][0]['table'][25]['name']
    ]
    calander=MongoMixin.userDb[
        CONFIG['database'][0]['table'][26]['name']
    ]
    role=MongoMixin.userDb[
        CONFIG['database'][0]['table'][15]['name']
    ]

    def options(self):
        self.set_status(204)
        self.finish()

    async def get(self):
        code = 4100
        message = ''
        status = False
        result = []

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

            user_id = payload.get('userId')
            role = payload.get('userRole')
            company_id = payload.get('companyId')

            
            


            # print("****",comp_name)
            if role not in ['branchManager', 'HR-1', 'HR-2', 'HR-3']:
                code=4003
                message='You are not Authorized to use this'
                status=False
                raise Exception
            # converting the body into json
            # print('**********')
            try:
                self.request.arguments=json.loads(self.request.body)

            except Exception as e:
                code=4004      
                message='Expected request type json'
                status=False
                raise Exception

            empUserId=self.request.arguments.get('empUserId')
            # print("userID",empUserId)
            if not empUserId:
                    message = 'employyee id is not coorect.'
                    code = 7003
                    status = False
                    raise Exception
                
            sartDate1=self.request.arguments.get('sartDate1')
            # print("*****************",sartDate1)
            if not sartDate1:
                    message = 'startDate1  is not coorect.'
                    code = 7004
                    status = False
                    raise Exception
                
            endDate1=self.request.arguments.get('endDate1')
            # print("*****************",endDate1)
            if not endDate1:
                    
                    message = 'EndDate1 id is not coorect.'
                    code = 7005
                    status = False
                    raise Exception
            sartDate2=self.request.arguments.get('sartDate2')
            # print("*****************",sartDate2)
            if not sartDate2:
                    message = 'startDate2 is not coorect.'
                    code = 7004
                    status = False
                    raise Exception
                
            endDate2=self.request.arguments.get('endDate2')
            # print("*****************",endDate2)
            if not endDate2:
                    
                    message = 'EndDate2 id is not coorect.'
                    code = 7005
                    status = False
                    raise Exception


            
            userQ = self.user.aggregate(
                [
                    {
                        '$match': {
                            '_id': ObjectId(empUserId)
                        }
                    }, {
                        '$project': {
                            'companyId': {
                                '$toString':'$companyId'
                            }, 
                            'branchId':{
                                '$toString':'$branchId'
                            }, 
                            'email': 1,
                            'companyId':1,
                            'PersonalInfo':1,
                            'role': 1, 
                            'createdBy': 1
                        }
                    }
                ]
            )

            user = []
            async for i in userQ:
                user.append(i)
            if not user:
                code = 4001
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception
            personal_info = user[0]['PersonalInfo']
            print("*******",personal_info)
            full_name = f"{personal_info['firstName']} {personal_info['lastName']}"
            phone = personal_info['phone']


            companyNameQ=self.company.aggregate(
                [
                    {
                        '$match': {
                            '_id': ObjectId(user[0]['companyId'])
                        }
                    }, {
                        '$project': {
                            'companyName': 1, 
                            '_id': 0
                        }
                    }
                ]
            )
            if not companyNameQ:
                 code=40004
                 message="cannot able to find company name "
                 status=False
                 raise Exception
            companyName=[]
            async for i in companyNameQ:
                 companyName.append(i)
            # comp_name=companyName[0]['companyName']

            roleQ=self.role.aggregate(
                [
                    {
                        '$match': {
                            '_id': ObjectId(user[0]['role'])
                        }
                    }, {
                        '$project': {
                            'role': 1, 
                            '_id': 0
                        }
                    }
                ]
            )
            if not roleQ:
                 code=40004
                 message="cannot able to find company name "
                 status=False
                 raise Exception
            role1=[]
            async for i in roleQ:
                role1.append(i)
           


            
            

            startDate1 = sartDate1
            endDate1 = endDate1
            month1 = datetime.strptime(startDate1, '%Y-%m-%d').month
    
            month_name1 = datetime.strptime(startDate1, '%Y-%m-%d').strftime('%B')
            month_days1=calendar.monthrange(datetime.strptime(startDate1, '%Y-%m-%d').year, datetime.strptime(startDate1, '%Y-%m-%d').month)[1]
            # print('***month name***********',month_days1)
            month2 = datetime.strptime(sartDate2, '%Y-%m-%d').month
            # print('month is *************',month2)
            month_name2 = datetime.strptime(sartDate2, '%Y-%m-%d').strftime('%B')
            month_days2=calendar.monthrange(datetime.strptime(sartDate2, '%Y-%m-%d').year, datetime.strptime(sartDate2, '%Y-%m-%d').month)[1]
            # print('***month name***********',month_days2)
            # nt('***month name***********',month_name2)
            if not startDate1:
                code = 4333
                message = 'Please enter the valid date in the format of YYYY-MM-DD.'
                status = False
                raise Exception

            startdate1 = str(startDate1)
            enddate1 = str(endDate1)

            startdate2 = str(sartDate2)
            enddate2 = str(endDate2)
            # print("*****************",endDate2)

            presentDayQ = self.attendance.aggregate(
                [
                    {
                        '$match': {
                            'user_id': ObjectId(empUserId), 
                            'is_absent': False, 
                            'date': {
                                '$gte': startdate1, 
                                '$lte': enddate1
                            }
                        }
                    }, {
                        '$group': {
                            '_id': None, 
                            'is_late_count': {
                                '$sum': {
                                    '$cond': [
                                        '$is_late', 1, 0
                                    ]
                                }
                            }, 
                            'leave_count': {
                                '$sum': {
                                    '$cond': [
                                        '$leave', 1, 0
                                    ]
                                }
                            }, 
                            'total_present_days': {
                                '$sum': 1
                            }
                        }
                    }, {
                        '$project': {
                            '_id': 0, 
                            'is_late_count': 1, 
                            'leave_count': 1, 
                            'total_present_days': 1
                        }
                    }
                ]
            )
            presentDay = []
            async for i in presentDayQ:
                presentDay.append(i)
            if not presentDay:
                    lateCount = 0
                    leaveCount = 0
                    totalPresentDay = 0
                 
            else:
                lateCount = presentDay[0]['is_late_count']
                leaveCount = presentDay[0]['leave_count']
                totalPresentDay = presentDay[0]['total_present_days']
            # print("******************",lateCount,leaveCount,totalPresentDay)


            try:

                presentDayQ2 = self.attendance.aggregate(
                    
                    [
                        {
                            '$match': {
                                'user_id': ObjectId(empUserId), 
                                'is_absent': False, 
                                'date': {
                                    '$gte': startdate2, 
                                    '$lte': enddate2
                                }
                            }
                        }, {
                            '$group': {
                                '_id': None, 
                                'is_late_count': {
                                    '$sum': {
                                        '$cond': [
                                            '$is_late', 1, 0
                                        ]
                                    }
                                }, 
                                'leave_count': {
                                    '$sum': {
                                        '$cond': [
                                            '$leave', 1, 0
                                        ]
                                    }
                                }, 
                                'total_present_days': {
                                    '$sum': 1
                                }
                            }
                        }, {
                            '$project': {
                                '_id': 0, 
                                'is_late_count': 1, 
                                'leave_count': 1, 
                                'total_present_days': 1
                            }
                        }
                    ]
                    
                )
                # print("*********************",presentDayQ2)
                presentDay2 = []
                async for i in presentDayQ2:
                    presentDay2.append(i)

                if not presentDay2:
                    lateCount2 = 0
                    leaveCount2 = 0
                    totalPresentDay2 = 0
                else:
                    lateCount2 = presentDay2[0]['is_late_count']
                    leaveCount2 = presentDay2[0]['leave_count']
                    totalPresentDay2 = presentDay2[0]['total_present_days']
                # print("******************",lateCount2,leaveCount2,totalPresentDay2)
            
            except Exception as e:
                code=400
                message='probelm in line no279'
                status=False
                raise Exception


            

            salaryQ = self.paySlip.aggregate(
                [
                    {
                        '$match': {
                            'userId': ObjectId(user_id),
                            'month':month2
                        }
                    }, {
                        '$project': {
                            'baseSalary': 1, 
                            'finalSalary': 1, 
                            '_id': 0
                        }
                    }
                ]
            )
            salary = []
            async for i in salaryQ:
                salary.append(i)
            
            baseSalary = salary[0]['baseSalary']
            finalSalary = round(salary[0]['finalSalary'])

            salaryQ2 = self.paySlip.aggregate(
                [
                    {
                        '$match': {
                            'userId': ObjectId(user_id),
                            'month':month1
                        }
                    }, {
                        '$project': {
                            'baseSalary': 1, 
                            'finalSalary': 1, 
                            '_id': 0
                        }
                    }
                ]
            )
            salary2 = []
            async for i in salaryQ2:
                salary.append(i)
            if not salary2:
                baseSalary2=0
                finalSalary2=0
            else:
            
                baseSalary2 = salary2[0]['baseSalary']
                finalSalary2 = round(salary2[0]['finalSalary'])

            projectQ = self.assignProject.aggregate(
                [
                    {
                        '$match': {
                            'users': {
                                '$in': [
                                    ObjectId(empUserId)
                                ]
                            }
                        }
                    }, {
                        '$project': {
                            'project_id': {'$toString':'$project_id'
                            }, 
                            'AssignedOn': 1, 
                            'tasks.taskId': 1, 
                            'tasks.taskName': 1, 
                            'tasks.dueDate': 1, 
                            '_id': 0
                        }
                    }
                ]
            )
            projects = []
            async for i in projectQ:
                projects.append(i)

            # print("************",projects)

            # projectDetails = [
            #     {
            #         "Project": f"{index + 1}",
            #        ' tasks':projects
            #         # "Date_of_Assign": project['AssignedOn'],

            #         # "List_of_task": [
            #         #     {
            #         #         "taskName": task['tasks.taskName'],
            #         #         "dueDate": task['tasks.dueDate']
            #         #     }
            #         #     for task in project.get('taskDetails', [])
            #         # ]
            #     }
            #     for index, project in enumerate(projects)
            # ]
            # print("8888888**********",projectDetails)

            projectDetails = [
                {
                    "Project": f"{index + 1}",
                    "project_id": project['project_id'],
                    "Date_of_Assign": project['AssignedOn'],
                    "List_of_tasks": [
                        {
                            "taskId": task['taskId'],
                            "taskName": task['taskName'],
                            "dueDate": task['dueDate']
                        }
                        for task in project['tasks']
                    ]
                }
                for index, project in enumerate(projects)
            ]

            print('**********************',datetime.now().date())
            

            response_data = {
                "Result": [
                    {
                        "Employee_info": {
                            "companyId": str(user[0]['companyId']),
                            "comp_name":companyName[0]['companyName'],
                            "branchId": user[0]['branchId'],
                            "user_id": str(empUserId),
                            "name": full_name,
                            "mobile_no.":phone,
                            "email": user[0]['email'],
                            "role_id": str(user[0]['role']),
                            "role_name":role1[0]['role'],
                            "createdBy": str(user[0]['createdBy'])
                        },
                        "Month": {
                            month_name1: {
                                "total_working_days": month_days1,
                                "total_present": totalPresentDay,
                                "total_absent": month_days1 - totalPresentDay,
                                "Leave_taken": leaveCount,
                                 "base_Salary":baseSalary2,
                                "salary_taken": finalSalary2
                                
                            },
                            month_name2: {
                                "total_working_days":month_days2,
                                "total_present": totalPresentDay2,
                                "total_absent": month_days2 - totalPresentDay2,
                                "Leave_taken": leaveCount2,
                                 "base_Salary":baseSalary2,
                                "salary_taken": finalSalary
                            }
                        },
                        "Task": projectDetails
                    }
                ]
            }
            code = 200
            message = 'Data fetched successfully'
            result = response_data
            status = True

        except Exception as e:
            status = False
            if not message:
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
                'message': message,
                'result': result
            }
            Log.d('RSP', response)
            try:
                self.write(json.loads(bdumps(response)))
                await self.finish()
                return
            except Exception as e:
                pass
