import requests
from contentapi.celery import app
from celery import shared_task


@app.task(bind=True)
def pull_content():
    from contents.content_service import ContentService

    content_service = ContentService()

    # TODO: The design of this celery task is very weird. It's posting the response to localhost:3000.
    #  which is not ideal
    url = "https://hackapi.hellozelf.com/api/v1/contents/"
    res = requests.get(url).json()

    content_service.prepare_content(res)


@app.task(queue="comment_generation", bind=True, rate_limit="1/m")
def generate_comment(content):
    from contents.content_service import ContentService

    content_service = ContentService()
    content_service.generate_comment(content)
