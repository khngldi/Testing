import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import openai
from products.models import Product

logger = logging.getLogger(__name__)

openai.api_key = settings.DEEPSEEK_API_KEY
openai.base_url = "https://api.deepseek.com/v1"  # замени, если другой URL

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_message = data.get('message', '').lower().strip()
            logger.info(f"Received message: {user_message}")

            if any(keyword in user_message for keyword in ["что есть", "товары", "ассортимент", "что продаете", "продукты"]):
                products = Product.objects.all()[:10]
                if products:
                    product_names = ", ".join([p.name for p in products])
                    bot_response = f"Вот некоторые товары из нашего ассортимента: {product_names}. Хотите подробнее?"
                else:
                    bot_response = "Пока товаров нет в базе. Попробуйте позже."
                return JsonResponse({'response': bot_response})

            product = None
            for p in Product.objects.all():
                if p.name.lower() in user_message:
                    product = p
                    break

            if product:
                bot_response = f"Вот информация о товаре: {product.name}:\n" \
                               f"- Описание: {product.description}\n" \
                               f"- Цена: {product.price}$\n" \
                               f"- Дата добавления: {product.created_at.strftime('%d-%m-%Y')}"
            else:
                client = openai.OpenAI(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url="https://api.deepseek.com/v1"
                )

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system",
                         "content": "Ты — вежливый и полезный ассистент Freshmart. Помогаешь покупателям с товарами, акциями и заказами."},
                        {"role": "user", "content": user_message}
                    ]
                )

                bot_response = response.choices[0].message.content

            logger.info(f"Bot response: {bot_response}")
            return JsonResponse({'response': bot_response})

        except Exception as e:
            logger.error(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
