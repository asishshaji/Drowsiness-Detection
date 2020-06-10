import React, { useEffect, useRef, useState } from 'react';
import { Text, View } from 'react-native';

import { Audio } from 'expo-av';
import { Camera } from 'expo-camera';

export default function App() {
  const [hasPermission, setHasPermission] = useState(null);
  const [text, setText] = useState("Checking")
  const camera = useRef(null)
  console.disableYellowBox = true;
  useEffect(() => {

    const interval = setInterval(async () => {
      await camera.current.takePictureAsync({
        base64: true,
        quality: 1,
        onPictureSaved: async (pic) => {
          console.log("Trying")
          const reqData = await fetch("https://drowsinessapiproject.herokuapp.com/detect", {
            method: 'POST',
            body: JSON.stringify({ file: pic.base64 }),
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
          });

          const { level, result } = await reqData.json()
          setText(result)
          console.log(result)
          if (level >= 1) {
            const soundObject = new Audio.Sound();
            try {
              await soundObject.loadAsync(require('./assets/hello.mp3'));
              await soundObject.playAsync();
            } catch (error) {
            }
          }

        }
      })
    }, 1000);


    return () => clearInterval(interval)
  }, []);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  return (
    <Camera style={{ flex: 1 }} ref={camera} type={Camera.Constants.Type.front}>
      <View
        style={{
          flex: 1,
          backgroundColor: 'transparent',
          flexDirection: 'row',
        }}>
        <View
          style={{
            flex: 1,
            alignSelf: 'flex-end',
            alignItems: 'center',
            marginBottom: 70
          }}
        >
          <Text style={{ fontSize: 28, color: 'white', fontWeight: 'bold' }}>{text}</Text>

        </View>
      </View>
    </Camera>
  );
}