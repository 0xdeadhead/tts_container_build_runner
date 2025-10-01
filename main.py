import asyncio
from chatterbox.tts import ChatterboxTTS
from src.telegram_client import TelegramClient
from src.s3_client import S3Client
from src.audio_generation import AudioGenerator
from src.text_preprocessing import TextPreProcessor
import logging
from pathlib import Path
import torchaudio as ta
import runpod
import os
import uuid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

DEVICE = os.getenv("INFERENCE_DEVICE", "mps")
LOGGER = logging.getLogger(__name__)
MODEL = ChatterboxTTS.from_pretrained(device=DEVICE)
FILE_SAVE_ROOT_DIR = Path(os.getenv("FILE_SAVE_ROOT_DIR", "."))
VOICE_SAMPLE_DIR = Path(os.getenv("VOICE_SAMPLE_DIR", "./voice_samples/"))
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


LOGGER.info(
    f" Initializing with FILE_SAVE_ROOT_DIR:{FILE_SAVE_ROOT_DIR} ,VOICE_SAMPLE_DIR:{VOICE_SAMPLE_DIR} "
)

s3_client = S3Client(
    access_key_id=AWS_ACCESS_KEY_ID,
    access_key_secret=AWS_SECRET_ACCESS_KEY,
    region=AWS_REGION,
)

telegram_client = TelegramClient(api_token=TELEGRAM_BOT_TOKEN)


def handler(params):
    model_inputs = params["input"]
    callback_url = params["webhook"]  # onhold
    delimiting_token = model_inputs["delimiting_token"]
    audio_format = model_inputs["audio_format"]
    silence_duration = model_inputs["silence_duration"]
    sent_limit_per_chunk = model_inputs["sent_limit_per_chunk"]
    temperature = model_inputs["temperature"]
    text = model_inputs["text"]
    repetition_penalty = float(model_inputs["repetition_penalty"])
    voice_path = VOICE_SAMPLE_DIR.joinpath(model_inputs["voice"])
    url_expiry_days = model_inputs["url_expiry_days"]
    chat_ids = model_inputs["chat_ids"]
    processor = TextPreProcessor(
        delimiting_token=delimiting_token,
        spacy_model_lang_code="en_core_web_sm",
        sent_limit_per_chunk=sent_limit_per_chunk,
    )
    audio_generator = AudioGenerator(
        text_preprocessor=processor,
        model=MODEL,
        break_duration_in_secs=silence_duration,
    )
    wav = audio_generator.text_to_wav(
        text=text,
        audio_prompt_path=Path(voice_path),
        progress_update_callback=lambda a, b: runpod.serverless.progress_update(
            params, {"sections_processed": a, "total_sections": b}
        ),
        temperature=temperature,
        repetition_penalty=repetition_penalty,
    )
    file_name = str(uuid.uuid4())
    file_path = FILE_SAVE_ROOT_DIR.joinpath(f"{file_name}.{audio_format}")
    ta.save(file_path, wav, audio_generator.model.sr)
    LOGGER.info(f" Uploading {file_name} to {AWS_S3_BUCKET_NAME} ")
    s3_client.upload_file(
        file_path=file_path, bucket_name=AWS_S3_BUCKET_NAME, object_key=file_name
    )
    LOGGER.info(f" Presigning {file_name} @ {AWS_S3_BUCKET_NAME} ")
    file_url = s3_client.generate_presigned_url(
        object_key=file_name,
        bucket_name=AWS_S3_BUCKET_NAME,
        expires_in=url_expiry_days * 86400,
    )
    # ignore errors here, runpod already runs in event loop
    await telegram_client.send_message(
        text=f"Script :\n\n {text[:60]} \n\n Download at : {file_url} ",
        chat_ids=chat_ids,
    )
    return {"file_url": f"{file_url}"}


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
