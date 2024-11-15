from behave import given, when, then, use_step_matcher
from unittest.mock import MagicMock, patch
from action import __main__

use_step_matcher("re")

@given(u'a repo and the bump_style `(?P<bump_style>[a-z_]+)`')
def step_impl(context, bump_style):
    context.bump_style = bump_style

@when(u'list_gh_tags is called then an empty list is returned')
def step_impl(context):
    context.github_tags = []


def tag_mock(tag):
    mm = MagicMock()
    mm.name = tag
    return mm

@when(u'list_gh_tags is called then these tags are returned')
def step_impl(context):
    context.github_tags = [tag_mock(r['tag']) for r in context.table]


@then(u'(?P<expected_tag>v[0-9.\-rc]+) is the expected response when calling main_release')
def step_impl(context, expected_tag):
    expected_tag_is_returned(context, expected_tag)


@patch('github.Github')
@patch('git.Repo')
def expected_tag_is_returned(context, expected_tag, mock_github, mock_repo):
    mock_github.get_repo.return_value.get_tags.return_value = context.github_tags
    get_gh = MagicMock()
    get_gh.return_value = mock_github, 'repo'
    mock_repo.bare = False
    mock_repo.git.return_value.tag.return_value = []
    get_repo = MagicMock(return_value=mock_repo)
    with patch('action.__main__.get_gh', get_gh):
        with patch('action.__main__.get_repo', get_repo):
            tag = __main__.main_release(context.bump_style)
            assert tag == expected_tag
    
