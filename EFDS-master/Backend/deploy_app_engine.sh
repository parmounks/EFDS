#!/bin/bash

# Prompt user for project ID
echo "Enter your Google Cloud project ID:"
read PROJECT_ID

echo "Setting up Google Cloud project: $PROJECT_ID..."

# Set the project in gcloud
gcloud config set project $PROJECT_ID

# Confirm the active project
echo "The active project is now:"
gcloud config get-value project

# Enable App Engine
echo "Enabling App Engine for the project..."
gcloud app create --region=us-central

# Deploy the application
echo "Deploying the application to App Engine..."
gcloud app deploy

# Open the application in a browser
echo "Opening the application in the browser..."
gcloud app browse

echo "Deployment complete!"
