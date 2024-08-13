import re

vs = re.compile(r"v(\d+)")
vps = re.compile(r"v(\d+)-rc(\d+)")

class MonoVersionTag:
    mono: int
    release_candidate: int
    is_rc: bool

    def __init__(self, tag):
        self.tag = tag
        self.mono = 0
        self.release_candidate = 0
        self.is_rc = False
        self.parse()

    def parse(self):
        m = vps.match(self.tag)
        if m:
            self.mono = int(m.group(1))
            self.release_candidate = int(m.group(2))
            self.is_rc = True
            return
        m = vs.match(self.tag)
        if m:
            self.mono = int(m.group(1))
            return
        raise ValueError(f"Invalid tag: {self.tag}")

    def __lt__(self, other):
        if not isinstance(other, MonoVersionTag):
            return NotImplemented        
        if self.mono < other.mono:
            return True
        if self.mono > other.mono:
            return False
        if self.is_rc and not other.is_rc:
            return True
        if not self.is_rc and other.is_rc:
            return False
        return self.release_candidate < other.release_candidate

    def next_rc(self):
        if self.is_rc:
            return MonoVersionTag(f"v{self.mono}-rc{self.release_candidate+1}")
        return MonoVersionTag(f"v{self.mono+1}-rc1")

    def next_mono(self):
        if self.is_rc:
            return MonoVersionTag(f"v{self.mono}")
        return MonoVersionTag(f"v{self.mono+1}")


if __name__ == "__main__":
    # import os
    # from github import Github
    # from github import Auth
    # token = os.getenv("GITHUB_TOKEN")
    # print(f"token: {token is not None}")
    # repo = os.getenv("GITHUB_REPOSITORY")
    # print(f"repo: {repo}")
    # auth = Auth.Token(token)
    # g = Github(auth=auth)
    # r = g.get_repo(repo)
    # for tag in r.get_tags():
    #     t = MonoVersionTag(tag.name)
    #     print(f"tag: {t.tag} mono: {t.mono} rc: {t.release_candidate} is_rc: {t.is_rc}")
    # g.close()

    test_tags = [
        "v8",
        "v2",
        "v3",
        "v4",
        "v5",
        "v6",
        "v9",
        "v8-rc4",
        "v8-rc3",
        "v8-rc2",
        "v8-rc1",
        "v1-rc1",
        "v1",
        "v7",
    ]
    tags = []
    for tag in test_tags:
        t = MonoVersionTag(tag)
        tags.append(t)
    sorted_tags = sorted(tags)
    print("sorted tags:")
    for tag in sorted_tags:
        print(f"::>>  tag: {tag.tag} mono: {tag.mono} rc: {tag.release_candidate} is_rc: {tag.is_rc}")
        print(f"      nxt: {tag.next_mono().tag}")
        print(f"   nxtpre: {tag.next_rc().tag}")
    latest = sorted_tags[-1]
