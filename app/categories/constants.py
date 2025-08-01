from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from flask_babel import lazy_gettext as _, LazyString


class FinancialAssessmentStatus(str, Enum):
    PASSED: str = "PASSED"
    FAILED: str = "FAILED"
    FAST_TRACK: str = "FAST_TRACK"
    SKIPPED: str = "SKIPPED"


class FinancialAssessmentReason(str, Enum):
    HARM: str = "HARM"
    MORE_INFO_REQUIRED: str = "MORE_INFO_REQUIRED"
    OTHER: str = "OTHER"

    @classmethod
    def get_reason_from_str(cls, reason: str) -> str:
        reasons = {
            "HARM": cls.HARM,
            "MORE-INFO-REQUIRED": cls.MORE_INFO_REQUIRED,
            "OTHER": cls.OTHER,
        }
        return reasons.get(reason.upper(), cls.OTHER)


@dataclass
class Category:
    title: LazyString
    description: LazyString
    article_category_name: Optional[str] = None
    # One of legalaid_categories.code
    chs_code: Optional[str] = None
    # Internal code
    code: Optional[str] = None
    in_scope: Optional[bool] = None
    children: dict[str, "Category"] | None = field(default_factory=dict)
    parent_code: Optional[str] = None
    _referrer_text: Optional[LazyString] = None
    eligible_for_HLPAS: bool = False
    exit_page: Optional[bool] = None

    @property
    def url_friendly_name(self):
        return self.code.replace("_", "-").lower()

    @property
    def display_text(self):
        return self.title

    @property
    def sub(self):
        # Allows you to do category_object.sub.sub_category
        class Subcategory:
            def __init__(self, category):
                self.children: dict[str, Category] = category.children
                self.category: Category = category

            def __getattr__(self, item):
                if item not in self.children:
                    raise AttributeError(f"Could not find {item} in category {self.category.title}")
                return self.children.get(item)

        return Subcategory(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        data = data.copy()
        children = {}
        if "children" in data:
            children: dict = data.pop("children")
        category = cls(**data)
        if children:
            for name, child in children.items():
                category.children[name] = Category(**child)
        return category

    @property
    def referrer_text(self):
        return self._referrer_text or self.title

    @referrer_text.setter
    def referrer_text(self, value):
        self._referrer_text = value

    def __str__(self):
        # Returns the translated display text
        return str(self.display_text)


# Categories definition
DOMESTIC_ABUSE = Category(
    title=_("Domestic abuse"),
    description=_(
        "Includes controlling behaviour, emotional abuse, or if someone is harassing, threatening or hurting you or a child. This could be a partner, ex-partner, or family member."
    ),
    article_category_name="Domestic Abuse",
    chs_code="family",
    code="domestic_abuse",
    exit_page=True,
    in_scope=True,
    children={
        "protect_you_and_your_children": Category(
            title=_("Help to keep yourself safe and protect children"),
            description=_(
                "Includes keeping you or your family safe, getting court orders and help if someone is ignoring a court order. Also, if you’re being stalked, threatened or harassed."
            ),
            code="protect_you_and_your_children",
            in_scope=True,
        ),
        "leaving_an_abusive_relationship": Category(
            title=_("Leaving an abusive relationship"),
            description=_(
                "Help with divorce, separation, or leaving your partner. Includes legal arrangements for children, money and housing."
            ),
            code="leaving_an_abusive_relationship",
            in_scope=True,
        ),
        "problems_with_ex_partner": Category(
            title=_("Problems with an ex-partner: children or money"),
            description=_(
                "Includes arrangements for children and money. If an ex-partner is not following agreements or court orders. If you’re worried about a child, or if a child is taken or kept without your permission."
            ),
            code="problems_with_ex_partner",
            in_scope=True,
        ),
        "housing_homelessness_losing_home": Category(
            title=_("Housing, homelessness, losing your home"),
            description=_(
                "Includes being forced to leave your home, problems with council housing, if you’re homeless or might be homeless in the next 2 months."
            ),
            code="housing_homelessness_losing_home",
        ),
        "forced_marriage": Category(
            title=_("Forced Marriage"),
            description=_("Help with forced marriage and Forced Marriage Protection Orders."),
            code="forced_marriage",
            in_scope=True,
        ),
        "fgm": Category(
            title=_("Female genital mutilation (FGM)"),
            description=_("If you or someone else is at risk of FGM."),
            code="fgm",
            in_scope=True,
        ),
        "accused_of_domestic_abuse": Category(
            title=_("Domestic abuse - if you have been accused"),
            description=_(
                "Legal help if you’ve been accused of domestic abuse or forced marriage. Includes non-molestation orders and other court orders."
            ),
            code="accused_of_domestic_abuse",
            exit_page=False,
            in_scope=True,
        ),
    },
)

FAMILY = Category(
    title=_("Children, families, relationships"),
    description=_(
        "Includes children in care, children and social services. Also, help with children and finances if you divorce or split up."
    ),
    article_category_name="Family",
    chs_code="family",
    code="family",
    children={
        "social_services": Category(
            title=_("Children and social services, children in care"),
            description=_(
                "Help for any problem if social services are involved with a child. Includes children in care, or being adopted. Also special guardianship."
            ),
            code="social_services",
            in_scope=True,
        ),
        "divorce": Category(
            title=_("Problems with an ex-partner, divorce, when a relationship ends"),
            description=_(
                "If you cannot agree about money, finances and property. Includes contact with children, where children live, and other child arrangements. If an ex-partner is not doing what they agreed. If you’re worried about a child."
            ),
            code="divorce",
            in_scope=True,
        ),
        "domestic_abuse": Category(
            title=_("If there is domestic abuse in your family"),
            description=_(
                "Making arrangements for children and finances. Also, keeping yourself safe, protecting children and legal help to leave the relationship."
            ),
            code="domestic_abuse",
            in_scope=True,
        ),
        "family_mediation": Category(
            title=_("Family mediation"),
            description=_(
                "Help to cover the costs of family mediation (solve problems about money and children before you go to court)."
            ),
            code="family_mediation",
            in_scope=True,
        ),
        "child_abducted": Category(
            title=_("Child taken without your consent"),
            description=_("If a child has been abducted (taken without your permission), including outside the UK."),
            code="child_abducted",
            in_scope=True,
        ),
        "send": Category(
            title=_("Children with special educational needs and disabilities (SEND)"),
            description=_("Get help with a child’s SEND."),
            code="send",
        ),
        "education": Category(
            title=_("Schools, colleges, other education settings"),
            description=_(
                "Advice about legal action against a school. Includes if a child is out of school, exclusions, transport to school, judicial reviews."
            ),
            code="education",
            in_scope=True,
        ),
        "forced_marriage": Category(
            title=_("Forced marriage"),
            description=_("Help with forced marriage and Forced Marriage Protection Orders."),
            code="forced_marriage",
        ),
    },
)

HOUSING = Category(
    title=_("Housing, homelessness, losing your home"),
    description=_(
        "Includes being evicted or forced to sell your home. Problems with landlords, repairs, neighbours or council housing."
    ),
    article_category_name="Housing",
    chs_code="housing",
    code="housing",
    children={
        "homelessness": Category(
            title=_("Homelessness"),
            description=_(
                "Help if you’re homeless, or might be homeless in the next 2 months. This could be because of rent arrears, debt, the end of a relationship, or because you have nowhere to live."
            ),
            code="homelessness",
            in_scope=True,
            eligible_for_HLPAS=True,
        ),
        "eviction": Category(
            title=_("Eviction, told to leave your home"),
            description=_(
                "Landlord has told you to leave or is trying to force you to leave. Includes if you’ve got a Section 21 or a possession order."
            ),
            code="eviction",
            in_scope=True,
            eligible_for_HLPAS=True,
        ),
        "forced_to_sell": Category(
            title=_("Forced to sell or losing the home you own"),
            description=_(
                "Repossession by your mortgage company; bankruptcy or other debt that means you will lose the home you own."
            ),
            code="forced_to_sell",
            in_scope=True,
            eligible_for_HLPAS=True,
        ),
        "repairs": Category(
            title=_("Repairs, health and safety"),
            description=_(
                "If your house is not safe to live in, or needs repairs, and this is causing health or safety problems."
            ),
            code="repairs",
            in_scope=True,
        ),
        "council_housing": Category(
            title=_("Problems with council housing"),
            description=_(
                "Help to challenge the council’s decision about giving you housing. It includes if the council has offered a house that is not right for you, or that needs repairs or adaptations."
            ),
            code="council_housing",
            in_scope=True,
        ),
        "threatened": Category(
            title=_("Being threatened or harassed where you live"),
            description=_("By a landlord, neighbour or someone else."),
            code="threatened",
            in_scope=True,
        ),
        "asylum_seeker": Category(
            title=_("If you’re an asylum-seeker"),
            description=_("Applying for housing, losing your housing or homelessness."),
            code="asylum_seeker",
            in_scope=True,
        ),
        "discrimination": Category(
            title=_("Discrimination"),
            description=_("Treated unfairly by a landlord, council or housing association."),
            code="discrimination",
        ),
        "antisocial_behaviour": Category(
            title=_("If you’ve been accused of anti-social behaviour"),
            description=_("Accused of anti-social behaviour by the landlord, council or housing association."),
            code="antisocial_behaviour",
            in_scope=True,
        ),
        "antisocial_behaviour_gangs": Category(
            title=_("Anti-social behaviour and gangs"),
            description=_("If you’re accused or taken to court for anti-social behaviour, including being in a gang."),
            code="antisocial_behaviour_gangs",
            in_scope=True,
        ),
        "problems_with_neighbours": Category(
            title=_("Problems with neighbours, landlords or other people"),
            description=_("Threats, abuse or harassment by someone who is not a family member."),
            code="problems_with_neighbours",
            in_scope=True,
        ),
    },
)

DISCRIMINATION = Category(
    title=_("Discrimination"),
    description=_(
        "Treated unfairly because of things like your disability or health condition, race, age, sex, religion or pregnancy."
    ),
    article_category_name="Discrimination",
    chs_code="discrimination",
    code="discrimination",
    in_scope=True,
)

EDUCATION = Category(
    title=_("Special educational needs and disability (SEND)"),
    description=_("Help if your child has SEND."),
    article_category_name="Education",
    chs_code="education",
    code="send",
    children={
        "child_young_person": Category(
            title=_("Help with a child or young person's SEND"),
            description=_(
                "Help with schools, other education settings and local authorities. Includes help with education, health and care plans (EHCP) or if a child’s needs are not being met."
            ),
            code="child_young_person",
            in_scope=True,
        ),
        "tribunals": Category(
            title=_("SEND tribunals"),
            description=_("Applying for or going to a SEND tribunal, appealing a decision by a tribunal."),
            code="tribunals",
            in_scope=True,
        ),
        "discrimination": Category(
            title=_("Child treated unfairly at school, discrimination"),
            description=_(
                "If a child is treated unfairly at school because of their disability. Or if you were treated badly for complaining about this."
            ),
            code="discrimination",
            in_scope=True,
        ),
        "schools": Category(
            title=_("Other problems with schools"),
            description=_(
                "Advice about legal action against a school. Includes if a child is out of school, exclusions, transport to school, judicial reviews."
            ),
            code="schools",
            in_scope=True,
        ),
        "care": Category(
            title=_("Care needs for disability (social care)"),
            description=_(
                "Problems getting the local authority or council to provide or pay for the right care. For carers, children, young people and adults."
            ),
            code="care",
        ),
    },
)

COMMUNITY_CARE = Category(
    title=_("Care needs for disability and old age (social care)"),
    description=_(
        "Problems getting the local authority or council to provide or pay for the right care. For carers, children, young people and adults."
    ),
    article_category_name="Community care",
    chs_code="commcare",
    code="community_care",
    children={
        "care_from_council": Category(
            title=_("Care from the council (local authority)"),
            description=_(
                "Includes problems with care needs assessments, financial assessments and care support plans. Getting an advocate for assessments. Problems with transport, personal budgets and direct payments."
            ),
            code="care_from_council",
        ),
        "carer": Category(
            title=_("If you’re a carer"),
            description=_(
                "Includes problems with carer’s assessments and respite care. Problems to do with making decisions about someone’s care."
            ),
            code="carer",
        ),
        "receive_care_in_own_home": Category(
            title=_("If you receive care in your own home"),
            description=_(
                "Problems with care providers, social workers, care agencies. Also getting adaptations and disabled facilities grants."
            ),
            code="receive_care_in_own_home",
        ),
        "care_or_funding_stops": Category(
            title=_("If care or funding stops"),
            description=_("Problems if care or money for care is stopped or reduced, or if care facilities close."),
            code="care_or_funding_stops",
        ),
        "placement_care_homes_care_housing": Category(
            title=_("Placements, care homes and care housing"),
            description=_(
                "Problems with placements in care homes, group homes or other supported housing. If a placement isn't working because someone's care needs have changed."
            ),
            code="placement_care_homes_care_housing",
        ),
        "problems_with_quality_of_care": Category(
            title=_("Problems with the quality of care, safeguarding"),
            description=_(
                "Issues with safeguarding, abuse, neglect, or care that is not good enough. This includes in group homes or other placements, or from a carer or social worker."
            ),
            code="problems_with_quality_of_care",
        ),
        "care_leaver": Category(
            title=_("If you’re a care leaver"),
            description=_(
                "Problems if the local authority is not providing the right support. Includes problems with housing, financial support, education, personal advisers and Pathway Plans."
            ),
            code="care_leaver",
        ),
    },
)

BENEFITS = Category(
    title=_("Benefits"),
    _referrer_text=_("Welfare benefits"),
    description=_("Appeal a decision about your benefits."),
    article_category_name="Welfare benefits",
    chs_code="benefits",
    code="benefits",
)

PUBLIC_LAW = Category(
    title=_("Legal action against police and public organisations"),
    description=_("Includes police, government, prisons, NHS, the council, care facilities and schools."),
    article_category_name="Public",
    chs_code="publiclaw",
    code="public_law",
)

ASYLUM_AND_IMMIGRATION = Category(
    title=_("Asylum and immigration"),
    description=_("Help if you’re seeking asylum. Help to stay in the UK if you experienced domestic abuse."),
    chs_code="immigration",
    code="asylum_and_immigration",
    article_category_name="Immigration and asylum",
    children={
        "apply": Category(
            title=_("Applying for asylum"),
            description=_("Help to apply for asylum, go to asylum interviews, or appeal an asylum decision."),
            code="apply",
        ),
        "housing": Category(
            title=_("Housing and homelessness"),
            description=_("Help to apply for housing, problems with housing or if you are homeless."),
            code="housing",
            in_scope=True,
            eligible_for_HLPAS=True,
        ),
        "domestic_abuse": Category(
            title=_("Stay in the UK if you experienced domestic abuse"),
            description=_(
                "Help to remain in the UK or EU if your relationship ended because of domestic abuse. This could be by a partner, ex-partner or family member."
            ),
            code="domestic_abuse",
        ),
        "detained": Category(
            title=_("Help if you’re being detained"),
            description=_(
                "Help if you’re in immigration detention, including if you want to apply for bail. Help if you’re in prison."
            ),
            code="detained",
        ),
        "modern_slavery": Category(
            title=_("Trafficking, modern slavery"),
            description=_("Help if you’re a victim of trafficking or modern slavery."),
            code="modern_slavery",
        ),
    },
)

MENTAL_CAPACITY = Category(
    title=_("Mental capacity, mental health"),
    description=_(
        "Help if someone cannot make decisions about their health, day-to-day life or care. Help at mental health tribunals."
    ),
    article_category_name="Mental health",
    chs_code="mentalhealth",
    code="mental_health",
    children={
        "mental_capacity": Category(
            title=_("If someone cannot decide for themselves (lacks mental capacity)"),
            description=_(
                "Help to challenge a decision made about someone’s living arrangements, care, health, relationships, family contact or finances. Includes if someone is deprived of their liberty, and ‘deprivation of liberty safeguards’ (DoLS)."
            ),
            code="mental_capacity",
        ),
        "court_of_protection": Category(
            title=_("Court of Protection"),
            description=_("Advice about issues covered by the Court of Protection."),
            code="court_of_protection",
        ),
        "detention": Category(
            title=_("Mental health detention and tribunals"),
            description=_(
                "Help if someone has been sectioned (held in a mental health hospital), or is under a community treatment order. Help with mental health tribunals."
            ),
            code="detention",
        ),
        "social_care": Category(
            title=_("Care needs for disability and old age (social care)"),
            description=_(
                "Problems getting the local authority or council to provide or pay for the right care. For carers, children, young people and adults."
            ),
            code="social_care",
        ),
    },
)
ADOPTING = Category(
    title=_("Adopting a child from outside the UK"),
    description=_("Adoption processes in the courts."),
    article_category_name="Family",
    chs_code="family",
    code="adopting",
    exit_page=False,
)
WORK_WITH_VULNERABLE = Category(
    title=_("Appeal a decision that you cannot work with children or vulnerable adults"),
    description=_("Including if you’re on a ‘barred list’ or disqualified from teaching."),
    code="work_with_vulnerable",
    exit_page=False,
)
CLINICAL_NEGLIGENCE = Category(
    title=_("Clinical negligence in babies"),
    description=_("Help if a baby has brain or nerve damage caused during pregnancy, childbirth or up to 8 weeks old."),
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
    description=_("Issues about air, water or land pollution that is harming you or the environment."),
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
MENTAL_HEALTH_DETENTION = Category(
    title=_("Mental health detention"),
    description=_(
        "Help if you’re held in hospital (‘sectioned’), mental health tribunals and community treatment orders."
    ),
    article_category_name="Mental health",
    chs_code="mentalhealth",
    code="mental_health_detention",
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


def init_children(category: Category) -> None:
    for child in category.children.values():
        child.chs_code = child.chs_code or category.chs_code
        child.parent_code = category.code
        child.article_category_name = child.article_category_name or category.article_category_name
        child.exit_page = child.exit_page if child.exit_page is not None else category.exit_page


ALL_CATEGORIES = {
    DOMESTIC_ABUSE.code: DOMESTIC_ABUSE,
    FAMILY.code: FAMILY,
    HOUSING.code: HOUSING,
    DISCRIMINATION.code: DISCRIMINATION,
    EDUCATION.code: EDUCATION,
    COMMUNITY_CARE.code: COMMUNITY_CARE,
    BENEFITS.code: BENEFITS,
    PUBLIC_LAW.code: PUBLIC_LAW,
    ASYLUM_AND_IMMIGRATION.code: ASYLUM_AND_IMMIGRATION,
    MENTAL_CAPACITY.code: MENTAL_CAPACITY,
    ADOPTING.code: ADOPTING,
    WORK_WITH_VULNERABLE.code: WORK_WITH_VULNERABLE,
    CLINICAL_NEGLIGENCE.code: CLINICAL_NEGLIGENCE,
    COMPENSATION.code: COMPENSATION,
    ENVIRONMENTAL_POLLUTION.code: ENVIRONMENTAL_POLLUTION,
    INQUEST.code: INQUEST,
    MENTAL_HEALTH_DETENTION.code: MENTAL_HEALTH_DETENTION,
    CRIME_ACT.code: CRIME_ACT,
    TERRORISM.code: TERRORISM,
    TRAFFICKING.code: TRAFFICKING,
}

list(map(init_children, ALL_CATEGORIES.values()))


def get_category_from_code(code: str) -> Category | None:
    if not code:
        return None
    try:
        return ALL_CATEGORIES[code]
    except KeyError:
        raise ValueError(f"{code} is an invalid category code.")


def get_subcategory_from_code(parent_code: str, code: str) -> Category | None:
    if not parent_code or not code:
        return None
    try:
        return get_category_from_code(parent_code).children[code]
    except KeyError:
        raise ValueError(f"{code} is an invalid subcategory code for {parent_code}.")
