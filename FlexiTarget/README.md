# FlexiTarget

A first Streamlit prototype for a flexible Class 12 daily study planner.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Files you can edit

- `app.py`: sign-in screen.
- `pages/student_info.py`: student profile and goal setup.
- `pages/planner.py`: daily to-do screen, hour adjustment, extra tasks and progress submission.
- `tasks.py`: **edit this file to add, remove or change daily tasks and resource links.**
- `info.py`: product information page.

## Important prototype limitations

The sign-in screen is a demo gate, not secure authentication. Data and progress are stored in Streamlit session state and may be lost when the session ends. There is no permanent user database yet. The task list is sample content, not an automatically generated syllabus plan. Replace the sample tasks and links in `tasks.py` with verified chapter-specific content before giving this to students.

For a production launch, add proper authentication and a database such as Supabase or Firebase, then build syllabus-aware task generation.
