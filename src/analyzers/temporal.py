from collections import Counter
from datetime import timedelta

from src.analyzers.base import AnalysisResult, IAnalyzer
from src.config.settings import Settings
from src.models.chat import Chat


class TemporalAnalyzer(IAnalyzer):
    def __init__(self, config: Settings):
        self._config = config

    def analyze(self, chat: Chat) -> AnalysisResult:
        user_msgs = [m for m in chat.messages if not m.is_system]
        if not user_msgs:
            return AnalysisResult(section_id="temporal", title="Temporal Analysis", stats={})

        # 3.1 Messages per week
        week_counts: Counter = Counter()
        for m in user_msgs:
            # ISO week: Monday-based, get the Monday of that week
            iso = m.datetime.isocalendar()
            week_start = m.datetime.date() - timedelta(days=m.datetime.weekday())
            week_counts[week_start.isoformat()] += 1

        # 3.2 Messages per hour (combined)
        hour_counts = Counter(m.datetime.hour for m in user_msgs)
        hour_data = {h: hour_counts.get(h, 0) for h in range(24)}

        # 3.3 Messages per day of week (combined)
        dow_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_counts_raw = Counter(m.datetime.weekday() for m in user_msgs)
        dow_data = {dow_names[d]: dow_counts_raw.get(d, 0) for d in range(7)}

        # 3.4 Messages per month
        month_counts: Counter = Counter()
        for m in user_msgs:
            month_key = m.datetime.strftime("%Y-%m")
            month_counts[month_key] += 1

        # 3.5 Top 5 most active days (combined)
        combined_day_counts = Counter(m.datetime.date() for m in user_msgs)
        top_active_days = [
            {"date": d.strftime("%B %d, %Y"), "count": c}
            for d, c in combined_day_counts.most_common(5)
        ]

        # 3.6 Top 5 most active hours (combined, as date+hour)
        combined_hour_counts = Counter(
            (m.datetime.date(), m.datetime.hour) for m in user_msgs
        )
        top_active_hours = []
        for (d, h), c in combined_hour_counts.most_common(5):
            period = "AM" if h < 12 else "PM"
            display_hour = h % 12 or 12
            top_active_hours.append({
                "date": d.strftime("%B %d, %Y"),
                "hour": f"{display_hour} {period}",
                "count": c,
            })

        # 3.7 Longest streak
        all_dates = sorted({m.datetime.date() for m in user_msgs})
        longest_streak = 0
        current_streak = 1
        streak_start = all_dates[0] if all_dates else None
        best_streak_start = streak_start
        for i in range(1, len(all_dates)):
            if (all_dates[i] - all_dates[i - 1]).days == 1:
                current_streak += 1
            else:
                if current_streak > longest_streak:
                    longest_streak = current_streak
                    best_streak_start = streak_start
                current_streak = 1
                streak_start = all_dates[i]
        if current_streak > longest_streak:
            longest_streak = current_streak
            best_streak_start = streak_start
        best_streak_end = best_streak_start + timedelta(days=longest_streak - 1) if best_streak_start else None

        # 3.8 Longest silence
        longest_gap = timedelta(0)
        gap_start = None
        gap_end = None
        for i in range(1, len(user_msgs)):
            gap = user_msgs[i].datetime - user_msgs[i - 1].datetime
            if gap > longest_gap:
                longest_gap = gap
                gap_start = user_msgs[i - 1].datetime
                gap_end = user_msgs[i].datetime

        gap_days = longest_gap.days
        gap_hours = longest_gap.seconds // 3600

        # 3.9 Response time per person
        _MAX_RESPONSE_SECS = self._config.conversation_gap_hours * 3600
        response_times = {p: [] for p in chat.participants}
        for i in range(1, len(user_msgs)):
            curr = user_msgs[i]
            prev = user_msgs[i - 1]
            if curr.sender != prev.sender and curr.sender in response_times:
                delta = (curr.datetime - prev.datetime).total_seconds()
                if 0 < delta <= _MAX_RESPONSE_SECS:
                    response_times[curr.sender].append(delta)

        response_stats = {}
        for p, times in response_times.items():
            if times:
                times_sorted = sorted(times)
                n = len(times_sorted)
                median = times_sorted[n // 2]
                avg = sum(times) / n
                p25 = times_sorted[n // 4]
                p75 = times_sorted[(3 * n) // 4]
                fastest = times_sorted[0]
                slowest = times_sorted[-1]
                under_1m = sum(1 for t in times if t <= 60)
                under_5m = sum(1 for t in times if t <= 300)
                under_1h = sum(1 for t in times if t <= 3600)
                response_stats[p] = {
                    "median_seconds": round(median),
                    "median_display": self._format_duration(median),
                    "average_seconds": round(avg),
                    "average_display": self._format_duration(avg),
                    "p25_display": self._format_duration(p25),
                    "p75_display": self._format_duration(p75),
                    "fastest_display": self._format_duration(fastest),
                    "slowest_display": self._format_duration(slowest),
                    "under_1m": under_1m,
                    "under_5m": under_5m,
                    "under_1h": under_1h,
                    "sample_count": n,
                }

        stats = {
            "top_active_days": top_active_days,
            "top_active_hours": top_active_hours,
            "longest_streak": {
                "days": longest_streak,
                "start": best_streak_start.strftime("%B %d, %Y") if best_streak_start else None,
                "end": best_streak_end.strftime("%B %d, %Y") if best_streak_end else None,
            },
            "longest_silence": {
                "days": gap_days,
                "hours": gap_hours,
                "total_display": f"{gap_days} days, {gap_hours} hours",
                "from": gap_start.strftime("%B %d, %Y %I:%M %p") if gap_start else None,
                "to": gap_end.strftime("%B %d, %Y %I:%M %p") if gap_end else None,
            },
            "response_time": response_stats,
        }

        chart_data = {
            "weekly_trend": {
                "type": "line",
                "title": "Messages Per Week",
                "data": dict(sorted(week_counts.items())),
                "kwargs": {"xlabel": "Week", "ylabel": "Messages"},
            },
            "hourly_dist": {
                "type": "bar",
                "title": "Messages by Hour of Day",
                "data": hour_data,
                "kwargs": {"xlabel": "Hour", "ylabel": "Messages"},
            },
            "dow_dist": {
                "type": "bar",
                "title": "Messages by Day of Week",
                "data": dow_data,
                "kwargs": {"xlabel": "Day", "ylabel": "Messages"},
            },
            "monthly_trend": {
                "type": "line",
                "title": "Messages Per Month",
                "data": dict(sorted(month_counts.items())),
                "kwargs": {"xlabel": "Month", "ylabel": "Messages"},
            },
            "daily_dist": {
                "type": "histogram_kde",
                "title": "Daily Message Count Distribution",
                "data": {"values": sorted(combined_day_counts.values())},
                "kwargs": {"xlabel": "Messages in a Day", "ylabel": "Number of Days"},
            },
        }

        return AnalysisResult(
            section_id="temporal",
            title="Temporal Analysis",
            stats=stats,
            chart_data=chart_data,
        )

    @staticmethod
    def _format_duration(seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}h {m}m"
        return f"{m}m {s}s"
