import json
import os
import urllib.request
from datetime import date, timedelta


USERNAME = "Bishweswar1709"

GRAPHQL_URL = "https://api.github.com/graphql"
TOKEN = os.environ["GITHUB_TOKEN"]

OUTPUT_FILE = "assets/github-streak.svg"


# ============================================================
# DATE RANGE
# ============================================================

today = date.today()
start_date = today - timedelta(days=370)


# ============================================================
# GITHUB GRAPHQL QUERY
# ============================================================

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {

  user(login: $login) {

    contributionsCollection(
      from: $from
      to: $to
    ) {

      totalContributions

      contributionCalendar {

        totalContributions

        weeks {

          contributionDays {
            date
            contributionCount
          }

        }

      }

    }

  }

}
"""


payload = {
    "query": query,
    "variables": {
        "login": USERNAME,
        "from": f"{start_date}T00:00:00Z",
        "to": f"{today}T23:59:59Z",
    },
}


# ============================================================
# REQUEST GITHUB
# ============================================================

request = urllib.request.Request(
    GRAPHQL_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "github-streak-generator",
    },
    method="POST",
)


with urllib.request.urlopen(request) as response:

    result = json.loads(
        response.read().decode("utf-8")
    )


if "errors" in result:

    print(json.dumps(result["errors"], indent=2))

    raise RuntimeError(
        "GitHub GraphQL request failed."
    )


# ============================================================
# EXTRACT CONTRIBUTIONS
# ============================================================

calendar = (
    result["data"]
    ["user"]
    ["contributionsCollection"]
    ["contributionCalendar"]
)


days = {}

for week in calendar["weeks"]:

    for contribution_day in week["contributionDays"]:

        days[
            contribution_day["date"]
        ] = contribution_day["contributionCount"]


# ============================================================
# CURRENT STREAK
# ============================================================

current_streak = 0

cursor = today


# If there is no contribution today,
# check from yesterday.

if days.get(cursor.isoformat(), 0) == 0:

    cursor -= timedelta(days=1)


while days.get(cursor.isoformat(), 0) > 0:

    current_streak += 1

    cursor -= timedelta(days=1)


# ============================================================
# LONGEST STREAK
# ============================================================

longest_streak = 0
running_streak = 0

cursor = start_date


while cursor <= today:

    contribution_count = days.get(
        cursor.isoformat(),
        0
    )

    if contribution_count > 0:

        running_streak += 1

        longest_streak = max(
            longest_streak,
            running_streak
        )

    else:

        running_streak = 0

    cursor += timedelta(days=1)


# ============================================================
# TOTAL CONTRIBUTIONS
# ============================================================

total_contributions = (
    calendar["totalContributions"]
)


# ============================================================
# GENERATE PREMIUM SVG
# ============================================================

svg = f'''<?xml version="1.0" encoding="UTF-8"?>

<svg
  width="900"
  height="260"
  viewBox="0 0 900 260"
  xmlns="http://www.w3.org/2000/svg"
>

  <defs>

    <linearGradient
      id="borderGradient"
      x1="0%"
      y1="0%"
      x2="100%"
      y2="0%"
    >

      <stop
        offset="0%"
        stop-color="#70A5FD"
      />

      <stop
        offset="50%"
        stop-color="#BF91F3"
      />

      <stop
        offset="100%"
        stop-color="#00FFFF"
      />

    </linearGradient>


    <linearGradient
      id="textGradient"
      x1="0%"
      y1="0%"
      x2="100%"
      y2="0%"
    >

      <stop
        offset="0%"
        stop-color="#70A5FD"
      />

      <stop
        offset="50%"
        stop-color="#BF91F3"
      />

      <stop
        offset="100%"
        stop-color="#00FFFF"
      />

    </linearGradient>


    <filter
      id="glow"
      x="-100%"
      y="-100%"
      width="300%"
      height="300%"
    >

      <feGaussianBlur
        stdDeviation="6"
        result="blur"
      />

      <feMerge>

        <feMergeNode in="blur"/>

        <feMergeNode in="SourceGraphic"/>

      </feMerge>

    </filter>

  </defs>


  <!-- ===================================================== -->
  <!-- BACKGROUND                                            -->
  <!-- ===================================================== -->

  <rect
    width="900"
    height="260"
    rx="24"
    fill="#0D1117"
  />


  <!-- ===================================================== -->
  <!-- BORDER                                                -->
  <!-- ===================================================== -->

  <rect
    x="2"
    y="2"
    width="896"
    height="256"
    rx="22"
    fill="none"
    stroke="url(#borderGradient)"
    stroke-width="2"
    opacity="0.9"
  />


  <!-- ===================================================== -->
  <!-- ANIMATED ORB                                          -->
  <!-- ===================================================== -->

  <circle
    cx="72"
    cy="65"
    r="7"
    fill="#70A5FD"
    filter="url(#glow)"
  >

    <animate
      attributeName="r"
      values="6;12;6"
      dur="2s"
      repeatCount="indefinite"
    />

    <animate
      attributeName="opacity"
      values="1;0.35;1"
      dur="2s"
      repeatCount="indefinite"
    />

  </circle>


  <!-- ===================================================== -->
  <!-- TITLE                                                 -->
  <!-- ===================================================== -->

  <text
    x="105"
    y="73"
    fill="#FFFFFF"
    font-family="Arial, Helvetica, sans-serif"
    font-size="28"
    font-weight="700"
  >
    GitHub Contribution Streak
  </text>


  <!-- ===================================================== -->
  <!-- CURRENT STREAK                                        -->
  <!-- ===================================================== -->

  <text
    x="75"
    y="145"
    fill="url(#textGradient)"
    font-family="Arial, Helvetica, sans-serif"
    font-size="46"
    font-weight="700"
  >
    {current_streak}
  </text>


  <text
    x="75"
    y="175"
    fill="#8B949E"
    font-family="Arial, Helvetica, sans-serif"
    font-size="14"
    font-weight="600"
    letter-spacing="1"
  >
    CURRENT STREAK
  </text>


  <!-- ===================================================== -->
  <!-- LONGEST STREAK                                        -->
  <!-- ===================================================== -->

  <text
    x="380"
    y="145"
    fill="#BF91F3"
    font-family="Arial, Helvetica, sans-serif"
    font-size="46"
    font-weight="700"
  >
    {longest_streak}
  </text>


  <text
    x="380"
    y="175"
    fill="#8B949E"
    font-family="Arial, Helvetica, sans-serif"
    font-size="14"
    font-weight="600"
    letter-spacing="1"
  >
    LONGEST STREAK
  </text>


  <!-- ===================================================== -->
  <!-- CONTRIBUTIONS                                         -->
  <!-- ===================================================== -->

  <text
    x="690"
    y="145"
    fill="#00FFFF"
    font-family="Arial, Helvetica, sans-serif"
    font-size="46"
    font-weight="700"
  >
    {total_contributions}
  </text>


  <text
    x="690"
    y="175"
    fill="#8B949E"
    font-family="Arial, Helvetica, sans-serif"
    font-size="14"
    font-weight="600"
    letter-spacing="1"
  >
    CONTRIBUTIONS
  </text>


  <!-- ===================================================== -->
  <!-- ANIMATED PROGRESS LINE                                -->
  <!-- ===================================================== -->

  <rect
    x="75"
    y="215"
    width="750"
    height="3"
    rx="2"
    fill="url(#borderGradient)"
  >

    <animate
      attributeName="opacity"
      values="0.25;1;0.25"
      dur="2.5s"
      repeatCount="indefinite"
    />

  </rect>


  <!-- ===================================================== -->
  <!-- FOOTER                                                -->
  <!-- ===================================================== -->

  <text
    x="450"
    y="242"
    text-anchor="middle"
    fill="#586069"
    font-family="Arial, Helvetica, sans-serif"
    font-size="11"
  >
    Updated automatically from GitHub contribution data
  </text>

</svg>
'''


# ============================================================
# WRITE SVG
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(svg)


# ============================================================
# LOG
# ============================================================

print("")
print("========================================")
print(" GitHub Streak Generated Successfully")
print("========================================")
print(f" Current streak : {current_streak}")
print(f" Longest streak : {longest_streak}")
print(f" Contributions  : {total_contributions}")
print("========================================")
