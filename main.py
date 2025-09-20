from chatterbox.tts import ChatterboxTTS
from src.audio_generation import AudioGenerator
from src.text_preprocessing import TextPreProcessor
import logging
from pathlib import Path
import torchaudio as ta
import torch
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


LOGGER.info(
    f" Initializing with FILE_SAVE_ROOT_DIR:{FILE_SAVE_ROOT_DIR} ,VOICE_SAMPLE_DIR:{VOICE_SAMPLE_DIR} "
)


def handler(params):
    model_inputs = params["input"]
    callback_url = params["webhook"]  # onhold
    delimiting_token = model_inputs["delimiting_token"]
    silence_duration = model_inputs["silence_duration"]
    sent_limit_per_chunk = model_inputs["sent_limit_per_chunk"]
    temperature = model_inputs["temperature"]
    text = model_inputs["text"]
    repetition_penalty = model_inputs["repetition_penalty"]
    voice_path = VOICE_SAMPLE_DIR.joinpath(model_inputs["voice"])
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
    file_name = uuid.uuid4()
    ta.save(
        FILE_SAVE_ROOT_DIR.joinpath(f"{file_name}.wav"), wav, audio_generator.model.sr
    )
    return {"file_name": f"{file_name}.wav"}


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
