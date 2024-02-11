import React, { useState ,useRef, useEffect} from 'react';
import socketIOClient from 'socket.io-client';



// account_sid = process.env.ACCOUNT_SID
// auth_token = process.env.AUTH_TOKEN
// client = Client(account_sid, auth_token)

function Drowsy() {
  const [recording, setRecording] = useState(false);
  const [alertFlag, setAlertFlag] = useState(false);
  const socket = socketIOClient('http://localhost:8000/');
  const videoRef = useRef([]);


  const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

    })
    .catch((error) => {
      console.error('Error accessing camera:', error);
    });
    socket.emit('start-recording');
    setRecording(true);
  
    
  };

  

  const stopRecording = () => {
    socket.emit('stop-recording');
    setRecording(false);
    const stream = videoRef.current.srcObject;
    if (stream) {
      const tracks = stream.getTracks();
      tracks.forEach((track) => track.stop());
    }
  };

  useEffect((client) => {
    socket.on('alert-triggered', (data) => {
      setAlertFlag(true);

      // When the alert is triggered, send a request to the backend to initiate the phone call
      
    });
    return () => {
      socket.off('Placing Call...');
    };
  }, []);


  socket.on('recording-started', (data) => {
    console.log('Recording started:', data);
  });

  socket.on('recording-error', (data) => {
    console.error('Recording error:', data);
  });

  

  return (
    <div className=' bg-black h-screen place-items-center grid justify-center items-center flex-wrap  justify-items-center '>
      
      {/* Display the alert flag value */}
      <div>{alertFlag && <h2 className=' text-white font-bold text-5xl'>
         !!!Alert!!!
      </h2>}</div>
      <div className=' bg-black rounded-md h-[500px] w-[800px]'>
        {/* Video element */}
        <video ref={videoRef} autoPlay playsInline muted />
      </div>  
      <div className='bg-yellow-400 p-4 rounded-lg mb-[-10px]'>
      {!recording ? (
        <button className='text-white' onClick={startRecording}>Start Recording</button>
      ) : (
        <button className='text-white' onClick={stopRecording}>Stop Recording</button>
      )}
      </div>
    </div>
  );
}

export default Drowsy;

