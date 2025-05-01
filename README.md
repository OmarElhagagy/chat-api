# Scalable Chat API with Load Balancing and Caching

A high-performance, scalable chat API built with FastAPI, PostgreSQL, Redis, and Nginx for load balancing.

## Features

- **Authentication**: User registration and JWT-based authentication
- **Chat Rooms**: Create and manage chat rooms
- **Real-time Messaging**: WebSocket support for real-time communication
- **REST API**: Traditional REST endpoints for CRUD operations
- **Load Balancing**: Nginx-based load balancing across multiple API instances
- **Caching**: Redis caching for improved performance
- **Monitoring**: Prometheus and Grafana for metrics and visualization
- **Rate Limiting**: Protection against abuse
- **Horizontal Scaling**: Easy to scale by adding more API instances

## Architecture

![Architecture](https://placeholder-api/1200/600)

The application consists of the following components:

1. **FastAPI Instances**: Multiple instances of the Chat API for horizontal scaling
2. **Nginx**: Load balancer that distributes traffic across API instances
3. **PostgreSQL**: Primary database for storing users, rooms, and messages
4. **Redis**: In-memory cache for improved performance and session management
5. **Prometheus & Grafana**: Monitoring and visualization of system metrics

## Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chat-api.git
   cd chat-api
   ```

2. Run the application:
   ```bash
   ./run.sh
   ```

3. The following services will be available:
   - API Documentation: http://localhost/docs
   - Grafana Dashboard: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token

### Chat

- `POST /api/chat/rooms` - Create a new chat room
- `GET /api/chat/rooms` - List all chat rooms
- `POST /api/chat/messages` - Send a message to a room
- `GET /api/chat/rooms/{room_id}/messages` - Get messages for a room

### WebSockets

- `WS /ws/{room_id}?token={token}` - WebSocket endpoint for real-time chat

## Development

### Project Structure

```
chat-api/
├── app/
│   ├── api/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── chat.py          # Chat endpoints
│   │   ├── dependencies.py  # Dependency injection helpers
│   │   ├── middleware.py    # Custom middlewares
│   │   └── websocket.py     # WebSocket handlers
│   ├── core/
│   │   ├── config.py        # Application configuration
│   │   └── metrics.py       # Prometheus metrics
│   ├── db/
│   │   ├── database.py      # Database connection
│   │   └── redis_cache.py   # Redis connection
│   ├── models/
│   │   ├── chat.py          # Chat models
│   │   └── user.py          # User models
│   ├── services/
│   │   ├── auth.py          # Authentication services
│   │   ├── chat_service.py  # Chat services
│   │   └── user_service.py  # User services
│   └── main.py              # Application entry point
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker build instructions
├── nginx.conf               # Nginx configuration
├── prometheus.yml           # Prometheus configuration
├── requirements.txt         # Python dependencies
└── run.sh                   # Start-up script
```

### Adding New Features

1. Create new models in the `app/models/` directory
2. Implement services in the `app/services/` directory
3. Add API endpoints in the `app/api/` directory
4. Update the main application in `app/main.py`

### Scaling

To scale the application, simply add more API instances to the `docker-compose.yml` file and update the Nginx configuration to include them.

## Testing

Run the included test script to verify that the API is working correctly:

```bash
pip install requests websockets
python test_api.py
```

## Production Considerations

Before deploying to production, make sure to:

1. Set secure passwords and environment variables
2. Use SSL/TLS for all connections
3. Implement proper logging and monitoring
4. Set up database backups
5. Configure auto-scaling based on load
6. Consider using managed services for databases and caching

## License

MIT
