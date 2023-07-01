# CallTime

CallTime is a web app created with the Django framework that allows for easily creating daily schedules for performing artists and stage managers.

The site is up and running on a cloud server. To test out the web app follow this link and start making schedules!
https://dylanelza.pythonanywhere.com/getdata/home/

Video Demo: https://youtu.be/Jsc_MZOkz2A

Features:
- Two account types: Artist and Company
- Company accounts can create Shows, Roles, Call Blocks (Schedules), Conflicts for Artists, Staff members, Venues with addresses for rehearsal and performance locations
- Company accounts can upload Documents for Artists to view - files are stored in a secure google drive for space management
- API endpoints for all CRUD operations for each table
- Artist accounts can be linked to Company accounts in order to view relevant schedules
- **_Pdf can be automatically generated from schedule data, and emailed to all Artists and Staff emails linked to the Company account at the push of a button_**
- Company accounts can send mass emails to Artists and Staff linked to Company
- Company accounts can create Categories to assign to Artist roles for quick selection later when making schedules and scheduling Artists
- Artist profile allows for basic user setting changes like email and phone number privacy
- Artist profile shows user-specific schedule information and an option to view the full schedule
- **_When creating a schedule, if a date is selected that is the same day as an Artist Conflict, a modal will immediately display, showing all Artists with a schedule conflict on that day_**
- QR code for mobile app

