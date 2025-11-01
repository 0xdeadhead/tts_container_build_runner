from pydub import AudioSegment, silence
import torch
import numpy as np


class AudioProcessor:
    def __init__(self):
        pass

    def torch_tensor_to_audiosegment(
        self, waveform: torch.Tensor, sample_rate: int
    ) -> AudioSegment:
        # Ensure CPU numpy array
        if waveform.dtype == torch.float32 or waveform.dtype == torch.float64:
            # floats assumed in [-1.0, 1.0] (common from torchaudio.load)
            # Convert to int16 PCM
            arr = waveform.detach().cpu().numpy()
            # If 1D (n,), make (1, n)
            if arr.ndim == 1:
                arr = np.expand_dims(arr, 0)
            # Clip then scale
            arr = np.clip(arr, -1.0, 1.0)
            pcm16 = (arr * 32767.0).astype(np.int16)
            sample_width = 2  # bytes
            raw_bytes = (
                pcm16.T.tobytes()
            )  # interleave channels by transposing (samples, channels)
            channels = pcm16.shape[0]
        else:
            # integer dtypes (int16, int32, uint8)
            arr = waveform.detach().cpu().numpy()
            if arr.ndim == 1:
                arr = np.expand_dims(arr, 0)
            # Determine sample width
            if np.issubdtype(arr.dtype, np.signedinteger) or np.issubdtype(
                arr.dtype, np.unsignedinteger
            ):
                sample_width = arr.dtype.itemsize
            else:
                raise ValueError(f"Unsupported tensor dtype: {arr.dtype}")
            # # pydub expects little-endian PCM interleaved by sample
            # # Ensure proper dtype endianness
            # if arr.dtype.byteorder == ">" or (
            #     arr.dtype.byteorder == "=" and not np.little_endian
            # ):
            #     arr = arr.byteswap().newbyteorder()
            raw_bytes = arr.T.tobytes()
            channels = arr.shape[0]

        # Create AudioSegment
        audio_segment = AudioSegment(
            data=raw_bytes,
            sample_width=sample_width,
            frame_rate=sample_rate,
            channels=channels,
        )
        return audio_segment

    def trim_silences(
        self,
        audio_segment: AudioSegment,
        min_silence_len=2000,
        silence_thresh=-40,
        hop_size=1,
    ):
        nonsilent_parts = silence.detect_nonsilent(
            audio_segment,
            min_silence_len=min_silence_len,
            silence_thresh=int(audio_segment.dBFS) + silence_thresh,
            seek_step=hop_size,
        )
        processed = AudioSegment.empty()

        for start, end in nonsilent_parts:
            processed += audio_segment[start:end]
        return processed
