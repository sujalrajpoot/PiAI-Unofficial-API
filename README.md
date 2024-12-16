# Pi AI Client

## Overview

The Pi AI Client is a Python library for interacting with the Pi AI service, providing robust chat and audio generation capabilities with comprehensive error handling.

## Disclaimer ⚠️

**IMPORTANT: EDUCATIONAL PURPOSE ONLY**

This library is developed solely for educational and research purposes. Users are expected to:

- Respect Pi AI's Terms of Service and Community Guidelines
- Use the library ethically and responsibly
- Not attempt to circumvent the service's intended use
- Obtain necessary permissions before any integration
- Refrain from any activities that could harm, exploit, or disrespect the Pi AI platform or its community

The developers of this library take no responsibility for misuse. Violation of Pi AI's guidelines may result in account suspension or legal action. This library is an unofficial implementation and may require updates as the Pi AI service evolves. Always respect the platform's terms of service and community guidelines.

## Prerequisites

- Python 3.7+
- Git
- `requests` library
- `cloudscraper` library

## Installation

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/sujalrajpoot/PiAI-Unofficial-API.git

# Navigate to the project directory
cd PiAI-Unofficial-API
```

### 2. Install Dependencies

```bash
pip install requests cloudscraper
```

## Obtaining Credentials

**Note:** To use this library, you'll need to obtain your:
- `host_session`
- `conversation_id`

These can typically be found by:
1. Logging into Pi AI in your web browser
2. Inspecting network requests
3. Extracting the necessary session cookies and identifiers

## Usage Example

```python
from pi_ai_client import PiAIClient

# Replace with your actual session credentials
client = PiAIClient(
    host_session='your_host_session',
    conversation_id='your_conversation_id'
)

# Send a chat prompt and generate audio
response = client.chat(
    prompt="Hello, how are you today?", 
    voice_name="Alice", 
    output_file="response.mp3"
)

print(response)
```

## Available Voices

The library supports the following voices:
- William
- Samantha
- Peter
- Amy
- Alice
- Harry

## Error Handling

The library provides specific exception classes for different error scenarios:

- `PiAIError`: Base exception for all Pi AI related errors
- `SessionExpiredError`: Raised when the AI session has expired
- `VoiceNotFoundError`: Raised when an invalid voice is selected
- `APIConnectionError`: Raised during network or API communication issues
- `AudioDownloadError`: Raised during audio download failures

## Configuration Options

- `host_session`: Unique session identifier (required)
- `conversation_id`: Conversation session identifier (required)
- `cf_bm`: Cloudflare bot management cookie (optional)
- `timeout`: Request timeout in seconds (default: 10)

## Troubleshooting

1. **Session Expired Error**
   - Regenerate your `host_session` and `conversation_id`
   - Ensure you're logged into Pi AI
   - Check network requests for updated credentials

2. **Dependency Issues**
   - Verify you're using Python 3.7+
   - Ensure `requests` and `cloudscraper` are installed
   - Use a virtual environment to avoid conflicts

## Dependencies

- `requests`: For making HTTP requests
- `cloudscraper`: For bypassing Cloudflare protection
- `json`: For parsing API responses
- `typing`: For type hints
- `re`: For text processing

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the project repository.
