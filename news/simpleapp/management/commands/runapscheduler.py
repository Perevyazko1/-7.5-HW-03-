# import datetime
# import logging
#
# from django.conf import settings
#
# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger
# from django.core.mail import EmailMultiAlternatives
# from django.core.management.base import BaseCommand
# from django.template.loader import render_to_string
# from django_apscheduler.jobstores import DjangoJobStore
# from django_apscheduler.models import DjangoJobExecution
#
# from ...models import NewsCategory, News
# from django.utils import timezone
# import pytz
#
# logger = logging.getLogger(__name__)
#
#
# # наша задача по выводу текста на экран
# def my_job():
#     #  Your job processing logic here...
#     print('hello from job')
#     today = timezone.now()
#     last_week = today - datetime.timedelta(days=7)
#     all_news = News.objects.filter(dateCreation__gte=last_week)
#     categories = set(all_news.values_list('category__name', flat=True))
#     subscribes = set(NewsCategory.objects.filter(name__in=categories).values_list('subscribes__email', flat=True))
#     subscribes = list(filter(None,subscribes))
#     print(subscribes)
#     html_content = render_to_string(
#         'news_week.html',
#         {
#             'link': settings.SITE_URL,
#             'all_news': all_news,
#         }
#     )
#     msg = EmailMultiAlternatives(
#         subject='Статьи за неделю',
#         body='',  # это то же, что и message
#         from_email= settings.DEFAULT_FROM_EMAIL,
#         to=subscribes,  # это то же, что и recipients_list
#
#     )
#     msg.attach_alternative(html_content, 'text/html')  # добавляем html
#     msg.send()  # отсылаем
#
#
# # функция, которая будет удалять неактуальные задачи
# def delete_old_job_executions(max_age=604_800):
#     """This job deletes all apscheduler job executions older than `max_age` from the database."""
#     DjangoJobExecution.objects.delete_old_job_executions(max_age)
#
#
# class Command(BaseCommand):
#     help = "Runs apscheduler."
#
#     def handle(self, *args, **options):
#         scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
#         scheduler.add_jobstore(DjangoJobStore(), "default")
#
#         # добавляем работу нашему задачнику
#         scheduler.add_job(
#             my_job,
#             trigger=CronTrigger(day_of_week="mon", hour="10", minute="00"),
#             # То же, что и интервал, но задача тригера таким образом более понятна django
#             id="my_job",  # уникальный айди
#             max_instances=1,
#             replace_existing=True,
#         )
#         logger.info("Added job 'my_job'.")
#
#         scheduler.add_job(
#             delete_old_job_executions,
#             trigger=CronTrigger(
#                 day_of_week="mon", hour="00", minute="00"
#             ),
#             # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
#             id="delete_old_job_executions",
#             max_instances=1,
#             replace_existing=True,
#         )
#         logger.info(
#             "Added weekly job: 'delete_old_job_executions'."
#         )
#
#         try:
#             logger.info("Starting scheduler...")
#             scheduler.start()
#         except KeyboardInterrupt:
#             logger.info("Stopping scheduler...")
#             scheduler.shutdown()
#             logger.info("Scheduler shut down successfully!")