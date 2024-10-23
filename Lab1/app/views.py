from django.shortcuts import render

resources = [
    {
        "id": 1,
        "name": "Железо",
        "description": "Железо - это ковкий переходный металл серебристо-белого цвета с высокой химической реакционной способностью: железо быстро корродирует на воздухе при высоких температурах или при высокой влажности. В чистом кислороде железо горит, а в мелкодисперсном состоянии самовозгорается на воздухе.",
        "density": 7.874,
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "Кремний",
        "description": "Кремний — второй по распространенности элемент на Земле после кислорода. В свободном виде кремний не встречается, существует только в виде соединений. Кремний химически малоактивен. В реакциях он может проявлять как окислительные, так и восстановительные свойства, восстановительные свойства выражены у него сильнее.",
        "density":  2.33,
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "Алюминий",
        "description": "Алюминий —легкий и пластичный белый металл, матово-серебристый благодаря тонкой оксидной пленке, которая сразу же покрывает его на воздухе. Он относится к III группе периодической системы, обозначается символом Al, имеет атомный номер 13.",
        "density": 2.7,
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "Вода",
        "description": "Вода — это жидкость без вкуса, запаха, цвета, которая входит в состав всех живых существ. Вода — это часть неживой природы. Вода содержится в реках, озёрах, болотах, морях и океанах, а также глубоко под землёй. Содержится вода и в атмосфере.",
        "density": 1,
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "Углекислый газ",
        "description": "Углекислый газ или диоксид углерода — малотоксичный газ, в нормальных условиях без запаха и цвета. CO₂ — небольшая, но важная составляющая воздуха, он является одним из элементов окружающей среды, участвует в процессе фотосинтеза, метаболизма, выделяется людьми и животными, а также в ходе брожения и гниения.",
        "density": 0.001976,
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "Гелий",
        "description": "Гелий – инертный газ, являющийся вторым элементом периодической системы элементов, а так же вторым элементом по легкости и распространенности во Вселенной. Он относится к простым веществам и при стандартных условиях представляет собой одноатомный газ.",
        "density": 0.00017846,
        "image": "http://localhost:9000/images/6.png"
    }
]

draft_report = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "company": "Алюминийпром",
    "month": "Октябрь",
    "resources": [
        {
            "id": 1,
            "value": 120
        },
        {
            "id": 2,
            "value": 75
        },
        {
            "id": 3,
            "value": 50
        }
    ]
}


def getResourceById(resource_id):
    for resource in resources:
        if resource["id"] == resource_id:
            return resource


def getResources():
    return resources


def filterResources(resource_density):
    res = []

    for resource in resources:
        if resource_density < resource["density"]:
            res.append(resource)

    return res


def getDraftReport():
    return draft_report


def getReportById(report_id):
    return draft_report


def index(request):
    resource_density = request.GET.get("resource_density", "")
    resources = filterResources(float(resource_density)) if resource_density else getResources()
    draft_report = getDraftReport()

    context = {
        "resources": resources,
        "resource_density": resource_density,
        "resources_count": len(draft_report["resources"]),
        "draft_report": draft_report
    }

    return render(request, "resources_page.html", context)


def resource(request, resource_id):
    context = {
        "id": resource_id,
        "resource": getResourceById(resource_id),
    }

    return render(request, "resource_page.html", context)


def report(request, report_id):
    report = getReportById(report_id)
    resources = [
        {**getResourceById(resource["id"]), "value": resource["value"]}
        for resource in report["resources"]
    ]

    context = {
        "report": report,
        "resources": resources
    }

    return render(request, "report_page.html", context)
