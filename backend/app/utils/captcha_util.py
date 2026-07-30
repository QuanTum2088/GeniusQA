# -*- coding: utf-8 -*-
"""图片验证码工具"""
from __future__ import annotations

import base64
import random
import string
from io import BytesIO
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


class CaptchaUtil:
    """生成带干扰的 4 位字符验证码图片。"""

    @classmethod
    def _load_font(cls, size: int = 28) -> ImageFont.ImageFont:
        for path in (
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    @classmethod
    def generate_captcha(cls, length: int = 4) -> Tuple[str, str]:
        """
        Returns:
            (base64_png, captcha_plaintext)
        """
        length = max(3, min(int(length or 4), 8))
        chars = string.digits + string.ascii_letters
        captcha_value = "".join(random.sample(chars, length))

        width, height = 120, 40
        background_color = tuple(random.randint(220, 255) for _ in range(3))
        image = Image.new("RGB", (width, height), color=background_color)
        draw = ImageDraw.Draw(image)
        font = cls._load_font(size=28)

        try:
            total_width = sum(draw.textbbox((0, 0), ch, font=font)[2] for ch in captcha_value)
            text_height = draw.textbbox((0, 0), captcha_value[0], font=font)[3]
            y_bias = draw.textbbox((0, 0), captcha_value[0], font=font)[1]
        except Exception:
            total_width = length * 16
            text_height = 20
            y_bias = 0

        x = max((width - total_width) / 2, 4)
        y = max((height - text_height) / 2 - y_bias, 2)

        for ch in captcha_value:
            color = tuple(random.randint(0, 90) for _ in range(3))
            draw.text(
                (x + random.uniform(-1.5, 1.5), y + random.uniform(-1.5, 1.5)),
                ch,
                font=font,
                fill=color,
            )
            try:
                x += draw.textbbox((0, 0), ch, font=font)[2] + random.uniform(1, 4)
            except Exception:
                x += 16

        for _ in range(3):
            line_color = tuple(random.randint(140, 200) for _ in range(3))
            draw.line(
                [
                    (random.randint(0, width), random.randint(0, height)),
                    (random.randint(0, width), random.randint(0, height)),
                ],
                fill=line_color,
                width=1,
            )

        for _ in range(width * height // 40):
            draw.point(
                (random.randint(0, width - 1), random.randint(0, height - 1)),
                fill=tuple(random.randint(0, 255) for _ in range(3)),
            )

        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        return base64.b64encode(buffer.getvalue()).decode(), captcha_value
