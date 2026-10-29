import { useState } from 'react';
import { ActivityIndicator, Button, Image, ScrollView, StyleSheet, Text, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

// `localhost` is the phone itself on a device or emulator, not your computer.
// Set EXPO_PUBLIC_API_URL to the backend's LAN address, e.g.
//   EXPO_PUBLIC_API_URL=http://192.168.1.20:8000 npx expo start
const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

type Analysis = {
  face_shape: string;
  symmetry: number;
  recommendations: string[];
  disclaimer: string;
};

export default function App() {
  const [image, setImage] = useState<string | null>(null);
  const [result, setResult] = useState<Analysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });
    const asset = res.canceled ? undefined : res.assets[0];
    if (asset) {
      setImage(asset.uri);
      await upload(asset.uri, asset.mimeType ?? 'image/jpeg');
    }
  };

  const upload = async (uri: string, type: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const form = new FormData();
      // React Native's FormData accepts { uri, name, type } for files.
      form.append('file', { uri, name: 'face.jpg', type } as unknown as Blob);

      // Do not set Content-Type by hand: fetch must add the multipart
      // boundary itself, and a manual header leaves it out, so the server
      // cannot parse the upload.
      const res = await fetch(`${API_URL}/analyze/face`, { method: 'POST', body: form });
      const body = await res.json();
      if (!res.ok) {
        setError(typeof body?.detail === 'string' ? body.detail : `Request failed (${res.status})`);
        return;
      }
      setResult(body as Analysis);
    } catch {
      setError(`Could not reach the backend at ${API_URL}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Button title="Upload Face" onPress={pickImage} disabled={loading} />
      {image && <Image source={{ uri: image }} style={styles.image} />}
      {loading && <ActivityIndicator style={styles.gap} />}
      {error && <Text style={[styles.gap, styles.error]}>{error}</Text>}
      {result && (
        <View style={styles.gap}>
          <Text>Face shape: {result.face_shape}</Text>
          <Text>Symmetry: {Math.round(result.symmetry * 100)}%</Text>
          {result.recommendations.map((r, i) => (
            <Text key={i}>• {r}</Text>
          ))}
          <Text style={styles.disclaimer}>{result.disclaimer}</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  image: { width: 200, height: 200, marginTop: 16, borderRadius: 8 },
  gap: { marginTop: 16 },
  error: { color: '#b00020' },
  disclaimer: { marginTop: 12, fontSize: 12, color: '#666' },
});
