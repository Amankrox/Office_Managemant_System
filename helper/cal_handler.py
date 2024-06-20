import tornado.web
import tornado.escape
from util.cal_api import create_event, get_events, delete_event, create_holiday_event

class CalHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.token = self.request.headers.get("Authorization", "").split(" ")[-1]
        self.user_id, self.company_id, self.role = self.decode_token(self.token)

    def decode_token(self, token):
        # Replace this method with actual token decoding logic
        return "user_id", "company_id", "role"

    def get(self):
        action = self.get_argument("action", None)
        event_id = self.get_argument("event_id", None)

        if action == "get_events":
            events = get_events()
            self.write({"events": events})
        elif action == "delete_event" and event_id:
            status_code = delete_event(event_id)
            if status_code == 204:
                self.write({"status": "Event deleted"})
            else:
                self.write({"error": "Failed to delete event"})
        else:
            self.write({"error": "Invalid action or missing parameters"})

    def post(self):
        action = self.get_argument("action", None)

        if action == "create_event":
            event_data = tornado.escape.json_decode(self.request.body)
            event = create_event(event_data)
            self.write(event)
        elif action == "create_holiday" and self.role == "Branch Manager":
            holiday_data = tornado.escape.json_decode(self.request.body)
            event = create_holiday_event(holiday_data["title"], holiday_data["start"], holiday_data["end"])
            self.write(event)
        else:
            self.write({"error": "Invalid action or insufficient permissions"})


#def create_event(event_data):
   # url = f"{CAL_API_BASE_URL}/events"
  #  headers = {
  #      "Authorization": f"Bearer {API_KEY}",
  #      "Content-Type": "application/json"
  #  }
  #  response = requests.post(url, json=event_data, headers=headers)
  #  return response.json()

#def get_events():
  #  url = f"{CAL_API_BASE_URL}/events"
  #  headers = {
  #      "Authorization": f"Bearer {API_KEY}"
  #  }
  #  response = requests.get(url, headers=headers)
   # return response.json()

#def delete_event(event_id):
  #  url = f"{CAL_API_BASE_URL}/events/{event_id}"
  #  headers = {
   #     "Authorization": f"Bearer {API_KEY}"
   # }
   # response = requests.delete(url, headers=headers)
   # return response.status_code
