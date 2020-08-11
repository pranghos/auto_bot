# auto_bot
automatic chatbot

Running the app:

Step 1: Run the data preparation module to ingest data by hitting the url with input data (file: csv, pdf or data: url) as form-data in postman:: http://localhost:5000/upload

Step2:  Run the nlp module by running the command in Windows powershell: Invoke-RestMethod -Method POST -Uri http://localhost:9099/nlp

Step3:  Run the manual curation module by running the url  in web browser: http://localhost:5000/upload
Step4:  Run the auto api module by running the url  in web browser: https://us-south.functions.cloud.ibm.com/api/v1/web/pranghos%40in.ibm.com_Hello/default/autoapi_1.json ? -X GET -H "X-Require-Whisk-Auth: 6432182022200363" Or, from Windows  command line: Curl https://us-south.functions.cloud.ibm.com/api/v1/web/pranghos%40in.ibm.com_Hello/default/autoapi_1.json ? -X GET -H "X-Require-Whisk-Auth: 6432182022200363"

It will create a new workspace in Watson Assistance skill with intents, entity and dialogues
