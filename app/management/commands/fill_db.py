from django.conf import settings
from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import *


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

    client = Minio(settings.MINIO_ENDPOINT,
                   settings.MINIO_ACCESS_KEY,
                   settings.MINIO_SECRET_KEY,
                   secure=settings.MINIO_USE_HTTPS)

    for i in range(1, 7):
        client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, f'{i}.png', f"app/static/images/{i}.png")

    client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, 'default.png', "app/static/images/default.png")


def add_reports():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    resources = Resource.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_report(status, resources, owner, moderators)

    add_report(1, resources, users[0], moderators)
    add_report(2, resources, users[0], moderators)
    add_report(3, resources, users[0], moderators)
    add_report(4, resources, users[0], moderators)
    add_report(5, resources, users[0], moderators)

    print("Заявки добавлены")


def add_report(status, resources, owner, moderators):
    report = Report.objects.create()
    report.status = status

    if status in [3, 4]:
        report.moderator = random.choice(moderators)
        report.date_complete = random_date()
        report.date_formation = report.date_complete - random_timedelta()
        report.date_created = report.date_formation - random_timedelta()
    else:
        report.date_formation = random_date()
        report.date_created = report.date_formation - random_timedelta()

    report.company = "Алюминийпром"
    report.month = "Октябрь"

    report.owner = owner

    for resource in random.sample(list(resources), 3):
        item = ResourceReport(
            report=report,
            resource=resource,
            plan_volume=random.randint(1, 10),
            volume=random.randint(1, 10) if report.status == 3 else None
        )
        item.save()

    report.save()


def calc():
    return random_date()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_resources()
        add_reports()
