from datetime import datetime
from enum import Enum
import os
import re
import sys
from uuid import uuid4

import click
from semver import Version
from git import Repo
from github import Github
from github import Auth

from action.mono import MonoVersionTag

def get_gh():
    token = os.getenv("GITHUB_TOKEN")
    print(f"token: {token is not None}")
    repo = os.getenv("GITHUB_REPOSITORY")
    print(f"repo: {repo}")
    if token is None or repo is None:
        die_with_intent("GITHUB_TOKEN and GITHUB_REPOSITORY must be set", 1)
    auth = Auth.Token(token)
    g = Github(auth=auth)
    return g, repo

def list_gh_tags():
    print("listing tags")
    tags = []
    g, repo = get_gh()
    for tag in g.get_repo(repo).get_tags():
        tags.append(tag.name)
        print(f"tag found: {tag.name}")
    g.close()
    if len(tags) == 0:
        print("no tags found")
    return tags

def get_latest_tag():
    tags = list_gh_tags()
    if len(tags) == 0:
        return MonoVersionTag("v0")
    parsed_tags = []
    for tag in tags:
        parsed_tags.append(MonoVersionTag(tag))
    sorted_tags = sorted(parsed_tags)
    for tag in sorted_tags:
        print(f"::>>  tag: {tag.tag} mono: {tag.mono} rc: {tag.release_candidate} is_rc: {tag.is_rc}")
        print(f"      nxt: {tag.next_mono().tag}")
        print(f"   nxtpre: {tag.next_rc().tag}")
    return sorted_tags[-1]

def die_with_intent(message: str, code: int):
    print(message)
    sys.exit(code)


class ReleaseType(Enum):
    build="build"
    major="major"
    minor="minor"
    patch="patch"
    prerelease="prerelease"
    timestamp="timestamp"
    auto="auto"
    mono="mono"
    mono_prerelease="mono_prerelease"


@click.command()
@click.argument('bump_style')
def main(bump_style: ReleaseType):
    tag = main_release(bump_style)
    print(tag)
    write_version_to_file(tag)


def get_repo():
    return Repo('.')

def main_release(bump_style: ReleaseType):
    bump_style = ReleaseType[bump_style]
    repo = get_repo()
    current_tags = ""
    try:
        current_tags = repo.git.tag(points_at="head")
    except:
        pass
    if repo.bare:
        die_with_intent("this script must be run in a git repository", 2)
    # make sure the release is valid
    if bump_style not in ReleaseType:
        die_with_intent(f"invalid release type {bump_style}, must be one of ['minor', 'major', 'patch', 'prerelease', 'timestamp', 'auto', 'mono', 'mono_prerelease']", 3)
    
    # auto is a future feature, should look at the latest commit message to determine the release type
    if bump_style == ReleaseType.auto:
        die_with_intent("auto release is not supported yet", 4)
    
    # a mono release is a release that is not semver, but is a single version that is incremented
    if bump_style in {ReleaseType.mono, ReleaseType.mono_prerelease}:
        current_version = None
        latest_version = 0
        last_rc = 0
        if current_tags:
            for tag in current_tags.split("\n"):
                if tag.startswith("v"):
                    current_version = MonoVersionTag(tag)
                    die_with_intent("version tag already set for this commit", 5)
        if not current_version:
            tag = "v0-rc0"
            try:
                last_tag = get_latest_tag()
                print(last_tag.tag)
                if bump_style == ReleaseType.mono:
                    tag = last_tag.next_mono().tag
                if bump_style == ReleaseType.mono_prerelease:
                    tag = last_tag.next_rc().tag
            except Exception as e:
                print("an error")
                import traceback
                traceback.print_exc()
                pass
    # for release types that are semver, we can bump the version
    if bump_style in {ReleaseType.prerelease, ReleaseType.build, ReleaseType.major, ReleaseType.minor, ReleaseType.patch}:
        current_version = None
        if current_tags:
            for tag in current_tags.split("\n"):
                if tag.startswith("v"):
                    current_version = Version.parse(tag[1:])
                    die_with_intent("version tag already set for this commit", 5)
        if not current_version:
            # look into the past to find the latest tag
            current_version = Version.parse("0.0.0")
            try:
                tag_list = list_gh_tags()
                ver_tags = []
                for tag in tag_list:
                    if tag.startswith("v"):
                        ver_tags.append(Version.parse(tag[1:]))
                for tag in sorted(ver_tags, reverse=True):
                    current_version = tag
                    print(tag)
                    break
            except Exception as e:
                print("an error")
                print(e)
                pass
        new_version: Version = None
        if bump_style == ReleaseType.build:
            new_version = current_version.bump_build()
        else:
            new_version = current_version.next_version(bump_style.name)
        tag = f"v{new_version}"
    # timestamp releases
    elif bump_style == ReleaseType.timestamp:
        if current_tags:
            for tag in current_tags.split("\n"):
                if tag.startswith("release-"):
                    die_with_intent("timestamp tag already set for this commit", 5)
        tag = datetime.now().strftime("release-%Y-%m-%d_%H-%M-%S")
    print(f"tag: {tag}")
    return tag


def write_version_to_file(version: str):
    fname = os.getenv("GITHUB_OUTPUT", "VERSION")
    with open(fname, "a") as f:
        f.write("TAG_NAME=")
        f.write(version)
        f.flush()

if __name__ == '__main__':
    main()
