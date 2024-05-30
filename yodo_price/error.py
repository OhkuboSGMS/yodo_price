import functools
import os

from yodo_price.notify import discord_webhook


def notify_discord_on_exception(user_name: str, env_var_key: str):
    """
    デコレータ関数。指定された環境変数から取得したDiscord Webhook URLに
    例外発生時に通知を送信する。
    :param user_name: 通知時のユーザ名
    :param env_var_key:
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            webhook_url = os.getenv(env_var_key)
            if not webhook_url:
                raise ValueError(
                    f"Environment variable '{env_var_key}' not set or empty"
                )

            try:
                return func(*args, **kwargs)
            except Exception as e:
                message = f"Exception occurred in {func.__name__}: {e}"
                payload = {"username": user_name, "content": message}
                try:
                    discord_webhook(payload, webhook_url)
                except Exception as req_e:
                    print(f"Failed to send notification to Discord: {req_e}")
                raise  # Re-raise the original exception after notification

        return wrapper

    return decorator
