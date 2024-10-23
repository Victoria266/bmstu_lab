import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

    print("Пользователи созданы")


def add_resources():
    Resource.objects.create(
        name="Железо",
        description="Железо - это ковкий переходный металл серебристо-белого цвета с высокой химической реакционной способностью: железо быстро корродирует на воздухе при высоких температурах или при высокой влажности. В чистом кислороде железо горит, а в мелкодисперсном состоянии самовозгорается на воздухе.",
        density=7.874,
        image="1.png"
    )

    Resource.objects.create(
        name="Кремний",
        description="Кремний — второй по распространенности элемент на Земле после кислорода. В свободном виде кремний не встречается, существует только в виде соединений. Кремний химически малоактивен. В реакциях он может проявлять как окислительные, так и восстановительные свойства, восстановительные свойства выражены у него сильнее.",
        density=2.33,
        image="2.png"
    )

    Resource.objects.create(
        name="Алюминий",
        description="Алюминий —легкий и пластичный белый металл, матово-серебристый благодаря тонкой оксидной пленке, которая сразу же покрывает его на воздухе. Он относится к III группе периодической системы, обозначается символом Al, имеет атомный номер 13.",
        density=2.7,
        image="3.png"
    )

    Resource.objects.create(
        name="Вода",
        description="Вода — это жидкость без вкуса, запаха, цвета, которая входит в состав всех живых существ. Вода — это часть неживой природы. Вода содержится в реках, озёрах, болотах, морях и океанах, а также глубоко под землёй. Содержится вода и в атмосфере.",
        density=1,
        image="4.png"
    )

    Resource.objects.create(
        name="Углекислый газ",
        description="Углекислый газ или диоксид углерода — малотоксичный газ, в нормальных условиях без запаха и цвета. CO₂ — небольшая, но важная составляющая воздуха, он является одним из элементов окружающей среды, участвует в процессе фотосинтеза, метаболизма, выделяется людьми и животными, а также в ходе брожения и гниения.",
        density=0.001976,
        image="5.png"
    )

    Resource.objects.create(
        name="Гелий",
        description="Гелий – инертный газ, являющийся вторым элементом периодической системы элементов, а так же вторым элементом по легкости и распространенности во Вселенной. Он относится к простым веществам и при стандартных условиях представляет собой одноатомный газ.",
        density=0.00017846,
        image="6.png"
    )

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_reports():
    users = User.objects.filter(is_superuser=False)
    moderators = User.objects.filter(is_superuser=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    resources = Resource.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        add_report(status, resources, users, moderators)

    add_report(1, resources, users, moderators)

    print("Заявки добавлены")


def add_report(status, resources, users, moderators):
    report = Report.objects.create()
    report.status = status

    if report.status in [3, 4]:
        report.date_complete = random_date()
        report.date_formation = report.date_complete - random_timedelta()
        report.date_created = report.date_formation - random_timedelta()
    else:
        report.date_formation = random_date()
        report.date_created = report.date_formation - random_timedelta()

    report.owner = random.choice(users)
    report.moderator = random.choice(moderators)

    report.company = "Алюминийпром"
    report.month = "Октябрь"

    for resource in random.sample(list(resources), 3):
        item = ResourceReport(
            report=report,
            resource=resource,
            value=random.randint(50, 200)
        )
        item.save()

    report.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_resources()
        add_reports()



















