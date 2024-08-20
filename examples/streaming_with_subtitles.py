#!/usr/bin/env python3

"""
Streaming TTS example with subtitles.

This example is similar to the example basic_audio_streaming.py, but it shows
WordBoundary events to create subtitles using SubMaker.
"""

import asyncio

import edge_tts

TEXT = "Hello World!"
VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "test.mp3"
WEBVTT_FILE = "test.vtt"


async def amain() -> None:
    """Main function"""
    communicate = edge_tts.Communicate(TEXT, VOICE)
    submaker = edge_tts.SubMaker()
    with open(OUTPUT_FILE, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    with open(WEBVTT_FILE, "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs())

async def amain2(text, voice, rate, volume, audio_file, subtitle_file, pitch="+0Hz") -> None:
    try_count = 0
    while try_count < 3:
        try:
            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
            submaker = edge_tts.SubMaker()
            with open(audio_file, "wb") as file:
                current_sentence = ""
                async for chunk in communicate.stream():
                    # print((chunk["offset"], chunk["duration"]), chunk["text"], chunk["type"])
                    # print( chunk["type"])
                    if chunk["type"] == "audio":
                        file.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

            sub_file: Union[TextIOWrapper, TextIO] = (
                open(subtitle_file, "w", encoding="utf-8")
                if subtitle_file
                else sys.stderr
            )
            with sub_file:
                sub_file.write(submaker.generate_subs_based_on_punc(text))
                break
        except:
            try_count += 1
            time.sleep(try_count * 2)


if __name__ == "__main__":
    #asyncio.run(amain())
    asyncio.run(amain2(TEXT, VOICE, 1.0, 1.0, OUTPUT_FILE, WEBVTT_FILE))