from app.categories.constants import Category
from flask_babel import lazy_gettext as _

ADOPTING = Category(
    title=_("Adopting a child from outside the UK"),
    description=_("Adoption processes in the courts."),
    article_category_name="Family",
    chs_code="family",
    code="adopting",
    exit_page=False,
)
WORK_WITH_VULNERABLE = Category(
    title=_(
        "Appeal a decision that you cannot work with children or vulnerable adults"
    ),
    description=_(
        "Including if you’re on a ‘barred list’ or disqualified from teaching."
    ),
    code="work_with_vulnerable",
    exit_page=False,
)
CLINICAL_NEGLIGENCE = Category(
    title=_("Clinical negligence in babies"),
    description=_(
        "Help if a baby has brain or nerve damage caused during pregnancy, childbirth or up to 8 weeks old."
    ),
    article_category_name="Clinical Negligence",
    code="clinical_negligence",
    exit_page=False,
)
COMPENSATION = Category(
    title=_("Compensation for abuse, assault or neglect"),
    description=_(
        "Includes child abuse, sexual assault, abuse of a vulnerable adult. Claims can be against a person or an organisation."
    ),
    code="compensation",
    exit_page=False,
)
ENVIRONMENTAL_POLLUTION = Category(
    title=_("Environmental pollution"),
    description=_(
        "Issues about air, water or land pollution that is harming you or the environment."
    ),
    article_category_name="Public",
    chs_code="publiclaw",
    code="environmental_pollution",
    exit_page=False,
)
INQUEST = Category(
    title=_("Inquests for family members"),
    description=_("Advice to prepare for the inquest of a family member."),
    code="inquest",
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
    code="crime_act",
    exit_page=False,
)
TERRORISM = Category(
    title=_("Terrorism"),
    description=_("If you’re accused of terrorism or financing terrorist groups."),
    chs_code="immigration",
    code="terrorism",
    article_category_name="Terrorism",
)
TRAFFICKING = Category(
    title=_("Trafficking, modern slavery"),
    description=_("Help if you’re a victim of human trafficking or modern slavery."),
    chs_code="immigration",
    code="tracking_modern_slavery",
    article_category_name="Trafficking, Modern Slavery",
)
