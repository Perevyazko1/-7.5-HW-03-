from celery import shared_task
import time
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import PostCategory, NewsCategory, News
from django.conf import settings
from django.utils import timezone
import datetime

# celery -A news worker -l INFO
@shared_task(serializer='json')
def send_notifications(id, title, text ):
    send_list = list(
        PostCategory.objects.filter(
            postThrough_id=id
        ).values_list(
            'categoryThrough__subscribes__username',
            'categoryThrough__subscribes__first_name',
            'categoryThrough__subscribes__email',
            'categoryThrough__name',
        )
    )

    for user, first_name, email, category in send_list:
            # получаем наш html
            to_email = [email]
            html_content = render_to_string(
                'post_created.html',
                {
                    'text': text,
                    'link': f'{settings.SITE_URL}/news/{id}',
                    'title': title,
                    'user': user,
                }
            )
            msg = EmailMultiAlternatives(
                subject= title,
                body='',  # это то же, что и message
                from_email=settings.DEFAULT_FROM_EMAIL,
                to= to_email,  # это то же, что и recipients_list

            )
            print('Send mail')
            msg.attach_alternative(html_content, 'text/html')  # добавляем html
            msg.send()  # отсылаем

@shared_task(serializer='json')
def send_subscribe():
    today = timezone.now()
    last_week = today - datetime.timedelta(days=7)
    all_news = News.objects.filter(dateCreation__gte=last_week)
    categories = set(all_news.values_list('category__name', flat=True))
    subscribes = set(NewsCategory.objects.filter(name__in=categories).values_list('subscribes__email', flat=True))
    subscribes = list(filter(None,subscribes))
    user = set(NewsCategory.objects.filter(name__in=categories).values_list('subscribes__username', flat=True))
    html_content = render_to_string(
        'news_week.html',
        {
            'link': settings.SITE_URL,
            'all_news': all_news,
            'user': user,
        }
    )
    msg = EmailMultiAlternatives(
        subject='Статьи за неделю',
        body='',  # это то же, что и message
        from_email= settings.DEFAULT_FROM_EMAIL,
        to=subscribes,  # это то же, что и recipients_list

    )
    msg.attach_alternative(html_content, 'text/html')  # добавляем html
    msg.send()  # отсылаем
