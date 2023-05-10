from vosk import Model, KaldiRecognizer  # оффлайн-распознавание от Vosk
import speech_recognition  # распознавание пользовательской речи (Speech-To-Text)
import pyttsx3  # синтез речи (Text-To-Speech)
import wave  # создание и чтение аудиофайлов формата wav
import json  # работа с json-файлами и json-строками
import os  # работа с файловой системой
from subprocess import Popen, PIPE

import math, random


def run_ssh_cmd(host, cmd):
    cmds = ['ssh', '-t', host, cmd]
    return Popen(cmds, stdout=PIPE, stderr=PIPE, stdin=PIPE)


class VoiceAssistant:
    """
    Настройки голосового ассистента, включающие имя, пол, язык речи
    """
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""


def setup_assistant_voice():
    """
    Установка голоса по умолчанию (индекс может меняться в 
    зависимости от настроек операционной системы)
    """
    voices = ttsEngine.getProperty("voices")


    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            # Microsoft Zira Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[1].id)
        else:
            # Microsoft David Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[2].id)
    else:
        assistant.recognition_language = "ru-RU"
        ru_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0"
        ttsEngine.setProperty('voice', ru_voice_id)


def play_voice_assistant_speech(text_to_speech):
    """
    Проигрывание речи ответов голосового ассистента (без сохранения аудио)
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()


def record_and_recognize_audio(*args: tuple):
    """
    Запись и распознавание аудио
    """
    with microphone:
        recognized_data = ""

        # регулирование уровня окружающего шума
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your microphone is on, please?")
            return

        # использование online-распознавания через Google 
        # (высокое качество распознавания)
        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            pass

        # в случае проблем с доступом в Интернет происходит 
        # попытка использовать offline-распознавание через Vosk
        except speech_recognition.RequestError:
            print("Trying to use offline recognition...")
            recognized_data = use_offline_recognition()

        return recognized_data


def ssh_command(command = ''):
    results = run_ssh_cmd('my_remote_host.com', command).stdout.read()
    print(results)


def use_offline_recognition():
    """
    Переключение на оффлайн-распознавание речи
    :return: распознанная фраза
    """
    recognized_data = ""
    try:
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("models/vosk-model-small-ru-0.4"):
            print("Please download the model from:\n"
                  "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit(1)

        # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model("models/vosk-model-small-ru-0.4")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()

                # получение данных распознанного текста из JSON-строки 
                # (чтобы можно было выдать по ней ответ)
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except:
        print("Sorry, speech service is unavailable. Try again later")

    return recognized_data


if __name__ == "__main__":

    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    # инициализация инструмента синтеза речи
    ttsEngine = pyttsx3.init()
    ttsEngine.setProperty('rate', 175)     # скорость речи
    ttsEngine.setProperty('volume', 0.9)   # громкость (0-1)

    # настройка данных голосового помощника
    assistant = VoiceAssistant()
    assistant.name = "russian"
    assistant.sex = "male"
    assistant.speech_language = "ru-RU"

    # установка голоса по умолчанию
    setup_assistant_voice()
    play_voice_assistant_speech("начинаю работу")
    #make_ssh_gitpull()

    print(ttsEngine.getProperty('voice'))
    while True:
        # старт записи речи с последующим выводом распознанной речи
        # и удалением записанного в микрофон аудио
        voice_input_raw = record_and_recognize_audio()

        try:
            os.remove("microphone-results.wav")
        except: 
            pass

        print(voice_input_raw)

        # отделение комманд от дополнительной информации (аргументов)
        if voice_input_raw == None:
            continue
        voice_input = voice_input_raw.split(" ")
        command = voice_input

        if command[0] == 'раб' or command[0] == 'работник':
            if command[1] == "привет":
                play_voice_assistant_speech("приветствую тебя хозяин")
            elif command[1] == "скажи":
                play_voice_assistant_speech(command[2:])
            elif (command[1] == 'git' and command[2] == 'pull') or command[1] == 'дэдпул':
                #ssh_command('git pull origin dev')
                play_voice_assistant_speech("я сделал гит пул на дэве, хозяин")
            elif voice_input_raw.find('перезапусти') != -1:
                #ssh_command('service gunicorn restart')
                play_voice_assistant_speech("я перезапустил гуник на мейне")
            elif voice_input_raw.find('подкинь монетку') != -1:
                rand = random.randint(0,1)
                if rand == 0:
                    play_voice_assistant_speech("орёл")
                else:
                    play_voice_assistant_speech("решка")
        if voice_input_raw.find('блин') != -1 or voice_input_raw.find('жесть') != -1:
            play_voice_assistant_speech("не ругайся хозяин")
        
        voice_input_raw = ''


'''
engine = pyttsx3.init()     # инициализация движка

engine.setProperty('voice','ru')
# зададим свойства
engine.setProperty('rate', 175)     # скорость речи
engine.setProperty('volume', 0.9)   # громкость (0-1)

engine.say("I have done, my master!")      # запись фразы в очередь
engine.say("Я всё сделал, мой хозяин!")  # запись фразы в очередь

# очистка очереди и воспроизведение текста
engine.runAndWait()'''