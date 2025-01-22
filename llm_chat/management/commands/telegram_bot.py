import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from django.core.management.base import BaseCommand
from llm_chat.services.llm_chat_actor import LLMService
from llm_chat.serializers import LLMResponseSerializer
from decouple import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Run the Telegram bot for the clothing assistant."

    def handle(self, *args, **options):
        """
        Start the Telegram bot.
        """
        TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')

        system_message = """
        You are a helpful and friendly clothing seller assistant. Your job is to help clients find the clothes they are looking for. 
        You should talk to clients like a human and assist them in finding the best clothes based on their preferences. 
        If the client wants to search for specific clothes, you can use the provided functions in tools to search for clothes (Use this tools always and make a function call). 
        Respect to the rules i say and in tools function Respect to structre of arg for function calling. Choose a correct path to answer to client.
        For filter colors and gender and other things you must use function structre in tools remember for example for search in color like red you must write red keyword inquery parameter.
        """
        llm_service = LLMService(
            api_url="https://api.deepinfra.com/v1/openai/chat/completions",
            api_key=config('DEEPINFRA_API_KEY'),
            system_message=system_message
        )

        tools = [{
            "type": "function",
            "function": {
                "name": "search_clothes",
                "description": "Search for clothes based on a query and optional filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "filters": {
                            "type": "object",
                            "properties": {
                                "attributesToSearchOn": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "id", "name", "description", "material", "rating", "code", 
                                            "brand_id", "brand_name", "category_id", "category_name", 
                                            "gender_id", "gender_name", "shop_id", "shop_name", "link", 
                                            "status", "colors", "sizes", "region", "currency", 
                                            "current_price", "old_price", "off_percent", "update_date"
                                        ]
                                    }
                                }
                            },
                            "additionalProperties": False
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }]

        async def start(update: Update, context: CallbackContext):
            """
            Send a welcome message when the user starts the bot.
            """
            welcome_message = (
                "👋 Welcome to the Clothing Assistant Bot!\n\n"
                "I can help you find the perfect clothes. Just describe what you're looking for, "
                "and I'll show you some options.\n\n"
                "For example, you can say: 'I need a red dress for a party.'"
            )
            await update.message.reply_text(welcome_message)

        async def handle_message(update: Update, context: CallbackContext):
            """
            Handle incoming messages from the user.
            """
            user_message = update.message.text

            messages = [{"role": "user", "content": user_message}]

            response = llm_service.process_chat_completion(messages, tools)
            print(response)

            serializer = LLMResponseSerializer(response)
            data = serializer.data

            assistant_response = data.get("assistant_response", {}).get("content", "")
            await update.message.reply_text(assistant_response)

            search_results = data.get("search_results", [])
            if search_results:
                for product in search_results[:5]:
                    caption = (
                        f"👗 *{product['name']}*\n"
                        f"💵 Price: {product['current_price']} {product['currency']}\n"
                        f"🔗 [View Product]({product['link']})"
                    )
                    if product.get("images"):
                        await update.message.reply_photo(
                            photo=product["images"][0],
                            caption=caption,
                            parse_mode="Markdown",
                        )
                    else:
                        await update.message.reply_text(caption, parse_mode="Markdown")

        application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        self.stdout.write(self.style.SUCCESS("Starting the Telegram bot..."))
        application.run_polling()