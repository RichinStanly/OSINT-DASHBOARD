"""
Demo mode data.

Provides a small, realistic, hand-crafted investigation so the app can be
demonstrated end-to-end without any network access. All content here is
clearly synthetic/illustrative and is labeled as DEMO DATA everywhere it
appears in the UI. The subject used, "Aurora Robotics" (a fictional
public technology company), is invented specifically to avoid presenting
fabricated claims about any real entity.
"""
from __future__ import annotations

import datetime as dt

DEMO_SUBJECT = "Aurora Robotics (Demo)"

DEMO_SOURCES = [
    {
        "title": "Aurora Robotics - Wikipedia",
        "url": "https://en.wikipedia.org/wiki/Aurora_Robotics_(demo)",
        "domain": "en.wikipedia.org",
        "source_type": "wikipedia",
        "published_at": None,
        "raw_text": (
            "Aurora Robotics is a fictional robotics and automation company founded in 2016 "
            "and headquartered in Austin, Texas. The company is known for its warehouse "
            "automation platform, Aurora Fleet, which competes with systems from Boston "
            "Dynamics and Fetch Robotics. In March 2021, Aurora Robotics announced a "
            "partnership with LogiCore Systems to deploy autonomous picking robots across "
            "LogiCore's distribution centers. The company's CEO, Maria Chen, previously "
            "worked at a major cloud computing company before founding Aurora Robotics. "
            "Aurora Robotics raised a Series C funding round in 2022 led by Meridian "
            "Ventures, valuing the company at approximately 800 million dollars."
        ),
        "summary": "Overview of the fictional company Aurora Robotics, its founding, products, and leadership.",
        "relevance_score": 1.0,
    },
    {
        "title": "LogiCore and Aurora Robotics Expand Automation Partnership",
        "url": "https://example-news.com/aurora-logicore-partnership",
        "domain": "example-news.com",
        "source_type": "news",
        "published_at": dt.datetime(2022, 8, 14),
        "raw_text": (
            "In August 2022, LogiCore Systems announced an expansion of its automation "
            "partnership with Aurora Robotics, adding Aurora Fleet robots to twelve "
            "additional distribution centers. The expansion follows a successful pilot "
            "program launched in March 2021. LogiCore's Chief Operating Officer, David "
            "Park, said the partnership had reduced order fulfillment times by roughly "
            "18 percent at pilot sites. Aurora Robotics' CEO Maria Chen called the "
            "expansion a milestone for the company's growth strategy."
        ),
        "summary": "News coverage of the expanded Aurora Robotics and LogiCore partnership.",
        "relevance_score": 0.9,
    },
    {
        "title": "Aurora Robotics Raises $120M Series C Led by Meridian Ventures",
        "url": "https://example-news.com/aurora-series-c",
        "domain": "example-news.com",
        "source_type": "news",
        "published_at": dt.datetime(2022, 2, 3),
        "raw_text": (
            "Aurora Robotics announced on February 3, 2022 that it had raised a 120 "
            "million dollar Series C funding round led by Meridian Ventures, with "
            "participation from Sequoia Growth and existing investor Northbridge Capital. "
            "The funding values Aurora Robotics at approximately 800 million dollars. "
            "CEO Maria Chen said the funds would be used to expand manufacturing capacity "
            "for the Aurora Fleet platform and to grow the company's engineering team in "
            "Austin, Texas."
        ),
        "summary": "Coverage of Aurora Robotics' Series C funding round.",
        "relevance_score": 0.85,
    },
    {
        "title": "Aurora Fleet vs. Competitors: A Warehouse Automation Comparison",
        "url": "https://example-tech-review.com/aurora-fleet-comparison",
        "domain": "example-tech-review.com",
        "source_type": "web",
        "published_at": dt.datetime(2023, 5, 20),
        "raw_text": (
            "Aurora Fleet, the flagship product from Aurora Robotics, competes directly "
            "with Boston Dynamics' Stretch platform and Fetch Robotics' warehouse robots. "
            "In our testing, Aurora Fleet robots demonstrated strong performance in "
            "high-density shelving environments. Aurora Robotics has focused heavily on "
            "integration with existing warehouse management software, which several "
            "LogiCore Systems facilities have adopted since 2021. The Austin, Texas-based "
            "company continues to expand its footprint in the logistics automation sector."
        ),
        "summary": "Independent comparison of Aurora Fleet against competing warehouse robotics platforms.",
        "relevance_score": 0.7,
    },
    {
        "title": "Maria Chen Named to Robotics Industry 40 Under 40",
        "url": "https://example-industry-mag.com/maria-chen-40-under-40",
        "domain": "example-industry-mag.com",
        "source_type": "news",
        "published_at": dt.datetime(2023, 11, 9),
        "raw_text": (
            "Aurora Robotics CEO Maria Chen was named to the Robotics Industry's 40 Under "
            "40 list in November 2023, recognizing her leadership in scaling Aurora "
            "Robotics from a small startup founded in 2016 into a major warehouse "
            "automation provider. The profile notes Chen's background in cloud computing "
            "prior to founding Aurora Robotics, and highlights the company's partnership "
            "with LogiCore Systems as a key driver of its growth."
        ),
        "summary": "Industry recognition profile of Aurora Robotics CEO Maria Chen.",
        "relevance_score": 0.6,
    },
]

                                       
DEMO_ENTITIES = [
    ("Aurora Robotics", "ORG", 5),
    ("Maria Chen", "PERSON", 3),
    ("LogiCore Systems", "ORG", 3),
    ("Aurora Fleet", "PRODUCT", 3),
    ("Meridian Ventures", "ORG", 2),
    ("Austin, Texas", "LOCATION", 3),
    ("Boston Dynamics", "ORG", 2),
    ("Fetch Robotics", "ORG", 2),
    ("David Park", "PERSON", 1),
    ("Sequoia Growth", "ORG", 1),
    ("Northbridge Capital", "ORG", 1),
    ("Series C", "EVENT", 1),
]

                                                                       
DEMO_RELATIONSHIPS = [
    ("Aurora Robotics", "Maria Chen", "led_by", "confirmed", 3.0),
    ("Aurora Robotics", "Aurora Fleet", "produces", "confirmed", 3.0),
    ("Aurora Robotics", "LogiCore Systems", "partnered_with", "confirmed", 2.0),
    ("Aurora Robotics", "Meridian Ventures", "funded_by", "confirmed", 2.0),
    ("Aurora Robotics", "Austin, Texas", "headquartered_in", "confirmed", 2.0),
    ("Aurora Fleet", "Boston Dynamics", "competes_with", "inferred", 1.0),
    ("Aurora Fleet", "Fetch Robotics", "competes_with", "inferred", 1.0),
    ("LogiCore Systems", "David Park", "employs", "inferred", 1.0),
    ("Aurora Robotics", "Sequoia Growth", "funded_by", "uncertain", 0.5),
    ("Aurora Robotics", "Northbridge Capital", "funded_by", "uncertain", 0.5),
]

                                                     
DEMO_EVENTS = [
    (dt.datetime(2016, 1, 1), "Aurora Robotics is founded in Austin, Texas.", "uncertain", "Aurora Robotics - Wikipedia"),
    (dt.datetime(2021, 3, 1), "Aurora Robotics announces automation partnership with LogiCore Systems.", "inferred", "Aurora Robotics - Wikipedia"),
    (dt.datetime(2022, 2, 3), "Aurora Robotics raises $120M Series C led by Meridian Ventures.", "confirmed", "Aurora Robotics Raises $120M Series C Led by Meridian Ventures"),
    (dt.datetime(2022, 8, 14), "LogiCore and Aurora Robotics expand automation partnership to 12 more sites.", "confirmed", "LogiCore and Aurora Robotics Expand Automation Partnership"),
    (dt.datetime(2023, 5, 20), "Independent review compares Aurora Fleet to competing warehouse robots.", "confirmed", "Aurora Fleet vs. Competitors: A Warehouse Automation Comparison"),
    (dt.datetime(2023, 11, 9), "Maria Chen named to Robotics Industry 40 Under 40.", "confirmed", "Maria Chen Named to Robotics Industry 40 Under 40"),
]

                                      
DEMO_TOPICS = [
    ("Warehouse Automation", 4, ["Aurora Robotics", "Aurora Fleet", "LogiCore Systems"]),
    ("Funding & Investment", 2, ["Meridian Ventures", "Sequoia Growth", "Northbridge Capital"]),
    ("Leadership", 3, ["Maria Chen"]),
    ("Competitive Landscape", 2, ["Boston Dynamics", "Fetch Robotics"]),
    ("Logistics Partnerships", 2, ["LogiCore Systems", "David Park"]),
]

DEMO_REPORT = {
    "executive_summary": (
        "This demo investigation covers Aurora Robotics, a fictional warehouse automation "
        "company, compiled from 5 sample sources. Aurora Robotics, founded in 2016 and led "
        "by CEO Maria Chen, produces the Aurora Fleet warehouse robotics platform and has "
        "an active partnership with LogiCore Systems. The company raised a $120M Series C "
        "round in February 2022 led by Meridian Ventures."
    ),
    "key_findings": [
        "Aurora Robotics is led by CEO Maria Chen, who previously worked in cloud computing.",
        "The company's core product, Aurora Fleet, competes with Boston Dynamics and Fetch Robotics.",
        "Aurora Robotics partnered with LogiCore Systems starting in March 2021, later expanded in August 2022.",
        "A $120M Series C round led by Meridian Ventures valued the company at ~$800M in February 2022.",
        "Aurora Robotics is headquartered in Austin, Texas.",
    ],
    "major_events": [
        "2016: Aurora Robotics founded in Austin, Texas.",
        "2021-03: Partnership announced with LogiCore Systems.",
        "2022-02-03: $120M Series C round led by Meridian Ventures.",
        "2022-08-14: Partnership with LogiCore expanded to 12 additional sites.",
        "2023-11-09: CEO Maria Chen named to Robotics Industry 40 Under 40.",
    ],
    "relationships_summary": [
        "Aurora Robotics ↔ Maria Chen (led_by, confirmed)",
        "Aurora Robotics ↔ Aurora Fleet (produces, confirmed)",
        "Aurora Robotics ↔ LogiCore Systems (partnered_with, confirmed)",
        "Aurora Robotics ↔ Meridian Ventures (funded_by, confirmed)",
    ],
    "emerging_themes": [
        "Warehouse Automation (seen in 4 source(s))",
        "Leadership (seen in 3 source(s))",
        "Funding & Investment (seen in 2 source(s))",
        "Competitive Landscape (seen in 2 source(s))",
    ],
    "source_notes": (
        "5 sample sources used. 4 relationships corroborated across multiple sources; "
        "2 relationships (Sequoia Growth, Northbridge Capital funding) are based on a "
        "single mention and should be treated as weaker evidence."
    ),
    "limitations": (
        "This is DEMO DATA using a fictional company created for demonstration purposes. "
        "It illustrates the app's analysis and reporting pipeline and should not be "
        "interpreted as real information about any actual company or person."
    ),
}
