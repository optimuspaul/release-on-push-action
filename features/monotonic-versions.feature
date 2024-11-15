Feature: Monotonic versions
  Semver is cool, but sometimes a simple monotonic version number is all you really need.

  Scenario: No existing tags
    Given a repo and the bump_style `mono`
     When list_gh_tags is called then an empty list is returned
     Then v1 is the expected response when calling main_release

  Scenario: Two existing tags
    Given a repo and the bump_style `mono`
     When list_gh_tags is called then these tags are returned
        | tag      |
        | v1       |
        | v2-rc1   |
     Then v2 is the expected response when calling main_release

  Scenario: No existing tags
    Given a repo and the bump_style `mono_prerelease`
     When list_gh_tags is called then an empty list is returned
     Then v1-rc1 is the expected response when calling main_release

  Scenario: Two existing tags
    Given a repo and the bump_style `mono_prerelease`
     When list_gh_tags is called then these tags are returned
        | tag      |
        | v1       |
        | v2-rc1   |
     Then v2-rc2 is the expected response when calling main_release

