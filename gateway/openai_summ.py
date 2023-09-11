import openai 


def generate_log_summary(api_key, log_data):
    openai.api_key = api_key

    prompt_prefix = """Can you summarize this log data in English? It is only a partial list of the log entries, 
    so keep that in mind when making statements about the entire dataset. Is this usual or unusual? Any patterns or anomalies?"""

    prompt = prompt_prefix + log_data

    res = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{'role' : 'user', 'content' : prompt}],
                )

    res_text = res['choices'][0]['message']['content']
    return res_text
