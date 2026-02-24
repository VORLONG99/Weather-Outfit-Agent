from __future__ import annotations

from dataclasses import dataclass
import logging
from datetime import date

from openai import OpenAI

from .weather_client import DailyWeather

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OutfitRecommendation:
    subject: str
    body: str


def _encouragement_line(day: str) -> str:
    phrases = [
        "今天也在好好照顾自己，已经很棒了。",
        "穿得舒适一点，状态会更在线。",
        "一步一步来，今天也会是有收获的一天。",
        "保持自己的节奏，你比想象中更稳定。",
        "愿你今天轻松出门、顺利收工。",
    ]
    try:
        idx = date.fromisoformat(day).toordinal() % len(phrases)
    except ValueError:
        idx = 0
    return phrases[idx]


def _outerwear(avg_apparent_temp: float) -> str:
    if avg_apparent_temp <= -5:
        return "羽绒服 + 保暖内搭"
    if avg_apparent_temp <= 5:
        return "厚外套/羊毛大衣 + 针织层"
    if avg_apparent_temp <= 12:
        return "风衣/夹克 + 长袖"
    if avg_apparent_temp <= 20:
        return "薄外套或衬衫叠穿"
    if avg_apparent_temp <= 28:
        return "短袖/薄衬衫"
    return "速干短袖 + 防晒外搭"


def _rule_based(weather: DailyWeather) -> OutfitRecommendation:
    avg_apparent_temp = (weather.apparent_temp_max + weather.apparent_temp_min) / 2
    outerwear = _outerwear(avg_apparent_temp)
    rain_note = (
        "降雨概率较高，建议防水鞋或带伞。"
        if weather.precipitation_probability_max >= 40
        else "降雨概率较低，可轻装出行。"
    )
    wind_note = (
        "风力较大，建议加一层防风外套。"
        if weather.wind_speed_max >= 30
        else "风力适中。"
    )
    encouragement = _encouragement_line(weather.date)

    subject = f"{weather.city} {weather.date} 每日穿搭建议"
    body = (
        f"今日天气（{weather.city}）\n"
        f"- 温度: {weather.temp_min:.1f}°C ~ {weather.temp_max:.1f}°C\n"
        f"- 体感: {weather.apparent_temp_min:.1f}°C ~ {weather.apparent_temp_max:.1f}°C\n"
        f"- 降雨概率: {weather.precipitation_probability_max}%\n"
        f"- 最大风速: {weather.wind_speed_max:.1f} km/h\n\n"
        "主推荐\n"
        f"- {outerwear}\n"
        "- 下装建议：长裤（气温高于 24°C 可选薄款或短裤）\n"
        "- 鞋履建议：舒适防滑鞋\n\n"
        "下雨备选\n"
        "- 轻防水外套 + 防水鞋 + 折叠伞\n\n"
        "理由\n"
        f"- {rain_note}\n"
        f"- {wind_note}\n"
        "\n鼓励\n"
        f"- {encouragement}\n"
    )
    return OutfitRecommendation(subject=subject, body=body)


def _llm_enhanced(
    weather: DailyWeather, llm_api_key: str, model: str, base_url: str | None
) -> OutfitRecommendation:
    if base_url and base_url.rstrip("/").count("/") == 2:
        # Most OpenAI-compatible providers expose endpoints under /v1.
        base_url = f"{base_url.rstrip('/')}/v1"
    client = OpenAI(api_key=llm_api_key, base_url=base_url)
    prompt = f"""
你是穿搭助手。请基于下述天气，输出简洁中文邮件内容。

城市: {weather.city}
日期: {weather.date}
气温: {weather.temp_min:.1f}~{weather.temp_max:.1f}°C
体感: {weather.apparent_temp_min:.1f}~{weather.apparent_temp_max:.1f}°C
降雨概率: {weather.precipitation_probability_max}%
最大风速: {weather.wind_speed_max:.1f} km/h

要求：
1) 包含「主推荐」「下雨备选」「理由」「鼓励」四个部分
2) 不要超过220字
3) 语气务实、可执行，不要花哨
"""
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是专业每日穿搭顾问。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    body = completion.choices[0].message.content.strip()
    if "鼓励" not in body:
        body = f"{body}\n\n鼓励\n- {_encouragement_line(weather.date)}"
    subject = f"{weather.city} {weather.date} 每日穿搭建议"
    return OutfitRecommendation(subject=subject, body=body)


def build_recommendation(
    weather: DailyWeather,
    llm_api_key: str | None = None,
    model: str = "gpt-4o-mini",
    base_url: str | None = None,
    strict_mode: bool = False,
) -> OutfitRecommendation:
    if llm_api_key:
        try:
            return _llm_enhanced(weather, llm_api_key, model, base_url)
        except Exception:
            logger.exception(
                "LLM generation failed (model=%s, base_url=%s).", model, base_url
            )
            if strict_mode:
                raise
            return _rule_based(weather)
    return _rule_based(weather)
