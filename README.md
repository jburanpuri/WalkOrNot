# WALK OR NOT – PROJECT REPORT

## Project Links
- **Live Application:** [Walk or Not on Heroku](https://walkornot-7a4f9baaf72e.herokuapp.com)
- **Code Repository:** [WalkorNot on GitHub](https://github.com/jburanpuri/WalkorNot)

## Introduction
This report details the system requirements and design decisions for the "Walk or Not" application.

## Requirements

### Software Requirements
- **Operating System**: Any OS capable of running Python, with WSL using venv recommended.
- **Database**: MongoDB.
- **Message Broker**: RabbitMQ, utilized via CloudAMQP add-on for Heroku.
- **Frontend**: Compatible with all modern web browsers.
- **Backend**: Developed using Python & Flask.
- **Development Tools**: Version control with Git, along with a suitable IDE for development.

### Hardware Requirements
- **Client**: No specific hardware required, runs on any standard web browser.
- **Server**: At least a 2 GHz dual-core processor and 4 GB RAM.

### Connectivity
A stable internet connection is necessary for API communication. API keys are required from the following services:
- [OpenWeather API](https://openweathermap.org/api)
- [Google Geocoding API](https://developers.google.com/maps/documentation/geocoding/overview)

An `.env` file is required to store these API keys securely.

### Project Setup
To run the project, modify `app.py` by removing `src` from the import statement:

```python
from messages import send_message, setup_queue
```

Then, in a WSL/Unix system, set the FLASK_APP environment variable and run Flask:

```python
export FLASK_APP=src/app.py
flask run
```

## Design Decisions

### Flask + RabbitMQ Integration
- Enables efficient concurrency handling and asynchronous processing with Flask and RabbitMQ.
 Provides reliability and task persistence through messages.py, which interfaces with RabbitMQ.
- Lays the groundwork for easy scaling and potential transition to a microservices architecture.
  
### MongoDB
- Selected for high performance and quick scalability.
- Accommodates the flexible and varied nature of weather data, typical of NoSQL databases.
  
### REST API
- Decouples the client and server, allowing them to scale independently.
- Adheres to REST principles, offering standardized, stateless, and cacheable endpoints for simplified integration.

### Security
- Keeps API keys secure on the server-side, away from the client.

## Whiteboard Design

![Web App](https://github.com/jburanpuri/WalkorNot/assets/60244493/975ba15c-2cf3-4aaf-a771-267cee071cad)




