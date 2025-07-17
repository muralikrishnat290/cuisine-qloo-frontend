# 🍽️ Kitchen Intel Frontend App

A secure Streamlit frontend application that provides an intuitive interface for AI-powered restaurant business intelligence, helping prospective restaurant owners and food truck entrepreneurs make data-driven decisions through a user-friendly web interface.

## 🔗 Backend Application

This frontend pairs with our powerful AI-driven backend platform available at: [Kitchen Intel Backend](https://github.com/muralikrishnat290/cuisine-qloo)

## ⚠️ Prototype Notice

**This is a prototype frontend application** designed to demonstrate AI-powered restaurant insights capabilities through a web interface. Please note:

- **Simple Authentication**: Uses environment variable-based authentication for demonstration purposes
- **No User Database**: This prototype does not include user registration or profile management
- **Limited Security**: Missing enterprise-grade security features required for production deployment
- **Simplified Architecture**: Built for demonstration purposes, not production scalability

For production deployment, additional infrastructure including proper user management, enhanced authentication, and security hardening would be required.

## 🌟 Overview

Kitchen Intel Frontend is a Streamlit-based web application that serves as the user interface for comprehensive restaurant business intelligence. By connecting to our AI-powered backend that leverages **Qloo's advanced AI technology**, users can analyze cuisine trends, get location recommendations, and develop marketing strategies through an intuitive, secure web interface powered by **Qloo Taste AI** and **Qloo Insights AI**.

## 📋 Table of Contents

- [🏗️ Architecture Overview](#️-architecture-overview)
- [🔄 Workflow Process](#-workflow-process)
- [🤖 AI Agents Working Behind the Scenes](#-ai-agents-working-behind-the-scenes)
- [💡 Use Cases](#-use-cases)
- [🚀 Quick Start](#-quick-start)
- [🔐 Environment Variables](#-environment-variables)

## 🏗️ Architecture Overview

The frontend connects to a sophisticated backend system powered by multiple AI agents:

```mermaid
graph TB
    A["🔍 User Query<br/>Natural Language Input"] 
    
    B["⚡ FastAPI Server<br/>Async Processing"]
    
    C["🔐 Auth Layer<br/>API Key Validation"]
    
    D["🎭 Workflow Orchestrator<br/>Stream Coordinator"]
    
    E["🍠🌮 Agent 1<br/>Cuisine & Location<br/>Detector"]
    
    F["🍣🌯 Agent 2<br/>Restaurant Insights<br/>Summarizer"]
    
    G["🍴📍 Agent 3<br/>Location Intelligence<br/>Recommender"]
    
    H["📢📊 Agent 4<br/>Demographics &<br/>Marketing Strategist"]
    
    I["🔧 TOOL: Restaurant Analytics<br/>Engine (Qloo Taste AI)"]
    J["🔧 TOOL: Location Heatmap<br/>Generator (Qloo Insights AI)"]
    K["🔧 TOOL: Reverse Geocoding<br/>Service"]
    L["🔧 TOOL: Demographics<br/>Intelligence (Qloo AI)"]
    
    M["🌊 Streaming Response<br/>Server-Sent Events"]
    
    N["💻 Frontend App<br/>Real-time Display"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    
    E --> I
    F --> J
    G --> K
    H --> L
    
    E --> M
    F --> M
    G --> M
    H --> M
    
    M --> N
    
    %% Uniform styling by component type
    %% Backend Infrastructure Components (A-D, M-N)
    style A fill:#f8f9fa,stroke:#1976d2,stroke-width:3px,color:#2c3e50,font-weight:600
    style B fill:#f8f9fa,stroke:#1976d2,stroke-width:3px,color:#2c3e50,font-weight:600
    style C fill:#f8f9fa,stroke:#1976d2,stroke-width:3px,color:#2c3e50,font-weight:600
    style D fill:#f8f9fa,stroke:#1976d2,stroke-width:3px,color:#2c3e50,font-weight:600
    style M fill:#f8f9fa,stroke:#1976d2,stroke-width:3px,color:#2c3e50,font-weight:600
    style N fill:#f8f9fa,stroke:#1976d2,stroke-width:3px,color:#2c3e50,font-weight:600
    %% AI Agents (E-H)
    style E fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#0d47a1,font-weight:600
    style F fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#0d47a1,font-weight:600
    style G fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#0d47a1,font-weight:600
    style H fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#0d47a1,font-weight:600
    %% Qloo-Powered Tools (I-L)
    style I fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100,font-weight:500
    style J fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100,font-weight:500
    style K fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100,font-weight:500
    style L fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100,font-weight:500
```

### 🎯 Qloo AI Integration Highlights

The architecture showcases **Qloo's AI technology** as the intelligence backbone of Kitchen Intel:

- **🏪 Qloo Taste AI**: Powers the Restaurant Analytics Engine, providing deep insights into food trends, dish popularity, and cuisine preferences with unmatched accuracy
- **🗺️ Qloo Insights AI**: Drives the Location Heatmap Generator, analyzing geographic data and location affinity patterns for optimal restaurant placement  
- **👥 Qloo AI**: Fuels the Demographics Intelligence tool, delivering sophisticated audience analysis and targeted marketing strategies

Each AI agent leverages these **Qloo-powered tools** to transform raw data into actionable business intelligence, making Kitchen Intel the most comprehensive restaurant planning platform available.

## 🔄 Workflow Process

The application follows a sophisticated 4-step workflow that processes user queries through specialized AI agents:

```mermaid
sequenceDiagram
    participant User as 🔍 User Query
    participant FastAPI as ⚡ FastAPI Server
    participant Auth as 🔐 Auth Layer
    participant Orchestrator as 🎭 Workflow Orchestrator
    participant Agent1 as 🍠🌮 Agent 1: Cuisine & Location Detector
    participant Agent2 as 🍣🌯 Agent 2: Restaurant Insights Summarizer
    participant Agent3 as 🍴📍 Agent 3: Location Intelligence Recommender
    participant Agent4 as 📢📊 Agent 4: Demographics & Marketing Strategist
    participant Tool1 as 🔧 Restaurant Analytics Engine (Qloo Taste AI)
    participant Tool2 as 🔧 Location Heatmap Generator (Qloo Insights AI)
    participant Tool3 as 🔧 Reverse Geocoding Service
    participant Tool4 as 🔧 Demographics Intelligence (Qloo AI)
    participant Stream as 🌊 Streaming Response
    participant Frontend as 💻 Frontend App

    User->>FastAPI: POST /stream with query
    FastAPI->>Auth: Validate API key
    Auth->>Orchestrator: Authenticated request
    
    Orchestrator->>Agent1: Extract cuisine & location
    Agent1->>Tool1: Query restaurant data
    Tool1->>Agent1: Restaurant analytics
    Agent1->>Stream: Cuisine/location results
    
    Orchestrator->>Agent2: Analyze restaurant insights
    Agent2->>Tool2: Generate location heatmap
    Tool2->>Agent2: Location affinity data
    Agent2->>Stream: Restaurant recommendations
    
    Orchestrator->>Agent3: Process location intelligence
    Agent3->>Tool3: Reverse geocode coordinates
    Tool3->>Agent3: Location names
    Agent3->>Stream: Location recommendations
    
    Orchestrator->>Agent4: Create marketing strategies
    Agent4->>Tool4: Analyze demographics
    Tool4->>Agent4: Demographics insights
    Agent4->>Stream: Marketing strategies
    
    Stream->>Frontend: Real-time streaming insights
```

## 🤖 AI Agents Working Behind the Scenes

### 1. Cuisine & Location Detector Agent 🍠🌮
- **Purpose**: Extracts cuisine type and location from natural language queries
- **Output**: Structured data with detected cuisine and location
- **Technology**: Uses structured output parsing for precise data extraction

### 2. Restaurant Insights Summarizer 🍣🌯
- **Purpose**: Analyzes restaurant data and provides trending food recommendations
- **Features**: 
  - Identifies popular dishes in specific cuisines and locations
  - Correlates restaurant popularity with cuisine preferences
  - Provides actionable recommendations for menu planning
- **Output**: Concise summaries without revealing specific data points

### 3. Location Intelligence Recommender 🍴📍
- **Purpose**: Recommends optimal locations for restaurant establishment
- **Features**:
  - Analyzes location affinity data for specific cuisines
  - Provides geographic recommendations with popularity rankings
  - Integrates reverse geocoding for human-readable location names
- **Output**: Prioritized location recommendations

### 4. Demographics & Marketing Strategist 📢📊
- **Purpose**: Creates targeted marketing strategies based on demographic data
- **Features**:
  - Analyzes demographic patterns for cuisine preferences
  - Generates marketing ideas and promotional strategies
  - Provides audience-specific recommendations
- **Output**: Actionable marketing strategies and promotional ideas

## 💡 Use Cases

- **New Restaurant Planning**: Get comprehensive insights before opening
- **Food Truck Route Optimization**: Find the best locations for mobile food service
- **Menu Development**: Understand trending dishes and customer preferences
- **Marketing Strategy**: Develop targeted promotional campaigns
- **Competitive Analysis**: Understand the local restaurant landscape

## 🚀 Quick Start

1. **Set up authentication:**
   ```bash
   python3 setup_env_auth.py
   ```

2. **Set environment variables** (copy from setup script output)

3. **Run the application:**
   ```bash
   streamlit run main.py
   ```

4. **Login** with your credentials

## 🔐 Environment Variables

### Required Variables
```bash
AUTH_USERNAME=admin
AUTH_NAME=Administrator
AUTH_EMAIL=admin@example.com
AUTH_PASSWORD=$2b$12$your_bcrypt_hashed_password
API_URL=http://localhost:8080
API_KEY=your_api_key_here
```

### Optional Variables
```bash
# Cookie configuration (omit for session-only auth)
AUTH_COOKIE_NAME=kitchen_intel_auth_cookie
AUTH_COOKIE_KEY=your_secret_key_here
AUTH_COOKIE_EXPIRY=1

# Suppress warnings
PYTHONWARNINGS=ignore
```

---

**Simple. Secure. Environment Variables Only.** 🎯