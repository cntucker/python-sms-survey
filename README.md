# python-sms-survey
Python example for automated SMS survey

#### Prerequisites
Python 3.4

Ngrok 2.2

#### Set Up Instructions
1. Clone and open the project
2. In your terminal window, navigate to the Ngrok source folder and enter the command `ngrok http 4000`
3. Record the forwarding URL
4. Sign in to your Catapult account (https://catapult.inetwork.com)
5. Under the Account tab, record `User ID`, `API Token` and `API Secret`
6. OPTIONAL: If you already have a phone number you wish to use, create a new application with the number.  
      Callback URL for the application should be the forwarding URL appended with `/callback`.
      If no application/number is created, a new one will be created automatically.
7. In the project, open the file `SurveySender.py`
8. Replace `BANDWIDTH_USER_ID`, `BANDWIDTH_API_TOKEN` and `BANDWIDTH_API_SECRET`with the values from step 5.
9. Replace `CALLBACK_URL` with the forwarding URL from step 3, appended with `/callback` (ex: https://12345678.ngrok.io/callback)
10. Replace PREFERRED_AREA_CODE with the 3 digit area code preffered for the sender phone number. Unless a number is provided,
    You will be assigned a number with this area code, if available.
11. Run `app.py`
12. Navigate to the forwarding URL in any web browser

#### Usage Instructions
Once you have navigated to the URL, a page will be displayed with an empty list of surveys. You can add surveys via the form
at the bottom of the page. If the Bandwidth Phone Number space is left blank, a new phone number will be added to your account
for each survey.
Once a survey has been added, links will appear to add questions and send the survey. Once the survey has received responses, 
they will appear in an additonal tab on the questions page.
