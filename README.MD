# Automated Training Data Transfer Between StudyTube and SolaForce

## Project description

Some_company uses two systems: StudyTube, a learning platform, and SolaForce, an HR system for tracking training records. Manual data transfer between these systems has led to delays, inefficiencies, and a higher risk of errors in HR records, which in turn increases administrative workload and can affect timely decision‑making.

To address these issues, the Metropolia team has developed an automated data‑transfer solution that synchronizes StudyTube and SolaForce, eliminates the need for manual updates, improves efficiency, and reduces errors.

## Technologies used

-   **Programming language**: Python 3.12
-   **Service**: Azure Functions with Timer trigger
-   **Development**: Azurite (for Azure Storage Account integration local development)
-   **GitHub repository**: https://github.com/AnastasiiaX/study_to_sola (repository is private)
-   **Documentation**: the Metropolia team received documentation from both partners, StudyTube and SolaForce.

## Installation & Setup

1. Clone the repository
2. Install required packages: `pip install -r requirements.txt`
3. Set up `local.settings.json` file with necessary environment variables
4. Run Azurite and start the Azure Function locally with `func start`

## Usage

### Main flow of the code

Azure Timer Function pulls data from StudyTube, processes it and then uploads to Solaforce. The function runs on a timer trigger at midnight in Finland. Then the function saves timecode to Azure Storage Account as a blob, so it will know for the next time since when data should be checked.

When the function runs it logs out some info and error messages, if they occur. If during function run it has not found any new study record, it will log: "No new trainings to export. No data to send." The message will differ if the function has found new study records, then it will log a small text line telling how many records were uploaded

### Key Files and Their Roles

-   `fetch.py`: File for fetching all completed courses after updated_after timestamp from Studytube and converts results to match Solaforce's requirements.

-   `function_app.py`: Azure Function configuration file, defines Timer trigger type.

-   `local.settings.json`: Local environment settings

-   `push.py`: File for pushing data to SolaForce

-   `requirements.txt`: List of all dependencies needed to run the project.

## Environment Variables:

### Azurite variables:

```
"STORAGE_ACC_CONN_STRING": "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
```

It’s not sensitive or secret information, because it’s only used for development purposes. These values are always the same, when using Azurite.

```
"STORAGE_ACC_CONT_NAME": Name of the container in Azure Storage Account
"STORAGE_ACC_BLOB_NAME": Name of the blob in Azure Storage Account
```

### StudyTube API access variables:

```
"STUDYTUBE_CLIENT_ID": StudyTube Client Id
"STUDYTUBE_CLIENT_SECRET": StudyTube Client Secret
"STUDYTUBE_TOKEN_URL": https://STUDYTUBE_INSTANCE/gateway/oauth/token
"STUDYTUBE_USERS_COURSES_URL": https://STUDYTUBE_INSTANCE/api/v2/users/courses
```

### SolaForce API access variables:

```
"SOLAFORCE_USER_ID": SolaForce User’s Id
"SOLAFORCE_USER_KEY": SolaForce User’s Key
"SOLAFORCE_API_URL": https://SOLAFORCE_INSTACE/d/json/uploadtrainings
```

## Testing:

The code was tested solely in the test environments of both systems.

## Limitations / Notes:

Maximum allowed length for trainingTypeStr is 63 characters in SolaForce.

## Working / Opening project

### VSCode

1. Open VSCode
2. Select File -> Open Folder and find study_to_sola from your Desktop

### Terminal

1. Open Terminal
2. type `cd Desktop/study_to_sola`

## Starting work (branching out and back to main)

### Create your own feature branch

0. You should be in Terminal, once you done step from Opening project chapter
1. Type: `git checkout main` and after that type: `git pull origin main`
2. Type: `git checkout -b feature/YOUR_BRANCH_NAME` (not in caps lock)

-   Do your programming here

3. Once you have made your change type: `git add .`
4. Type: `git commit -m "DESCRIBE THE CHANGE YOU MADE HERE"` (not in capse lock)
5. Type: `git push origin feature/YOUR_BRANCH_NAME` branch name you need to use from the second step
6. In response from git you will get smth like: "Create Pull Request: https://XXXX". Open this link in browser and go through the process to first create and then merge Pull Request. Don't forget to delete the branch.
7. Type: `git checkout origin main`
