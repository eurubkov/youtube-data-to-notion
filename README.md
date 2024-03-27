# Youtube Stats to Notion Database Updater

This repo will set up infrastructure for AWS Lambda to run on hourly basis to update your Notion Database with Youtube stats, such as likes, comments, views, as well as the title of the video based on the YT ID value from your Notion dataset.

Here's an example dataset prefilled with 200 YT IDs for MrBeast videos: https://www.notion.so/a6dd95d55f2243008216b84ffe03e464?v=8a7bd9bae8d84690a011a01bb6ba7201&pvs=4


## Instructions
1. #### Retrieve API Keys for Notion, Youtube and AWS
A detailed list of all the instructions to build this solution from scratch, which includes the instructions for setting up API keys, can be found [here]().

2. #### Retrieve the Notion Database ID
 It's the value between .so/ and ?v when you look at the Notion URL in the address bar. If we look at the example dataset above, the database ID will be `a6dd95d55f2243008216b84ffe03e464`.

3. #### Store API Keys in AWS Parameter store
In your AWS account, go to the Parameter Store and add your API keys and the Notion Database ID as secret keys with the following names:
`/yt_notion_lambda/notion_api_key`
`/yt_notion_lambda/youtube_api_key`
`/yt_notion_lambda/notion_db_id`

4. #### Retrieve AWS Account ID
After you've stored these keys, you can click on one of them and look at its ARN. It should look like `arn:aws:ssm:us-west-2:{YOUR_AWS_ACCOUNT_ID}:parameter/yt_notion_lambda/notion_api_key`. Copy the value for {YOUR_ACCOUNT_ID}.

5. #### Update cdk_stack.py
In `cdk/cdk/cdk_stack.py`, replace `{YOUR_AWS_ACCOUNT_ID}` with the value retrieved in step 4.

6. #### Create a new user in AWS
In your AWS account, go to IAM -> Users and Create a new user.
On the "Set permissions" screen, choose "Attach Policies Directly." Search for and select the "AdministratorAccess" policy. Follow the rest of the prompts.

7. #### Create Access Key
Go to the newly created user -> Security Credentials -> Access Keys -> Create Access Key.

Select "Command Line Interface (CLI)" and check the box to confirm that you understand that there are other recommendations. Follow the rest of the prompts until you see the "Access Key" and "Secret Access Key".

8. #### Create .env file
At the root of the project, create the file named `.env`. 
Paste the following:
```
AWS_ACCESS_KEY_ID={YOUR_ACCESS_KEY}
AWS_SECRET_ACCESS_KEY={YOUR_SECRET_ACCESS_KEY}
AWS_DEFAULT_REGION=us-west-2
```
and replace {YOUR_ACCESS_KEY} and {YOUR_SECRET_ACCESS_KEY} with the values retrieved from step 7.

9. #### Install Docker
Go to https://docs.docker.com/get-docker/ and download and install Docker. This is to automatically set up the remaining steps after running a couple of commands.

10. #### Run these commands
Open the terminal and navigate to the root of this project.
Run the following commands (one by one).
`docker-compose up --build -d` -> this will build and start a Docker container.
`docker-compose exec dev-environment bash` -> this will open a bash session in the Docker container
`make` -> this will take care of packaging the code to be executed in AWS Lamda, and then will use CDK to create new resources in your AWS account and deploy the packaged code.


The Lambda is currently set up to run once an hour, but feel free to go to your AWS account -> Lambda, find the function that has `update_notion_db` in its name and click `Test` to invoke it manually. You should see it successfully executing and your Notion database should be updated with Youtube stats.
If that doesn't happen, check the logs to see what's wrong. Make sure you followed all the 10 steps from this Readme.
