# t-pomo
t-pomo is a lightweight Pomodoro timer designed for the terminal. The "t" stands for terminal, and "pomo" is short for Pomodoro, a time management technique that boosts productivity by alternating focused work sessions with short breaks.

## 🛠 Installation
Ensure you have Python installed (>=3.9), then install the package using pip:
```
pip install t-pomo
```

## 📌 Usage
Run the Pomodoro timer with:
```
t-pomo
```

You'll be prompted to enter:
1. Work duration (default: 25 minutes)
2. Break duration (default: 5 minutes)
3. Number of Pomodoro loops (default: 1)

Example:

```
Enter working time in minutes [25]: 30
Enter break time in minutes [5]: 10
Enter countdown loop time [1]: 4
```
This starts a 30-minute work session followed by a 10-minute break, repeating 4 times.

After each break, an inspirational quote is displayed to keep you motivated.

Use `[p] PAUSE | [q] STOP` to control the timer.

## 🖼 Preview
The timer features an ASCII-style countdown with a modern, solid block progress bar. The interface changes color dynamically to indicate urgency:
- **Cyan**: Relaxed (> 50% time remaining)
- **Yellow**: Warning (20-50% time remaining)
- **Red**: Urgent (< 20% time remaining)
- Work
![timer_display_sample_work](https://github.com/uuboyscy/t-pomo/raw/main/timer_display_sample_work.png)
![timer_display_sample_work](https://github.com/uuboyscy/t-pomo/raw/main/timer_display_sample_work_middle.png)
- Break
![timer_display_sample_break](https://github.com/uuboyscy/t-pomo/raw/main/timer_display_sample_break.png)
