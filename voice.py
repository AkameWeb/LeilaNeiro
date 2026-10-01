# voice.py
import sounddevice as sd
import numpy as np
import speech_recognition as sr
import pyttsx3
import time

class VoiceController:
    def __init__(self, input_device=None, output_device=None):
        devices = sd.query_devices()
        self.input_device = input_device
        self.output_device = output_device

        # Автовыбор устройства ввода (микрофон)
        if self.input_device is None:
            for i, dev in enumerate(devices):
                if 'Микрофон' in dev['name'] and dev['max_input_channels'] > 0:
                    self.input_device = i
                    break
        # Автовыбор устройства вывода (динамики)
        if self.output_device is None:
            for i, dev in enumerate(devices):
                if 'Динамики' in dev['name'] and dev['max_output_channels'] > 0:
                    self.output_device = i
                    break

        print(f"[VOICE] Устройство ввода: {self.input_device} - {devices[self.input_device]['name'] if self.input_device is not None else 'по умолчанию'}")
        print(f"[VOICE] Устройство вывода: {self.output_device} - {devices[self.output_device]['name'] if self.output_device is not None else 'по умолчанию'}")

        # Синтез речи
        self.engine = pyttsx3.init()
        self.is_speaking = False
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                print(f"[VOICE] Голос: {voice.name}")
                break
        self.engine.setProperty('rate', 160)
        self.engine.setProperty('volume', 0.9)

        # Распознавание
        self.recognizer = sr.Recognizer()
        self.sample_rate = 16000

    def listen(self, timeout=5) -> str:
        print("🎤 Слушаю...")
        try:
            recording = sd.rec(
                int(self.sample_rate * timeout),
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                device=self.input_device
            )
            sd.wait()
            audio_bytes = recording.flatten().tobytes()
            audio = sr.AudioData(audio_bytes, self.sample_rate, 2)
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            print(f"✅ Распознано: {text}")
            return text
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return ""

    def speak(self, text: str):
        if self.is_speaking:
            return
        self.is_speaking = True
        print(f"🔊 Лейла говорит: {text}")
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
        except Exception as e:
            print(f"❌ Ошибка озвучивания: {e}")
        finally:
            self.is_speaking = False