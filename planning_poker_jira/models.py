# -*- coding: utf-8 -*
import logging
from typing import List, Optional

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_fields import fields
from jira import JIRA

#from planning_poker.models import PokerSession, Story

logger = logging.getLogger(__name__)


class PokerSession(models.Model):
    #: The date on which the poker session should take place.
    poker_date = models.DateField(verbose_name=_('Poker Date'))
    #: The poker session's name. Used for displaying it to the user.
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    #: The story which is currently active in this poker session.
    active_story = models.OneToOneField(
        'Story',
        on_delete=models.SET_NULL,
        verbose_name=_('Active Story'),
        related_name='active_in',
        null=True
    )

    class Meta:
        ordering = ['-poker_date']
        verbose_name = _('Poker Session')
        verbose_name_plural = _('Poker Sessions')

    def __str__(self) -> str:
        return self.name


class Story(models.Model):
    #: The story's ticket number. Used for displaying the story to the user.
    ticket_number = models.CharField(max_length=200, verbose_name=_('Ticket Number'))
    #: The story's title. Used for displaying the story to the user.
    title = models.CharField(max_length=200, verbose_name=_('Title'), blank=True)
    #: The story's description. This is the main source of information for participants in a poker session.
    description = models.TextField(verbose_name=_('Description'), blank=True)
    #: The estimated story points. The value is either an element of
    #: :py:data:`planning_poker.constants.FIBONACCI_CHOICES` or ``None``.
    story_points = models.PositiveSmallIntegerField(
        verbose_name=_('Story Points'),
        help_text=_('The amount of points this story takes up in the sprint'),
        null=True,
        blank=True,
        choices=[(None, '-')] + [(int(number), label) for number, label in HOUR_CHOICES]
    )
    #: The poker session to which this story belongs to.
    poker_session = models.ForeignKey(
        PokerSession, on_delete=models.SET_NULL,
        verbose_name=_('Poker Session'),
        related_name='stories',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Story')
        verbose_name_plural = _('Stories')
        order_with_respect_to = 'poker_session'
        permissions = [
            ('vote', 'Can vote for a story.'),
            ('moderate', 'Is able to moderate a planning_poker session.'),
        ]

    def __str__(self) -> str:
        if self.title:
            return '{}: {}'.format(self.ticket_number, self.title)
        return self.ticket_number

    def get_votes_with_voter_information(self) -> OrderedDictType[str, List[Dict[str, str]]]:
        """Return a sorted list with each choice + the users who voted for that choice.

        :return: A sorted list with each choice + the users who voted for that choice.
        """
        votes = defaultdict(list)
        for vote in self.votes.select_related('user'):
            votes[vote.choice].append({'id': vote.user.id, 'name': vote.user.username})
        return OrderedDict(sorted(votes.items(), key=lambda vote: len(vote[1]), reverse=True))


class Vote(models.Model):
    #: The story for which this vote was casted for.
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        verbose_name=_('Story'),
        related_name='votes'
    )
    #: The user who casted the vote.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        related_name='votes'
    )
    #: The option which was voted for. See :py:data:`planning_poker.constants.ALL_VOTING_OPTIONS` for all possible
    #: values.
    choice = models.CharField(
        max_length=200,
        verbose_name=_('Choice'),
        choices=ALL_VOTING_OPTIONS
    )

    class Meta:
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')
        constraints = [
            models.UniqueConstraint(fields=['story', 'user'], name='A user can only vote once for each story.')
        ]

    def __str__(self) -> str:
        return _('{user} voted {choice} for story {story}').format(
            user=self.user,
            choice=self.get_choice_display(),
            story=self.story
        )


class JiraConnection(models.Model):
    #: Used solely for displaying the Jira Connection to the user.
    label = models.CharField(verbose_name=_('Label'), max_length=200, blank=True)
    #: The API URL used for making requests to the Jira backend.
    api_url = models.CharField(verbose_name=_('API URL'), default='https://sjira.funkemedien.de', max_length=200)
    #: The username used for the authentication at the API.
    username = models.CharField(verbose_name=_('API Username'), max_length=200, blank=True)
    #: The password used for the authentication at the API.
    pat = fields.EncryptedCharField(verbose_name=_('Personal Access Token'), max_length=200, blank=True)
    #: The name of the field the Jira backend uses to store the story points.
    story_points_field = models.CharField(verbose_name=_('Story Points Field'), default= 'customfield_10702', max_length=200)
    

    class Meta:
        verbose_name = _('Jira Connection')
        verbose_name_plural = _('Jira Connections')

    def __str__(self) -> str:
        return self.label or self.api_url

    def get_client(self) -> JIRA:
        """Authenticate at the jira backend and return a client to communicate with it."""
        #     return JIRA(self.api_url, basic_auth=(self.username, self.password),
        # return JIRA(self.api_url, basic_auth=(self.username, self.password),
        #             timeout=getattr(settings, 'JIRA_TIMEOUT', (3.05, 7)),
        #             max_retries=getattr(settings, 'JIRA_NUM_RETRIES', 0))

        return JIRA(server = self.api_url,
                    token_auth=(self.pat),
                    timeout=getattr(settings, 'JIRA_TIMEOUT', (3.05, 7)),
                    max_retries=getattr(settings, 'JIRA_NUM_RETRIES', 0))

    def create_stories(self, query_string: str, poker_session: Optional[PokerSession] = None,
                       client: Optional[JIRA] = None) -> List[Story]:
        """Fetch issues from the Jira client with the given query string and add them to the poker session.

        :param query_string: The string which should be used to query the stories.
        :param poker_session: The poker session to which the stories should be added.
        :param client: The jira client which should be used to import the stories. Optional.
        :return: A list containing the created stories.
        """

        results = (client or self.get_client()).search_issues(
            jql_str=query_string,
            expand='renderedFields',
            fields=['summary', 'description']
        )
        order_start = getattr(poker_session.stories.last(), '_order', -1) + 1 if poker_session else 0
        stories = [Story(
            ticket_number=story.key, title=story.fields.summary,
            description=story.renderedFields.description, poker_session=poker_session,
            _order=index
        ) for index, story in enumerate(results, start=order_start)]
        return Story.objects.bulk_create(stories)

    def get_epics(self, client: Optional[JIRA] = None) -> List[Story]:
        """Fetch issues from the Jira client with the given query string and add them to the poker session.

        :param query_string: The string which should be used to query the stories.
        :param poker_session: The poker session to which the stories should be added.
        :param client: The jira client which should be used to import the stories. Optional.
        :return: A list containing the created stories.
        """

        results = (client or self.get_client()).search_issues(
            jql_str='project = "DATAAS - Data Audience and Subscription" AND issuetype = "Epos" AND updated >= startOfDay(-14d)',
        )
        issue_keys = [(issue.fields.customfield_10706, issue.fields.customfield_10706) for issue in results]
        no_epic = ('ohne Epic', 'ohne Epic')
        issue_keys.append(no_epic)
        return tuple(issue_keys)
