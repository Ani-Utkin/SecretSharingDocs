# SecretSharingDocs

This project will implement Shamir's Secret Sharing on Google Drive Files. Google Docs and Google Sheets are the prime files used. Both encryption and reconstruction are implemented in this project.

# Installation

```bash
npm install
```

Packages required:

* Python3
* Flask
* React
* googleapiclient
* Google API Library


# Start the Application

To run the project, the python backend needs to be running:

```python
python app.py
```

Next would be to start the frontend found in the react-frontend folder

```react
cd react-frontend
cd secret-sharing-doc

npm start
```