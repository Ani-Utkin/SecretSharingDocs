import React, { useEffect, useState } from 'react';
import useDrivePicker from 'react-google-drive-picker'
import ReactLoading from 'react-loading';
import './App.css'


// When uploading a file, will need to pass id and mimetype to the backend to find out which encryption type to use.

const App = () => {
  const [openPicker, data] = useDrivePicker();
  const [loading, setLoading] = useState(false);

  const handleOpenPicker = (encrypt, mult) => {
    openPicker({
      clientId: "72145292632-7qcefgk96q5j4abotf8vrjr5gvsu0l45.apps.googleusercontent.com",
      developerKey: "AIzaSyA3MfY1PcmhSlm0m2SWclfP1zNDtUer3do",
      viewId: ["DOCS", "SHEETS", "DOCUMENTS"],
      setEnableDrives: false,
      showUploadView: encrypt,
      showUploadFolders: true,
      supportDrives: true,
      multiselect: mult,
    })
  }

  useEffect(() => {

    // Once files are uploaded, pass data to the backend
    if(data){

      // For reconstruction
      if(data.docs.length > 1){
        const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        };
        setLoading(true);
        fetch('/post/decode', requestOptions).then((response) => response.json()).then(response => setLoading(false)).then(response => {return alert('Finished. View Changes on Google')}).catch((error) => {setLoading(false); alert('Error! Retry.')});
        // alert('Finished. View Changes on Google');

      }
      // For Encoding
      else{

        var i = data.docs[0]
          var Uploaddata = {
            "docs": [
                {
                    "name": i.name, 
                    "id": i.id,
                    "mimeType": i.mimeType,
                },
            ]
          }
      
          const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(Uploaddata)
          };

          setLoading(true);
          fetch('/post/encode', requestOptions).then(response => response.json()).then(response => setLoading(false)).then(response => {return alert('Finished. View Changes on Google')}).catch((error) => {setLoading(false); alert('Error! Retry.')} );
          // alert('Finished. View Changes on Google');

      }
      
    }

  }, [data])

  
  return (
    <React.Fragment>
    <div className='App'>
      <header className='App-header'>
            Google Drive Secret Sharing
          </header>
      {loading ? 
        (<div className="loading" >
          <ReactLoading type={"spinningBubbles"} color="aquamarine" />
        </div>
        ) : (
          <div className='main'>
          <div className='buttons'>
            <button className='google-picker' onClick={() => handleOpenPicker(true, false)}>Encrypt Your Documents</button>
            <button className='google-picker' onClick={() => handleOpenPicker(false, true)}>Decrypt Your Shares</button>
          </div>
        </div>
      )}
    </div>
    </React.Fragment>
  );
}

export default App;