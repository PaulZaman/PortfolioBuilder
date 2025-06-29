import openai
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import HTTPException
import re

load_dotenv()
api  = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api)


def getTickerSuggestions(stk_firebase, responses):
    stocks_json = json.dumps(stk_firebase, indent=2)
    responses_str = json.dumps(responses, indent=2)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert in portfolio creation. "
                    "You must ONLY output a minified and valid JSON object. "
                    "Do NOT include any markdown, explanations, or text outside of the JSON."
                )
            },
            {
                "role": "user",
                "content": f"""
						Given this list of available stocks:
						{stocks_json}

						And this user's portfolio preferences:
						{responses_str}

						Return the most suitable tickers for this user using ONLY this strict JSON format:

						{{
						"tickers": ["TICK1", "TICK2", "TICK3"],
						"explanation": "A few sentences justifying all the selected tickers, based on the user's preferences. Be clear and concise."
						}}

						→ Return ONLY a valid JSON object. No markdown, no code block, no extra explanation.
						→ Return between 3 and 10 tickers.
						"""
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"The response from OpenAI was not valid JSON: {e}, content: {content}"
        )



def getRecommendedMetrics(responses):
    responses_str = json.dumps(responses, indent=2)

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert in portfolio management, financial analysis, and risk metrics. "
                "Based on the user's preferences, you must propose one optimal metric to optimize "
                "(e.g., sharpe ratio, total return, etc.). "
                "Return ONLY a valid minified JSON object — no markdown, no extra explanation."
            )
        },
        {
            "role": "user",
            "content": f"""
Here are the user's investment preferences:
{responses_str}

Select one metric the user should optimize for, from the following list:
["sharpe", "sortino", "total_return", "weekly_return", "daily_return", "periodic_avg_return"]

Return ONLY the following strict JSON format:

{{
  "recommended_metric": "<metric_name>",
  "explanation": "1-2 clear sentences justifying the choice based on the user's preferences."
}}

→ Do not include markdown or any content outside this object.
→ Only valid JSON should be returned.
"""
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    content = response.choices[0].message.content.strip()

    # Strip markdown/code formatting if present
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n", "", content)
        content = re.sub(r"\n```$", "", content)

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"The response from OpenAI was not valid JSON: {e}, content: {content}"
        )
