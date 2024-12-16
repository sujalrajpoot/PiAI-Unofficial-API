import json
import re
from typing import Dict, Optional
import requests
import cloudscraper

class PiAIError(Exception):
    """Base exception for PiAI-related errors."""
    pass

class SessionExpiredError(PiAIError):
    """Raised when the AI session has expired."""
    pass

class VoiceNotFoundError(PiAIError):
    """Raised when an invalid voice is selected."""
    pass

class APIConnectionError(PiAIError):
    """Raised when there are issues connecting to the Pi AI API."""
    pass

class AudioDownloadError(PiAIError):
    """Raised when there are issues downloading the audio response."""
    pass

class PiAIClient:
    """
    A comprehensive client for interacting with the Pi AI service.
    
    This class provides methods for chat interactions and audio generation 
    with robust error handling and configurable parameters.
    """

    # Define voice constants as a class-level attribute
    AVAILABLE_VOICES: Dict[str, int] = {
        "William": 1,
        "Samantha": 2,
        "Peter": 3,
        "Amy": 4,
        "Alice": 5,
        "Harry": 6
    }

    def __init__(
        self, 
        host_session: str, 
        conversation_id: str, 
        cf_bm: str = "", 
        timeout: int = 10
    ) -> None:
        """
        Initialize the PiAI client with session and connection parameters.

        Args:
            host_session (str): Unique session identifier
            conversation_id (str): Conversation session identifier
            cf_bm (str, optional): Cloudflare bot management cookie. Defaults to "".
            timeout (int, optional): Request timeout in seconds. Defaults to 10.
        
        Raises:
            ValueError: If session parameters are invalid
        """
        self._validate_session_parameters(host_session, conversation_id)

        self._scraper = cloudscraper.create_scraper()
        self._base_url = 'https://pi.ai/api/chat'
        self._host_session = host_session
        self._cf_bm = cf_bm
        self._timeout = timeout
        
        self._headers = self._create_headers()
        self._cookies = {
            '__Host-session': self._host_session,
            '__cf_bm': self._cf_bm
        }

        self._conversation_id = conversation_id

    def _validate_session_parameters(
        self, 
        host_session: str, 
        conversation_id: str
    ) -> None:
        """
        Validate the session parameters before initialization.

        Args:
            host_session (str): Session identifier to validate
            conversation_id (str): Conversation identifier to validate

        Raises:
            ValueError: If session parameters are empty or invalid
        """
        if not host_session or not conversation_id:
            raise ValueError("Host session and conversation ID must be non-empty strings.")

    def _create_headers(self) -> Dict[str, str]:
        """
        Create standardized headers for API requests.

        Returns:
            Dict[str, str]: Configured request headers
        """
        return {
            'Accept': 'text/event-stream',
            'Content-Type': 'application/json',
            'Origin': 'https://pi.ai',
            'Referer': 'https://pi.ai/talk',
            'X-Api-Version': '3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def chat(
        self, 
        prompt: str, 
        voice_name: str = "Alice", 
        verbose: bool = True,
        output_file: str = "PiAI.mp3"
    ) -> str:
        """
        Send a chat prompt and retrieve AI's response with optional audio generation.

        Args:
            prompt (str): Text prompt to send to AI
            voice_name (str, optional): Voice for audio response. Defaults to "Alice".
            verbose (bool, optional): Enable detailed logging. Defaults to True.
            output_file (str, optional): Path to save audio response. Defaults to "PiAI.mp3".

        Returns:
            str: AI's text response

        Raises:
            VoiceNotFoundError: If an invalid voice is specified
            SessionExpiredError: If the session has expired
            APIConnectionError: For network or API communication issues
        """
        self._validate_voice(voice_name)

        try:
            response = self._send_chat_request(prompt)
            ai_response = self._process_chat_response(response, voice_name, verbose, output_file)
            return ai_response
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Failed to communicate with Pi AI: {e}")

    def _validate_voice(self, voice_name: str) -> None:
        """
        Validate the selected voice name.

        Args:
            voice_name (str): Voice name to validate

        Raises:
            VoiceNotFoundError: If the voice is not in available voices
        """
        if voice_name not in self.AVAILABLE_VOICES:
            raise VoiceNotFoundError(
                f"Invalid voice. Available voices: {list(self.AVAILABLE_VOICES.keys())}"
            )

    def _send_chat_request(self, prompt: str) -> requests.Response:
        """
        Send the chat request to Pi AI API.

        Args:
            prompt (str): Text prompt to send

        Returns:
            requests.Response: API response
        """
        request_data = {
            'text': prompt,
            'conversation': self._conversation_id
        }

        response = self._scraper.post(
            self._base_url, 
            headers=self._headers, 
            cookies=self._cookies, 
            json=request_data, 
            stream=True, 
            timeout=self._timeout
        )

        if response.status_code in (401, 403):
            raise SessionExpiredError("Session expired. Please update credentials.")

        return response

    def _process_chat_response(
        self, 
        response: requests.Response, 
        voice_name: str, 
        verbose: bool, 
        output_file: str
    ) -> str:
        """
        Process the chat response and handle audio generation.

        Args:
            response (requests.Response): API response to process
            voice_name (str): Selected voice for audio
            verbose (bool): Enable detailed logging
            output_file (str): Path to save audio response

        Returns:
            str: Processed text response
        """
        output_str = response.content.decode('utf-8')
        sids = re.findall(r'"sid":"(.*?)"', output_str)
        second_sid = sids[1] if len(sids) >= 2 else None

        streaming_text = self._extract_streaming_text(output_str)
        
        self._download_audio_threaded(voice_name, second_sid, verbose, output_file)
        
        return streaming_text

    def _extract_streaming_text(self, output_str: str) -> str:
        """
        Extract streaming text from the API response.

        Args:
            output_str (str): Raw API response string

        Returns:
            str: Extracted text response
        """
        streaming_text = ""
        for line in output_str.splitlines():
            try:
                modified_line = re.sub("data: ", "", line)
                parsed_data = json.loads(modified_line)
                if 'text' in parsed_data:
                    streaming_text += parsed_data['text']
            except (json.JSONDecodeError, KeyError):
                continue
        return streaming_text

    def _download_audio_threaded(
        self, 
        voice_name: str, 
        message_sid: Optional[str], 
        verbose: bool, 
        output_file: str
    ) -> None:
        """
        Download audio response in a separate thread.

        Args:
            voice_name (str): Selected voice name
            message_sid (Optional[str]): Message identifier for audio
            verbose (bool): Enable detailed logging
            output_file (str): Path to save audio file

        Raises:
            AudioDownloadError: If audio download fails
        """
        if not message_sid:
            return

        params = {
            'mode': 'eager',
            'voice': f'voice{self.AVAILABLE_VOICES[voice_name]}',
            'messageSid': message_sid,
        }

        try:
            audio_response = self._scraper.get(
                'https://pi.ai/api/chat/voice', 
                params=params, 
                cookies=self._cookies, 
                headers=self._headers, 
                timeout=self._timeout
            )
            audio_response.raise_for_status()

            with open(output_file, "wb") as file:
                file.write(audio_response.content)

            if verbose:
                print("\033[1;92mAudio file downloaded successfully.\033[0m")

        except requests.exceptions.RequestException as e:
            raise AudioDownloadError(f"Failed to download audio: {e}")

# Example usage
def main():
    """
    Example usage of the PiAIClient class.
    """
    try:
        client = PiAIClient(
            host_session='your_host_session', 
            conversation_id='your_conversation_id',
        )
        response = client.chat("and what is neurall network?")
        print(f"\nPiAI: {response}\n")
    except PiAIError as e:
        print(f"PiAI Error: {e}")

if __name__ == "__main__":
    main()