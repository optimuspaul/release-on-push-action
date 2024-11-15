Feature: Monotonic versions
  Semver is cool, but sometimes a simple monotonic version number is all you really need.

  Scenario: No existing tags
    Given a repo and the bump_style `major`
     When list_gh_tags is called then an empty list is returned
     Then v1.0.0 is the expected response when calling main_release

  Scenario: three existing tags
    Given a repo and the bump_style `major`
     When list_gh_tags is called then these tags are returned
        | tag      |
        | v1.0.0   |
        | v1.0.1   |
        | v1.0.2   |
        | v1.0.2   |
     Then v2.0.0 is the expected response when calling main_release

  Scenario: No existing tags
    Given a repo and the bump_style `minor`
     When list_gh_tags is called then an empty list is returned
     Then v0.1.0 is the expected response when calling main_release

  Scenario: three existing tags
    Given a repo and the bump_style `minor`
     When list_gh_tags is called then these tags are returned
        | tag      |
        | v1.0.0   |
        | v1.0.1   |
        | v1.0.2   |
     Then v1.1.0 is the expected response when calling main_release

  Scenario: three existing tags
    Given a repo and the bump_style `prerelease`
     When list_gh_tags is called then these tags are returned
        | tag      |
        | v1.0.0   |
        | v1.0.1   |
        | v1.0.2   |
     Then v1.0.3-rc.1 is the expected response when calling main_release

  Scenario: many existing tags
    Given a repo and the bump_style `minor`
     When list_gh_tags is called then these tags are returned
        | tag      |
        | v1.0.0   |
        | v1.0.1   |
        | v1.0.2   |
        | v2.0.0   |
        | v2.9.1   |
     Then v2.10.0 is the expected response when calling main_release

  Scenario: many existing tags with release candidates
    Given a repo and the bump_style `prerelease`
     When list_gh_tags is called then these tags are returned
        | tag         |
        | v1.0.0      |
        | v1.0.1      |
        | v1.0.2      |
        | v2.0.0      |
        | v2.9.1      |
        | v2.9.2-rc.1 |
     Then v2.9.2-rc.2 is the expected response when calling main_release

  Scenario: many existing tags with release candidates
    Given a repo and the bump_style `minor`
     When list_gh_tags is called then these tags are returned
        | tag         |
        | v1.0.0      |
        | v1.0.1      |
        | v1.0.2      |
        | v2.0.0      |
        | v2.9.1      |
        | v2.9.2-rc.1 |
     Then v2.10.0 is the expected response when calling main_release


  Scenario: many existing tags with release candidates
    Given a repo and the bump_style `minor`
     When list_gh_tags is called then these tags are returned
        | tag          |
        | v0.10.0      |
        | v0.9.1-rc.5  |
        | v0.9.1-rc.4  |
        | v0.9.1-rc.3  |
        | v0.9.1-rc.2  |
        | v0.9.1-rc.1  |
        | v0.9.0       |
        | v0.8.1-rc.2  |
        | v0.8.1-rc.1  |
        | v0.8.0       |
        | v0.7.1-rc.8  |
        | v0.7.1-rc.7  |
        | v0.7.1-rc.6  |
        | v0.7.1-rc.5  |
        | v0.7.1-rc.4  |
        | v0.7.1-rc.3  |
        | v0.7.1-rc.2  |
        | v0.7.1-rc.1  |
        | v0.7.0       |
        | v0.6.1-rc.1  |
        | v0.6.0       |
        | v0.5.1-rc.1  |
        | v0.5.0       |
        | v0.4.1-rc.1  |
        | v0.4.0       |
        | v0.3.1-rc.4  |
        | v0.3.1-rc.3  |
        | v0.3.1-rc.2  |
        | v0.3.1-rc.1  |
        | v0.3.0       |
        | v0.2.1-rc.2  |
        | v0.2.1-rc.1  |
        | v0.2.0       |
        | v0.1.1-rc.1  |
        | v0.1.0       |
     Then v0.11.0 is the expected response when calling main_release


