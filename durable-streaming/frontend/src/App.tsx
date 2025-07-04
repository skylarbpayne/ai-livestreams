// Import React hooks for managing component state and side effects
import { useState, useEffect } from 'react';
// Import CSS for basic styling
import './App.css';

// Define the shape of data we expect from the server
interface StoryData {
  story: string;
  streamId: string;
  eventId: number;
}

function App() {
  // State to store the current number received from the server
  // useState hook manages component state - starts with null (no number yet)
  const [streamedStories, setStreamedStories] = useState<string[]>([]);
  
  // State to track connection status for user feedback
  const [isConnected, setIsConnected] = useState<boolean>(false);
  
  // State to track which stream we're connected to
  const [selectedStream, setSelectedStream] = useState<string>('stream1');

  // useEffect hook runs after component mounts (similar to componentDidMount)
  // Dependency array includes selectedStream so effect runs when stream changes
  useEffect(() => {
    // Clear previous numbers when switching streams
    setStreamedStories([]);
    setIsConnected(false);
    
    // Create a new EventSource to connect to our FastAPI server's SSE endpoint
    // EventSource is the browser's built-in API for server-sent events
    // Using relative URL since we're served from the same server now
    const eventSource = new EventSource(`http://localhost:3001/events/${selectedStream}`);

    // Event handler for when the connection is successfully opened
    eventSource.onopen = () => {
      console.log('Connected to server');
      setIsConnected(true);  // Update UI to show we're connected
    };

    // Event handler for when we receive a message from the server
    eventSource.onmessage = (event) => {
      try {
        // Parse the JSON data sent from the server
        const data: StoryData = JSON.parse(event.data);
        console.log('Received story:', data.story, data.streamId, data.eventId);
        // Update our state with the new number, which will trigger a re-render
        setStreamedStories(prev => [...prev, data.story]);
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };

    // Event handler for connection errors
    eventSource.onerror = (error) => {
      console.error('EventSource error:', error);
      setIsConnected(false);  // Update UI to show we're disconnected
    };

    // Cleanup function that runs when component unmounts
    // This prevents memory leaks by closing the EventSource connection
    return () => {
      eventSource.close();
    };
  }, [selectedStream]); // Dependency array includes selectedStream

  return (
    <div className="App">
      <header className="App-header">
        <h1>Story Stream</h1>
        
        {/* Stream selector */}
        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="stream-select">Select Stream: </label>
          <select 
            id="stream-select"
            value={selectedStream} 
            onChange={(e) => setSelectedStream(e.target.value)}
            style={{ padding: '5px', fontSize: '16px' }}
          >
            <option value="stream1">Stream 1</option>
            <option value="stream2">Stream 2</option>
            <option value="stream3">Stream 3</option>
          </select>
        </div>
        
        {/* Show connection status to the user */}
        <div style={{ marginBottom: '20px' }}>
          Status: {isConnected ? 
            <span style={{ color: 'green' }}>Connected to {selectedStream}</span> : 
            <span style={{ color: 'red' }}>Disconnected</span>
          }
        </div>
        
        {/* Display the current number, or a message if no number yet */}
        <div style={{ fontSize: '3rem', fontWeight: 'bold', color: '#61dafb' }}>
          {streamedStories.join('')}
        </div>
      </header>
    </div>
  );
}

export default App;
