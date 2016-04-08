# #import <signal.h>
# //#import <syslog.h>
# #import <sys/param.h>
# #import <unistd.h>
# 
# #include <CoreFoundation/CoreFoundation.h>
# #include <CoreServices/CoreServices.h>
# 
# void fsevent_callback ( 
#     ConstFSEventStreamRef           streamRef, 
#     void *                          clientCallBackInfo, 
#     int                             numEvents, 
#     const char *const               eventPaths[], 
#     const FSEventStreamEventFlags   eventFlags[], 
#     const FSEventStreamEventId      eventIds[]
# ) {
#     for (int i=0; i<numEvents; i++) { 
#         // flags are unsigned long, IDs are uint64_t
#         printf("Notification change %llu in %s, flags %lu\n",
#             eventIds[i], 
#             eventPaths[i], 
#             eventFlags[i]
#         );
#     } 
# } // fsevent_callback

import os, sys

from twisted.internet import reactor
from twisted.internet.threads import deferToThread

from allmydata.util.fake_inotify import humanReadableMask, \
    IN_WATCH_MASK, IN_ACCESS, IN_MODIFY, IN_ATTRIB, IN_CLOSE_NOWRITE, IN_CLOSE_WRITE, \
    IN_OPEN, IN_MOVED_FROM, IN_MOVED_TO, IN_CREATE, IN_DELETE, IN_DELETE_SELF, \
    IN_MOVE_SELF, IN_UNMOUNT, IN_Q_OVERFLOW, IN_IGNORED, IN_ONLYDIR, IN_DONT_FOLLOW, \
    IN_MASK_ADD, IN_ISDIR, IN_ONESHOT, IN_CLOSE, IN_MOVED, IN_CHANGED
[humanReadableMask, \
    IN_WATCH_MASK, IN_ACCESS, IN_MODIFY, IN_ATTRIB, IN_CLOSE_NOWRITE, IN_CLOSE_WRITE, \
    IN_OPEN, IN_MOVED_FROM, IN_MOVED_TO, IN_CREATE, IN_DELETE, IN_DELETE_SELF, \
    IN_MOVE_SELF, IN_UNMOUNT, IN_Q_OVERFLOW, IN_IGNORED, IN_ONLYDIR, IN_DONT_FOLLOW, \
    IN_MASK_ADD, IN_ISDIR, IN_ONESHOT, IN_CLOSE, IN_MOVED, IN_CHANGED]

from allmydata.util.assertutil import _assert, precondition
from allmydata.util.encodingutil import quote_output
from allmydata.util import log, fileutil
from allmydata.util.pollmixin import PollMixin

from ctypes import POINTER, byref, create_string_buffer, addressof

print "IMPORTED OSX INOTIFY ---<< <---!!\n\n"

class Event(object):
    """
    * id:    an integer event ID
    * flags: an integer of type FSEventStreamEventFlags
    * path:  a Unicode string, giving the absolute path of the notified file
    """
    def __init__(self, id, flags, path):
        self.id = id
        self.flags = flags
        self.path = path

    def __repr__(self):
        return ("Event(%r, %r, %r)" % (self.id, self.flags, self.path))
#% (self.id, _flags_to_string.get(self.flags, self.flags), self.path)


NOT_STARTED = "NOT_STARTED"
STARTED     = "STARTED"
STOPPING    = "STOPPING"
STOPPED     = "STOPPED"

class INotify(PollMixin):
    def __init__(self):
        self._state = NOT_STARTED
        self._filter = None
        self._callbacks = None
        self._pending = set()
        self._pending_delay = 1.0

    def set_pending_delay(self, delay):
        self._pending_delay = delay

    def startReading(self):
        deferToThread(self._thread)
        return self.poll(lambda: self._state != NOT_STARTED)

    def stopReading(self):
        # FIXME race conditions
        if self._state != STOPPED:
            self._state = STOPPING

    def watch(self, path, mask=IN_WATCH_MASK, autoAdd=False, callbacks=None, recursive=False):
        precondition(self._state == NOT_STARTED, "watch() can only be called before startReading()", state=self._state)
        precondition(self._filter is None, "only one watch is supported")
        precondition(isinstance(autoAdd, bool), autoAdd=autoAdd)
        precondition(isinstance(recursive, bool), recursive=recursive)
        print "WATCH no-op!"

# 
# //-----------------------------------------------------------------------------
# int register_callback(const char *path_buffer) {
# //-----------------------------------------------------------------------------
#     
#     CFStringRef path_array[1];
#     path_array[0] = CFStringCreateWithCString(
#         kCFAllocatorDefault,
#         path_buffer,
#         kCFStringEncodingUTF8
#     );
#     assert(path_array[0] != NULL);
#     CFArrayRef paths_to_watch = CFArrayCreate(
#         NULL,                       // allocator
#         (const void **)path_array,  // values
#         1,                          // number of values
#         NULL                        // callbacks
#     ); 
#     assert(paths_to_watch != NULL);
#     
#     FSEventStreamContext context;
#     bzero(&context, sizeof context);
#     context.info = (void *) NULL; // cookie
#     
#     CFAbsoluteTime latency = 3.0; /* Latency in seconds */
#     CFAbsoluteTime fire_date = CFAbsoluteTimeGetCurrent();
#     CFTimeInterval interval = 3.0;
#     
#     /* Create the stream, passing in a callback, */ 
#     FSEventStreamRef stream = FSEventStreamCreate(
#         kCFAllocatorDefault, 
#         (FSEventStreamCallback) fsevent_callback, 
#         &context, 
#         paths_to_watch, 
#         kFSEventStreamEventIdSinceNow, /* Or a previous event ID */ 
#         latency, 
#         kFSEventStreamCreateFlagWatchRoot 
#     ); 
# 
#     FSEventStreamScheduleWithRunLoop(
#         stream, 
#         CFRunLoopGetCurrent(),         
#         kCFRunLoopDefaultMode
#     ); 
#     
#     Boolean result = FSEventStreamStart(stream);
#     if (!result) {
#         // syslog(LOG_ERR, "FSEventStreamStart failed");
#         error_file = open_error_file();
#         fprintf(error_file, "FSEventStreamStart failed: (%d) %s\n", 
#             errno, strerror(errno)
#         );
#         fclose(error_file);
#         FSEventStreamInvalidate(stream);
#         FSEventStreamRelease(stream);
#         return -12;
#     }
# 
#     CFRunLoopTimerRef timer = CFRunLoopTimerCreate(
#         kCFAllocatorDefault,
#         fire_date,
#         interval,
#         0, /* flags */
#         0, /* order */
#         (CFRunLoopTimerCallBack) timer_callback,
#         NULL /* context */
#     );
#     
#     CFRunLoopAddTimer(
#         CFRunLoopGetCurrent(),         
#         timer,
#         kCFRunLoopDefaultMode
#     );
#     
#     // break out of CFRunLoop on SIGTERM (kill TERM)
#     signal(SIGTERM, handleTERM);
#     
#     // syslog(LOG_NOTICE, "Entering CFRunLoopRun");
#     CFRunLoopRun();
#     // syslog(LOG_NOTICE, "Exited CFRunLoopRun");
#     
#     FSEventStreamStop(stream);
#     FSEventStreamInvalidate(stream);
#     FSEventStreamRelease(stream);
#     CFRelease(paths_to_watch);
#     
#     return 0;
# } // main
