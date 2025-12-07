from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio

# 본인의 API ID와 HASH 입력
api_id = '27060733'
api_hash = '820d4d04351967e58147a86fb5349d57'

# 임의 세션 이름
client = TelegramClient('stock_agent_session', api_id, api_hash)

async def crawl_messages(channel_username, limit=100):
    await client.start()
    # 채널 객체 가져오기
    channel = await client.get_entity(channel_username)

    # 메시지 가져오기
    history = await client(GetHistoryRequest(
        peer=channel,
        limit=limit,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))

    for message in history.messages:
        print(f"{message.id}: {message.message}")

    await client.disconnect()

# 실행
# channel_url = 'https://t.me/FastStockNews'  # 또는 '@채널아이디'
channel_url = 'https://t.me/realtime_stock_news'
asyncio.run(crawl_messages(channel_url, limit=50))
