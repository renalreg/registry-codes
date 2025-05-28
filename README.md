# Registry Codes
## What is this?
This repository holds standard codes used throughout registry systems. These codes ensure that all our systems reference and update to a single source of truth. The github artifacts created by this repository can be used to restore the reference tables in the ukrdc and ukrr or create a local redis cache. 

## How to use
- code sets can be downloaded as stand alone csv files 
- pg_dump artifact can be used to restore tables in ukrdc or other postgres databases
- TODO: Redis cache can be set up via the docker image
- TODO: sqlite cache can be setup by downloading sqlite file 


## Adding new code 
To release new codes create a branch with incoming changes. After it has be fully reviewed by the relavent medical and technical expertise it can be merged in to create new artifacts and update all the services which point at it. 

## Keeping services in sync
Databases and other services should be kept in sync with a chron jobs and tools such as:
https://github.com/SimonCropp/GitHubSync

To pg_restore when new artifacts are released 