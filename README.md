# Brandmeister Last Heard Monitor
Brandmeister Last Heard Monitor/Notifier

###### Forked from [mclemens/pyBMNotify](https://codeberg.org/mclemens/pyBMNotify) and modified.
###### Forked from [n8acl/bm_monitor](https://github.com/n8acl/bm_monitor) and modified.

This Python script will listen to the Brandmeister Last Heard API endpoint for any callsign or Talkgroup (or both) that you configure and it will send you a notification when there is activity for those callsigns and/or talkgroups.

This script is really just a refactoring using a newer socketIO python library from what the orginal pyBMNotify script was using. Brandmesiter updated the protocol that their API was using a few months ago and the old script did not support the newer protocol, so I just refactored the script for this newer protocol. The actual logic and guts of the script are still the same as the original pyBMNotify script that [Michael Clemens, DK1MI](https://qrz.is/) wrote and [Jeff Lehman, N8ACL] modified and that is all THEIR work. That is why this is a fork, not an original work. I wanted to make sure that was clear. I did not do the heavy lifting for this project, I just added and modified some code. Everything else is their work.

This script is for use by Amateur Radio Operators Only.

---

## Supported Services

This script will push a notification to the following services:

- Discord
- Telegram
- Pushover
- DAPNET

---

## Installation/Setup Instructions

[Click here to see the installation and setup steps](https://github.com/mi-gri/bm_monitor/blob/master/installation-setup.md). Then come back here. This is a bit of a long document, so read it all carefully.

---
## Contact
If you have questions, please feel free to reach out to me. You can reach me in one of the following ways:

- Mastodon: @DO3BOX@social.darc.de
- E-mail: do3box@darc.de

Or open an issue on Github. I will respond to it, and of course you, when I can. 

If you reach out to me and have an error, please include what error you are getting and what you were doing. I may also ask you to send me certain files to look at. Otherwise just reach out to me :).

---

## Change Log

* 08/10/2023 - Release 1.2 - added long notify (for telegram) and notification based on used repeater/hotspot callsign 
