'''
A system for retrieving and assigning tasks for the bot as well as updating
their statuses once acted up. This file contains two abstract classes,
Tasker and Task, which define a class to manage tasks and a task class
respectively.
'''
from datetime import datetime
from abc import ABCMeta, abstractmethod

import pytz

from securitybot.util import enum

__author__ = 'Alex Bertsch'
__email__ = 'abertsch@dropbox.com'


class Tasker(object):
    '''
    A simple interface to retrieve tasks on which the bot should act upon.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_new_tasks(self):
        # type: () -> List[Task]
        '''
        Returns a list of new Task objects that need to be acted upon, i.e.
        the intial message needs to be sent out to the alertee.
        '''
        pass

    @abstractmethod
    def get_active_tasks(self):
        # type: () -> List[Task]
        '''
        Returns a list of Task objects for which the alertees have been
        contacted but have not replied. Periodically this list should be polled
        and stale tasks should have their alertees pinged.
        '''
        pass

    @abstractmethod
    def get_pending_tasks(self):
        # type: () -> List[Task]
        '''
        Retrieves a list of tasks for which the user has responded and it now
        waiting for manual closure.
        '''
        pass

# Task status levels
STATUS_LEVELS = enum('OPEN', 'INPROGRESS', 'VERIFICATION')


class Task(object):
    __metaclass__ = ABCMeta

    def __init__(self, title, username, reason, description, url, performed, comment,
            authenticated, status, event_time=None, escalation=None):
        # type: (str, str, str, str, str, bool, str, bool, int) -> None
        '''
        Creates a new Task for an alert that should go to `username` and is
        currently set to `status`.

        Args:
            title (str): The title of this task.
            username (str): The user who should be alerted from the Task.
            reason (str): The reason that the alert was fired.
            description (str): A description of the alert in question.
            url (str): A URL in which more information can be found about the
                       alert itself, not the Task.
            performed (bool): Whether or not the user performed the action that
                              caused this alert.
            comment (str): The user's comment on why the action occured.
            authenticated (bool): Whether 2FA has suceeded.
            status (enum): See `STATUS_LEVELS` from above.
        '''
        self.title = title
        self.username = username
        self.reason = reason
        self.description = description
        self.url = url
        self.performed = performed
        self.comment = comment
        self.authenticated = authenticated
        self.status = status
        self.event_time = pytz.utc.localize(event_time)
        self.escalation = escalation

    @abstractmethod
    def set_open(self):
        # type: () -> None
        '''
        Sets this task to be open and performs any needed actions to ensure that
        the corresponding tasker will be able to properly see it as such.
        '''
        pass

    @abstractmethod
    def set_in_progress(self):
        # type: () -> None
        '''
        Sets this task to be in progress and performs any needed actions to
        ensure the corresponding tasker will be able to see it as such.
        '''
        pass

    @abstractmethod
    def set_verifying(self):
        # type: () -> None
        '''
        Sets this task to be waiting for verification and performs and needed
        actions to ensure that the corresponding tasker sees it as such.
        '''
        pass

    def is_open(self):
        # type: () -> bool
        '''
        Returns True if the task is Open, False otherwise
        '''
        return self.status == STATUS_LEVELS.OPEN

    def is_in_progress(self):
        # type: () -> bool
        '''
        Returns True if the task is InProgress, False otherwise
        '''
        return self.status == STATUS_LEVELS.INPROGRESS

    def is_verifying(self):
        # type: () -> bool
        '''
        Returns True if the task is in Verifying state, False otherwise
        '''
        return self.status == STATUS_LEVELS.VERIFICATION

    @abstractmethod
    def set_escalated(self, escalation):
        # type: (Escalation) -> None
        '''
        Sets the associated escalation as escalated.
        '''
        pass

    def __str__(self):
        return str(self.__dict__)


class Escalation(object):
    def __init__(self, ldap, delay_in_sec, notified_at=None):
        self.ldap = ldap
        self.delay_in_sec = delay_in_sec
        self._notified_at = pytz.utc.localize(notified_at) if notified_at else None

    def is_notified(self):
        return self._notified_at is not None

    def set_notified(self):
        self._notified_at = datetime.now(tz=pytz.utc)

    def should_notify(self, elapsed_timedelta):
        return not self.is_notified() and elapsed_timedelta.seconds > self.delay_in_sec

    def __repr__(self):
        return str(self.__dict__)
