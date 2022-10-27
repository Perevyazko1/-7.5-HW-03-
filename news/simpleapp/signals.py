from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from django.conf import settings
from .models import PostCategory,User


def send_notifications(preview,id, title, subscribes ):
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
                    'text': preview,
                    'link': f'{settings.SITE_URL}/news/{id}',
                    'title': title,
                    'user': user,
                }
            )
            msg = EmailMultiAlternatives(
                subject= title,
                body='',  # это то же, что и message
                from_email= 'news.portal@inbox.ru',
                to= to_email,  # это то же, что и recipients_list

            )
            msg.attach_alternative(html_content, 'text/html')  # добавляем html
            msg.send()  # отсылаем

@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.category.all()
        subscribes: list[str] = []
        # users: list[str] = []
        for category in categories:
            subscribes += category.subscribes.all()
        # users = [s.username for s in subscribes]
        # subscribes = [s.email for s in subscribes]
        # print(users)
        # print(subscribes)
        send_notifications(instance.preview, instance.id, instance.title, subscribes)



def send_new_user(user, email ):
        html_content = render_to_string(
            'new_user.html',
            {
                'link': f'{settings.SITE_URL}/accounts/login/',
                'user': user,
            }
        )
        message = EmailMultiAlternatives(
            subject= 'Регистрация',
            body='',  # это то же, что и message
            from_email= 'news.portal@inbox.ru',
            to= email,  # это то же, что и recipients_list

        )
        message.attach_alternative(html_content, 'text/html')  # добавляем html
        message.send()  # отсылаем



@receiver(post_save, sender=User)
def hello_new_user(sender, instance,created, **kwargs):
    if created:
        email = [instance.email]
        user = instance
        # user: list[str] = []
        # email: list[str] = []
        # for new_user in user:
        #     user += new_user.user.all()
        # user = [s.first_name for s in user]
        # email = [s.email for s in user]
        # send_new_user(instance.id, user)
        # print(user)
        # print(email)
        send_new_user(user,email)