# AI Unit Testing Agent

An intelligent AI-powered agent that automatically generates and runs unit tests for GitHub repositories using OpenRouter's free AI models.

## Features

- 🔍 **Repository Analysis**: Automatically clones and analyzes GitHub repositories
- 🤖 **AI-Powered Testing**: Uses DeepSeek R1/V3 and other free OpenRouter models
- 🌐 **Multi-Language Support**: Auto-detects and supports Python, JavaScript, Java, C#, Go, and more
- 📊 **Coverage Reports**: Generates comprehensive test coverage reports
- 🎯 **Smart Framework Selection**: Uses the most popular testing framework for each language
- 📈 **Progress Tracking**: Real-time progress monitoring and status updates
- 🔧 **Local Development**: Runs entirely on your local machine

## Supported Languages & Frameworks

| Language | Framework | Coverage Tool |
|----------|-----------|---------------|
| Python | pytest | pytest-cov |
| JavaScript/TypeScript | Jest | Jest built-in |

## Prerequisites

- Python 3.8+
- Node.js 16+
- Git
- OpenRouter API key (free tier available)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Unit_Test_Agent
   ```

2. **Install dependencies**
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenRouter API key
   ```

4. **Run the application**
   ```bash
   # Terminal 1: Backend
   python main.py
   
   # Terminal 2: Frontend
   cd frontend
   npm start
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Usage

1. Enter a GitHub repository URL
2. Provide your OpenRouter API key
3. Select analysis options (optional)
4. Click "Analyze Repository"
5. Monitor progress in real-time
6. View generated tests and coverage reports

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI Backend│    │   AI Models     │
│                 │    │                 │    │                 │
│ - Repository    │◄──►│ - GitHub Clone  │◄──►│ - DeepSeek R1   │
│   Input         │    │ - Code Analysis │    │ - DeepSeek V3   │
│ - Progress      │    │ - Test Gen      │    │ - Qwen 2.5      │
│   Tracking      │    │ - Test Execution│    │ - Gemini 2.0    │
│ - Results       │    │ - Coverage      │    │                 │
│   Display       │    │   Reports       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## API Endpoints

- `POST /api/analyze` - Start repository analysis
- `GET /api/status/{task_id}` - Get analysis status
- `GET /api/results/{task_id}` - Get analysis results
- `GET /api/download/{task_id}` - Download test files

## Configuration

### Environment Variables

```env
OPENROUTER_API_KEY=your_api_key_here
GITHUB_TOKEN=optional_github_token
MAX_REPOSITORY_SIZE=100MB
MAX_ANALYSIS_TIME=3600
```

### Model Configuration

The agent uses a fallback strategy:
1. **Primary**: DeepSeek R1 (best reasoning)
2. **Secondary**: DeepSeek V3 (efficient processing)
3. **Backup**: Qwen 2.5 Coder (specialized coding)

## Rate Limits & Optimization

- **Free Tier**: 200 requests/day per model
- **With $10 Credit**: 1000 requests/day
- **Smart Batching**: Multiple functions per request
- **Intelligent Chunking**: Optimal code segmentation

## Development

### Project Structure

```
Unit_Test_Agent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── utils/
│   └── package.json
├── docs/
└── README.md
```


