from datetime import datetime
from enum import Enum
import sys

import click
from semver import Version
from git import Repo


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


@click.command()
@click.argument('bump_style')
def main(bump_style: ReleaseType):
    repo = Repo('.')
    current_tags = ""
    try:
        current_tags = repo.git.describe(tags=True, abbrev=0)
        print("-----------------------")
        print(current_tags)
        print("-----------------------")
        current_tags = repo.git.describe(tags=True)
        print("-----------------------")
        print(current_tags)
        print("-----------------------")
    except:
        pass
    if repo.bare:
        die_with_intent("this script must be run in a git repository", 2)
    # make sure the release is valid
    if bump_style not in dir(ReleaseType):
        die_with_intent(f"invalid release type {bump_style}, must be one of ['minor', 'major', 'patch', 'prerelease', 'timestamp', 'auto']", 3)
    
    # auto is a future feature, should look at the latest commit message to determine the release type
    if bump_style == ReleaseType.auto.value:
        die_with_intent("auto release is not supported yet", 4)
    
    # for release types that are semver, we can bump the version
    if bump_style in ['prerelease', 'build', 'major', 'minor', 'patch']:
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
                print(repo.git.tag())
            except:
                pass
            current_version = Version.parse(latest_version)
        new_version: Version = None
        if bump_style == ReleaseType.build.value:
            new_version = current_version.bump_build()
        else:
            new_version = current_version.next_version(bump_style)
        tag = f"v{new_version}"
    # timestamp releases
    elif bump_style == ReleaseType.timestamp.value:
        if current_tags:
            for tag in current_tags.split("\n"):
                if tag.startswith("release-"):
                    die_with_intent("timestamp tag already set for this commit", 5)
        tag = datetime.now().strftime("release-%Y-%m-%d_%H-%M-%S")
        
    print(tag)
    repo.create_tag(tag)
    repo.remotes.origin.push(tag)


if __name__ == '__main__':
    main()
