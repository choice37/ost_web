from google.cloud import texttospeech
from google.oauth2.service_account import Credentials
import os
import zipfile
import tarfile

def zip_files(input_path, output_zip):
    # zip 파일 생성
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        # list/daily_test 디렉토리의 파일들 추가
        for foldername, subfolders, filenames in os.walk(input_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zipf.write(file_path, os.path.relpath(file_path, input_path))
    
    print(f"Files zipped successfully into {output_zip}")

def tar_gz_files(input_path, output_tar_gz):
    # tar.gz 파일 생성
    with tarfile.open(output_tar_gz, "w:gz") as tar:
        # list/daily_test 디렉토리의 파일들 추가
        for foldername, subfolders, filenames in os.walk(input_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                tar.add(file_path, arcname=os.path.relpath(file_path, input_path))
    
    print(f"Files tar.gz successfully into {output_tar_gz}")


def generate_spk2gender(text_list, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for i, _ in enumerate(text_list, start=1):
            f.write(f"dailyset_{i}\tm\n")
    print(f"spk2gender file written to {output_file}")

def generate_spk2utt(text_list, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for i, _ in enumerate(text_list, start=1):
            f.write(f"dailyset_{i}\tdailyset_{i}\n")
    print(f"spk2utt file written to {output_file}")

def generate_utt2spk(text_list, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for i, _ in enumerate(text_list, start=1):
            f.write(f"dailyset_{i}\tdailyset_{i}\n")
    print(f"utt2spk file written to {output_file}")

def generate_text(text_list, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for i, text in enumerate(text_list, start=1):
            f.write(f"dailyset_{i}\t{text}\n")
    print(f"text file written to {output_file}")

def generate_wav_scp(text_list, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for i, _ in enumerate(text_list, start=1):
            f.write(f"dailyset_{i}\t/nas_model/TOOL_LIBS/testset/wav/daily_test/daily_spk_file_{i}.wav\n")
    print(f"wav.scp file written to {output_file}")

def text_to_speech(text, output_file, json_path, language_code="ko-KR", gender="NEUTRAL", sample_rate=44100):
    # 서비스 계정 키 파일 로드
    credentials = Credentials.from_service_account_file(json_path)
    
    # Text-to-Speech 클라이언트 생성
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    # 입력 텍스트 설정
    input_text = texttospeech.SynthesisInput(text=text)

    # 성별 옵션 설정
    if gender.upper() == "MALE":
        ssml_gender = texttospeech.SsmlVoiceGender.MALE
    elif gender.upper() == "FEMALE":
        ssml_gender = texttospeech.SsmlVoiceGender.FEMALE
    else:
        ssml_gender = texttospeech.SsmlVoiceGender.NEUTRAL

    # 음성 설정
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=ssml_gender
    )

    # 오디오 설정
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,  # WAV 포맷을 위한 LINEAR16 설정
        sample_rate_hertz=sample_rate
    )

    # 텍스트를 음성으로 변환
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    # 오디오 파일로 저장
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio content written to {output_file}")

# 사용 예시
# text_list = [
#     "주택", "전세", "전세자금", "전세대출", "전세대", "전세자금대출", "주택전세", "보증료", "절차", "주택자금",
#     "주택대출", "주택담보", "주택담보대출", "주담대", "아파트", "저당", "저당권", "근저당", "근저당권",
#     "갚으려면", "갚기", "말소", "등기부등본", "등기", "담보대출", "예금", "금융상품", "예금담보", "수신담보",
#     "청약", "청약담보", "청약대출", "청약담보대출", "청약 담보대출", "주택청약", "주택청약담보", "주택청약 담보"
# ]

text_list =[
    "5분 뒤로",
    "아트월",
    "마음을 바라던 너 앨범 들려줘",
    "전란 틀어줘",
    "영웅들의 눈물 틀어줘",
    "마더 안드로이드 틀어줘",
    "서울대 야구부 틀어줘",
    "지옥에서 온 판사 틀어줘"
]

list_path = "./list/daily_test"
json_path = "./bgm-537-b9fa3d50e755.json"  # 서비스 계정 키 파일 경로
wav_path = "./wav/daily_test"
output_zip = "./daily_test.zip"

# spk2gender 파일 생성
generate_spk2gender(text_list, os.path.join(list_path, "spk2gender"))
generate_spk2utt(text_list, os.path.join(list_path, "spk2utt"))
generate_utt2spk(text_list, os.path.join(list_path, "utt2spk"))
generate_text(text_list, os.path.join(list_path, "text"))
generate_wav_scp(text_list, os.path.join(list_path, "wav.scp"))

# wav 디렉토리에 있는 기존 파일 삭제
os.system("rm -rf ./wav/daily_test/*")

# 텍스트 리스트를 순회하며 음성 파일 생성 (max sample_rate=44100 default=24000)
for i, text in enumerate(text_list, start=1):
    output_file = f"{wav_path}/daily_spk_file_{i}.wav"
    text_to_speech(text, output_file, json_path, language_code="ko-KR", gender="NEUTRAL", sample_rate=22000)

tar_gz_files(list_path, "./category.txt")
tar_gz_files(wav_path, "./pattern.txt")

