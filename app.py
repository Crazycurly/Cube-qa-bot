import logging
import os
import time
import json
import requests
import asyncio
from openai import OpenAI
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATA_FILE_PATH = "cube_cards_data.json"
client = OpenAI(api_key=OPENAI_API_KEY)

def scrape_cathay_cube_cards(url):
    # Fetch the content from the URL
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <img> tags with the specific class
    img_tags = soup.find_all('img', class_='cubre-a-image')

    # Initialize a result string
    result = ""

    def extract_categories(soup):
        nonlocal result
        # Find all cube card components
        cube_cards = soup.find_all('div', class_='cubre-m-cubeCard')

        for card in cube_cards:
            # Get the category title
            category = card.find('div', class_='cubre-a-iconTitle__text')
            if category:
                category_text = category.get_text(strip=True)
                result += f"{category_text} :\n"

            # Get all items under the category
            items = card.find_all('span', attrs={'data-ga-lv3-title': True})
            for item in items:
                item_text = item.get_text(strip=True)
                result += f"{item_text}\n"

            result += "\n"  # Add a newline for better readability

    # Iterate over each <img> tag to find and print their parent <p> tag text and the <div> with class cubre-o-block__wrap
    for img_tag in img_tags:
        parent_p_tag = img_tag.find_parent('p', class_='cubre-a-blockTitle')
        if parent_p_tag:
            text = parent_p_tag.get_text(strip=True)
            result += f"權益: {text}\n"

            # Find the parent <div> with class cubre-o-block__wrap
            parent_div_tag = img_tag.find_parent('div', class_='cubre-o-block__wrap')
            if parent_div_tag:
                extract_categories(parent_div_tag)

    return result

def update_data_file():
    url = 'https://www.cathaybk.com.tw/cathaybk/personal/product/credit-card/cards/cube-list'
    data = scrape_cathay_cube_cards(url)
    with open(DATA_FILE_PATH, 'w') as file:
        json.dump(data, file)

async def get_data_from_file():
    with open(DATA_FILE_PATH, 'r') as file:
        data = json.load(file)
    return data

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await get_data_from_file()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "以下是Cube信用卡的回饋明細，請根據輸入回答是否包含在清單內，並提供所屬權益，如有標註回答比例的話請列出，沒有不用提出未標註，回答精簡。" + data},
            {"role": "user", "content": update.message.text}
        ]
    )
    res = completion.choices[0].message.content
    await context.bot.send_message(chat_id=update.effective_chat.id, text=res)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

if __name__ == '__main__':
    # Initialize the scheduler
    scheduler = AsyncIOScheduler()

    # update the data
    update_data_file()
    # Add a job to update the data file every day
    scheduler.add_job(update_data_file, 'interval', days=1)

    # Start the scheduler
    scheduler.start()

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)
    application.add_handler(start_handler)

    application.run_polling()