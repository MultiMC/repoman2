# repoman2
A tool to update and manage GoUpdate repositories.

# Design

With the repository manager, the GoUpdate spec will be somewhat overhauled, but
the goal is to do so in a manner which is backwards compatible.

Firstly, in repoman2, we are introducing the concept of a "collection". A
collection is simply one big folder containing a folder for each platform the
application runs on.

A platform directory, or platform, refers to a folder containing GoUpdate
repositories (or channels) for a particular platform. Inside this platform
directory is a `channels.json` file, which contains information about all of the
repositories available on that platform.

Within each channel, everything should act in accordance with the GoUpdate
specification.
