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


def list_gh_tags():
    tags = []
    token = os.getenv("GITHUB_TOKEN")
    print(f"token: {token is not None}")
    repo = os.getenv("GITHUB_REPOSITORY")
    print(f"repo: {repo}")
    if token is None or repo is None:
        die_with_intent("GITHUB_TOKEN and GITHUB_REPOSITORY must be set", 1)
    auth = Auth.Token(token)
    g = Github(auth=auth)
    for tag in g.get_repo(repo).get_tags():
        tags.append(tag.name)
        print(f"tag found: {tag.name}")
    g.close()
    if len(tags) == 0:
        print("no tags found")
    return tags


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
    bump_style = ReleaseType[bump_style]
    repo = Repo('.')
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
                    current_version = Version.parse(tag[1:])
                    die_with_intent("version tag already set for this commit", 5)
        if not current_version:
            try:
                tag_list = list_gh_tags()
                vs = re.compile(r"v(\d+)")
                vps = re.compile(r"v(\d+)-rc(\d+)")
                if bump_style == ReleaseType.mono:
                    tag_list = filter(lambda x: vs.match(x), tag_list)
                    tag_list =  sorted(map(lambda x: int(x), tag_list), reverse=True)
                    if len(tag_list) > 0:
                        latest_version = tag_list[0]
                else:
                    versions = dict()
                    for tag in tag_list:
                        print(f"checking tag: {tag}")
                        if vps.match(tag):
                            vers, rc = vps.match(tag).groups()
                            latest_version = max(latest_version, int(vers))
                            if vers not in versions:
                                versions[vers] = []
                            versions[vers].append(int(rc))
                            print(f"found version: {vers} rc: {rc}")
                        elif vs.match(tag):
                            vers = vs.match(tag).groups()[0]
                            latest_version = max(latest_version, int(vers))
                            if vers not in versions:
                                versions[vers] = []
                            print(f"found version: {latest_version} rc: -")
                    rc_list =  sorted(map(lambda x: int(x), versions[vers]), reverse=True)
                    print(rc_list)
                    if len(rc_list) > 0:
                        last_rc = rc_list[0]
                    else:
                        latest_version += 1
            except:
                pass
        tag = f"v{latest_version}"
        if bump_style == ReleaseType.mono_prerelease:
            tag = f"v{latest_version}-rc{last_rc+1}"
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
            latest_version = "0.0.0"
            try:
                tag_list = list_gh_tags()
                for tag in sorted(tag_list, reverse=True):
                    if tag.startswith("v"):
                        latest_version = tag[1:]
                        break
            except Exception as e:
                print("an error")
                print(e)
                pass
            current_version = Version.parse(latest_version)
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
    print(tag)
    write_version_to_file(tag)


def write_version_to_file(version: str):
    fname = os.getenv("GITHUB_OUTPUT", "VERSION")
    with open(fname, "a") as f:
        f.write("TAG_NAME=")
        f.write(version)
        f.flush()

if __name__ == '__main__':
    main()
