"""
SubMaker package for the Edge TTS project.

SubMaker is a package that makes the process of creating subtitles with
information provided by the service easier.
"""

import math
from typing import List, Tuple
from xml.sax.saxutils import escape, unescape


def formatter(start_time: float, end_time: float, subdata: str) -> str:
    """
    formatter returns the timecode and the text of the subtitle.
    """
    return (
        f"{mktimestamp(start_time)} --> {mktimestamp(end_time)}\r\n"
        f"{escape(subdata)}\r\n\r\n"
    )


def mktimestamp(time_unit: float) -> str:
    """
    mktimestamp returns the timecode of the subtitle.

    The timecode is in the format of 00:00:00.000.

    Returns:
        str: The timecode of the subtitle.
    """
    hour = math.floor(time_unit / 10**7 / 3600)
    minute = math.floor((time_unit / 10**7 / 60) % 60)
    seconds = (time_unit / 10**7) % 60
    return f"{hour:02d}:{minute:02d}:{seconds:06.3f}"


class SubMaker:
    """
    SubMaker class
    """

    def __init__(self) -> None:
        """
        SubMaker constructor.
        """
        self.offset: List[Tuple[float, float]] = []
        self.subs: List[str] = []

    def create_sub(self, timestamp: Tuple[float, float], text: str) -> None:
        """
        create_sub creates a subtitle with the given timestamp and text
        and adds it to the list of subtitles

        Args:
            timestamp (tuple): The offset and duration of the subtitle.
            text (str): The text of the subtitle.

        Returns:
            None
        """
        self.offset.append((timestamp[0], timestamp[0] + timestamp[1]))
        self.subs.append(text)

    def generate_subs(self, words_in_cue: int = 10) -> str:
        """
        generate_subs generates the complete subtitle file.

        Args:
            words_in_cue (int): defines the number of words in a given cue

        Returns:
            str: The complete subtitle file.
        """
        if len(self.subs) != len(self.offset):
            raise ValueError("subs and offset are not of the same length")

        if words_in_cue <= 0:
            raise ValueError("words_in_cue must be greater than 0")

        data = "WEBVTT\r\n\r\n"
        sub_state_count = 0
        sub_state_start = -1.0
        sub_state_subs = ""
        for idx, (offset, subs) in enumerate(zip(self.offset, self.subs)):
            start_time, end_time = offset
            subs = unescape(subs)

            # wordboundary is guaranteed not to contain whitespace
            if len(sub_state_subs) > 0:
                sub_state_subs += " "
            sub_state_subs += subs

            if sub_state_start == -1.0:
                sub_state_start = start_time
            sub_state_count += 1

            if sub_state_count == words_in_cue or idx == len(self.offset) - 1:
                subs = sub_state_subs
                split_subs: List[str] = [
                    subs[i : i + 79] for i in range(0, len(subs), 79)
                ]
                for i in range(len(split_subs) - 1):
                    sub = split_subs[i]
                    split_at_word = True
                    if sub[-1] == " ":
                        split_subs[i] = sub[:-1]
                        split_at_word = False

                    if sub[0] == " ":
                        split_subs[i] = sub[1:]
                        split_at_word = False

                    if split_at_word:
                        split_subs[i] += "-"

                data += formatter(
                    start_time=sub_state_start,
                    end_time=end_time,
                    subdata="\r\n".join(split_subs),
                )
                sub_state_count = 0
                sub_state_start = -1
                sub_state_subs = ""
        return data


    def generate_subs_based_on_punc(self, text,) -> str:
        """
        generate_subs generates the complete subtitle file according to the punctuation.

        Returns:
            str: The complete subtitle file.
        """



        PUNCTUATION = ['，', '。', '！', '？', '；', '：', '\n', '“', '”', ',', '!', '.', ';', '?', ',', '؟', '،', '؛', '.',
                       '!', ':']
        punctuation_set = set(re.escape(punc) for punc in PUNCTUATION)
        BREAK = ['\n', '。', '！', '？', '.', '?', '!', '؟']
        break_set = set(re.escape(punc) for punc in BREAK)

        def remove_punctuations_and_lower(text):
            for punc in punctuation_set:
                text = re.sub(punc, '', text)
            return text.lower()

        def clause(self) -> list[str]:

            words = text.split()
            result = []
            current_sentence = ""

            for word in words:
                # Check if the word is a punctuation
                if re.search(f"[{''.join(break_set)}]$", word):
                    current_sentence += word + " "
                    result.append(current_sentence.rstrip())
                    current_sentence = ""
                elif re.search(f"[{''.join(punctuation_set)}]$", word):
                    if len(current_sentence) > 20 and len(current_sentence) + len(word) + 1 <= 60:  # 最小句子长度20，有标点时立即停止
                        current_sentence += word + " "
                        result.append(current_sentence.rstrip())
                        current_sentence = ""
                    else:
                        current_sentence += word + " "
                else:
                    # Add word to current sentence if it keeps the length within the limit
                    if len(current_sentence) + len(word) + 1 <= 50:  # 无标点的句子的最大长度50
                        current_sentence += word + " "
                    else:
                        # If adding the word exceeds the limit, append the current sentence and start a new one
                        result.append(current_sentence.rstrip())
                        current_sentence = word + " "

            # Append the last sentence if it's not empty and within the length limit
            if current_sentence:
                result.append(current_sentence.rstrip())

            return result

        self.text_list = clause(self)
        if len(self.subs) != len(self.offset):
            raise ValueError("subs and offset are not of the same length")
        print(self.subs)
        print(self.offset)
        data = "WEBVTT\r\n\r\n"
        j = 0
        for text in self.text_list:
            print("text", text)
            t = remove_punctuations_and_lower(text)
            try:
                start_time = self.offset[j][0]
            except IndexError:
                return data

            t = t.replace(remove_punctuations_and_lower(self.subs[j]), '', 1)

            try:
                while (remove_punctuations_and_lower(self.subs[j + 1]) in t):
                    t = t.replace(remove_punctuations_and_lower(self.subs[j + 1]), '', 1)
                    j += 1
            except IndexError:
                pass
            data += formatter(start_time, self.offset[j][1], text)
            j += 1
        return data

