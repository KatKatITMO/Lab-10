# Лабораторная работа №10 - Голосовой ассистент.

'''# реализовать голосового ассистента, умеющего распознавать не менее четырех разных команд.'''


import speech_recognition as sr
import pyttsx3
import requests
import random
from datetime import datetime

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.currency_data = None
        self.last_update = None

    def speak(self, text):
        print(f"{text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with self.microphone as source:
            print("Говорите...")
            audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
        
        try:
            text = self.recognizer.recognize_google(audio, language="ru-RU").lower()
            print(f"{text}")
            return text
        except sr.UnknownValueError:
            self.speak("Ошибка распознавания команды")
            return None
        except Exception as e:
            self.speak(f"Ошибка микрофона: {str(e)}")
            return None

    def update_currency_data(self):
        try:
            response = requests.get(
                "https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/rub.json",
                timeout=5
            )
            response.raise_for_status()
            self.currency_data = response.json().get("rub", {})
            self.last_update = datetime.now()
            return True
        except Exception as e:
            self.speak(f"Не удалось получить курсы валют. Ошибка: {str(e)}")
            return False

    def get_rate(self, currency_code):
        if not self.currency_data or (datetime.now() - self.last_update).seconds > 3600:
            if not self.update_currency_data():
                return None
        
        rate = self.currency_data.get(currency_code)
        if rate:
            return f"1 рубль = {rate:.2f} {currency_code.upper()}"
        return f"Валюта {currency_code.upper()} не найдена"

    def handle_command(self, command):
        if not command:
            return

        if any(word in command for word in ["доллар"]):
            self.speak(self.get_rate("usd") or "Не удалось получить курс доллара")

        elif any(word in command for word in ["евро"]):
            self.speak(self.get_rate("eur") or "Не удалось получить курс евро")

        elif any(word in command for word in ["фунт"]):
            self.speak(self.get_rate("gbp") or "Не удалось получить курс фунта")

        elif any(word in command for word in ["йена"]):
            self.speak(self.get_rate("jpy") or "Не удалось получить курс йены")

        elif any(word in command for word in ["случайный"]):
            if self.currency_data:
                currency = random.choice(list(self.currency_data.keys()))
                self.speak(f"Случайная валюта: {self.get_rate(currency)}")
            else:
                self.speak("Сначала нужно загрузить данные о валютах")

        elif any(word in command for word in ["все валюты", "все"]):
            if self.currency_data:
                rates = "\n".join([f"{k.upper()}: {v:.2f}" for k, v in self.currency_data.items()])
                self.speak("Текущие курсы валют к рублю: " + rates.replace("\n", ", "))
            else:
                self.speak("Данные о валютах не загружены")

        else:
            self.speak("Ошибка в запросе. Попробуйте: доллар, евро, фунт, йена, случайный, все валюты")

    def run(self):
        self.speak("Голосовой ассистент для курсов валют запущен. Скажите команду. Для того, чтобы выйти, скажите СТОП")
        while True:
            try:
                command = self.listen()
                if command and any(word in command for word in ["стоп"]):
                    self.speak("До свидания!")
                    break
                self.handle_command(command)
            except KeyboardInterrupt:
                self.speak("Работа завершена")
                break

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()