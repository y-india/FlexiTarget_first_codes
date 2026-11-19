"""
EDIT THIS FILE TO CHANGE THE DEFAULT DAILY TASKS.

Each task is a dictionary with:
- subject: subject name
- title: what the student should do
- minutes: estimated time
- url: optional trusted resource link

Replace the sample links with links to the exact videos or official resources
you want your students to use. These are editable starter examples.
"""

DAY_1_TASKS = [
    {
        "subject": "Accountancy",
        "title": "Revise one topic from your current chapter and solve 10 questions.",
        "minutes": 60,
        "url": "https://www.cbse.gov.in/"
    },
    {
        "subject": "Economics",
        "title": "Watch one concept video for a topic you have not fully understood.",
        "minutes": 45,
        "url": "https://www.youtube.com/"
    },
    {
        "subject": "Business Studies",
        "title": "Read one section of your current chapter and make short notes.",
        "minutes": 45,
        "url": "https://ncert.nic.in/"
    },
    {
        "subject": "English",
        "title": "Practise one writing question or solve 5 questions from a literature chapter.",
        "minutes": 40,
        "url": "https://cbseacademic.nic.in/"
    },
    {
        "subject": "Mathematics",
        "title": "Solve 10 questions from a topic you are currently studying.",
        "minutes": 60,
        "url": "https://ncert.nic.in/"
    },
]

# Optional additional tasks shown when the student asks for more work.
EXTRA_TASKS = [
    {"subject": "Revision", "title": "Revise yesterday's notes for 20 minutes.", "minutes": 20, "url": ""},
    {"subject": "Practice", "title": "Solve 5 extra questions from your weakest subject.", "minutes": 25, "url": ""},
    {"subject": "Testing", "title": "Attempt a short timed test and mark your mistakes.", "minutes": 30, "url": ""},
]
