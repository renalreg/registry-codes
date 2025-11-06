# Registry Codes
This repository holds standard codes used throughout registry systems. These codes ensure that all our systems reference and update to a single source of truth. Each release automatically produces a set of files that can be used to create or sync ukrdc referance tables.  

# Usage

## Downloading Codes

Codes can be downloaded from GitHub using two methods: via the UI or direct download links.

### Via GitHub UI

1. Navigate to the [releases page](https://github.com/renalreg/registry-codes/releases).
2. Find the release you are interested in.
3. Click on the assets dropdown to view available files.
4. Click on the file you want to download (e.g., `registry_codes.dump` or `registry_codes.sqlite`).

### Direct Download Links

You can download the release assets directly using `curl`. Here is an example:

1. **Download Asset**: Use the following command to download the file.
   ```bash
   curl -L -o registry_codes.dump \
       https://github.com/renalreg/registry-codes/releases/download/latest/registry_codes.dump
   ```

   Replace the URL with the direct link to the asset you want to download.

## Syncing reference tables in postgres
1. **Get Dump of Codes:**
   - Download the registry codes dump file using `curl`.
   ```bash
   curl -L -o registry_codes.dump https://github.com/renalreg/registry-codes/releases/download/refs/tags/limited/registry_codes.dump
   ```

2. **Restore Table Using Dump File:**
   - Use `pg_restore` with the `--table` option to restore the modality codes table from the downloaded dump file.
   ```bash
   pg_restore -U postgres -d your_database_name --table=modality_codes registry_codes.dump
   ```

3. **Cleanup:**
   - Delete the downloaded dump file to clean up your directory.
   ```bash
   rm registry_codes.dump
   ```

## TODO: Syncing reference tables with sqlserver

## Local caching with sqlite 
Here is an example of how to use the sqlite database with Python and the `ukrdc-sqla` models:

1. **Download the SQLite Database:**
   - Use `curl` to download the `registry_codes.sqlite` file from the GitHub repository (useful in docker).
   ```bash
   curl -L -o registry_codes.sqlite https://github.com/renalreg/registry-codes/releases/download/latest/registry_codes.sqlite
   ```
   - Doing the equivalent in pure python is also straightforward:
   ```python
   import pathlib
   import urllib.request
   codes_path = pathlib.Path("xyz:/mypreferedpath/registry_codes.sqlite")

   if not codes_path.exists():
      urllib.request.urlretrieve("https://github.com/renalreg/registry-codes/releases/latest/download/registry_codes.sqlite", codes_path)
   ```

2. **Set up the Environment:**
   - Ensure you have the `ukrdc-sqla` package installed.
   ```bash
   pip install ukrdc-sqla
   ```

3. **Connect to the SQLite Database:**
   - Use SQLAlchemy to establish a connection to the `registry_codes.sqlite` database.
   ```python
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   from ukrdc_sqla.ukrdc import Codes

   # Create an engine connected to the SQLite database
   engine = create_engine('sqlite:///registry_codes.sqlite')

   # Create a configured session class
   Session = sessionmaker(bind=engine)

   # Create a session
   session = Session()

   # Query the modality codes table
   modality_codes = session.query(Codes).limit(10).all()
   for code in modality_codes:
       print(code.registry_code, code.registry_code_desc)

   # Close the session
   session.close()
   ```

   This example demonstrates how to configure a session with the `ukrdc-sqla` ORM and query the `modality_codes` table within the SQLite database.

## TODO: Local caching with redis

## TODO: Integrate auto importer of ods codes

## Available tables 
- modality_codes. TODO: v5 dataset codes.
- TODO: satellite_map
- TODO: code_list
- TODO: code_map
- TODO: code_exclusion
- TODO: rr_codes  
- TODO: rr_data_definition
- TODO: facility


# Modifying Codeset (Non-technical)

Follow these steps to update the registry codes:

1. **Request a branch** - Ask a systems team member to create a new branch named something clear like `update-modality-codes-2025`

2. **Update CSV files** - Download, edit, and upload the CSV files in the 
`tables` directory:
[!important] csv files exclude created on dates and updated on dates 
   - Open the CSV file in Excel or similar program
   - Make your changes (without altering column structure)
   - Save as CSV with the same filename if updating or new filename if adding
   
   ### How to Upload CSV Files via GitHub UI
   
   If you have GitHub access, you can upload files directly:
   
   1. Navigate to the repository on GitHub
   2. Switch to your branch using the dropdown menu (usually says "main" by default)
   3. Navigate to the correct folder (e.g., `/tables/modality_codes/`)
   4. Click the "Add file" button near the top right of the file list
   5. Select "Upload files" from the dropdown
   6. Either drag and drop your CSV file or click "choose your files" to browse
   7. Scroll down and add a commit message describing your changes (e.g., "Update modality codes for 2025")
   8. Click the green "Commit changes" button

3. **Request review**
   - Ask for a Pull Request to be created from your branch
   - Request specific reviewers (e.g., medical experts for clinical codes, systems team for technical validation)
   - Provide a description explaining what changes you've made and why

4. **Address feedback** - If changes are requested, update your CSV files and share them with the technical team

5. **Approval and release** - Once approved, systems will handle merging and creating a new version tag

The GitHub Actions workflow will automatically create a new release with updated database files.

# Releasing new codeset
When satisfied that a new version of the codes is ready to be released and has been merged in main it can be published via a github action.
1. Tag the master branch with a new tag. This can be done with the git client or with the releases sidebar.
2. This will trigger a workflow to publish the release in draft. The postgres dump and sqlite files will be attach along with some docs.
3. Generate change log and make any manual changes required.
4. Publish draft release.

# Automatically sync databases 
Schedule periodic checks for new releases using `cron` and trigger a sync if a new release is found. Example:
  ```bash
  0 * * * * TAG=$(curl -s https://api.github.com/repos/renalreg/registry-codes/releases/latest | grep '"tag_name":' | awk -F'"' '{print $4}') && \
  [ "$TAG" != "$(cat latest_release.txt)" ] && echo "$TAG" > latest_release.txt && /path/to/sync_script.sh
  ```
where path/to/sync_script.sh follows the steps in the sync postgres section. 
