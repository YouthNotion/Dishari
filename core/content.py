"""All website copy and contact details, in one place.

The site has no database yet: edit this file to change what the pages show.
The dataclasses mirror the shape a future admin-editable model would take, so
moving to the database later is a mechanical change.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Organisation:
    name: str
    tagline: str
    established_year: int
    location: str
    mission: str
    summary: str  # one sentence for link previews and search results (~150 chars)
    hero_phrases: tuple[str, ...]
    phone: str  # display format
    email: str
    address: str
    facebook_url: str

    @property
    def phone_e164(self) -> str:
        """Digits with a leading +, e.g. +8801864272727 (for tel: links)."""
        return "+" + "".join(ch for ch in self.phone if ch.isdigit())

    @property
    def whatsapp_url(self) -> str:
        return "https://wa.me/" + self.phone_e164.removeprefix("+")


@dataclass(frozen=True, slots=True)
class ServiceArea:
    title: str
    icon: str  # name from core/templatetags/site_tags.py
    items: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Project:
    name: str
    beneficiaries: str
    provisions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Training:
    title: str
    image: str  # path under static/
    image_alt: str
    description: str


ORGANISATION = Organisation(
    name="Dishari",
    tagline="Dream of New Earth",
    established_year=2001,
    location="Noakhali, Bangladesh",
    mission=(
        "Dishari is a nonprofit and nonpolitical organisation working to raise social "
        "awareness, provide rehabilitation, medical attention, education, legal aid and "
        "training to abandoned children and helpless women, build youth capacity, and "
        "nurture the next generation of leaders for a socially inclusive and economically "
        "sustainable Bangladesh."
    ),
    summary=(
        "Dishari provides shelter, care, education and skills training for abandoned "
        "children and vulnerable women in Noakhali, Bangladesh, since 2001."
    ),
    hero_phrases=(
        "education for children",
        "employment for women",
        "shelter for the elderly",
    ),
    phone="+880 1864-272727",
    email="dishari.org2023@gmail.com",
    address=(
        "Momotaj Moholl, Road No. 8, House No. 1, Maijdee Housing Estate, "
        "Maijdee Court, Noakhali, Bangladesh"
    ),
    facebook_url="https://www.facebook.com/share/1FNyF5h8Qc/",
)

SERVICE_AREAS: tuple[ServiceArea, ...] = (
    ServiceArea(
        title="Legal activities",
        icon="law",
        items=(
            "Support for socially disadvantaged groups",
            "Environmental protection legislation",
            "Combating trafficking of women and children",
            "Legal apprenticeship",
        ),
    ),
    ServiceArea(
        title="Environmental initiatives",
        icon="environment",
        items=("Afforestation", "Agriculture", "Environmental hygiene"),
    ),
    ServiceArea(
        title="Women and children",
        icon="people",
        items=("Project Sandhyatara", "Project Aparajita", "Project Suktara"),
    ),
)

PROJECTS: tuple[Project, ...] = (
    Project(
        name="Project Sandhyatara",
        beneficiaries="Homeless and abandoned orphans under 18 years of age.",
        provisions=("Food", "Clothing", "Shelter", "Healthcare", "Legal aid", "Education"),
    ),
    Project(
        name="Project Aparajita",
        beneficiaries=(
            "Homeless, divorced, widowed and autistic women, and survivors of acid attacks, "
            "aged roughly 18 to 50 and able to work."
        ),
        provisions=(
            "Food",
            "Clothing",
            "Shelter",
            "Healthcare",
            "Legal aid",
            "Training",
            "Employment",
        ),
    ),
    Project(
        name="Project Suktara",
        beneficiaries="Homeless and helpless elderly women over 50 who are unable to work.",
        provisions=("Food", "Clothing", "Shelter", "Healthcare", "Legal aid"),
    ),
)

_HANDCRAFTED = "Handcrafted · Made in Bangladesh"
_FARMING = "Sustainable farming skills"

TRAININGS: tuple[Training, ...] = (
    Training(
        title="Baby frock cutting and stitching",
        image="img/training/baby-frock-cutting-and-stitching.jpg",
        image_alt="Display of handmade baby frocks made by trainees",
        description=_HANDCRAFTED,
    ),
    Training(
        title="Hand embroidery",
        image="img/training/hand-embroidery.jpg",
        image_alt="Young women practising hand embroidery together",
        description=_HANDCRAFTED,
    ),
    Training(
        title="Sewing",
        image="img/training/sewing.jpg",
        image_alt="Women at an outdoor sewing training session",
        description=_HANDCRAFTED,
    ),
    Training(
        title="Agriculture: homestead gardening",
        image="img/training/agriculture-1.jpg",
        image_alt="Fruit and vegetable plants in a homestead garden",
        description=_FARMING,
    ),
    Training(
        title="Agriculture: vegetable beds",
        image="img/training/agriculture-2.jpg",
        image_alt="Rows of vegetable beds between trees",
        description=_FARMING,
    ),
    Training(
        title="Agriculture: gourd cultivation",
        image="img/training/agriculture-3.jpg",
        image_alt="Gourd plant with a growing fruit",
        description=_FARMING,
    ),
)
