# Multi-layered Network Progress Presentation Script

## Slide 1 - Current Progress

This slide shows my current progress on the multi-layered network feature.

Right now, the system already supports multiple levels of nested subnets, so a network can contain subnetworks inside other subnetworks.

On top of this structure, the system can correctly compute nested subnets across multiple layers. It can also correctly duplicate diagrams with nested subnets, which means the nested content and structure can be copied without being broken.

In addition, exporting and importing nested diagrams now works correctly, so the multi-layered information can be preserved during data transfer as well.

So overall, my current progress is that the core logic for handling multi-layered nested diagrams is now working in a stable and usable way. This also creates the foundation for the next step, which is version compatibility.

## Slide 2 - Goal

This slide shows my next goal, which is user version compatibility.

The current problem is that when the database or data structure changes, some old diagrams may fail because they no longer fully match the latest format. Also, the upgrade process is still slow. Right now, upgrading 9 diagrams takes around 30 seconds.

My plan is to introduce version control starting from version 6.0.0. After that, every time the database is modified, the system will automatically update the version number.

Then, when a user opens an older diagram, the system will be able to detect the version difference and support upgrading that diagram to the latest version.

At the same time, older versions will be archived as backups. So if any issue happens during or after the upgrade, the system can revert to the previous correct version at any time.

So the goal is to make upgrading old diagrams faster, safer, traceable, and reversible.
