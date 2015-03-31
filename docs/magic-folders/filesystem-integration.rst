
**Magic Folders local filesystem integration design**


**scope**

This document describes an efficient and reliable manner in which to integrate the local filesystem with Magic Folders. For now we ignore Remote to Local sync and ignore other writers for the same Magic Folder. The design here will be updated to account for those features in later Objectives. Objective 3 may require modifying the schema or operation, Objective 5 may modify the Usability.

 
**eventual consistency property of local scanning**

Race conditions between local writes and the current scan will result in temporary inconsistency. Eventual consistency is reached when the queue of pending uploads is empty. That is, a consistent snapshot will be uploaded eventually when local writes to the target folder cease for a sufficiently long period of time.


**avoiding full re-uploads**

After the initial full scan of the local directory, subsequent full directory uploads are avoided by using the same machanism the Tahoe backup command uses. Essentially we keep track of previous scans, recording each file's metadata such as size, CTIME and MTIME. Using this previously recorded state we can ensure that when Magic Folders is subsequently started, the local directory will quickly be scanned by comparing current filesystem metadata with the previously recorded metadata. Files are added to the upload queue only if their metadata differs.

For tracking this filesystem metadata we will use an SQLite schema that initially is the existing Tahoe-LAFS backup schema. This schema may change in  later objectives. This is okay, because this is a new feature and we don't need backwards compatibility. However we will have a separate SQLite file and mutex lock just for Magic Folders, to avoid usability problems related to mutual exclusion (a backup prevents Magic Folder updates for a long time, or a user cannot tell when backups are possible because Magic Folder acquires a lock at arbitrary times).

For the Linux implementation we will use the inotify Linux kernel subsystem to gather write events upon the target local directory. When we receive such an event the SQLite db will be updated with the new file metadata. Additionally the file will be added to the upload queue.


**User interface**

The configuration file, tahoe.cfg, must define a target local directory to be synced::

 [magic_folders]
 enabled = true
 local.directory = "/home/human"

