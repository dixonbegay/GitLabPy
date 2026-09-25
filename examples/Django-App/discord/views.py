import hmac
import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.conf import settings
import time

import json
import requests
from GitLabPy import GitLab

class GitLabHookView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(GitLabHookView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponse("Get Request... GitLab WebHook")

    def post(self, request, *args, **kwargs):
        token = request.headers.get("X-Gitlab-Token", "")
        if not hmac.compare_digest(token, settings.GITLAB_SECRET_TOKEN):
            return HttpResponseForbidden("Invalid or missing X-Gitlab-Token")

        json_data = json.loads(request.body.decode('utf-8'))

        with open("{}\gitlab-webhook-debug-{}.json".format(settings.TMP_DIR, time.strftime("%j%H%M", time.localtime())), 'w') as f:
            f.write(json.dumps(json_data, indent=4, sort_keys=True))

        GitLab_Obj = GitLab(json_data)

        if GitLab_Obj.build("failed"):
            msg = "[BUILD] Commit: {} Author: {}\nBuild Duration: {}\nBuild Status: {}\nhttps://gitlab.com/organization/project/pipelines/{}".format(
                GitLab_Obj.commit.get("message"), GitLab_Obj.user.get("name"),
                GitLab_Obj.json_data.get("build_duration"), GitLab_Obj.build_status.upper(),
                GitLab_Obj.commit.get("id")
            )
            r = requests.post(settings.DISCORD_WEBHOOK, json={"content" : msg})
        elif GitLab_Obj.issue("open"):
            msg = "[ISSUE] #{} {}\nCreated by {}\n{}".format(GitLab_Obj.object_attributes.get("iid"),
                GitLab_Obj.object_attributes.get("title"), GitLab_Obj.user.get("name"),
                GitLab_Obj.object_attributes.get("url")
            )
            r = requests.post(settings.DISCORD_WEBHOOK, json={"content" : msg})
        elif GitLab_Obj.issue("update"):
            msg = "[ISSUE] #{} {}\nUpdated by {}\n{}".format(GitLab_Obj.object_attributes.get("iid"),
                GitLab_Obj.object_attributes.get("title"), GitLab_Obj.user.get("name"),
                GitLab_Obj.object_attributes.get("url")
            )
            r = requests.post(settings.DISCORD_WEBHOOK, json={"content" : msg})
        elif GitLab_Obj.issue("closed"):
            msg = "[ISSUE] #{} {}\nClosed by {}\n{}".format(GitLab_Obj.object_attributes.get("iid"),
                GitLab_Obj.object_attributes.get("title"), GitLab_Obj.user.get("name"),
                GitLab_Obj.object_attributes.get("url")
            )
            r = requests.post(settings.DISCORD_WEBHOOK, json={"content" : msg})
        elif GitLab_Obj.note(True):
            msg = "[{}] {} commented on {}\n'{}'\n{}".format(
                GitLab_Obj.object_attributes.get("noteable_type"), GitLab_Obj.user.get("name"),
                GitLab_Obj.object_attributes.get("id"), GitLab_Obj.object_attributes.get("note"),
                GitLab_Obj.object_attributes.get("url")
            )
            r = requests.post(settings.DISCORD_WEBHOOK, json={"content" : msg})
        elif GitLab_Obj.merge_request(True):
            msg = "[MERGE REQUEST] {} wants to merge '{}' into '{}'\n{}\n{}".format(
                GitLab_Obj.user.get("name"), GitLab_Obj.object_attributes.get("source_branch"), GitLab_Obj.object_attributes.get("target_branch"),
                GitLab_Obj.object_attributes.get("title"), GitLab_Obj.json_data.get("url")
            )
            r = requests.post(settings.DISCORD_WEBHOOK, json={"content" : msg})
        else:
            msg = "Error occured in the view... No filter for this JSON POST request from GitLab... object_kind={}".format(GitLab_Obj.object_kind)
            r = requests.post(settings.DISCORD_WEBHOOK, json={"content" : msg})

        return HttpResponse("POST METHOD: Done!")
