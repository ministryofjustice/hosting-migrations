''' Retrieve current on-call user from Pager Duty

Requires 3 environment variables to be set:

PAGERDUTY_API_KEY
Set to pager duty API key

SQUAD_TO_PAGERDUTY_SCHEDULE_ID 
Set to a json string mapping squad name to pager duty schedule ID, e.g. 
{
  "dso": "REDACTED",
  "laa": "REDACTED",
  "probation": "REDACTED"
}

EMAIL_TO_SLACK_MEMBER_ID
Set to a json string mapping email to slack member ID, e.g. 
{
  "joe.bloggs@somewhere.com": "REDACTED"
}
'''

import os
import json
import time
import pagerduty

pagerduty_api_key              = os.environ['PAGERDUTY_API_KEY']
squad_to_pagerduty_schedule_id = json.loads(os.environ['SQUAD_TO_PAGERDUTY_SCHEDULE_ID'])
email_to_slack_member_id       = json.loads(os.environ['EMAIL_TO_SLACK_MEMBER_ID'])

client             = pagerduty.RestApiV2Client(pagerduty_api_key)
date               = time.strftime("%Y-%m-%d")
no_concierge_found = 'true'

for squad_name in squad_to_pagerduty_schedule_id.keys():
    schedule_id  = squad_to_pagerduty_schedule_id[squad_name]
    query_string = f'?since={date}T09%3A00Z&until={date}T10%3A00Z'
    schedules    = client.rget(f'/schedules/{schedule_id}/users{query_string}')
    if len(schedules) > 0 and 'email' in schedules[0]:
        no_concierge_found = 'false'
        schedule           = schedules[0]
        email              = schedule['email']
        print(f'{squad_name}_email={email}')
        if email in email_to_slack_member_id:
            member_id = email_to_slack_member_id[email]
            print(f'{squad_name}_slack=<@{member_id}>')
        else:
            print(f'{squad_name}_slack={email.split(".")[0].capitalize()}')
    else:
        print(f'{squad_name}_slack=')
print(f'no_concierge_found={no_concierge_found}')
