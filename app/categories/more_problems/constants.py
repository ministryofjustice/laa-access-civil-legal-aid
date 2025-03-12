from app.categories.constants import Category
from flask_babel import lazy_gettext as _

ADOPTING = Category(
    title=_("Adopting a child from outside the UK"),
    description=_("Adoption processes in the courts."),
    article_category_name="Family",
    chs_code="family",
    code="family",
    exit_page=False,
)
WORK_WITH_VULNERABLE = Category(
    title=_(
        "Appeal a decision that you cannot work with children or vulnerable adults"
    ),
    description=_(
        "Including if you’re on a ‘barred list’ or disqualified from teaching."
    ),
    exit_page=False,
)
ANTI_SOCIAL = Category(
    title=_("Anti-social behaviour and gangs"),
    description=_(
        "If you’re accused or taken to court for anti-social behaviour, including being in a gang."
    ),
    exit_page=False,
)
CLINICAL_NEGLIGENCE = Category(
    title=_("Clinical negligence in babies"),
    description=_(
        "Help if a baby has brain or nerve damage caused during pregnancy, childbirth or up to 8 weeks old."
    ),
    article_category_name="Clinical Negligence",
    exit_page=False,
)
COMPENSATION = Category(
    title=_("Compensation for abuse, assault or neglect"),
    description=_(
        "Includes child abuse, sexual assault, abuse of a vulnerable adult. Claims can be against a person or an organisation."
    ),
    exit_page=False,
)
ACCUSED_DA = Category(
    title=_("Domestic abuse - if you have been accused"),
    description=_(
        "Legal help if you’ve been accused of domestic abuse or forced marriage. Includes non-molestation orders and other court orders."
    ),
    article_category_name="Domestic Abuse",
    chs_code="family",
    code="domestic_abuse",
    exit_page=True,
)
ENVIRONMENTAL_POLLUTION = Category(
    title=_("Environmental pollution"),
    description=_(
        "Issues about air, water or land pollution that is harming you or the environment."
    ),
    article_category_name="Public",
    chs_code="publiclaw",
    code="public_law",
    exit_page=False,
)
FGM = Category(
    title=_("Female genital mutilation (FGM)"),
    description=_("If you or someone else is at risk of FGM"),
    article_category_name="Domestic Abuse",
    chs_code="family",
    code="domestic_abuse",
    exit_page=True,
)
FORCED_MARRIAGE = Category(
    title=_("Forced marriage"),
    description=_("Help with forced marriage and Forced Marriage Protection Orders."),
    article_category_name="Domestic Abuse",
    chs_code="family",
    code="domestic_abuse",
    exit_page=True,
)
INQUEST = Category(
    title=_("Inquests for family members"),
    description=_("Advice to prepare for the inquest of a family member."),
    exit_page=False,
)
MENTAL_HEALTH = Category(
    title=_("Mental health detention"),
    description=_(
        "Help if you’re held in hospital (‘sectioned’), mental health tribunals and community treatment orders."
    ),
    article_category_name="Mental health",
    chs_code="mentalhealth",
    code="mental_health",
    exit_page=False,
)
CRIME_ACT = Category(
    title=_("Proceeds of Crime Act"),
    description=_("If you’re facing legal action to take your money or other assets."),
    exit_page=False,
)
TERRORISM = Category(
    title=_("Terrorism"),
    description=_("If you’re accused of terrorism or financing terrorist groups."),
    chs_code="immigration",
    code="asylum_and_immigration",
    article_category_name="Terrorism",
)
TRAFFICKING = Category(
    title=_("Trafficking, modern slavery"),
    description=_("Help if you’re a victim of human trafficking or modern slavery."),
    chs_code="immigration",
    code="asylum_and_immigration",
    article_category_name="Trafficking, Modern Slavery",
)
