AGRINOVA – ADVANCED SMART AGRICULTURE
====================================

WINDOWS 10-এ চালানোর নিয়ম
1) ZIP ফাইলটি Extract All করে একটি ফোল্ডারে রাখো।
2) Python 3.10 বা তার নতুন সংস্করণ ইনস্টল থাকতে হবে।
   Python ইনস্টল করার সময় "Add Python to PATH" টিক দেবে।
3) Extract করা ফোল্ডারের START_WINDOWS.bat-এ ডাবল ক্লিক করো।
4) প্রথমবার ইন্টারনেট লাগবে, কারণ Flask লাইব্রেরি ইনস্টল হবে।
5) কালো Command Prompt উইন্ডো খোলা রাখবে।
6) Chrome/Edge-এ http://127.0.0.1:5000 খুলবে।
7) নিজের নাম, ইমেল ও কমপক্ষে ৮ অক্ষরের পাসওয়ার্ড দিয়ে Register করবে।
8) পরেরবার START_WINDOWS.bat চালিয়ে Login করবে।

অ্যাডমিন ডেমো অ্যাকাউন্ট
Email: admin@agrinova.local
Password: AgriNova@123
এটি শুধু লোকাল ডেমোর জন্য। প্রথমবার চালানোর পর নিজের অ্যাকাউন্ট ব্যবহার করাই ভালো।
এই ডেমো অ্যাডমিন লগইন অনলাইনে প্রকাশ করবে না।

যা যা আছে
- Login / Register / Logout
- Password hash করে SQLite database-এ সংরক্ষণ
- ব্যক্তিগত Crop & Field record
- Soil pH, moisture এবং N-P-K log
- Farm Task planner এবং Done/Pending status
- Live clock/date
- Open-Meteo থেকে live weather (internet প্রয়োজন)
- Temperature, humidity, wind, weather condition
- Seed rate, irrigation water, pH reference ও area calculator
- Drone, IoT, smart irrigation, remote sensing এবং AI technology information
- Responsive dashboard ও bundled website images

গুরুত্বপূর্ণ সীমাবদ্ধতা ও নিরাপত্তা
- এটি Beginner-friendly local development project; public production server নয়।
- Real production login-এর জন্য HTTPS, CSRF protection, rate limiting,
  secure secret management, password reset ও deployment hardening যোগ করতে হবে।
- Demo admin credentials public server-এ ব্যবহার কোরো না।
- Weather live; কিন্তু soil sensor readings manual/demo data, real sensor নয়।
- Drone/pump/valve control যুক্ত নেই। Toggle/technology content কোনো physical
  equipment চালায় না।
- Weather ও Google Fonts-এর জন্য internet দরকার।
- SQLite database agrinova.db ফাইলে তৈরি হবে এবং user data সেখানে থাকবে।
- Database backup করতে server বন্ধ করে agrinova.db কপি করে রাখবে।

সমস্যা হলে
- Python version দেখতে: py --version
- Browser-এ: http://127.0.0.1:5000
- START_WINDOWS.bat উইন্ডো বন্ধ কোরো না, যতক্ষণ সাইট ব্যবহার করবে।
