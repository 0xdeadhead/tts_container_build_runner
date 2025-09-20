from ast import Call
from chatterbox.tts import ChatterboxTTS
from .text_preprocessing import TextPreProcessor
import torch
from typing import Callable, Optional


class AudioGenerator:
    def __init__(
        self,
        text_preprocessor: TextPreProcessor,
        model: ChatterboxTTS,
        break_duration_in_secs: float,
    ):
        self.model = model
        self.text_preprocessor = text_preprocessor
        self.silence = torch.zeros(
            int(self.model.sr * break_duration_in_secs)
        ).unsqueeze(0)

    def text_to_wav(
        self,
        text: str,
        repetition_penalty=1.2,
        min_p=0.05,
        top_p=1.0,
        audio_prompt_path=None,
        exaggeration=0.5,
        cfg_weight=0.5,
        temperature=0.8,
        progress_update_callback: Optional[Callable[[int, int], None]] = None,
    ):
        sections = self.text_preprocessor.get_sections(text=text)
        audio_chunks = []
        for section_index, section in enumerate(sections):
            if section != self.text_preprocessor.delimiting_token:
                partitions_generator = self.text_preprocessor.get_partitions(section)
                for chunk in partitions_generator:
                    audio_chunks.append(
                        self.model.generate(
                            text=chunk,
                            repetition_penalty=repetition_penalty,
                            min_p=min_p,
                            top_p=top_p,
                            audio_prompt_path=audio_prompt_path,
                            exaggeration=exaggeration,
                            cfg_weight=cfg_weight,
                            temperature=temperature,
                        )
                    )
            else:
                audio_chunks.append(self.silence)
            if progress_update_callback:
                progress_update_callback(section_index, len(sections))
        return torch.cat(tuple(audio_chunks), dim=1)
