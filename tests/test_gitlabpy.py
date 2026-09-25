import pytest

from GitLabPy import GitLab


def make_payload(**overrides):
    payload = {
        "object_kind": "issue",
        "project_id": 1,
        "ref": "master",
        "project_name": "example",
        "user": {"name": "Dixon Begay"},
        "commit": {"id": "abc123", "message": "test commit"},
        "object_attributes": {"iid": 1, "title": "Example issue"},
        "build_status": "",
        "repository": {
            "name": "example",
            "homepage": "https://gitlab.com/example",
            "url": "git@gitlab.com:example/example.git",
            "git_ssh_url": "git@gitlab.com:example/example.git",
            "git_http_url": "https://gitlab.com/example/example.git",
        },
    }
    payload.update(overrides)
    return payload


class TestInit:
    def test_parses_common_fields(self):
        payload = make_payload()
        gl = GitLab(payload)

        assert gl.object_kind == "issue"
        assert gl.project_id == 1
        assert gl.ref == "master"
        assert gl.project_name == "example"
        assert gl.user == {"name": "Dixon Begay"}
        assert gl.commit == {"id": "abc123", "message": "test commit"}
        assert gl.object_attributes == {"iid": 1, "title": "Example issue"}
        assert gl.repo_name == "example"
        assert gl.repo_homepage == "https://gitlab.com/example"

    def test_missing_keys_default_to_empty_string(self):
        gl = GitLab({})

        assert gl.object_kind == ""
        assert gl.project_id == ""
        assert gl.ref == ""
        assert gl.project_name == ""
        assert gl.user == ""
        assert gl.commit == ""
        assert gl.object_attributes == ""
        assert gl.build_status == ""
        assert gl.repository == ""
        assert gl.repo_name == ""
        assert gl.repo_homepage == ""


class TestCheckRepositoryAttr:
    def test_true_when_repository_present(self):
        gl = GitLab(make_payload())
        assert gl.check_repository_atttr() is True

    def test_false_when_repository_missing(self):
        gl = GitLab({})
        assert gl.check_repository_atttr() is False


class TestGetUrl:
    def test_returns_false_without_repository(self):
        gl = GitLab({})
        assert gl.get_url() is False

    def test_default_returns_url(self):
        gl = GitLab(make_payload())
        assert gl.get_url() == "git@gitlab.com:example/example.git"

    def test_ssh(self):
        gl = GitLab(make_payload())
        assert gl.get_url("ssh") == "git@gitlab.com:example/example.git"

    def test_http(self):
        gl = GitLab(make_payload())
        assert gl.get_url("http") == "https://gitlab.com/example/example.git"

    def test_homepage(self):
        gl = GitLab(make_payload())
        assert gl.get_url("homepage") == "https://gitlab.com/example"

    def test_case_insensitive(self):
        gl = GitLab(make_payload())
        assert gl.get_url("SSH") == "git@gitlab.com:example/example.git"


class TestGetRepoDescription:
    def test_returns_description_when_present(self):
        gl = GitLab(make_payload(repository={
            "name": "example",
            "homepage": "https://gitlab.com/example",
            "description": "An example repo",
        }))
        assert gl.get_repo_description() == "An example repo"

    def test_returns_false_without_repository(self):
        gl = GitLab({})
        assert gl.get_repo_description() is False


class TestBuild:
    def test_true_for_matching_status(self):
        gl = GitLab(make_payload(object_kind="build", build_status="failed"))
        assert gl.build("failed", "success") is True

    def test_false_for_non_matching_status(self):
        gl = GitLab(make_payload(object_kind="build", build_status="running"))
        assert gl.build("failed", "success") is False

    def test_false_for_wrong_object_kind(self):
        gl = GitLab(make_payload(object_kind="issue", build_status="failed"))
        assert gl.build("failed") is False


class TestNote:
    def test_true_when_note_and_requested(self):
        gl = GitLab(make_payload(object_kind="note"))
        assert gl.note(True) is True

    def test_false_when_not_requested(self):
        gl = GitLab(make_payload(object_kind="note"))
        assert gl.note(False) is False

    def test_false_for_wrong_object_kind(self):
        gl = GitLab(make_payload(object_kind="issue"))
        assert gl.note(True) is False


class TestMergeRequest:
    def test_true_when_merge_request_and_requested(self):
        gl = GitLab(make_payload(object_kind="merge_request"))
        assert gl.merge_request(True) is True

    def test_false_when_not_requested(self):
        gl = GitLab(make_payload(object_kind="merge_request"))
        assert gl.merge_request(False) is False

    def test_false_for_wrong_object_kind(self):
        gl = GitLab(make_payload(object_kind="issue"))
        assert gl.merge_request(True) is False


class TestIssue:
    def test_open(self):
        gl = GitLab(make_payload(
            object_kind="issue",
            object_attributes={"action": "open"},
        ))
        assert gl.issue("open") is True

    def test_update(self):
        gl = GitLab(make_payload(
            object_kind="issue",
            object_attributes={"action": "update"},
        ))
        assert gl.issue("update") is True

    def test_closed(self):
        gl = GitLab(make_payload(
            object_kind="issue",
            object_attributes={"state": "closed"},
        ))
        assert gl.issue("closed") is True

    def test_false_for_wrong_object_kind(self):
        gl = GitLab(make_payload(object_kind="merge_request"))
        assert gl.issue("open") is False

    def test_false_when_action_not_requested(self):
        gl = GitLab(make_payload(
            object_kind="issue",
            object_attributes={"action": "update"},
        ))
        assert gl.issue("open", "closed") is False
