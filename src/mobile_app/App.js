import React, { useState } from 'react';
import { StyleSheet, View, TextInput, Button, ScrollView, Text } from 'react-native';
import WebView from 'react-native-webview';

const STREAMLIT_URL = 'https://your-streamlit-url.com/';
const AGENT_ENDPOINT = 'https://your-agent-endpoint.com/agent';
const VIZIO_TV_IP = '192.168.1.100';

export default function App() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const sendQuestion = async () => {
    const res = await fetch(AGENT_ENDPOINT, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({question})
    });
    const json = await res.json();
    setAnswer(json.answer);
  };

  const launchTV = async () => {
    await fetch(`http://${VIZIO_TV_IP}/launch`, {method:'POST'});
  };

  return (
    <View style={{flex:1}}>
      <WebView source={{uri: STREAMLIT_URL}} style={{flex:1}} />
      <ScrollView style={styles.chat}>
        <TextInput value={question} onChangeText={setQuestion} placeholder="Ask about EAI" style={styles.input} />
        <Button title="Send" onPress={sendQuestion} />
        <Text>{answer}</Text>
        <Button title="Launch TV" onPress={launchTV} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  chat: { padding: 10 },
  input: { borderWidth: 1, marginBottom: 5, padding: 8 }
});
