###Sprint 1: Setting Up Development Environment and Basic Architecture
Tasks:
Set Up Project Environment:
Install HTML-CSSfor the frontend.
Set up Google Colab and Google Earth Engine (Google cloud) environment to run your AI model.
Ensure the project is integrated with Git for version control.
Fixing datasets resolution and pixels
Initial Backend Setup:
Flask for API setup
Frontend Setup:
Set up basic components for the user interface (e.g., a basic dashboard).
Deliverable: A structured project environment where front-end and API communicate over basic routes, and google cloud is ready for AI integration.

Sprint 2: AI Integration with Google cloud and Backend Development
Milestone: The AI model is integrated with the backend and responds to API requests.
Tasks:
Integrate Google cloud with API:
Deploy the AI model to google cloud. 
Continue gathering data and coding, implementing image patching
Use Axios or HTTP requests in flask to communicate with the environment.
Ensure that real-time fire detection data can be fetched from the cloud.
API Development:
Create API endpoints for the frontend to request data (e.g., real-time fire detection results).
Develop logic for handling AI responses and formatting the results for the frontend.
WebSocket Integration:
Ensure that any fire detection event from the AI model triggers an update in the frontend.
Deliverable: A backend that successfully communicates with the Cloud, fetches fire detection data, and changes the frontend in real-time.

Sprint 3: Frontend Development and UI/UX Design
Milestone: A functional user interface (UI) that can receive real-time data and interact with the backend.
Tasks:
Design UI Components:
Create an integrated/functional in HTML-CSS that displays real-time fire detection status (e.g., fire or no fire, confidence level, location).
Configure and connect the "Run Detection" button to manually trigger the AI detection process.
Implement real-time updates for fire detection( pop-ups or page transfer for example).
Interactive Map Integration:
Integrate a map (Database link) into the dashboard to display the detected fire locations.
Notification System:
Develop functionality to notify users with alerts (e.g., text, email) when a fire is detected.
Backend:
Detection has a mid-accuracy
Deliverable: A fully functional and interactive frontend that displays real-time fire detection results and provides user interaction.

Sprint 4: Email/SMS Notifications and Automation
Milestone: Automated email and SMS alerts are sent upon fire detection.
Tasks:
SMS Alerts:
Use Twilio to integrate SMS notifications for real-time fire detection.(check)
Add an option in the frontend for users to configure SMS alerts.
Backend:
Write logic in the backend to automatically trigger email/SMS alerts when the AI model detects fire.
Ensure the system can send these alerts in real-time using WebSockets or HTTP triggers.
Fire detection from dataset accuracy is acceptable.
Deliverable: Automated email and SMS notifications are sent in real-time based on AI model results.

Sprint 5: Testing, Deployment, and Final Improvements
Milestone: A fully tested and deployed system with real-time data functionality.
Tasks:
Added task: fire prediction 
End-to-End Testing:
Perform unit and integration testing on all components (frontend, backend, AI integration, notifications).
Ensure that all edge cases are handled (e.g., network interruptions, false positives).
Deployment:
Deploy the frontend and backend on Google cloud (Final).
Update git.
Performance Optimization:
Optimize real-time data handling (e.g., minimize latency in WebSocket communication).
Ensure that the system can handle scaling (multiple users, more real-time data).
Deliverable: A deployed, scalable, and fully functional system that detects fires in real-time and alerts relevant authorities or users.

 

