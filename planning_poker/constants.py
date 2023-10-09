from django.utils.translation import gettext_lazy as _

#: The options for a story's possible points.
FIBONACCI_CHOICES = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('5', '5'),
    ('8', '8'),
    ('13', '13'),
    ('21', '21'),
    ('34', '34'),
]

HOUR_CHOICES = [
    ('1', '1'),
    ('2', '2'),
    ('4', '4'),
    ('8', '8'),
    ('16', '16'),
    ('24', '24'),
]


#: The value which represents the story's scope being too large.
TOO_LARGE = 'Too large (89)'
#: The value which represents a voter not being able to estimate a story's scope.
NO_IDEA = 'No idea (?)'

#: The options which voters can choose, but are not valid story point options.
NON_POINT_OPTIONS = [
    (TOO_LARGE, _('Too large (89)')),
    (NO_IDEA, _('No idea (?)'))
]

#: All the options a voter has when voting.
ALL_VOTING_OPTIONS = FIBONACCI_CHOICES + NON_POINT_OPTIONS + HOUR_CHOICES
